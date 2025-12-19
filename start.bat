@echo off
chcp 65001 >nul
echo ================================
echo GMGN API 爬虫 - 快速启动
echo ================================
echo.

REM 检查是否安装了依赖
python -c "import playwright" 2>nul
if errorlevel 1 (
    echo [错误] 未检测到 Playwright，正在安装依赖...
    pip install -r requirements.txt
    echo.
    echo 正在安装浏览器驱动...
    playwright install chromium
    echo.
)

echo 选择运行模式:
echo [1] 高级版爬虫 - 支持代理 (推荐)
echo [2] 去重版爬虫
echo [3] 基础版爬虫
echo [4] 数据分析
echo [5] 按标签导出数据
echo.

set /p choice=请输入选项 (1-5):

if "%choice%"=="1" (
    echo.
    set /p use_proxy=是否使用代理? (y/n):
    if /i "%use_proxy%"=="y" (
        set /p proxy_url=请输入代理地址 (例如: http://127.0.0.1:7890):
        echo.
        echo 启动高级版爬虫（使用代理）...
        python gmgn_crawler_advanced.py --proxy %proxy_url%
    ) else (
        echo.
        echo 启动高级版爬虫...
        python gmgn_crawler_advanced.py
    )
) else if "%choice%"=="2" (
    echo.
    echo 启动去重版爬虫...
    python gmgn_crawler_dedup.py
) else if "%choice%"=="3" (
    echo.
    echo 启动基础版爬虫...
    python gmgn_crawler.py
) else if "%choice%"=="4" (
    echo.
    echo 执行数据分析...
    python analyze_data.py analyze
    pause
) else if "%choice%"=="5" (
    echo.
    echo 按标签导出数据...
    python analyze_data.py export
    pause
) else (
    echo.
    echo [错误] 无效的选项
    pause
)