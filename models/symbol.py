from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Symbol:
    symbol_id: int
    symbol_code: str
    symbol_name: str
    symbol_type: str
    data_source: str
    update_interval: int
    latency_notes: str
    is_active: bool
    alert_threshold: float = 1.0
    backfill_enabled: bool = False

@dataclass
class MarketData:
    data_id: Optional[int]
    symbol_id: int
    market_time: datetime
    local_time: datetime
    price: float
    volume: Optional[float]
    source_api: str
