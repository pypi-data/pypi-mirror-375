import sys
from .process_data import read_data_odps
import torch
import json
import torch.distributed as dist
from torch.utils.data import DataLoader, IterableDataset
# from daily_funcs import *  # 确保你可以访问 daily_funcs 中所需的模块和函数
from transformers import AutoModelForCausalLM,AutoTokenizer
from accelerate import Accelerator
from accelerate.utils import gather_object
import common_io
from odps import ODPS
import os
from enum import Enum
from tqdm import tqdm
import threading
from vllm import LLM, SamplingParams
from .odps_utils import get_odps_columns_name,gen_output_table_schema,parse_table_path,create_odps_table,OutputType
# CUDA_VISIBLE_DEVICES=0,1 accelerate launch test_daily_func.py
# # python -m torch.distributed.run --nproc_per_node=1 test_daily_func.py




def is_dist_avail_and_initialized():
    if not dist.is_available():
        return False
    if not dist.is_initialized():
        return False
    return True

def get_world_size():
    if not is_dist_avail_and_initialized():
        return 1
    return dist.get_world_size()

def get_rank():
    if not is_dist_avail_and_initialized():
        return 0
    return dist.get_rank()

class OdpsTableIterableDataset(IterableDataset):
    def __init__(self, table_path, selected_cols,tokenizer,prompt_cols_idx=None,prompt_cols_name='prompt',system_prompt='',max_length=1024, slice_id=0, slice_count=1):
        self.table_path = table_path
        reader = common_io.table.TableReader(table_path,
                                             slice_id=slice_id,
                                             slice_count=slice_count,
                                             num_threads=0)
        self.tokenizer = tokenizer
        self.prompt_cols_idx = prompt_cols_idx
        self.prompt_cols_name = prompt_cols_name
        self.selected_cols = selected_cols
        self.row_count = reader.get_row_count()
        self.max_length = max_length
        self.system_prompt = system_prompt
        self.rank = get_rank()
        self.world_size = get_world_size()

        self.per_worker = int(self.row_count / self.world_size)
        self.start_index, self.end_index = self._get_slice_range(self.row_count, self.rank, self.world_size)

        reader.close()
        super(OdpsTableIterableDataset, self).__init__()
        print("current gpu is:{}, world_size is:{}, table total_row_count:{}, start_pos:{}, end_pos:{}".format(self.rank, self.world_size, self.row_count, self.start_index, self.end_index))

    def __iter__(self):
        worker_info = torch.utils.data.get_worker_info()
        if worker_info is None:
            worker_id = 0
            num_workers = 1
        else:
            worker_id = worker_info.id
            num_workers = worker_info.num_workers
        print("worker_id:{}, num_workers:{}".format(worker_id, num_workers))

        table_start, table_end = self._get_slice_range(self.per_worker, worker_id, num_workers, self.start_index)
        table_path = "{}?start={}&end={}".format(self.table_path, table_start, table_end)
        print("table_path:%s" % table_path)

        def table_data_iterator():
            reader = common_io.table.TableReader(table_path,selected_cols=self.selected_cols)
            selected_cols_list = self.selected_cols.split(',')
            while True:
                try:
                    records = reader.read(num_records=1, allow_smaller_final_batch=True)
                    for item in records:
                        new_item = {}
                        for j in range(len(selected_cols_list)):
                            new_item[selected_cols_list[j]] = item[j]
                        if self.prompt_cols_idx is not None:
                            prompt = item[self.prompt_cols_idx]
                        else:
                            prompt = new_item[self.prompt_cols_name]
                        # prompt = "Give me a short introduction to large language model."
                        messages = [
                            {"role": "system", "content": self.system_prompt},
                            {"role": "user", "content": prompt}
                        ]
                        text = self.tokenizer.apply_chat_template(
                            messages,
                            tokenize=False,
                            add_generation_prompt=True
                        )
                        new_item['vllm_input'] = text
                except common_io.exception.OutOfRangeException:
                    reader.close()
                    break
                yield new_item
        return table_data_iterator()

    def _get_slice_range(self, row_count, worker_id, num_workers, baseline=0):
        size = int(row_count / num_workers)
        split_point = row_count % num_workers
        if worker_id < split_point:
            start = worker_id * (size + 1) + baseline
            end = start + (size + 1)
        else:
            start = split_point * (size + 1) + (worker_id - split_point) * size + baseline
            end = start + size
        return start, end

    def __len__(self):
        return self.row_count


