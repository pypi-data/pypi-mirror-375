from cmbot import BaseProcess
from cmbot import logger

__version__ = '1.0.0'


class RpaProcess(BaseProcess):
    process_name = '$process_name'
    max_attempts = $max_attempts
    version = __version__

    def __init__(self):
        super().__init__()

    def front_hook(self):
        """
        流程前钩子:用于流程初始化，例如：
        1. 清理临时文件夹
        2. 清理进程等
        """

    def finally_hook(self):
        """
        流程后钩子:用于流程结束后的收尾，例如：
        1. 清理临时文件夹
        2. 清理主流程开启的进程等
        """

    def main_process(self, *args, **kwargs):
        """
        主流程，业务主要逻辑
        """


if __name__ == '__main__':
    RpaProcess().run()
