import threading


class ThreadFactory:
    def __init__(self, fix_name: str):
        self.fix_name = fix_name
        self.counter = 0

    def start_thread(self, *args, **kwargs):
        thread_name = f"{self.fix_name}-{self.counter}"
        self.counter += 1
        t = threading.Thread(name=thread_name, *args, **kwargs)
        return t