class JsonFileIterableDataset(IterableDataset):
    def __init__(self, file_path, tokenizer,prompt_cols_idx,prompt_cols_name='prompt',system_prompt='', max_length=1024):
        """
        Args:
            file_path (str): Path to the input file.
            tokenizer: The tokenizer to use for processing text.
            max_length (int): Maximum length for tokenized input.
        """
        self.file_path = file_path
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.system_prompt = system_prompt
        self.prompt_cols_idx = prompt_cols_idx
        self.prompt_cols_name = prompt_cols_name
        # Determine file format from the file extension
        _, file_extension = os.path.splitext(file_path)
        if file_extension == '.jsonl':
            self.file_format = 'jsonl'
        elif file_extension == '.json':
            self.file_format = 'json'
        else:
            raise ValueError("Unsupported file format: must be '.json' or '.jsonl'")

        # Calculate the number of lines or entries in the file
        if self.file_format == 'jsonl':
            with open(self.file_path, 'r') as f:
                self.row_count = sum(1 for _ in f)
        elif self.file_format == 'json':
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.row_count = len(data)

        # Initialize rank and world size for distributed processing
        self.rank = get_rank()
        self.world_size = get_world_size()

        self.per_worker = int(self.row_count / self.world_size)
        self.start_index, self.end_index = self._get_slice_range(self.row_count, self.rank, self.world_size)

        print(f"current gpu is: {self.rank}, world_size is: {self.world_size}, total_row_count: {self.row_count}, start_pos: {self.start_index}, end_pos: {self.end_index}")

    def __iter__(self):
        worker_info = torch.utils.data.get_worker_info()
        if worker_info is None:
            worker_id = 0
            num_workers = 1
        else:
            worker_id = worker_info.id
            num_workers = worker_info.num_workers

        print(f"worker_id: {worker_id}, num_workers: {num_workers}")

        file_start, file_end = self._get_slice_range(self.per_worker, worker_id, num_workers, self.start_index)

        def jsonl_data_iterator():
            with open(self.file_path, 'r') as f:
                for i, line in enumerate(f):
                    if i < file_start:
                        continue
                    if i >= file_end:
                        break
                    yield json.loads(line)

        def json_data_iterator():
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                for i in range(file_start, file_end):
                    yield data[i]
        
        # Select iterator based on file format
        data_iterator = jsonl_data_iterator if self.file_format == 'jsonl' else json_data_iterator

        # Process data from iterator
        for data in data_iterator():
            # Assume 'text' is the key for the input text in the JSON
            if self.prompt_cols_idx is not None:
                key = list(data.keys())[self.prompt_cols_idx]
                prompt = data.get(key, '')
            else:
                prompt = data.get(self.prompt_cols_name, '')
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            new_item = {'vllm_input':text, **data}
            yield new_item

    def _get_slice_range(self, row_count, worker_id, num_workers, baseline=0):
        size = int(row_count / num_workers)
        split_point = row_count % num_workers
        if worker_id < split_point:
            start = worker_id * (size + 1) + baseline
            end = start + (size + 1)
        else:
            start = split_point * (size + 1) + (worker_id - split_point) * size + baseline
            end = start + size
        return start, end

    def __len__(self):
        return self.row_count

def collate_fn(batch):
    """Custom collate function to separate tensor and non-tensor data."""
    tensor_batch = {}
    non_tensor_batch = {}
    for key in batch[0].keys():
        if key not in ['input_ids','attention_mask']:
            non_tensor_batch[key] = [item[key] for item in batch]
    return tensor_batch, non_tensor_batch

