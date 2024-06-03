from common import Thread, Process, \
    List, Callable, Iterable, Optional, Any, Union, Type, Dict, Tuple, \
    process_args_kwargs, process_single_arg_to_args_and_kwargs, \
    is_function, sleep, current_thread


class MultiTaskLauncher:
    OptionalTask = Union[Thread, Process, None]

    def __init__(self, task_meta_data: Optional[Dict[str, Any]] = None):
        if task_meta_data is None:
            task_meta_data = {}

        self.task_ls: list = []
        self.task_meta_data_kwargs: dict = task_meta_data

    def create_task(self,
                    target: Callable,
                    args: Optional[Any] = None,
                    kwargs: Optional[dict] = None,
                    TaskType=Thread) -> Union[Thread, Process]:
        args, kwargs = process_args_kwargs(args, kwargs)
        t = self.new_task(TaskType,
                          target=target,
                          args=args,
                          kwargs=kwargs,
                          meta_data=self.task_meta_data_kwargs)
        t.start()
        self.task_ls.append(t)
        return t

    def add_task(self, task: OptionalTask):
        if task is not None and task.is_alive():
            self.task_ls.append(task)

    def wait_finish(self):
        self.wait_tasks(self.task_ls)

    """
    收集所有的 Task
    """
    tasks_of_launcher_context = []

    @classmethod
    def new_task(cls,
                 TaskType: Type,
                 target: Callable,
                 args: Iterable,
                 kwargs: dict,
                 meta_data: dict):

        task = TaskType(target=target,
                        args=args,
                        kwargs=kwargs,
                        **meta_data)
        cls.tasks_of_launcher_context.append(task)

        return task

    @classmethod
    def sleep_with_condition(cls, condition, index, obj):
        if condition is None:
            return

        interval_to_sleep = condition(index, obj) if is_function(condition) else condition

        if isinstance(interval_to_sleep, int) or isinstance(interval_to_sleep, float):
            if interval_to_sleep > 0:
                cls.do_sleep(interval_to_sleep)
        else:
            # condition 不是以下类型，则暂未实现以何种方式调用
            # 1. 函数
            # 2. int
            # 3. float
            raise NotImplementedError

    @classmethod
    def build_daemon(cls):
        return MultiTaskLauncher({"daemon": True})

    @classmethod
    def wait_a_task(cls, task):
        if task == current_thread():
            return

        while task.is_alive():
            task.join(timeout=1)

    @classmethod
    def wait_tasks(cls, tasks: Iterable[Any]):
        for task in tasks:
            if isinstance(task, list):
                cls.wait_tasks(task)
                continue

            cls.wait_a_task(task)

    do_sleep = sleep

def multi_task_launcher(iter_objs: Iterable,
                        apply_each_obj_func: Callable,
                        TaskType: Union[Type[Thread], Type[Process]],
                        wait_finish=True,
                        sleep_interval: Any = -1,
                        batch_size: Optional[int] = None,
                        **meta_data_kwargs
                        ) -> list:
    if batch_size is not None:
        return multi_task_launcher_batch(
            iter_objs,
            apply_each_obj_func,
            batch_size,
            TaskType,
            sleep_interval,
        )

    task_ls: list = []

    for index, obj in enumerate(iter_objs):
        args, kwargs = process_single_arg_to_args_and_kwargs(obj)
        meta_data = {
            meta_arg: meta_value(index) if is_function(meta_value) else meta_value
            for meta_arg, meta_value in meta_data_kwargs.items()
        }

        # set daemon default True to ensure that
        # program can be forced to exit by ctrl + c successfully in windows
        meta_data.setdefault("daemon", True)

        task = MultiTaskLauncher.new_task(TaskType=TaskType,
                                          target=apply_each_obj_func,
                                          args=args,
                                          kwargs=kwargs,
                                          meta_data=meta_data)
        task.start()
        task_ls.append(task)

        MultiTaskLauncher.sleep_with_condition(sleep_interval, index + 1, obj)

    if wait_finish is True:
        MultiTaskLauncher.wait_tasks(task_ls)

    return task_ls


def multi_thread_launcher(iter_objs: Iterable,
                          apply_each_obj_func: Callable,
                          wait_finish=True,
                          sleep_interval=-1,
                          batch_size=None,
                          **meta_data_kwargs
                          ) -> List[Thread]:
    return multi_task_launcher(iter_objs,
                               apply_each_obj_func,
                               Thread,
                               wait_finish,
                               sleep_interval,
                               batch_size,
                               **meta_data_kwargs
                               )


def multi_process_launcher(iter_objs: Iterable,
                           apply_each_obj_func: Callable,
                           wait_finish=True,
                           sleep_interval=-1,
                           batch_size=None,
                           **meta_data_kwargs,
                           ) -> List[Process]:
    return multi_task_launcher(iter_objs,
                               apply_each_obj_func,
                               Process,
                               wait_finish,
                               sleep_interval,
                               batch_size,
                               **meta_data_kwargs
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


def multi_task_launcher_batch(iter_objs: Iterable,
                              apply_each_obj_func: Callable,
                              batch_size: int,
                              TaskType=Thread,
                              sleep_interval: Any = -1,
                              **meta_data_kwargs):
    meta_data_kwargs.setdefault("daemon", True)
    task_ls = []

    for index, obj in enumerate(iter_objs):
        args, kwargs = process_single_arg_to_args_and_kwargs(obj)
        meta_data = {
            meta_arg: meta_value(index) if is_function(meta_value) else meta_value
            for meta_arg, meta_value in meta_data_kwargs.items()
        }

        task = MultiTaskLauncher.new_task(TaskType=TaskType,
                                          target=apply_each_obj_func,
                                          args=args,
                                          kwargs=kwargs,
                                          meta_data=meta_data)
        task.start()
        task_ls.append(task)

        if len(task_ls) == batch_size:
            MultiTaskLauncher.wait_tasks(task_ls)
            task_ls.clear()

        MultiTaskLauncher.sleep_with_condition(sleep_interval, index + 1, obj)

    if task_ls:
        MultiTaskLauncher.wait_tasks(task_ls)

    return task_ls


def multi_call(func, iter_objs, launcher=multi_thread_launcher, wait=True) -> Union[dict, Tuple[dict, List]]:
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

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super().__init__(group, self.deco_target(target, args, kwargs), name, args, kwargs, daemon=daemon)
        self._cache = None

    def get(self) -> Any:
        cache = self._cache

        if cache is not None:
            return cache

        # noinspection PyUnresolvedReferences
        if not self._started.is_set() and not self.is_alive():
            self.start()

        self.join()
        return self._cache

    def deco_target(self, target, args, kwargs):
        if kwargs is None:
            kwargs = {}

        def deco_cache():
            result = target(*args, **kwargs)
            self._cache = result

        return deco_cache

    def __call__(self, *args, **kwargs):
        return self.get()


def cache_async_run(func) -> CacheRunner:
    cache_runner = CacheRunner(target=func, daemon=True)
    cache_runner.start()
    return cache_runner


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
