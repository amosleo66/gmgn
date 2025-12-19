"""
GMGN API 爬虫（高级版本）- 支持配置文件
使用 Playwright 来拦截和记录 API 响应，自动去重用户
支持代理、自定义配置等高级功能
"""
import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright, Route
from datetime import datetime

# 尝试加载配置文件
try:
    from config import PROXY, HEADLESS, OUTPUT_FILE
except ImportError:
    print("未找到 config.py，使用默认配置")
    PROXY = None
    HEADLESS = False
    OUTPUT_FILE = "gmgn_users_dedup.json"

class GmgnCrawlerAdvanced:
    def __init__(self, output_file=OUTPUT_FILE, proxy=PROXY):
        self.output_file = Path(output_file)
        self.users_dict = {}  # 使用字典存储，key 为 user_id，自动去重
        self.target_url_prefix = 'https://gmgn.ai/vas/api/v1/twitter/user/search'
        self.request_count = 0
        self.proxy = proxy

        # 如果文件已存在，加载已有数据
        self.load_existing_data()

    def load_existing_data(self):
        """加载已存在的数据文件"""
        if self.output_file.exists():
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'users' in data:
                        for user in data['users']:
                            self.users_dict[user['user_id']] = user
                        print(f"✓ 加载已有数据: {len(self.users_dict)} 个用户")
            except Exception as e:
                print(f"⚠ 加载已有数据失败: {e}")

    async def handle_route(self, route: Route):
        """处理网络请求并提取数据"""
        request = route.request

        # 检查是否是目标 API
        if request.url.startswith(self.target_url_prefix):
            try:
                # 只对目标 API 进行拦截处理
                response = await route.fetch()

                # 获取响应数据
                body = await response.body()
                data = json.loads(body.decode('utf-8'))

                # 提取 users 数据
                if data.get('code') == 0 and 'data' in data and 'users' in data['data']:
                    users = data['data']['users']

                    # 统计新增用户
                    new_users = 0
                    for user in users:
                        user_id = user['user_id']
                        if user_id not in self.users_dict:
                            new_users += 1
                        self.users_dict[user_id] = user  # 更新或添加用户

                    self.request_count += 1

                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✅ 捕获到第 {self.request_count} 个请求")
                    print(f"📊 本次获取: {len(users)} 个用户，新增: {new_users} 个")
                    print(f"📈 累计用户数（去重后）: {len(self.users_dict)}")

                    # 实时保存到文件
                    if new_users > 0:
                        self.save_data()

                # 继续响应
                await route.fulfill(response=response)

            except Exception as e:
                print(f"❌ 解析响应时出错: {e}")
                # 如果处理失败，继续传递原始请求
                await route.continue_()
        else:
            # 非目标 API，直接放行
            await route.continue_()

    def save_data(self):
        """保存数据到 JSON 文件"""
        users_list = list(self.users_dict.values())
        # 按照 followers 数量排序
        users_list.sort(key=lambda x: x.get('followers', 0), reverse=True)

        output_data = {
            'total_users': len(users_list),
            'last_updated': datetime.now().isoformat(),
            'users': users_list
        }

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"💾 数据已保存到: {self.output_file.absolute()}")

    async def start_browser(self, headless=HEADLESS):
        """启动浏览器并开始监控"""
        async with async_playwright() as p:
            # 浏览器启动参数
            launch_args = {
                'headless': headless,
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ]
            }

            # 如果提供了代理，添加代理参数
            if self.proxy:
                launch_args['proxy'] = {'server': self.proxy}

            # 启动浏览器
            print("\n🚀 正在启动浏览器...")
            browser = await p.chromium.launch(**launch_args)

            # 设置上下文参数，模拟真实浏览器
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            )

            page = await context.new_page()

            # 拦截所有请求
            await page.route('**/*', self.handle_route)

            print("\n" + "=" * 70)
            print("🎯 GMGN API 爬虫已启动（高级版本）")
            print("=" * 70)
            print(f"📡 目标 API: {self.target_url_prefix}")
            print(f"💾 输出文件: {self.output_file.absolute()}")
            print(f"📊 已有用户: {len(self.users_dict)}")
            if self.proxy:
                print(f"🔐 代理设置: {self.proxy}")
            else:
                print(f"🌐 代理设置: 无（直连）")

            print("\n" + "!" * 70)
            print("📋 使用说明：")
            print("  1️⃣  浏览器窗口已打开")
            print("  2️⃣  请手动在浏览器地址栏输入: https://gmgn.ai/")
            print("  3️⃣  在页面中搜索、浏览用户")
            print("  4️⃣  爬虫会自动捕获 API 响应并保存数据")
            print("  5️⃣  按 Ctrl+C 停止爬虫")
            print("!" * 70 + "\n")

            # 打开空白页，让用户手动访问 gmgn.ai
            try:
                await page.goto('about:blank', timeout=5000)
                print("✅ 浏览器已就绪")
                print("👉 请在浏览器中手动访问: https://gmgn.ai/\n")
                print("⏳ 等待捕获数据...\n")
            except Exception as e:
                print(f"⚠️  页面加载警告: {e}")
                print("👉 请继续在浏览器中手动访问: https://gmgn.ai/\n")

            try:
                # 保持浏览器打开，直到用户按 Ctrl+C
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n\n" + "=" * 70)
                print("🛑 正在停止爬虫...")
                print("=" * 70)
                print(f"📊 统计信息：")
                print(f"   - 捕获请求数: {self.request_count}")
                print(f"   - 收集用户数: {len(self.users_dict)}")
                if len(self.users_dict) > 0:
                    self.save_data()
                    print(f"\n✅ 爬虫已成功停止")
                else:
                    print(f"\n⚠️  未捕获到任何数据")
            finally:
                await browser.close()

async def main():
    # 支持命令行参数
    proxy = PROXY
    output_file = OUTPUT_FILE

    if len(sys.argv) > 1:
        if '--proxy' in sys.argv:
            idx = sys.argv.index('--proxy')
            if idx + 1 < len(sys.argv):
                proxy = sys.argv[idx + 1]

        if '--output' in sys.argv:
            idx = sys.argv.index('--output')
            if idx + 1 < len(sys.argv):
                output_file = sys.argv[idx + 1]

        if '--help' in sys.argv or '-h' in sys.argv:
            print("GMGN API 爬虫 - 高级版本")
            print("\n用法:")
            print("  python gmgn_crawler_advanced.py [选项]")
            print("\n选项:")
            print("  --proxy <代理地址>    设置代理服务器")
            print("                       例如: --proxy http://127.0.0.1:7890")
            print("  --output <文件名>     设置输出文件名")
            print("                       例如: --output my_data.json")
            print("  --help, -h           显示此帮助信息")
            print("\n示例:")
            print("  python gmgn_crawler_advanced.py --proxy http://127.0.0.1:7890")
            print("  python gmgn_crawler_advanced.py --output my_users.json")
            print("\n配置文件:")
            print("  可以编辑 config.py 文件来设置默认配置")
            return

    crawler = GmgnCrawlerAdvanced(output_file=output_file, proxy=proxy)
    await crawler.start_browser(headless=HEADLESS)

if __name__ == '__main__':
    asyncio.run(main())