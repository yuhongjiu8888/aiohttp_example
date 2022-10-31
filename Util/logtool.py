import logging
import os
import sys
import time


def log(logfile_path, log_name):
    logger = logging.getLogger(__name__)
    # 设置日志级别
    logger.setLevel(level=logging.DEBUG)
    # 设置日志的格式
    formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    logfile_path = logfile_path

    """在log文件中输出日志"""
    # 日志文件名称显示一天的日志
    log_name_path = os.path.join(logfile_path, "{}_{}.log".format(log_name, time.strftime('%Y_%m_%d')))
    # 创建文件处理程序并实现追加
    file_log = logging.FileHandler(log_name_path, 'a', encoding='utf-8')
    # 设置日志文件里的格式
    file_log.setFormatter(formatter)
    # 设置日志文件里的级别
    file_log.setLevel(logging.DEBUG)
    # 把日志信息输出到文件中
    logger.addHandler(file_log)
    # 关闭文件
    file_log.close()

    """在控制台输出日志"""
    # 日志在控制台
    console = logging.StreamHandler()
    # 设置日志级别
    console.setLevel(logging.DEBUG)
    # 设置日志格式
    console.setFormatter(formatter)
    # 把日志信息输出到控制台
    logger.addHandler(console)
    # 关闭控制台日志
    console.close()
    return logger

#增加一行
logger = log(".\\logs", "calmcar_http")