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
        import sys
        try:
            print(self.msg)
            self.user_input = sys.stdin.readline()
        except BaseException:
            return

    def get_input(self, timeout):
        self.join(timeout)  # 等待指定时间
        if self.is_alive():  # 如果线程还在运行，说明没有输入
            return None
        else:
            return self.user_input

    def join_wait_input(self, exit_msg):
        self.start()
        sentinel = object()
        self.user_input = sentinel

        while True:
            # 设置1秒超时
            user_input = self.get_input(1)

            # 如果线程异常退出了
            if user_input is sentinel:
                raise KeyboardInterrupt(exit_msg)

            # 已收到用户输入
            if user_input is not None:
                return
