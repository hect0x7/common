from common import fix_windir_name, current_thread, fix_filepath, atexit_register
from .packer import PackerUtil


class SaveableEntity:
    when_del_save_file = True
    after_save_print_info = True

    def __del__(self):
        if self.when_del_save_file is not True:
            return

        filepath = f"{fix_filepath(self.save_base_dir(), is_dir=True)}" \
                   f"{fix_windir_name(self.save_file_name())}"

        atexit_register(self.save_to_file, filepath)

    def save_file_name(self) -> str:
        raise NotImplementedError

    def save_base_dir(self):
        raise NotImplementedError

    def save_to_file(self, filepath):
        PackerUtil.pack(self, filepath)
        if self.after_save_print_info is True:
            print(f"[{current_thread().name}]保存文件: {filepath}")


class IterableEntity:
    cache_getitem_result = False
    cache_field_name = 'IterableEntity_cache_items_dict'

    def __getitem__(self, item):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __iter__(self):
        for item in range(len(self)):
            yield self.__getitem__(item)

    def getitem(self, item):
        # 不使用缓存
        if self.cache_getitem_result is False:
            return self.__getitem__(item)
        else:
            field_name = self.cache_field_name

            # 缓存还没有创建
            if not hasattr(self, field_name):
                setattr(self, field_name, {item: self.__getitem__(item)})

            # 缓存已创建
            caches: dict = getattr(self, field_name)

            # 缓存命中
            if item in caches:
                return caches[item]

            # 缓存未命中
            obj = self.__getitem__(item)
            caches[item] = obj
            return obj
