"""
代理配置检测工具
帮助检测代理是否可用，以及是否需要代理
"""
import requests
import sys

def test_direct_connection():
    """测试直接连接"""
    print("🔍 测试1: 检查是否可以直接访问 gmgn.ai...")
    try:
        response = requests.get('https://gmgn.ai/', timeout=10)
        if response.status_code == 200:
            print("✅ 可以直接访问！不需要代理")
            return True
    except Exception as e:
        print(f"❌ 无法直接访问: {e}")
    return False

def test_proxy(proxy_url):
    """测试代理是否可用"""
    print(f"\n🔍 测试2: 检查代理 {proxy_url} 是否可用...")
    try:
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        response = requests.get('https://www.google.com/', proxies=proxies, timeout=10)
        if response.status_code == 200:
            print("✅ 代理可用！")
            return True
    except Exception as e:
        print(f"❌ 代理不可用: {e}")
    return False

def test_gmgn_with_proxy(proxy_url):
    """测试通过代理访问 gmgn.ai"""
    print(f"\n🔍 测试3: 通过代理访问 gmgn.ai...")
    try:
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        response = requests.get('https://gmgn.ai/', proxies=proxies, timeout=10)
        if response.status_code == 200:
            print("✅ 可以通过代理访问 gmgn.ai！")
            return True
    except Exception as e:
        print(f"❌ 无法通过代理访问: {e}")
    return False

def main():
    print("=" * 70)
    print("🔧 GMGN 爬虫代理检测工具")
    print("=" * 70)

    # 测试直接连接
    if test_direct_connection():
        print("\n" + "=" * 70)
        print("✅ 结论: 你不需要代理！")
        print("=" * 70)
        print("\n📝 建议:")
        print("1. 编辑 config.py，将 PROXY 设置为 None：")
        print("   PROXY = None")
        print("\n2. 然后运行爬虫：")
        print("   python gmgn_crawler_v2.py")
        return

    # 测试常见代理
    common_proxies = [
        'http://127.0.0.1:7890',  # Clash 默认
        'http://127.0.0.1:7891',
        'socks5://127.0.0.1:1080',  # v2ray 默认
        'http://127.0.0.1:1087',
        'http://127.0.0.1:10809',
    ]

    print("\n🔍 扫描常见代理端口...")
    working_proxy = None

    for proxy in common_proxies:
        if test_proxy(proxy):
            working_proxy = proxy
            if test_gmgn_with_proxy(proxy):
                print("\n" + "=" * 70)
                print(f"✅ 找到可用的代理: {proxy}")
                print("=" * 70)
                print("\n📝 建议:")
                print("1. 编辑 config.py，设置代理：")
                print(f"   PROXY = '{proxy}'")
                print("\n2. 然后运行爬虫：")
                print("   python gmgn_crawler_v2.py")
                return
            break

    # 没有找到可用的代理
    print("\n" + "=" * 70)
    print("❌ 未找到可用的代理")
    print("=" * 70)
    print("\n📝 建议:")
    print("1. 检查你的代理软件（Clash/v2ray）是否正在运行")
    print("2. 检查代理软件的端口设置")
    print("3. 常见端口：")
    print("   - Clash: 7890")
    print("   - v2ray: 1080")
    print("   - Shadowsocks: 1087")
    print("\n4. 如果使用其他端口，请手动设置 config.py：")
    print("   PROXY = 'http://127.0.0.1:你的端口'")

    # 提示用户手动输入
    print("\n" + "-" * 70)
    user_proxy = input("\n如果你知道代理地址，请输入（或直接回车跳过）: ").strip()
    if user_proxy:
        if not user_proxy.startswith(('http://', 'socks5://')):
            user_proxy = f'http://{user_proxy}'
        print(f"\n测试用户提供的代理: {user_proxy}")
        if test_proxy(user_proxy) and test_gmgn_with_proxy(user_proxy):
            print(f"\n✅ 代理可用！请在 config.py 中设置:")
            print(f"   PROXY = '{user_proxy}'")
        else:
            print(f"\n❌ 代理不可用，请检查地址和端口")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消")