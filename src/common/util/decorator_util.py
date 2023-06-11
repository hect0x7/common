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


def enable_cache(
        key_arg_index=0,
        cache_dict=None,
        cache_hit_msg=None,
        cache_miss_msg=None,
        key_kwarg_name='key',
        accept_none_value_cache=False,
):
    """
    usage:

    as simple
    ```
    @enable_cache()
    def get(key):
        ...
    ```

    as advanced
    ```
    @classmethod
    @enable_cache(
        1,
        cache_hit_msg='cache hit! [{}]→[{}]',
        cache_miss_msg='cache miss! [{}]←[{}]'
    )
    def get(cls, key, *args, **kwargs):
        ...
    ```

    :param key_arg_index: 作为键的参数所在参数列表的位置，优先级高于 key_kwarg_name
    :param key_kwarg_name: 作为键的参数所在具名参数列表的位置，优先级低于 key_arg_index
    :param cache_dict: 缓存存放容器
    :param cache_hit_msg: 缓存命中时打印的消息
    :param cache_miss_msg: 缓存没命中时打印的消息
    :param accept_none_value_cache: 是否接收空值作为cache
    """
    if cache_dict is None:
        cache_dict = {}

    def wrapper(func):

        def cache_control_func(*args, **kwargs):
            if len(args) > key_arg_index:
                key = args[key_arg_index]
            elif key_kwarg_name in kwargs:
                key = kwargs[key_kwarg_name]
            else:
                raise NotImplementedError(f'Key is not found in both args and kwargs: {args}, {kwargs}. '
                                          f'Using index {key_arg_index} and name "{key_kwarg_name}"')

            if key in cache_dict:
                # cache hit
                value = cache_dict[key]
                if cache_hit_msg is not None:
                    print(cache_hit_msg.format(key, value))

                return value

            # cache miss
            value = func(*args, **kwargs)
            if cache_miss_msg is not None:
                print(cache_miss_msg.format(key, value))

            # accept None as a value of caches?
            if value is None and accept_none_value_cache is False:
                # do not accept, return
                return value

            cache_dict[key] = value
            return value

        return cache_control_func

    return wrapper
