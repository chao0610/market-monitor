#!/usr/bin/env python3
"""
行情监控主程序
定时获取行情数据
"""

import sys
import time
import schedule
from datetime import datetime

sys.path.insert(0, '/Users/yuchao/.openclaw/workspace/market_monitor')

from config.database import init_db, init_default_data
from fetcher import MarketDataFetcher

def job():
    """定时任务"""
    print(f"\n[{datetime.now()}] Running scheduled job...")
    fetcher = MarketDataFetcher()
    result = fetcher.fetch_all()
    
    # 如果有预警，发送到飞书
    if isinstance(result, dict) and 'alert_message' in result and result['alert_message']:
        try:
            import subprocess
            msg = result['alert_message']
            # 使用 openclaw 命令发送消息
            subprocess.run(
                ['openclaw', 'message', 'send', msg],
                capture_output=True,
                text=True
            )
        except Exception as e:
            print(f"[ERROR] Failed to send Feishu message: {e}")
    
    print(f"[{datetime.now()}] Job completed\n")

def main():
    """主函数"""
    print("Market Monitor - Starting up...")
    
    # 初始化数据库
    print("Initializing database...")
    init_db()
    init_default_data()
    
    # 立即执行一次
    job()
    
    # 设置定时任务（每5分钟）
    schedule.every(5).minutes.do(job)
    
    print("\nScheduler started. Press Ctrl+C to stop.")
    print("Fetching data every 5 minutes...\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)

if __name__ == '__main__':
    main()
