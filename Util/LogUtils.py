import time
import os
import logging
logfile_path = ".\\logs"
log_name = "calmcar_http"
class Log:
    def __init__(self, logfile_path=logfile_path, log_name=log_name):
        self.set_log_env(logfile_path, log_name)
    def set_log_env(self,logfile_path, log_name):
        # 创建日志对象logger
        self.logger = logging.getLogger(__name__)
        # 设置日志级别
        self.logger.setLevel(level=logging.INFO)
        # 设置日志的格式
        formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

        self.logfile_path = logfile_path

        """在log文件中输出日志"""
        # 日志文件名称显示一天的日志
        self.log_name_path = os.path.join(self.logfile_path, "{}_{}.log".format(log_name, time.strftime('%Y_%m_%d')))
        # 创建文件处理程序并实现追加
        self.file_log = logging.FileHandler(self.log_name_path, 'a', encoding='utf-8')
        # 设置日志文件里的格式
        self.file_log.setFormatter(formatter)
        # 设置日志文件里的级别
        self.file_log.setLevel(logging.INFO)
        # 把日志信息输出到文件中
        self.logger.addHandler(self.file_log)
        # 关闭文件
        self.file_log.close()

        """在控制台输出日志"""
        # 日志在控制台
        self.console = logging.StreamHandler()
        # 设置日志级别
        self.console.setLevel(logging.INFO)
        # 设置日志格式
        self.console.setFormatter(formatter)
        # 把日志信息输出到控制台
        self.logger.addHandler(self.console)
        # 关闭控制台日志
        self.console.close()

        # 在新增handler时判断是否为空
        if not self.logger.handlers:
            self.logger.addHandler(self.file_log)
            self.logger.addHandler(self.console)


    def get_log(self):
        return self.logger
