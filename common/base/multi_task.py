from common import Thread, Process, \
    List, Callable, Iterable, Optional, Any, Union, Type, Dict
from common import process_args_kwargs, process_single_arg_to_args_and_kwargs, \
    is_function, sleep


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
    _tasks_of_launcher_context = []

    @classmethod
    def of_launcher_context_tasks(cls) -> list:
        return cls._tasks_of_launcher_context

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
        cls._tasks_of_launcher_context.append(task)

        return task

    @classmethod
    def wait_tasks(cls, task_ls):
        do_remove = task_ls is not cls._tasks_of_launcher_context
        for task in task_ls:
            cls.wait_task(task, do_remove)

    @classmethod
    def wait_task(cls, task, remove_task_from_launcher_context=True):
        while task.is_alive():
            task.join(timeout=1)

        if remove_task_from_launcher_context:
            if task in cls._tasks_of_launcher_context:
                cls._tasks_of_launcher_context.remove(task)

    @classmethod
    def sleep_with_condition(cls, condition, index, obj):
        if condition is None:
            return

        interval_to_sleep = condition(index, obj) if is_function(condition) else condition

        if isinstance(interval_to_sleep, int) or isinstance(interval_to_sleep, float):
            if interval_to_sleep > 0:
                sleep(interval_to_sleep)
        else:
            # condition 不是以下类型，则暂未实现以何种方式调用
            # 1. 函数
            # 2. int
            # 3. float
            raise NotImplementedError

    @classmethod
    def build_daemon(cls):
        return MultiTaskLauncher({"daemon": True})


def multi_task_launcher(iter_objs: Iterable,
                        apply_each_obj_func: Callable[[Any], None],
                        TaskType: Union[Type[Thread], Type[Process]],
                        wait_finish=True,
                        sleep_interval: Any = -1,
                        **meta_data_kwargs
                        ) -> list:
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
                          apply_each_obj_func: Callable[[Any], None],
                          wait_finish=True,
                          sleep_interval=-1,
                          **meta_data_kwargs
                          ) -> List[Thread]:
    return multi_task_launcher(iter_objs,
                               apply_each_obj_func,
                               Thread,
                               wait_finish,
                               sleep_interval,
                               **meta_data_kwargs
                               )


def multi_process_launcher(iter_objs: Iterable,
                           apply_each_obj_func: Callable[[Any], None],
                           wait_finish=True,
                           sleep_interval=-1,
                           **meta_data_kwargs
                           ) -> List[Process]:
    return multi_task_launcher(iter_objs,
                               apply_each_obj_func,
                               Process,
                               wait_finish,
                               sleep_interval,
                               **meta_data_kwargs
                               )


wait_task = MultiTaskLauncher.wait_task
wait_tasks = MultiTaskLauncher.wait_tasks
