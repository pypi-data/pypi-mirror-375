# daily_funcs/__init__.py

__all__ = ['read_data', 'save_data', 'read_data_odps', 'upload2odps', 'infer_llm_pt', 'infer_llm_vllm']

def load_module(module_name, attribute_name):
    import importlib
    module = importlib.import_module(module_name)
    return getattr(module, attribute_name)

def __getattr__(name):
    if name == "read_data":
        return load_module('daily_funcs.process_data', 'read_data')
    elif name == "save_data":
        return load_module('daily_funcs.process_data', 'save_data')
    elif name == "read_data_odps":
        return load_module('daily_funcs.process_data', 'read_data_odps')
    elif name == "upload2odps":
        return load_module('daily_funcs.process_data', 'upload2odps')
    elif name == "infer_llm_pt":
        return load_module('daily_funcs.infer_pt', 'infer_llm_pt')
    elif name == "infer_llm_vllm":
        return load_module('daily_funcs.infer_vllm', 'infer_llm_vllm')
    else:
        raise AttributeError(f"module 'daily_funcs' has no attribute '{name}'")