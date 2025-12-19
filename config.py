# GMGN 爬虫配置文件
# 如果需要使用代理，取消下面的注释并填入你的代理地址

# 代理设置示例：
# PROXY = "http://127.0.0.1:7890"
# PROXY = "socks5://127.0.0.1:1080"

# 🔥 如果你访问 gmgn.ai 需要代理，请修改下面这行为你的代理地址
# 例如 Clash 默认代理: http://127.0.0.1:7890
# 例如 v2ray 默认代理: socks5://127.0.0.1:1080
PROXY = "http://127.0.0.1:7890"  # 修改为你的实际代理地址，如果不需要代理改为 None

# 浏览器设置
HEADLESS = False  # False 表示显示浏览器窗口

# 输出文件
OUTPUT_FILE = "gmgn_users_dedup.json"