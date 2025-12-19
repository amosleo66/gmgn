# 快速入门指南

## 🚀 3步开始使用

### 第1步：安装依赖
```bash
pip install -r requirements.txt
playwright install chromium
```

### 第2步：配置代理（重要！）
如果你访问 gmgn.ai 需要代理，编辑 `config.py` 文件：
```python
PROXY = "http://127.0.0.1:7890"  # 改为你的代理地址
```

常见代理地址：
- Clash 默认: `http://127.0.0.1:7890`
- v2ray 默认: `socks5://127.0.0.1:1080`

### 第3步：运行爬虫（推荐 v2 版本）
```bash
# 使用配置文件中的代理
python gmgn_crawler_v2.py

# 或使用命令行指定代理
python gmgn_crawler_v2.py --proxy http://127.0.0.1:7890
```

或者使用快速启动脚本：
```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

## 📖 使用说明
1. ✅ 浏览器会自动打开（显示空白页）
2. ✅ 在浏览器地址栏手动输入: `https://gmgn.ai/`
3. ✅ 在网站上搜索用户、浏览列表（随便浏览即可）
4. ✅ 观察终端，看到捕获信息就说明成功了
5. ✅ 按 `Ctrl+C` 停止

## 📊 查看数据

运行完成后，查看统计：
```bash
python analyze_data.py analyze
```

## ❓ 常见问题

### Q: 报错 `ETIMEDOUT` 连接超时？
A: 这是因为没有配置代理。请编辑 `config.py` 设置代理地址，或使用命令行参数：
```bash
python gmgn_crawler_v2.py --proxy http://127.0.0.1:7890
```

### Q: 没有捕获到数据？
A: 确保在网站上进行了搜索或浏览操作，爬虫只会捕获用户搜索相关的 API 请求

### Q: 页面加载很慢或卡顿？
A: 使用 v2 版本，它采用响应监听模式，不会影响页面加载速度

### Q: 想要长期收集数据？
A: 使用 v2 版本或去重版，支持断点续传，多次运行会自动合并数据

## 📁 输出文件

- `gmgn_users_dedup.json` - 包含所有去重后的用户数据
- 数据格式：JSON，包含 user_id, handle, followers, user_tags 等字段

## 💡 提示

- 爬虫会**实时保存**数据，不用担心丢失
- 可以**多次运行**，数据会自动累加去重
- 在网站上**多翻页、多搜索**，抓取更多数据
- 推荐使用 **v2 版本**，更稳定、不卡顿

## 🆚 版本对比

| 版本 | 去重 | 代理 | 稳定性 | 推荐度 |
|------|------|------|--------|--------|
| v2 (最新) | ✅ | ✅ | ⭐⭐⭐ | 🔥🔥🔥 |
| advanced | ✅ | ✅ | ⭐⭐ | 🔥🔥 |
| dedup | ✅ | ❌ | ⭐⭐ | 🔥 |
| 基础版 | ❌ | ❌ | ⭐ | - |