#!/usr/bin/env python3
"""
历史数据补充模块
使用 Binance Kline API 补充缺失的 5分钟数据
"""

import sys
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

sys.path.insert(0, '/Users/yuchao/.openclaw/workspace/market_monitor')

from config.logger import setup_logger
from models.symbol import Symbol
from models.market_data import MarketDataRepository
from api_clients.binance_client import BinanceClient

logger = setup_logger('backfill')

class BackfillService:
    """历史数据补充服务"""
    
    def __init__(self):
        self.repo = MarketDataRepository()
        self.binance = BinanceClient()
    
    def get_last_record_time(self, symbol_id: int) -> Optional[datetime]:
        """获取标的最近记录时间"""
        conn = sqlite3.connect('/Users/yuchao/.openclaw/workspace/market_monitor/data/market_monitor.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT MAX(market_time) FROM market_data WHERE symbol_id = ?
        ''', (symbol_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0]:
            return datetime.fromisoformat(row[0]) if isinstance(row[0], str) else row[0]
        return None
    
    def backfill_symbol(self, symbol: Symbol) -> int:
        """
        补充单个标的的历史数据
        返回补充的数据条数
        """
        if not symbol.backfill_enabled:
            logger.info(f"{symbol.symbol_code}: backfill not enabled")
            return 0
        
        if symbol.data_source != 'binance':
            logger.info(f"{symbol.symbol_code}: only binance supports backfill")
            return 0
        
        # 获取最近记录时间
        last_time = self.get_last_record_time(symbol.symbol_id)
        if not last_time:
            logger.info(f"{symbol.symbol_code}: no existing data, skip backfill")
            return 0
        
        now = datetime.now()
        
        # 如果最近记录在5分钟内，不需要补充
        if now - last_time < timedelta(minutes=5):
            logger.info(f"{symbol.symbol_code}: data is up to date ({last_time})")
            return 0
        
        logger.info(f"{symbol.symbol_code}: backfilling from {last_time} to {now}")
        
        try:
            # 计算需要获取的K线数量（每5分钟一条）
            minutes_diff = int((now - last_time).total_seconds() / 60)
            limit = min(minutes_diff // 5 + 1, 1000)  # Binance 限制最多1000条
            
            # 获取K线数据
            klines = self.binance.get_kline(symbol.symbol_code, interval='5m', limit=limit)
            
            count = 0
            for kline in klines:
                # Binance Kline 格式: [open_time, open, high, low, close, volume, close_time, ...]
                open_time = datetime.fromtimestamp(kline[0] / 1000)
                close_price = float(kline[4])
                volume = float(kline[5])
                
                # 只补充缺失的数据（时间戳大于最后记录时间）
                if open_time > last_time:
                    self.repo.save_market_data(
                        symbol_id=symbol.symbol_id,
                        market_time=open_time,
                        price=close_price,
                        volume=volume,
                        source_api='binance_backfill'
                    )
                    count += 1
            
            logger.info(f"{symbol.symbol_code}: backfilled {count} records")
            return count
            
        except Exception as e:
            logger.error(f"{symbol.symbol_code}: backfill failed - {e}")
            return 0
    
    def backfill_all(self) -> Dict[str, int]:
        """补充所有启用 backfill 的标的数据"""
        logger.info("Starting backfill service...")
        
        symbols = self.repo.get_active_symbols()
        results = {}
        
        for symbol in symbols:
            count = self.backfill_symbol(symbol)
            if count > 0:
                results[symbol.symbol_code] = count
        
        logger.info(f"Backfill completed: {results}")
        return results


if __name__ == '__main__':
    import sqlite3
    service = BackfillService()
    results = service.backfill_all()
    print(f"Backfill results: {results}")
