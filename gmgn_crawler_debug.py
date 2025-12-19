"""
GMGN API 爬虫（调试版本）- 显示所有 API 请求
帮助找到正确的目标 API URL
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright, Response
from datetime import datetime

# 尝试加载配置文件
try:
    from config import PROXY, HEADLESS, OUTPUT_FILE
except ImportError:
    PROXY = None
    HEADLESS = False
    OUTPUT_FILE = "gmgn_users_dedup.json"

class GmgnCrawlerDebug:
    def __init__(self, proxy=PROXY):
        self.proxy = proxy
        self.api_requests = []  # 记录所有 API 请求

    async def handle_response(self, response: Response):
        """处理响应数据 - 调试模式"""
        try:
            url = response.url

            # 只显示 gmgn.ai 的 API 请求
            if 'gmgn.ai' in url and '/api/' in url:
                status = response.status
                method = response.request.method

                # 记录请求信息
                request_info = {
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'method': method,
                    'url': url,
                    'status': status
                }

                # 检查是否是用户搜索 API
                is_target = '/twitter/user/search' in url

                print(f"\n[{request_info['time']}] {'🎯' if is_target else '📡'} {method} {status}")
                print(f"URL: {url}")

                # 如果是目标 API，尝试解析响应
                if is_target and status == 200:
                    try:
                        data = await response.json()
                        if data.get('code') == 0 and 'data' in data and 'users' in data['data']:
                            users = data['data']['users']
                            print(f"✅ 目标 API！获取到 {len(users)} 个用户")

                            # 显示前3个用户
                            for i, user in enumerate(users[:3], 1):
                                print(f"   {i}. @{user.get('handle')} ({user.get('followers')} 粉丝)")
                        else:
                            print(f"⚠️  响应格式不符合预期")
                    except Exception as e:
                        print(f"❌ 解析失败: {e}")

                self.api_requests.append(request_info)

        except Exception as e:
            pass

    async def start_browser(self):
        """启动浏览器并开始监控"""
        async with async_playwright() as p:
            # 浏览器启动参数
            launch_args = {
                'headless': False,
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ]
            }

            # 设置代理
            context_args = {
                'viewport': {'width': 1920, 'height': 1080},
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            }

            if self.proxy:
                context_args['proxy'] = {'server': self.proxy}

            print("\n🚀 正在启动浏览器...")
            browser = await p.chromium.launch(**launch_args)
            context = await browser.new_context(**context_args)
            page = await context.new_page()

            # 监听所有响应
            page.on('response', lambda response: asyncio.create_task(self.handle_response(response)))

            print("\n" + "=" * 70)
            print("🐛 GMGN API 爬虫 - 调试模式")
            print("=" * 70)
            print("📋 功能: 显示所有 gmgn.ai 的 API 请求")
            print("🎯 目标: /twitter/user/search")
            if self.proxy:
                print(f"🔐 代理: {self.proxy}")
            else:
                print("🌐 代理: 无（直连）")

            print("\n" + "!" * 70)
            print("📖 使用说明：")
            print("  1️⃣  浏览器窗口已打开")
            print("  2️⃣  手动访问: https://gmgn.ai/")
            print("  3️⃣  在页面上进行以下操作：")
            print("     - 点击「用户」或「User」标签")
            print("     - 搜索用户")
            print("     - 浏览用户列表")
            print("     - 切换用户分类标签")
            print("  4️⃣  观察终端输出，找到目标 API")
            print("  5️⃣  按 Ctrl+C 停止")
            print("!" * 70 + "\n")

            try:
                await page.goto('about:blank', timeout=5000)
                print("✅ 浏览器已就绪")
                print("👉 请在浏览器中访问: https://gmgn.ai/")
                print("\n⏳ 监听中...\n")
            except Exception as e:
                print(f"⚠️  {e}")

            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n\n" + "=" * 70)
                print("🛑 停止调试")
                print("=" * 70)
                print(f"📊 捕获到 {len(self.api_requests)} 个 API 请求")

                # 统计 API URL
                if self.api_requests:
                    print("\n📋 API 请求汇总:")
                    url_counts = {}
                    for req in self.api_requests:
                        # 简化 URL（去掉查询参数）
                        base_url = req['url'].split('?')[0]
                        url_counts[base_url] = url_counts.get(base_url, 0) + 1

                    for url, count in sorted(url_counts.items(), key=lambda x: x[1], reverse=True):
                        print(f"  [{count:2d}x] {url}")

                    # 检查是否有目标 API
                    target_found = any('/twitter/user/search' in req['url'] for req in self.api_requests)
                    if target_found:
                        print("\n✅ 已捕获到目标 API！")
                        print("💡 现在可以使用正式版本:")
                        print("   python gmgn_crawler_v2.py")
                    else:
                        print("\n⚠️  未捕获到目标 API")
                        print("💡 建议:")
                        print("  1. 确保在页面上点击了「用户」标签")
                        print("  2. 尝试搜索用户或浏览用户列表")
                        print("  3. 查看上面的 API 列表，找到用户相关的接口")
            finally:
                await browser.close()

async def main():
    import sys

    proxy = PROXY
    if '--proxy' in sys.argv:
        idx = sys.argv.index('--proxy')
        if idx + 1 < len(sys.argv):
            proxy = sys.argv[idx + 1]

    crawler = GmgnCrawlerDebug(proxy=proxy)
    await crawler.start_browser()

if __name__ == '__main__':
    asyncio.run(main())