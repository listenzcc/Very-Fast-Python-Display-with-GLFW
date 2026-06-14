from multiprocessing import Queue, Process
from pathlib import Path
from qlsdk.rsc import *
from loguru import logger


def fix_csv_encoding_for_excel(folder_path):
    """
    自动后处理：将文件夹下所有新生成的 CSV/TXT 文件转换为 Excel 完美兼容的 utf-8-sig 编码
    """
    logger.info("正在优化阻抗等数据文件的 Excel 兼容性...")
    p = Path(folder_path)
    print(p)
    # 扫描常见的数据后缀名
    for file in list(p.glob("*.csv")) + list(p.glob("*.txt")):
        try:
            # 尝试用 utf-8 读取
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
            # 用 utf-8-sig (带BOM) 重新写入，Excel 双击打开便不会乱码
            with open(file, "w", encoding="utf-8-sig") as f:
                f.write(content)
            logger.info(f"文件编码修正成功: {file.name}")
        except Exception as e:
            # 忽略已经被转码或无法用utf-8打开的文件
            pass

def consumer_process_wrapper(queue: Queue, data_type: str) -> None:
    """消费者进程通用处理函数"""
    if queue is None:
        logger.warning(f"{data_type} queue is None")
        return
    
    logger.info(f"Starting {data_type} consumer q: {queue}")
    try:
        while True:
            item = queue.get()
            if item is None:
                logger.info(f"{data_type} 消费结束")
                break
    except KeyboardInterrupt:
        logger.info(f"{data_type} consumer terminated")
    except Exception as e:
        logger.error(f"{data_type} 进程异常: {e}")

def start_consumer_process(target: callable, queue: Queue, data_type: str, name: str) -> Process:
    """启动消费者进程的通用方法"""
    process = Process(target=target, args=(queue, data_type,), name=name)
    process.daemon = True
    process.start()
    return process  