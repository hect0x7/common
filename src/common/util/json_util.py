from json import load, loads, dump, dumps

from .typing_util import *

json_loads = loads
json_load = load

json_dumps = dumps
json_dump = dump


class DictModel:

    def __init__(self, data: dict):
        if data is None:
            raise AssertionError(f"data is None")

        self._data = data

    def __getattr__(self, item):
        v = self._data[item]
        if isinstance(v, (list, tuple)):
            v = [self.__class__(e) if isinstance(e, dict) else e for e in v]
        elif isinstance(v, dict):
            v = self.__class__(v)

        setattr(self, item, v)
        return v

    def __getitem__(self, item):
        return self._data[item]

    def __contains__(self, item):
        return item in self._data

    @property
    def src_dict(self):
        return self._data

    def get(self, *args, **kwargs):
        return self._data.get(*args, **kwargs)


def dict_2_obj(data: dict):
    return DictModel(data)


def json_loadf(filepath,
               encoding='utf-8',
               decode_unicode=False,
               ):
    from .file_util import file_not_exists
    if file_not_exists(filepath):
        raise AssertionError(f"不存在的json文件路径：{filepath}")

    with open(filepath, 'r', encoding=encoding) as f:
        if decode_unicode is False:
            return json_load(f)
        else:
            from .sys_util import parse_unicode_escape_text
            return json_loads(parse_unicode_escape_text(f.read()))


def json_dumpf(obj, fp, encoding='utf-8', indent=2):
    with open(fp, 'w', encoding=encoding) as f:
        json_dump(obj, f, indent=indent)


def accpet_json(fp, accept_v: Callable[[Any], None] = None, accpet_k: Callable[[str], None] = None):
    def __accept_json_keys_values(data):
        if isinstance(data, list):
            for each in data:
                __accept_json_keys_values(each)

        elif isinstance(data, dict):
            for k, v in data.items():
                if accpet_k is not None:
                    accpet_k(k)
                __accept_json_keys_values(v)
        else:
            if accept_v is not None:
                accept_v(data)

    data = json_load(fp)

    if accpet_k is not None or accept_v is not None:
        __accept_json_keys_values(data)

    return data


def keys_of_json(data) -> Generator:
    if isinstance(data, list):
        for each in data:
            keys_of_json(each)

    elif isinstance(data, dict):
        for k, v in data.items():
            yield k
            keys_of_json(v)


def values_of_json(data) -> Generator:
    if isinstance(data, list):
        for each in data:
            yield from values_of_json(each)

    elif isinstance(data, dict):
        for v in data.values():
            yield from values_of_json(v)

    else:
        yield data
