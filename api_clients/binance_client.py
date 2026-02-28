import requests
from datetime import datetime
from typing import Dict, Any, Optional
from .base_client import BaseAPIClient

class BinanceClient(BaseAPIClient):
    """Binance API 客户端 - 用于加密货币"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__('binance', 'https://api.binance.com', api_key)
    
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """
        获取最新价格
        symbol: 如 BTCUSDT, ETHUSDT
        """
        self._rate_limit(0.1)  # Binance 限制较宽松
        
        url = f"{self.base_url}/api/v3/ticker/24hr"
        params = {'symbol': symbol}
        
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Binance 返回的是24小时统计数据
        return {
            'symbol': symbol,
            'price': float(data['lastPrice']),
            'volume': float(data['volume']),
            'market_time': datetime.fromtimestamp(data['closeTime'] / 1000),
            'source_api': 'binance'
        }
    
    def get_kline(self, symbol: str, interval: str = '1m', limit: int = 1) -> list:
        """获取K线数据"""
        self._rate_limit(0.1)
        
        url = f"{self.base_url}/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
