from common import Dict, List, Thread, current_thread, atexit_register, atexit_unregister
from .multi_task import wait_a_task


class ThreadRegistry:

    def __init__(self):
        self.thread_mapping: Dict[str, List[Thread]] = {}

    def register(self,
                 tag: str,
                 thread: Thread = None,
                 ):
        if thread is None:
            thread = current_thread()

        setattr(thread, tag, True)
        if tag in self.thread_mapping:
            self.thread_mapping[tag].append(thread)
        else:
            self.thread_mapping[tag] = [thread]

    def stop(self,
             tag: str,
             finish_message=None,
             wait_finish=False,
             ) -> List[Thread]:
        if tag not in self.thread_mapping:
            return []

        thread_ls = self.thread_mapping[tag]
        for thread in thread_ls:
            if getattr(thread, tag) is True and thread.is_alive():
                setattr(thread, tag, False)

                if finish_message is not None:
                    print(finish_message)
                if wait_finish is True:
                    wait_a_task(thread)

        return thread_ls

    def stop_all(self, finish_message=None):
        for tag in self.thread_mapping.keys():
            self.stop(tag, finish_message)


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
