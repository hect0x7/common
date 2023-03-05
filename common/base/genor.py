from common import Optional, Iterable, Callable
from .hook import JudgeHook, ProcessHook


class Genor(JudgeHook, ProcessHook):

    def product(self) -> Iterable:
        raise NotImplementedError

    def remaining(self) -> int:
        raise NotImplementedError

    def giveback(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def append(self, obj: object):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError


class ListGenerator(Genor):

    def __init__(self, data: Iterable):
        super().__init__()
        # 转为 list
        data = data if isinstance(data, list) else list(data)
        self.element_list = data
        self.max_index = len(data)
        self.done_list = [False] * self.max_index
        self.__index = 0

    def register_hook(self, callback: Callable, chain_key: int):
        super().register_hook(callback, chain_key)

        if chain_key is self.judge_chain_key:
            self.reset()

    def product(self):
        # ordered
        while self.__index < self.max_index:
            if self.done_list[self.__index] is False:
                self.done_list[self.__index] = True
                yield self.process(self.element_list[self.__index])
                # check for give-back case
                if self.done_list[self.__index] is True:
                    self.__index += 1
                    continue
            else:
                self.__index += 1

    def remaining(self) -> int:
        # return len(tuple(i for i in filter(lambda done: done is False, self.done_list)))
        return self.max_index - self.__index - self.done_list[self.__index]

    def giveback(self):
        self.done_list[self.__index] = False

    def reset(self):
        self.element_list = [it for it in self.element_list if self.judge(self.process(it)) is True]
        self.max_index = len(self.element_list)
        self.done_list = [False] * self.max_index
        self.__index = 0

    def __iter__(self):
        return self.product()

    def __len__(self):
        return self.max_index

    def append(self, obj: object):
        if self.judge(obj) is True:
            self.element_list.append(obj)
            self.max_index += 1
            self.done_list.append(False)


class GeneratorFactory:

    @staticmethod
    def get_generator(data: Iterable,
                      judge_hook: Optional[JudgeHook.JudgeFunc] = None,
                      process_hook: Optional[ProcessHook.ProcessFunc] = None) -> Genor:
        list_genor = ListGenerator(data)
        list_genor.register_ifnn(process_hook, ProcessHook.process_chain_key)
        list_genor.register_ifnn(judge_hook, JudgeHook.judge_chain_key)
        return list_genor
