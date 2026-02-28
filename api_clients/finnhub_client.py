import requests
from datetime import datetime
from typing import Dict, Any, Optional
from .base_client import BaseAPIClient

class FinnhubClient(BaseAPIClient):
    """Finnhub API 客户端 - 用于美股指数和ETF"""
    
    def __init__(self, api_key: str):
        super().__init__('finnhub', 'https://finnhub.io/api/v1', api_key)
    
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """
        获取最新价格
        symbol: 如 ^GSPC, ^DJI, ^IXIC, USO
        """
        self._rate_limit(1.0)  # 免费版 60 calls/min
        
        url = f"{self.base_url}/quote"
        params = {
            'symbol': symbol,
            'token': self.api_key
        }
        
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Finnhub 返回的是当前报价
        return {
            'symbol': symbol,
            'price': data['c'],  # 当前价格
            'volume': data.get('v'),  # 成交量
            'market_time': datetime.now(),  # Finnhub 不返回精确时间戳
            'source_api': 'finnhub',
            'open': data['o'],
            'high': data['h'],
            'low': data['l'],
            'previous_close': data['pc']
        }
    
    def get_company_profile(self, symbol: str) -> Dict[str, Any]:
        """获取公司信息"""
        self._rate_limit(1.0)
        
        url = f"{self.base_url}/stock/profile2"
        params = {
            'symbol': symbol,
            'token': self.api_key
        }
        
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
