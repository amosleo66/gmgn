#!/bin/bash

echo "================================"
echo "GMGN API 爬虫 - 快速启动"
echo "================================"
echo ""

# 检查是否安装了依赖
if ! python3 -c "import playwright" 2>/dev/null; then
    echo "[错误] 未检测到 Playwright，正在安装依赖..."
    pip3 install -r requirements.txt
    echo ""
    echo "正在安装浏览器驱动..."
    playwright install chromium
    echo ""
fi

echo "选择运行模式:"
echo "[1] 去重版爬虫 (推荐)"
echo "[2] 基础版爬虫"
echo "[3] 数据分析"
echo "[4] 按标签导出数据"
echo ""

read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "启动去重版爬虫..."
        python3 gmgn_crawler_dedup.py
        ;;
    2)
        echo ""
        echo "启动基础版爬虫..."
        python3 gmgn_crawler.py
        ;;
    3)
        echo ""
        echo "执行数据分析..."
        python3 analyze_data.py analyze
        ;;
    4)
        echo ""
        echo "按标签导出数据..."
        python3 analyze_data.py export
        ;;
    *)
        echo ""
        echo "[错误] 无效的选项"
        ;;
esac