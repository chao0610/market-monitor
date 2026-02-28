#!/usr/bin/env python3
"""
行情监控主程序
定时获取行情数据
"""

import sys
import time
import schedule
import traceback
from datetime import datetime

sys.path.insert(0, '/Users/yuchao/.openclaw/workspace/market_monitor')

from config.database import init_db, init_default_data
from config.logger import setup_logger
from fetcher import MarketDataFetcher
from backfill import BackfillService

# 设置日志
logger = setup_logger('market_monitor', 'market_monitor.log')

def job():
    """定时任务"""
    logger.info("=" * 60)
    logger.info("Starting scheduled job...")
    
    try:
        fetcher = MarketDataFetcher()
        result = fetcher.fetch_all()
        
        # 记录统计信息
        logger.info(f"Job completed: {result.get('success', 0)}/{result.get('total', 0)} succeeded")
        
        # 如果有预警，发送到飞书
        if isinstance(result, dict) and 'alert_message' in result and result['alert_message']:
            logger.info(f"Alerts triggered: {len(result.get('alerts', []))}")
            try:
                import subprocess
                msg = result['alert_message']
                subprocess.run(
                    ['openclaw', 'message', 'send', msg],
                    capture_output=True,
                    text=True
                )
                logger.info("Feishu notification sent")
            except Exception as e:
                logger.error(f"Failed to send Feishu message: {e}")
        else:
            logger.info("No alerts triggered")
            
    except Exception as e:
        logger.error(f"Job failed with exception: {e}")
        logger.error(traceback.format_exc())
    
    logger.info("Job finished")
    logger.info("=" * 60)

def main():
    """主函数"""
    logger.info("Market Monitor - Starting up...")
    
    try:
        # 初始化数据库
        logger.info("Initializing database...")
        init_db()
        init_default_data()
        logger.info("Database initialized")
        
        # 启动时补充历史数据
        logger.info("Starting backfill service...")
        backfill = BackfillService()
        backfill_results = backfill.backfill_all()
        if backfill_results:
            logger.info(f"Backfill completed: {backfill_results}")
        
        # 立即执行一次
        job()
        
        # 设置定时任务（每5分钟）
        schedule.every(5).minutes.do(job)
        
        logger.info("Scheduler started. Fetching data every 5 minutes...")
        
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down by user (KeyboardInterrupt)...")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        logger.critical(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()
