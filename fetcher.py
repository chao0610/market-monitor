#!/usr/bin/env python3
"""
统一行情获取程序 + 波动检测
针对每个标的，从基础信息表获取需要使用的API，然后调用对应API工具获取行情，写入行情信息表，并检测波动发送预警
"""

import sys
import traceback
from datetime import datetime
from typing import List, Dict, Any

# 添加项目路径
sys.path.insert(0, '/Users/yuchao/.openclaw/workspace/market_monitor')

from config.logger import setup_logger
from models.symbol import Symbol
from models.market_data import MarketDataRepository
from api_clients import APIClientFactory
from volatility_detector import VolatilityDetector, AlertResult
from notifier import AlertNotifier

# 设置日志
logger = setup_logger('fetcher')

class MarketDataFetcher:
    """行情数据获取器"""
    
    def __init__(self):
        self.repo = MarketDataRepository()
        self.detector = VolatilityDetector()
        self.notifier = AlertNotifier()
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'errors': []
        }
        self.alerts: List[AlertResult] = []
    
    def fetch_symbol(self, symbol: Symbol) -> bool:
        """获取单个标的的行情并检测波动"""
        logger.info(f"Fetching {symbol.symbol_code} ({symbol.symbol_name}) from {symbol.data_source}...")
        
        try:
            # 获取对应 API 客户端
            client = APIClientFactory.get_client(symbol.data_source)
            
            # 调用 API 获取数据
            data = client.get_price(symbol.symbol_code)
            
            # 保存到数据库
            data_id = self.repo.save_market_data(
                symbol_id=symbol.symbol_id,
                market_time=data['market_time'],
                price=data['price'],
                volume=data.get('volume'),
                source_api=data['source_api']
            )
            
            logger.info(f"  ✓ Saved: price={data['price']}, time={data['market_time']}")
            
            # 检测波动
            alert = self.detector.check_symbol(symbol, data['price'])
            if alert:
                self.alerts.append(alert)
                logger.warning(f"  ⚠ Alert triggered for {symbol.symbol_code}!")
            
            self.stats['success'] += 1
            return True
            
        except Exception as e:
            error_msg = f"{symbol.symbol_code}: {str(e)}"
            logger.error(f"  ✗ Error: {error_msg}")
            logger.error(traceback.format_exc())
            self.stats['errors'].append(error_msg)
            self.stats['failed'] += 1
            return False
    
    def fetch_all(self) -> Dict[str, Any]:
        """获取所有活跃标的的行情"""
        logger.info(f"{'='*60}")
        logger.info(f"Market Data Fetcher - {datetime.now()}")
        logger.info(f"{'='*60}")
        
        # 获取所有活跃标的
        symbols = self.repo.get_active_symbols()
        self.stats['total'] = len(symbols)
        
        logger.info(f"Found {len(symbols)} active symbols")
        
        # 逐个获取
        for symbol in symbols:
            self.fetch_symbol(symbol)
        
        # 统计
        logger.info(f"Summary: {self.stats['success']}/{self.stats['total']} succeeded")
        if self.stats['failed'] > 0:
            logger.warning(f"Failed: {self.stats['failed']}")
            for error in self.stats['errors']:
                logger.warning(f"  - {error}")
        
        # 发送预警
        if self.alerts:
            self.notifier.send(self.alerts)
            return {
                **self.stats,
                'alerts': self.alerts,
                'alert_message': self.notifier.get_message(self.alerts)
            }
        else:
            logger.info("No alerts triggered")
            return self.stats
    
    def fetch_single(self, symbol_code: str) -> bool:
        """获取单个标的的行情（用于测试）"""
        symbol = self.repo.get_symbol_by_code(symbol_code)
        if not symbol:
            logger.error(f"Symbol {symbol_code} not found")
            return False
        return self.fetch_symbol(symbol)


def main():
    """主函数"""
    fetcher = MarketDataFetcher()
    
    # 如果有命令行参数，获取单个标的
    if len(sys.argv) > 1:
        symbol_code = sys.argv[1]
        success = fetcher.fetch_single(symbol_code)
        sys.exit(0 if success else 1)
    else:
        # 获取所有标的
        stats = fetcher.fetch_all()
        sys.exit(0 if stats['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
