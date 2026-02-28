# Market Monitor

市场行情监控和重大波动信息推送项目

## 功能

- 监控 8 个主流标的：BTC、ETH、黄金ETF、白银ETF、原油ETF、美股三大指数ETF
- 每 5 分钟获取实时行情
- 波动检测：5分钟 / 30分钟 / 2小时 三个时间窗口
- 自动推送预警到飞书

## 波动检测规则

| 时间窗口 | 阈值 | 说明 |
|---------|------|------|
| 5分钟 | 固定阈值 | 触发即推送，不去重 |
| 30分钟 | 动态阈值 (1+n)*x | n 为连续触发次数，30分钟过期重置 |
| 2小时 | 动态阈值 (1+m)*x | m 为连续触发次数，2小时过期重置 |

## 标的阈值

| 标的 | 阈值 |
|-----|------|
| BTCUSDT, ETHUSDT | 2.0% |
| GLD, SLV | 1.0% |
| USO | 1.2% |
| SPY, DIA, QQQ | 0.8% |

## 安装

```bash
pip3 install requests schedule --user --break-system-packages
```

## 配置

```bash
# 设置 Finnhub API key
python3 -c "from api_clients import APIClientFactory; APIClientFactory.set_api_key('finnhub', 'your_key')"
```

## 使用

```bash
# 启动监控
python3 main.py

# 测试单个标的
python3 fetcher.py BTCUSDT
```

## 项目结构

```
market_monitor/
├── config/
│   └── database.py          # 数据库配置
├── models/
│   ├── symbol.py            # 数据模型
│   ├── market_data.py       # 数据访问层
│   └── alert_state.py       # 预警状态
├── api_clients/             # API客户端
├── fetcher.py               # 行情获取
├── volatility_detector.py   # 波动检测
├── notifier.py              # 消息推送
└── main.py                  # 主程序
```

## 简报格式

```
📊 行情预警 MM-DD HH:MM
🔴 BTCUSDT: 5分钟+2.30% | 30分钟+5.10% | 2小时+8.50%
🟢 SPY: 5分钟-0.80% | 30分钟-1.50% | 2小时-2.20%
```

## License

MIT
