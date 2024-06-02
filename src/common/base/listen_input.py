import threading


class ListenInputThread(threading.Thread):
    """
    InputThread('请输入内容').join_wait_input('遇到ctrl+c或其他异常，强制退出')
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

            print(self.msg)
