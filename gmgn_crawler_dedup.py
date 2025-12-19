"""
GMGN API 爬虫（去重版本）- 监控浏览器网络请求并提取 users 数据
使用 Playwright 来拦截和记录 API 响应，自动去重用户
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright, Route
from datetime import datetime

class GmgnCrawlerDedup:
    def __init__(self, output_file='gmgn_users_dedup.json'):
        self.output_file = Path(output_file)
        self.users_dict = {}  # 使用字典存储，key 为 user_id，自动去重
        self.target_url_prefix = 'https://gmgn.ai/vas/api/v1/twitter/user/search'
        self.request_count = 0

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
                        print(f"加载已有数据: {len(self.users_dict)} 个用户")
            except Exception as e:
                print(f"加载已有数据失败: {e}")

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

                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 捕获到第 {self.request_count} 个请求")
                    print(f"URL: {request.url}")
                    print(f"本次获取: {len(users)} 个用户，新增: {new_users} 个")
                    print(f"累计用户数（去重后）: {len(self.users_dict)}")

                    # 实时保存到文件
                    if new_users > 0:
                        self.save_data()

                # 继续响应
                await route.fulfill(response=response)

            except Exception as e:
                print(f"解析响应时出错: {e}")
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

        print(f"✅ 数据已保存到: {self.output_file.absolute()}")

    async def start_browser(self, headless=False, proxy=None):
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
            if proxy:
                launch_args['proxy'] = {'server': proxy}

            # 启动浏览器
            browser = await p.chromium.launch(**launch_args)

            # 设置上下文参数，模拟真实浏览器
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            )

            page = await context.new_page()

            # 拦截所有请求
            await page.route('**/*', self.handle_route)

            print("=" * 60)
            print("GMGN API 爬虫已启动（去重版本）")
            print("=" * 60)
            print(f"目标 API: {self.target_url_prefix}")
            print(f"输出文件: {self.output_file.absolute()}")
            print(f"已有用户: {len(self.users_dict)}")
            if proxy:
                print(f"代理设置: {proxy}")
            print("\n" + "!" * 60)
            print("重要提示：")
            print("1. 浏览器窗口已打开，请手动访问 https://gmgn.ai/")
            print("2. 在浏览器中正常操作页面（搜索用户、浏览等）")
            print("3. 爬虫会自动捕获 API 响应并保存数据")
            print("4. 按 Ctrl+C 停止爬虫")
            print("!" * 60 + "\n")

            # 打开空白页，让用户手动访问 gmgn.ai
            try:
                await page.goto('about:blank', timeout=5000)
                print("✓ 浏览器已就绪")
                print("→ 请在浏览器中手动访问: https://gmgn.ai/\n")
            except Exception as e:
                print(f"⚠ 页面加载警告: {e}")
                print("→ 请继续在浏览器中手动访问: https://gmgn.ai/\n")

            try:
                # 保持浏览器打开，直到用户按 Ctrl+C
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n\n停止爬虫...")
                print(f"总共捕获 {self.request_count} 个请求")
                print(f"总共收集 {len(self.users_dict)} 个不同用户")
                if len(self.users_dict) > 0:
                    self.save_data()
            finally:
                await browser.close()

async def main():
    crawler = GmgnCrawlerDedup(output_file='gmgn_users_dedup.json')
    # headless=False 表示显示浏览器窗口，方便你操作
    await crawler.start_browser(headless=False)

if __name__ == '__main__':
    asyncio.run(main())