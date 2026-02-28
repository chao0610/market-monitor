import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "market_monitor.db"

def init_db():
    """初始化数据库，创建表结构"""
    DB_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 标的表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS symbols (
            symbol_id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol_code TEXT NOT NULL UNIQUE,
            symbol_name TEXT NOT NULL,
            symbol_type TEXT NOT NULL,
            data_source TEXT NOT NULL,
            update_interval INTEGER DEFAULT 10,
            latency_notes TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 行情表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_data (
            data_id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol_id INTEGER NOT NULL,
            market_time TIMESTAMP NOT NULL,
            local_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            price REAL NOT NULL,
            volume REAL,
            source_api TEXT NOT NULL,
            FOREIGN KEY (symbol_id) REFERENCES symbols(symbol_id)
        )
    ''')
    
    # API配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_configs (
            api_name TEXT PRIMARY KEY,
            base_url TEXT NOT NULL,
            rate_limit INTEGER,
            api_key TEXT,
            status INTEGER DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_market_data_symbol_time ON market_data(symbol_id, market_time)')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_default_data():
    """初始化默认标的和API配置"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 初始化API配置
    apis = [
        ('finnhub', 'https://finnhub.io/api/v1', 60, None),
        ('binance', 'https://api.binance.com', 1200, None),
        ('metals-api', 'https://metals-api.com/api', 60, None),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO api_configs (api_name, base_url, rate_limit, api_key)
        VALUES (?, ?, ?, ?)
    ''', apis)
    
    # 初始化标的
    symbols = [
        # 加密货币 - Binance
        ('BTCUSDT', 'Bitcoin', 'crypto', 'binance', 10, '实时'),
        ('ETHUSDT', 'Ethereum', 'crypto', 'binance', 10, '实时'),
        
        # 贵金属 - Metals-API
        ('XAU', 'Gold', 'commodity', 'metals-api', 10, '10分钟延迟'),
        ('XAG', 'Silver', 'commodity', 'metals-api', 10, '10分钟延迟'),
        
        # 原油 - 通过Finnhub的USO ETF
        ('USO', 'Crude Oil ETF', 'commodity', 'finnhub', 10, '实时(ETF)'),
        
        # 美股指数 - Finnhub
        ('^GSPC', 'S&P 500', 'index', 'finnhub', 10, '实时'),
        ('^DJI', 'Dow Jones', 'index', 'finnhub', 10, '实时'),
        ('^IXIC', 'NASDAQ', 'index', 'finnhub', 10, '实时'),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO symbols 
        (symbol_code, symbol_name, symbol_type, data_source, update_interval, latency_notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', symbols)
    
    conn.commit()
    conn.close()
    print("Default data initialized")

if __name__ == '__main__':
    init_db()
    init_default_data()
