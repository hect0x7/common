from common import Dict, List, Callable, Any, Optional


class HookChainContainer:
    """
    封装数据结构：Dict[int, List[callable]]
    键是int -> chain_key
    值是List[callable] -> chain

    """

    def __init__(self):
        self.__chain_dict: Dict[int, List[Callable]] = {}

    def get_chain(self, chain_key: int) -> List[Callable]:
        return self.__chain_dict.get(chain_key)

    def register_hook(self, callback: Callable, chain_key: int):
        if callback is None:
            raise AssertionError(f"Parameter 'callback' mustn't be None (key is {chain_key})")

        chain = self.get_chain(chain_key)

        if chain is None:
            self.__chain_dict[chain_key] = [callback]
        else:
            self.__chain_dict[chain_key].append(callback)

    def register_ifnn(self, callback: Optional[Callable], chain_key: int):
        if callback is not None:
            self.register_hook(callback, chain_key)

    def add_chain(self, chain_key: int):
        if chain_key in self.__chain_dict:
            raise KeyError(f"chain_key已存在: '{chain_key}'")
        self.__chain_dict[chain_key] = []

    def clear_chain(self, chain_key: int = None):
        if chain_key is None:
            self.__chain_dict.clear()
        else:
            self.get_chain(chain_key).clear()


class ProcessHook(HookChainContainer):
    ProcessFunc = Callable[[Any], Any]
    process_chain_key = 1

    def __init__(self):
        super().__init__()
        self.add_chain(self.process_chain_key)

    def process(self, value: Any) -> Any:
        process_chain = self.process_chain()

        for processor in process_chain:
            value = processor(value)

        return value

    def process_chain(self) -> List[Callable]:
        return self.get_chain(self.process_chain_key)


class JudgeHook(HookChainContainer):
    JudgeFunc = Callable[[Any], bool]
    judge_chain_key = 2

    def __init__(self):
        super().__init__()
        self.add_chain(self.judge_chain_key)

    def judge(self, value: Any, condition: bool = True) -> bool:
        if condition is False:
            return False

        judge_chain = self.judge_chain()

        for asserter in judge_chain:
            if asserter(value) is False:
                return False

        return condition

    def judge_chain(self) -> List[Callable]:
        return self.get_chain(self.judge_chain_key)


class ProcessSupport:

    @staticmethod
    def apply_callback(callback: ProcessHook.ProcessFunc,
                       data,
                       error_msg: str = '回调返回值不能为None'):
        if callback is None:
            return data

        data = callback(data)
        if data is None:
            raise AssertionError(f"{error_msg}：callback={callback}")

        return data
