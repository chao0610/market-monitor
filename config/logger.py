import logging
import sys
from datetime import datetime
from pathlib import Path

def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """设置日志记录器"""
    
    # 创建日志目录
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    if log_file is None:
        log_file = log_dir / f"{datetime.now().strftime('%Y%m%d')}.log"
    else:
        log_file = log_dir / log_file
    
    # 创建记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 清除已有处理器
    logger.handlers.clear()
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    return logger