class JSONLWriter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.lock = threading.Lock()

    def write_records(self, records):
        with self.lock:
            with open(self.file_path, 'a') as f:
                for item in records:
                    f.write(json.dumps(item) + '\n')
    def close(self):
        pass

def infer_llm_vllm(
    model_path,
    input_data_path,
    output_data_path,
    prompt_cols_idx=None,
    prompt_cols_name=None,
    system_prompt='',
    batch_size = 32,
    selected_cols='',
    vllm_config = {},
    vllm_generation_config={}
):
    # os.environ["VLLM_DP_RANK"] = 2 # str(global_dp_rank)
    # os.environ["VLLM_DP_RANK_LOCAL"] = '0'# str(local_dp_rank) # str(local_dp_rank)
    # os.environ["VLLM_DP_SIZE"] = '1' # str(dp_size)
    assert prompt_cols_idx or prompt_cols_name, "One of prompt_cols_idx and prompt_cols_name must exist."
    assert system_prompt != '',"system_prompt is none, which may cause unexpected result."
    sampling_params = SamplingParams(**vllm_generation_config)
    tokenizer = AutoTokenizer.from_pretrained(model_path,padding_side="left")
    model = LLM(model=model_path,**vllm_config)
    all_col_names = get_odps_columns_name(input_data_path)
    if selected_cols == '':
        selected_cols = ','.join(all_col_names)
    select_col_indexes = []
    for cols in selected_cols.split(','):
        select_col_indexes.append(all_col_names.index(cols))
    
    if input_data_path.startswith('odps'):
        dataset = OdpsTableIterableDataset(
            input_data_path,
            selected_cols=selected_cols,
            prompt_cols_idx=prompt_cols_idx,
            prompt_cols_name=prompt_cols_name,
            system_prompt=system_prompt,
            max_length = max_prompt_length,
            tokenizer=tokenizer
        )
    else:
        dataset = JsonFileIterableDataset(
            input_data_path,
            tokenizer=tokenizer,
            prompt_cols_idx=prompt_cols_idx,
            prompt_cols_name=prompt_cols_name,
            max_length = max_prompt_length,
            system_prompt=system_prompt
        )
    dataloader = DataLoader(dataset, batch_size=batch_size, num_workers=1,collate_fn=collate_fn)

    # dataloader = accelerator.prepare(dataloader) # 有非tensor，不能用accelerator

    if output_data_path.startswith('odps'):
        create_odps_table(input_data_path, output_data_path, select_col_indexes=select_col_indexes)
        writer = common_io.table.TableWriter(output_data_path,slice_id=0)
    else:
        dir_path = os.path.dirname(output_data_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        writer = JSONLWriter(output_data_path)
    # print('258:',writer)
    all_results = []
    for tensor_batch, non_tensor_batch in tqdm(dataloader,desc='Infer Results ing'):
        # print('426:',sampling_params)
        outputs = model.generate(
            non_tensor_batch['vllm_input'],
            sampling_params
        )
        batch_results = []
        for i in range(len(outputs)):
            result = {key: non_tensor_batch[key][i] for key in non_tensor_batch if key not in ['input_ids', 'attention_mask']}
            result['generated_results'] = outputs[i].outputs[0].text
            batch_results.append(result)

        # Gather results across all processes
        # gathered_results = accelerator.gather_for_metrics(batch_results)
        if output_data_path.startswith('odps'):
            for result in batch_results:
                records = writer.write(list(result.values()),col_indices=list(range(len(result))))
        else:
            writer.write_records(batch_results)
        all_results.extend(batch_results)

    writer.close()
    # print(all_results)
    # all_results = accelerator.gather_for_metrics(all_results)
    # all_results = accelerator.gather(all_results)
    # 如果在主进程上，输出或处理结果
    # if accelerator.is_main_process:
    #     save_data(all_results,'test_output.jsonl')