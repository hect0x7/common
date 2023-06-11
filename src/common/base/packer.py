from common import Callable, Type, Dict, Union, Optional, Any, Tuple


class Packer:

    def pack(self, obj: object, filepath: str):
        raise NotImplementedError

    def unpack(self, filepath: str, clazz=None) -> Any:
        """
        反序列化得到对象

        :param filepath: 文件路径
        :param clazz: 预期的class对象，Packer不一定会使用此参数（如YmlPacker就不会，而JsonPacker会）。
        此参数需要是callable，并且能返回一个对象，即：obj = clazz()
        :return:
        """
        raise NotImplementedError


class AbstractSerializablePacker(Packer):
    pack_mode = 'w'
    unpack_mode = 'r'
    encoding = 'utf-8'

    def pack(self, obj: object, filepath: str):
        self.with_file(filepath,
                       self.pack_mode,
                       self.dump,
                       obj=obj,
                       )

    def unpack(self, filepath: str, clazz=None) -> Any:
        return self.with_file(filepath,
                              self.unpack_mode,
                              self.load,
                              clazz=clazz,
                              )

    def dump(self, fp, obj: object):
        raise NotImplementedError

    def load(self, fp, clazz: Optional[Type]) -> Any:
        raise NotImplementedError

    @classmethod
    def with_file(cls,
                  filepath: str,
                  mode: str,
                  visitor: Callable,
                  **kwargs
                  ):
        with open(filepath, mode, encoding=cls.encoding) as f:
            return visitor(f, **kwargs)


class YmlPacker(AbstractSerializablePacker):

    def dump(self, fp, obj):
        import yaml
        yaml.dump(obj,
                  fp,
                  allow_unicode=True,
                  indent=2,
                  )

    def load(self, fp, clazz) -> Any:
        import yaml
        return yaml.load(fp, yaml.FullLoader)

    @staticmethod
    def add_constructor(tag, constructor: Callable):
        from yaml import add_constructor
        add_constructor(tag, constructor)


class JsonPacker(AbstractSerializablePacker):

    def dump(self, fp, obj, indent=2):
        from json import dump
        dump(self.to_dict(obj),
             fp,
             ensure_ascii=False,
             indent=indent,
             )

    def load(self, fp, clazz) -> Any:
        from json import load
        dic: dict = load(fp)
        if clazz is None:
            return dic

        obj: object = clazz()
        obj.__dict__.update(dic)
        return obj

    @classmethod
    def to_dict(cls, obj):
        """将对象转换为字典"""
        if hasattr(obj, "__dict__"):
            d = dict(obj.__dict__)
            for key, value in d.items():
                if hasattr(value, "__dict__"):
                    d[key] = cls.to_dict(value)
            return d
        elif isinstance(obj, list):
            return [cls.to_dict(item) for item in obj]
        else:
            return obj


class PicklePacker(AbstractSerializablePacker):
    pack_mode = 'wb'
    unpack_mode = 'rb'
    encoding = None

    def dump(self, fp, obj: object):
        import pickle
        pickle.dump(obj, fp)

    def load(self, fp, clazz: Optional[Type]) -> Any:
        import pickle
        return pickle.load(fp)


class PackerFactory:
    mode_yml = 'yml'
    mode_json = 'json'
    mode_py_pickle = 'pickle'

    mode_mapping: Dict[str, Union[Packer, Type[Packer]]] = {
        mode_yml: YmlPacker,
        mode_json: JsonPacker,
        mode_py_pickle: PicklePacker,

    }

    @classmethod
    def get_packer(cls, mode: str) -> Packer:
        packer_caller = cls.mode_mapping.get(mode, None)

        if packer_caller is None:
            raise AssertionError(f"unknown mode: '{mode}', acceptable modes={list(cls.mode_mapping.keys())}")

        packer: Packer
        if isinstance(packer_caller, Packer):
            packer_caller: Packer
            packer = packer_caller
        else:
            packer_caller: Type[Packer]
            packer = packer_caller()
            # cache
            cls.mode_mapping[mode] = packer

        return packer


class PackerUtil:

    @staticmethod
    def get_packer(filepath: str):
        mode_intelligent = filepath[filepath.rfind('.') + 1::]
        return PackerFactory.get_packer(mode=mode_intelligent)

    @classmethod
    def pack(cls, obj: object, filepath: str, packer=None, only_fields=False):
        packer = packer or cls.get_packer(filepath)

        # 只序列化类属性
        if only_fields is True:
            import inspect
            obj = inspect.getmembers(obj, lambda f: not inspect.ismethod(f))
            obj = dict(filter(lambda f: not f[0].startswith('_'), obj))

        packer.pack(obj, filepath)

    @classmethod
    def unpack(cls, filepath: str, clazz=None, packer=None) -> Tuple[Any, Packer]:
        packer = packer or cls.get_packer(filepath)
        return packer.unpack(filepath, clazz), packer
