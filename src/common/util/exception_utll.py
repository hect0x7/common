import sys
import threading
import traceback
from typing import List, Tuple, Type
import types

ExceptHookArgs = Tuple[Type[BaseException], BaseException, types.TracebackType]


def print_exception(except_info: ExceptHookArgs):
    """
    打印所有未捕获异常
    """
    if len(except_info) == 0:
        return

    print(except_info)
    print(len(except_info))
    print(f"Unhandled exception: {except_info[0]} - {except_info[1]}")
    print(*traceback.format_exception(*except_info), sep='')


class UncaughtExceptionHandler:

    def __init__(self):
        self.uncaught_exceptions: List[ExceptHookArgs] = []
        self.handle_exception_func = print_exception  # 默认的处理方式是打印

    @property
    def except_count(self):
        """
        for tests
        """
        return len(self.uncaught_exceptions)

    # noinspection PyUnresolvedReferences, PyAttributeOutsideInit, PyProtectedMember
    def register(self, at_exit=True):
        # 注册全局的sys.excepthook
        sys.excepthook = self.hook_uncaught_exception

        if sys.version_info >= (3, 8):
            threading.excepthook = self.hook_uncaught_exception
        else:
            import warnings
            warnings.warn('python version <= 3.7 may not work')
            self.threading_org_hook = threading._format_exc
            threading._format_exc = self.hook_uncaught_exception

        if at_exit is True:
            # 自动在程序退出时，处理所有未捕获异常
            import atexit
            atexit.unregister(self.handle_all_exception)
            atexit.register(self.handle_all_exception)

    def handle_all_exception(self):
        """
        处理所有未捕获异常
        """
        func = self.handle_exception_func
        for except_info in self.uncaught_exceptions:
            func(except_info)

    def hook_uncaught_exception(self, except_info):
        """
        将未捕获异常添加到列表中
        """
        # noinspection PyTypeChecker
        print(except_info, len(except_info))
        self.uncaught_exceptions.append(except_info)

        if sys.version_info < (3, 8):
            return self.threading_org_hook()


def global_caught(at_exit=True, except_handler=None):
    uncaught_exception_handler = UncaughtExceptionHandler()

    if except_handler is not None:
        uncaught_exception_handler.handle_exception_func = uncaught_exception_handler

    def decorator(func):
        uncaught_exception_handler.register(at_exit)

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
