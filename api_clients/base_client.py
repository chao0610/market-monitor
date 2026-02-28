import requests
import time
from typing import Optional, Dict, Any

class BaseAPIClient:
    """API客户端基类"""
    
    def __init__(self, api_name: str, base_url: str, api_key: Optional[str] = None):
        self.api_name = api_name
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.last_request_time = 0
    
    def _rate_limit(self, min_interval: float = 0.5):
        """简单的速率限制"""
        elapsed = time.time() - self.last_request_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()
    
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """获取价格，子类必须实现"""
        raise NotImplementedError
