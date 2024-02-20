from typing import Dict, List, TypeVar, Type, Optional, Iterable

from common import Thread, current_thread, atexit_register, atexit_unregister
from .multi_task import MultiTaskLauncher


class ThreadRegistry:

    def __init__(self):
        self.thread_mapping: Dict[str, List[Thread]] = {}

    def register(self,
                 tag: str,
                 thread: Thread = None,
                 ):
        if thread is None:
            thread = current_thread()

        setattr(thread, tag, True)
        if tag in self.thread_mapping:
            self.thread_mapping[tag].append(thread)
        else:
            self.thread_mapping[tag] = [thread]

    def stop(self,
             tag: str,
             finish_message=None,
             wait_finish=False,
             ) -> List[Thread]:
        if tag not in self.thread_mapping:
            return []

        thread_ls = self.thread_mapping[tag]
        for thread in thread_ls:
            if getattr(thread, tag) is True and thread.is_alive():
                setattr(thread, tag, False)

                if finish_message is not None:
                    print(finish_message)
                if wait_finish is True:
                    MultiTaskLauncher.wait_a_task(thread)

        return thread_ls

    def stop_all(self, finish_message=None):
        for tag in self.thread_mapping.keys():
            self.stop(tag, finish_message)


class AtexitRegistry:

    def __init__(self,
                 atexit_hooks,
                 register_at_once=True
                 ) -> None:
        self.atexit_hooks = atexit_hooks
        if register_at_once is True:
            self.register()

    def register(self):
        for func in self.atexit_hooks:
            func, args = func if isinstance(func, tuple) else (func, None)
            atexit_register(func, args)

    def unregister(self):
        for func in self.atexit_hooks:
            atexit_unregister(func if not isinstance(func, tuple) else func[0])


# 注册组件
class ComponentRegistry:
    registry: Dict[Type, Dict[str, Type]] = {}

    @classmethod
    def register_component(cls, interface: type, key_name: str, variables: Optional[Iterable[Type]] = None):
        if variables is None:
            variables = filter(lambda v: isinstance(v, type), globals().values())

        cls.registry.setdefault(interface, {})
        for clazz in variables:
            if clazz != interface and issubclass(clazz, interface):
                try:
                    key = getattr(clazz, key_name)
                except AttributeError:
                    raise AssertionError(f'register failed, {clazz} must have a "{key_name}" attribute')

                cls.registry[interface][key] = clazz

        return cls.registry[interface]

    __T = TypeVar('__T')

    @classmethod
    def get_impl_clazz(cls, interface: Type[__T], key: str) -> Type[__T]:
        if interface not in cls.registry:
            raise AssertionError(f'interface {interface} not found in registry')

        clazz: Optional[Type[cls.__T]] = cls.registry[interface].get(key, None)
        if clazz is None:
            raise AssertionError(f'key {key} not found in registry of {interface}')

        return clazz

    @classmethod
    def get_all_impl(cls, interface: type) -> Dict[str, Type]:
        return cls.registry[interface]
