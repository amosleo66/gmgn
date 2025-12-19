"""
GMGN API 爬虫（简化版）- 不使用代理
直接监听浏览器响应，适合能直接访问 gmgn.ai 的用户
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright, Response
from datetime import datetime

class GmgnCrawlerSimple:
    def __init__(self, output_file='gmgn_users_dedup.json'):
        self.output_file = Path(output_file)
        self.users_dict = {}
        self.target_url_prefix = 'https://gmgn.ai/vas/api/v1/twitter/user/search'
        self.request_count = 0

        # 加载已有数据
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

    async def handle_response(self, response: Response):
        """处理响应数据"""
        try:
            if response.url.startswith(self.target_url_prefix) and response.status == 200:
                try:
                    data = await response.json()
                    if data.get('code') == 0 and 'data' in data and 'users' in data['data']:
                        users = data['data']['users']
                        new_users = 0
                        for user in users:
                            user_id = user['user_id']
                            if user_id not in self.users_dict:
                                new_users += 1
                            self.users_dict[user_id] = user

                        self.request_count += 1
                        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ✅ 捕获到第 {self.request_count} 个请求")
                        print(f"📊 本次获取: {len(users)} 个用户，新增: {new_users} 个")
                        print(f"📈 累计用户数（去重后）: {len(self.users_dict)}")

                        if new_users > 0:
                            self.save_data()
                except Exception as e:
                    print(f"❌ 解析响应时出错: {e}")
        except Exception:
            pass

    def save_data(self):
        """保存数据到 JSON 文件"""
        users_list = list(self.users_dict.values())
        users_list.sort(key=lambda x: x.get('followers', 0), reverse=True)

        output_data = {
            'total_users': len(users_list),
            'last_updated': datetime.now().isoformat(),
            'users': users_list
        }

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"💾 数据已保存到: {self.output_file.absolute()}")

    async def start_browser(self):
        """启动浏览器并开始监控"""
        async with async_playwright() as p:
            print("\n🚀 正在启动浏览器...")
            browser = await p.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )

            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            )

            page = await context.new_page()
            page.on('response', lambda response: asyncio.create_task(self.handle_response(response)))

            print("\n" + "=" * 70)
            print("🎯 GMGN API 爬虫已启动（简化版 - 无代理）")
            print("=" * 70)
            print(f"📡 目标 API: {self.target_url_prefix}")
            print(f"💾 输出文件: {self.output_file.absolute()}")
            print(f"📊 已有用户: {len(self.users_dict)}")
            print(f"🌐 连接方式: 直连（不使用代理）")

            print("\n" + "!" * 70)
            print("📋 使用说明：")
            print("  1️⃣  浏览器窗口已打开")
            print("  2️⃣  请手动在浏览器地址栏输入: https://gmgn.ai/")
            print("  3️⃣  在页面中搜索、浏览用户")
            print("  4️⃣  爬虫会自动捕获 API 响应并保存数据")
            print("  5️⃣  按 Ctrl+C 停止爬虫")
            print("!" * 70 + "\n")

            try:
                await page.goto('about:blank', timeout=5000)
                print("✅ 浏览器已就绪")
                print("👉 请在浏览器中手动访问: https://gmgn.ai/\n")
                print("⏳ 等待捕获数据...\n")
            except Exception as e:
                print(f"⚠️  页面加载警告: {e}")
                print("👉 请继续在浏览器中手动访问: https://gmgn.ai/\n")

            try:
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
    crawler = GmgnCrawlerSimple()
    await crawler.start_browser()

if __name__ == '__main__':
    asyncio.run(main())