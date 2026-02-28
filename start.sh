#!/bin/bash
# 启动监控程序的脚本

cd /Users/yuchao/.openclaw/workspace/market_monitor

# 检查是否已在运行
if pgrep -f "python3 main.py" > /dev/null; then
    echo "Market Monitor is already running"
    exit 0
fi

# 使用 nohup 后台运行
nohup python3 main.py >> logs/market_monitor.log 2>&1 &

echo "Market Monitor started (PID: $!)"
