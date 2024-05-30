import threading


class ListenInputThread(threading.Thread):
    """
    author: AI
    example:
    ```python
    input_thread = InputThread('请输入内容')
    while True:
        user_input = input_thread.get_input(1)  # 设置1秒超时
        if user_input is not None:
            print(f"你输入了：{user_input}")
            break
        else:  # 超时处理，这里简单打印一个点作为示例
            print(".", end='', flush=True)
    ```

    """

    def __init__(self, msg):
        super().__init__()
        self.user_input = None
        self.msg = msg

    def run(self):
        try:
            self.user_input = input(self.msg)
        except (KeyboardInterrupt, UnicodeDecodeError):
            raise AssertionError

    def get_input(self, timeout):
        self.join(timeout)  # 等待指定时间
        if self.is_alive():  # 如果线程还在运行，说明没有输入
            print(self.msg)
            return None
        else:
            return self.user_input
