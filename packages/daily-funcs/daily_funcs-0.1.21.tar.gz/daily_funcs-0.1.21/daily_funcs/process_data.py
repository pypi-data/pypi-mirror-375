import json
import pandas as pd
from tqdm import tqdm
import math
import warnings
import datetime
def read_data(
    file_path,
    input_type=None,
    return_type='json',
    abandon_wrong_lines=False,
    keep_keys=None,
    remove_keys=None
):
    if input_type is None:
        input_type = file_path.split('.')[-1]
    if keep_keys is not None and remove_keys is not None:
        raise ValueError("keep_keys 和 remove_keys 只能设置一个")
    
    # 统一读取，全部读成 list[dict] 或 DataFrame
    if input_type == 'jsonl':
        wrong_lines = 0
        data = []
        with open(file_path, 'r', encoding='utf-8') as fp:
            for line_number, line in enumerate(fp, start=1):
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    if abandon_wrong_lines:
                        wrong_lines += 1
                        warnings.warn(f"Error decoding JSON on line {line_number}. Line will be skipped.")
                        continue
                    else:
                        raise ValueError(f"Error decoding JSON on line {line_number}. You can set abandon_wrong_lines=True to skip it.")
                data.append(item)
            if wrong_lines > 0:
                warnings.warn(f'Abandoned {wrong_lines} lines in the original jsonl file.', UserWarning)
    elif input_type == 'json':
        with open(file_path, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
    elif input_type == 'csv':
        df = pd.read_csv(file_path)
        data = df.to_dict(orient='records')
    elif input_type == 'parquet':
        df = pd.read_parquet(file_path)
        data = df.to_dict(orient='records')
    elif input_type == 'pickle':
        df = pd.read_pickle(file_path)
        data = df.to_dict(orient='records')
    elif input_type == 'feather':
        df = pd.read_feather(file_path)
        data = df.to_dict(orient='records')
    elif input_type == 'hdf5':
        df = pd.read_hdf(file_path)
        data = df.to_dict(orient='records')
    elif input_type == 'xlsx':
        df = pd.read_excel(file_path)
        data = df.to_dict(orient='records')
    else:
        raise ValueError(f"Unsupported input type: {input_type}")

    # ------------------------------
    # 加入 keep_keys / remove_keys 逻辑
    # ------------------------------
    if keep_keys is not None:
        data = [
            {k: v for k, v in item.items() if k in keep_keys}
            for item in data
        ]
    elif remove_keys is not None:
        data = [
            {k: v for k, v in item.items() if k not in remove_keys}
            for item in data
        ]

    # ------------------------------
    # 输出格式 return_type 支持 'json', 'csv', 'df'
    # ------------------------------
    if return_type == 'csv':
        df = pd.DataFrame(data)
        return df.to_csv(index=False)
    elif return_type == 'df':
        return pd.DataFrame(data)
    else:  # 默认json或list[dict]
        return data

def save_data(data,file_path,output_type=None):
    if output_type is None:
        output_type = file_path.split('.')[-1]
    if output_type == 'jsonl':
        with open(file_path,'w') as fp:
            for item in data:
                fp.write(json.dumps(item,ensure_ascii=False) + '\n')
    elif output_type == 'json':
        with open(file_path,'w') as fp:
            json.dump(data,fp,ensure_ascii=False,indent=2)
    elif output_type == 'csv':
        data.to_csv(file_path,index=False)
    else:
        raise ValueError(f"Unsupported output type: {output_type}")


def filter_jsonl_keys(input_path, output_path, remove_keys=None, keep_keys=None):
    """
    - remove_keys: 要移除的字段列表（如 ["a", "b"]）
    - keep_keys: 只保留这几个字段（如 ["id", "text"]）；如果未设置，则按 remove_keys 删除。
    只能二选一：传 remove_keys 或 keep_keys。
    """
    assert not (remove_keys and keep_keys), "remove_keys 和 keep_keys 只能设置一个"
    with open(input_path, 'r', encoding='utf-8') as fin, \
         open(output_path, 'w', encoding='utf-8') as fout:
        for line in fin:
            obj = json.loads(line)
            if keep_keys:
                new_obj = {k: obj[k] for k in keep_keys if k in obj}
            elif remove_keys:
                new_obj = {k: v for k, v in obj.items() if k not in remove_keys}
            else:
                new_obj = obj
            fout.write(json.dumps(new_obj, ensure_ascii=False) + '\n')
    print(f'Done. Saved to {output_path}')

def read_data_odps(path,selected_cols='',batch_size=2048):
    import common_io
    reader = common_io.table.TableReader(path,
                                        slice_id=0,
                                        slice_count=1,
                                        num_threads=12,
                                        selected_cols=selected_cols,
                                        capacity=2048)
    total_records_num = reader.get_row_count()
    print("total_records_num:", total_records_num)
    data = []
    batch_num = math.ceil(total_records_num / batch_size)
    values = []
    if selected_cols != '':
        selected_cols_list = selected_cols.split(',')
        for i in tqdm(range(0, batch_num)):
            records = reader.read(batch_size, allow_smaller_final_batch=True)
            for item in records:
                new_item = {}
                for j in range(len(selected_cols_list)):
                    new_item[selected_cols_list[j]] = item[j]
                data.append(new_item)
    else:
        for i in tqdm(range(0, batch_num)):
            records = reader.read(batch_size, allow_smaller_final_batch=True)
            for item in records:
                data.append(item)
    return data

def excel_to_jsonl(excel_path, jsonl_path, sheet_name=0):
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    records = df.to_dict(orient='records')
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    print(f'Success: {len(records)} rows written to {jsonl_path}')

def jsonl_to_excel(jsonl_path, excel_path):
    data = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    df = pd.DataFrame(data)
    df.to_excel(excel_path, index=False)
    print(f'Success: {len(df)} rows written to {excel_path}')

def csv_to_jsonl(csv_path, jsonl_path):
    df = pd.read_csv(csv_path)
    records = df.to_dict(orient='records')
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    print(f'Success: {len(records)} rows written to {jsonl_path}')
def jsonl_to_json(jsonl_path, json_path):
    data = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'Success: {len(data)} objects written to {json_path}')

