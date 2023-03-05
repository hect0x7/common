import time


def sleep(second: float):
    time.sleep(second)


def time_stamp(as_int=True) -> int:
    return int(time.time()) if as_int is True else time.time()


def format_ts(ts: float = None, f_time: str = "%Y-%m-%d %H:%M:%S") -> str:
    return time.strftime(f_time, time.localtime(ts))


def sleep_conditional_func(batch_count,
                           sleep_period,
                           debug=False,
                           debug_message_template="[count: {}次, 睡眠: {}秒]",
                           ):
    # noinspection PyUnusedLocal
    def sleep_interval(count, *args, **kwargs) -> int:
        if count != 0 and count % batch_count == 0:
            if debug is True:
                print(debug_message_template.format(count, sleep_period))
            return sleep_period
        else:
            return 0

    return sleep_interval
