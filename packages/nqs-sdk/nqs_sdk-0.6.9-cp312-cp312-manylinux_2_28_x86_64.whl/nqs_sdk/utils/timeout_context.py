import platform
import signal
import threading


def timeout_handler(signum, frame):
    raise TimeoutError("Policy execution timed out")


class TimeoutContext:
    """Cross-platform timeout context manager"""

    def __init__(self, timeout_seconds: int):
        self.timeout_seconds = timeout_seconds
        self.timer = None
        self.timed_out = False

    def _timeout_callback(self):
        self.timed_out = True
        raise TimeoutError("Policy execution timed out")

    def __enter__(self):
        if platform.system() != "Windows":
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.timeout_seconds)
        else:
            self.timer = threading.Timer(self.timeout_seconds, self._timeout_callback)
            self.timer.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if platform.system() != "Windows":
            signal.alarm(0)
        else:
            if self.timer:
                self.timer.cancel()

        if self.timed_out and not issubclass(exc_type, TimeoutError):
            raise TimeoutError("Policy execution timed out")