def json_to_jsonl(json_path, jsonl_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f'Success: {len(data)} objects written to {jsonl_path}')

def upload2odps(data, outputs, slice_id=0, batch_size=2048):
    import common_io
    with common_io.table.TableWriter(outputs, slice_id=slice_id) as table_writer:
        values = []
        count_unicode_decode_error = 0
        total_records_num = len(data)
        batch_num = math.ceil(total_records_num / batch_size)
        for i in range(0, batch_num):
            records = data[i * batch_size:(i+1)* batch_size]
            # 定义其字段
            keys = records[0].keys()
            for item in records:
                values.append(list(item.values()))
            if i == 0:
                print(values[:1])

            if (i+1)%10==0 and (i+1)%50!=0:
                print(f"[{datetime.datetime.now()}] {i + 1}/{batch_num} batches processed. current row num is {len(values)}")

            if (i + 1) % 50 == 0:
                print (values[:1])
                print(f"[{datetime.datetime.now()}] {i + 1}/{batch_num} batches write to table.")
                table_writer.write(values, col_indices=tuple(range(0,len(keys))))
                values = []
                
        if (len(values)>0):
            table_writer.write(values, col_indices=tuple(range(0,len(keys))))
            print(f"[{datetime.datetime.now()}] {i + 1}/{batch_num} batches write to table sucess.")



def to_single_line(s: str) -> str:
    """多行文本转成一行，换行变 \\n"""
    return s.replace('\n', '\\n')

def to_multi_line(s: str) -> str:
    """一行文本里的 \\n 恢复为多行换行"""
    return s.replace('\\n', '\n')


# excel_to_jsonl('/Users/gouqi/Downloads/precision_recall_data (8).xlsx', '/Users/gouqi/Downloads/precision_recall_data (8).jsonl')
# jsonl_to_excel('/Users/gouqi/Downloads/precision_recall_data (8).jsonl', '/Users/gouqi/Downloads/precision_recall_data (8)2.xlsx')
