import time


def sleep(second: float):
    time.sleep(second)


def time_stamp(as_int=True) -> int:
    return int(time.time()) if as_int is True else time.time()


def format_ts(ts: float = None, f_time: str = "%Y-%m-%d %H:%M:%S") -> str:
    return time.strftime(f_time, time.localtime(ts))


def unformat_ts(time_str: str, pattern: str = "%Y-%m-%d %H:%M:%S", as_int=True) -> int:
    from datetime import datetime
    ts = datetime.strptime(time_str, pattern).timestamp()
    return int(ts) if as_int else ts
