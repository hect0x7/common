from .time_util import time_stamp


def timeit(topic: str = '程序运行', print_template='耗时{:.02f}秒', loop_times=1):
    if loop_times < 0:
        raise AssertionError('循环次数不可小于0，因为无意义')

    def with_print_template(func):
        def timeit_func(*args, **kwargs):
            x = time_stamp(as_int=False)
            obj = None
            for _ in range(loop_times):
                obj = func(*args, **kwargs)
            print(topic + print_template.format(time_stamp(as_int=False) - x))
            return obj

        return timeit_func

    return with_print_template


decorator_thread_force_async_kwargs_key = "__force_sync__"


def thread(func, daemon=True):
    from threading import Thread

    def thread_exec(*args, **kwargs):
        check_force_sync = kwargs.get(decorator_thread_force_async_kwargs_key,
                                      False)

        if check_force_sync is True:
            del kwargs[decorator_thread_force_async_kwargs_key]
            return func(*args, **kwargs)

        t = Thread(target=func, args=args, kwargs=kwargs, daemon=daemon)
        t.start()
        return t

    return thread_exec


def disable(_func):
    def do_nothing_func(*_args, **_kwargs):
        pass

    return do_nothing_func
