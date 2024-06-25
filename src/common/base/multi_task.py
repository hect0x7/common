from ..util import Thread, Process, \
    List, Callable, Iterable, Optional, Any, Union, Type, Dict, Tuple, \
    process_args_kwargs, process_single_arg_to_args_and_kwargs, \
    current_thread
from .registry import StopThreadFlag


class MultiTaskLauncher:
    Task = Union[Thread, Process]
    TaskClass = Union[Type[Thread], Type[Process]]

    def __init__(self, task_metadata: Optional[Dict[str, Any]] = None):
        if task_metadata is None:
            task_metadata = {}

        self.flag: Optional[StopThreadFlag] = None
        self.task_ls: list = []
        self.task_metadata: dict = task_metadata

    def check_stop_flag(self):
        if self.flag and self.flag.should_stop():
            self.flag.raise_stop_exception()

    def create_task(self,
                    target: Callable,
                    args: Optional[Any] = None,
                    kwargs: Optional[dict] = None,
                    clazz: TaskClass = Thread,
                    start=True,
                    ) -> Union[Thread, Process]:
        args, kwargs = process_args_kwargs(args, kwargs)

        task = clazz(target=target,
                     args=args,
                     kwargs=kwargs,
                     **self.task_metadata,
                     )
        self.task_ls.append(task)

        if self.flag is not None:
            self.flag.mark_run(task)

        if start:
            task.start()

        return task

    def wait_finish(self):
        for task in self.task_ls:
            self.wait_task(task)

    def wait_task(self, task: Task):
        if task == current_thread():
            return

        while task.is_alive():
            self.check_stop_flag()
            task.join(timeout=0.1)

    def pause(self, duration: float):
        from time import sleep
        if duration < 0.1:
            sleep(duration)

        times = int(duration / 0.1)
        for _ in range(times):
            self.check_stop_flag()
            sleep(0.1)

        self.check_stop_flag()
        sleep(duration - 0.1 * times)

    @classmethod
    def build_daemon(cls):
        return MultiTaskLauncher({"daemon": True})


def multi_task_launcher(clazz: Union[Type[Thread], Type[Process]],
                        iter_objs: Iterable,
                        apply_each_obj_func: Callable,
                        wait_finish=True,
                        *,
                        batch_size: Optional[int] = None,
                        pause_duration=-1,
                        flag: Optional[StopThreadFlag] = None,
                        **metadata
                        ) -> MultiTaskLauncher:
    metadata.setdefault("daemon", True)
    launcher = MultiTaskLauncher(metadata)
    launcher.flag = flag

    for index, obj in enumerate(iter_objs):
        args, kwargs = process_single_arg_to_args_and_kwargs(obj)

        task = launcher.create_task(target=apply_each_obj_func,
                                    args=args,
                                    kwargs=kwargs,
                                    clazz=clazz,
                                    )
        if batch_size is not None and (index + 1) % batch_size == 0:
            launcher.pause(pause_duration)

    if wait_finish is True:
        launcher.wait_finish()

    return launcher


def multi_thread_launcher(iter_objs: Iterable,
                          apply_each_obj_func: Callable,
                          wait_finish=True,
                          batch_size: Optional[int] = None,
                          pause_duration=-1,
                          flag: Optional[StopThreadFlag] = None,
                          **metadata
                          ) -> MultiTaskLauncher:
    return multi_task_launcher(Thread,
                               iter_objs,
                               apply_each_obj_func,
                               wait_finish,
                               batch_size=batch_size,
                               pause_duration=pause_duration,
                               flag=flag,
                               **metadata
                               )


def thread_pool_executor(
        iter_objs: Iterable,
        apply_each_obj_func: Callable,
        wait_finish=True,
        max_workers=None,
):
    ret = []
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor(max_workers)
    for obj in iter_objs:
        args, kwargs = process_single_arg_to_args_and_kwargs(obj)
        future = executor.submit(apply_each_obj_func, *args, **kwargs)
        ret.append(future)

    executor.shutdown(wait_finish)
    return ret


def multi_call(func, iter_objs, launcher=multi_thread_launcher, wait=True):
    ret_dict = {}

    def get_ret(obj):
        ret = func(obj)
        ret_dict[obj] = ret

    task_ls = launcher(
        iter_objs=iter_objs,
        apply_each_obj_func=get_ret,
        wait_finish=wait
    )

    if wait is not True:
        return ret_dict, task_ls

    return ret_dict


"""
提供阻塞获取一个线程的target函数返回值
"""


class CacheRunner(Thread):

    def __init__(self, target, args=(), kwargs=None, flag=None):
        super().__init__(target=self.wrap_func(target, args, kwargs))
        self.daemon = True

        self._sentinel = object()
        self._cache = self._sentinel
        self._flag = flag

    def wrap_func(self, target: callable, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}

        def wrapper():
            self._cache = target(*args, **kwargs)
            return

        wrapper.__name__ = target.__name__
        return wrapper

    def get(self) -> Any:
        cache = self._cache

        if cache is not self._sentinel:
            return cache

        # noinspection PyUnresolvedReferences
        if not self._started.is_set() and not self.is_alive():
            self.start()

        while self.is_alive():
            if self._flag and self._flag.should_stop():
                self._flag.raise_stop_exception()
            self.join(0.1)

        return self._cache

    def __call__(self, *args, **kwargs):
        return self.get()


def invoke_all(args_func_list: List[Tuple], wait=True, executor=None):
    if executor is None:
        from concurrent.futures import ThreadPoolExecutor
        executor = ThreadPoolExecutor()

    future_ls = []
    for args, func in args_func_list:
        args, kwargs = process_single_arg_to_args_and_kwargs(args)
        future = executor.submit(func, *args, **kwargs)
        future_ls.append(future)

    executor.shutdown(wait)

    if wait:
        return [f.result() for f in future_ls]
    else:
        return future_ls


def cache_run(func):
    runner = CacheRunner(func)
    runner.start()
    return runner
