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


def thread(func):
    from threading import Thread

    def thread_exec(*args, **kwargs):
        t = Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        t.start()
        return t

    return thread_exec


def disable(_func):
    def do_nothing_func(*_args, **_kwargs):
        pass

    return do_nothing_func


class SimpleCacheWrapper:

    def __init__(self, func, cache_dict, cache_miss_msg, cache_hit_msg):
        self.func = func
        if cache_dict is None:
            cache_dict = {}

        self.cache_dict = cache_dict
        self.cache_miss_msg = cache_miss_msg
        self.cache_hit_msg = cache_hit_msg

    def key(self, args: tuple, kwargs: dict):
        return str(args) + str(kwargs)

    def invoke(self, args, kwargs):
        return self.func(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        key = self.key(args, kwargs)
        cache_dict = self.cache_dict

        if key in cache_dict:
            # cache hit
            value = cache_dict[key]
            self.hit_callback(key, value)
        else:
            # cache miss
            value = self.invoke(args, kwargs)
            self.miss_callback(key, value)
            cache_dict[key] = value

        return value

    def miss_callback(self, key, value):
        miss_msg = self.cache_miss_msg
        if miss_msg is not None:
            print(miss_msg.format(key, value))

    def hit_callback(self, key, value):
        hit_msg = self.cache_hit_msg
        if hit_msg is not None:
            print(hit_msg.format(key, value))


def cache(
        cache_dict=None,
        cache_hit_msg=None,
        cache_miss_msg=None,
):
    def wrapper(func):
        return SimpleCacheWrapper(func, cache_dict, cache_miss_msg, cache_hit_msg)

    return wrapper


enable_cache = cache
