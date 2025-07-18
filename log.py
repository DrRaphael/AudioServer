import logging
import os
import sys
from datetime import datetime
from logging import Formatter, Logger, FileHandler
from typing import Optional, Union


# 定义ANSI颜色代码
class Color:
    RESET = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'


class CustomFormatter(Formatter):
    """自定义格式化器，支持彩色输出和自定义时间格式"""

    # 为不同日志级别定义不同的格式和颜色
    FORMATS = {
        logging.DEBUG: f"{Color.BLUE}[%(asctime)s.%(msecs)03d] [DEBUG] [{Color.BLUE}%(filename)s:%(lineno)d{Color.RESET}] {Color.BLUE}%(message)s{Color.RESET}",
        logging.INFO: f"{Color.GREEN}[%(asctime)s.%(msecs)03d] [INFO] [{Color.GREEN}%(filename)s:%(lineno)d{Color.RESET}] {Color.GREEN}%(message)s{Color.RESET}",
        logging.WARNING: f"{Color.YELLOW}[%(asctime)s.%(msecs)03d] [WARNING] [{Color.YELLOW}%(filename)s:%(lineno)d{Color.RESET}] {Color.YELLOW}%(message)s{Color.RESET}",
        logging.ERROR: f"{Color.RED}[%(asctime)s.%(msecs)03d] [ERROR] [{Color.RED}%(filename)s:%(lineno)d{Color.RESET}] {Color.RED}%(message)s{Color.RESET}",
        logging.CRITICAL: f"{Color.MAGENTA}[%(asctime)s.%(msecs)03d] [CRITICAL] [{Color.MAGENTA}%(filename)s:%(lineno)d{Color.RESET}] {Color.MAGENTA}%(message)s{Color.RESET}"
    }

    def format(self, record):
        """根据日志级别应用不同的格式"""
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = Formatter(log_fmt, datefmt='%y-%m-%d %H:%M:%S')
        return formatter.format(record)


class FileFormatter(Formatter):
    """文件输出的格式化器，不包含颜色代码"""

    def __init__(self):
        super().__init__('[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(filename)s] [%(lineno)d] %(message)s',
                         datefmt='%y-%m-%d %H:%M:%S')


class SingleRunFileHandler(FileHandler):
    """每次运行覆盖之前内容的文件处理器"""

    def __init__(self, filename, mode='w', encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)


def setup_logger(
        name: str = __name__,
        log_dir: str = 'logs',
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        create_dir: bool = True,
        encoding: str = 'utf-8'
) -> Logger:
    """
    设置一个支持控制台和文件输出的日志记录器

    参数:
        name: 日志记录器名称
        log_dir: 日志文件目录
        console_level: 控制台输出的日志级别
        file_level: 文件输出的日志级别
        create_dir: 是否创建日志目录
        encoding: 文件编码

    返回:
        配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # 设置最低级别，由各处理器控制具体级别

    # 避免重复添加处理器
    if not logger.handlers:
        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(CustomFormatter())
        logger.addHandler(console_handler)

        # 确保日志目录存在
        if create_dir and log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # 创建全量日志文件处理器（追加模式）
        all_log_path = os.path.join(log_dir, 'log.log')
        all_file_handler = FileHandler(all_log_path, mode='a', encoding=encoding)
        all_file_handler.setLevel(file_level)
        all_file_handler.setFormatter(FileFormatter())
        logger.addHandler(all_file_handler)

        # 创建单次运行日志文件处理器（覆盖模式）
        single_run_log_path = os.path.join(log_dir, 'log.tmp.log')
        single_run_handler = SingleRunFileHandler(single_run_log_path, mode='w', encoding=encoding)
        single_run_handler.setLevel(file_level)
        single_run_handler.setFormatter(FileFormatter())
        logger.addHandler(single_run_handler)

    return logger

logger = setup_logger(
    name='my_logger',
    console_level=logging.DEBUG,
    file_level=logging.INFO
)

logger.info("*************************************************************************************************************")
logger.info("日志系统启动")
logger.info("*************************************************************************************************************")