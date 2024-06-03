from typing import Dict, TypeVar, Type, Optional, Iterable

from common import atexit_register, atexit_unregister, current_thread


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
    def register_component(cls, interface: type, key_name: str, variables: Iterable):
        cls.registry.setdefault(interface, {})
        for clazz in variables:
            if isinstance(clazz, type) and clazz != interface and issubclass(clazz, interface):
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


class StopThreadFlag:
    RUN = True
    STOP = False

    def __init__(self, key):
        self.key = key
        self._marked = set()

    @property
    def marked_thread_set(self):
        return self._marked

    def should_stop(self, thread=None):
        try:
            return self.STOP == getattr(thread or current_thread(), self.key)
        except AttributeError:
            print(f"{self.key} is not set for current thread {current_thread()}")

    def mark_run(self, thread=None):
        thread = thread or current_thread()
        setattr(thread, self.key, self.RUN)
        self._marked.add(thread)

    def mark_stop(self, thread):
        thread = thread or current_thread()
        setattr(thread, self.key, self.STOP)

    def mark_stop_for_all(self):
        for thread in self._marked:
            self.mark_stop(thread)
