# GMGN API 爬虫使用说明

## 功能说明
这个爬虫会自动监控浏览器中 gmgn.ai 网站的网络请求，当检测到 Twitter 用户搜索 API 的调用时，自动提取并保存所有的用户数据到 JSON 文件中。

## 安装步骤

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 安装浏览器驱动
```bash
playwright install chromium
```

## 使用方法

### 🔥 方式一：v2 高级版（最推荐）⭐⭐⭐
**适用场景：需要代理访问、追求稳定性**

```bash
# 使用配置文件中的代理（推荐）
python gmgn_crawler_v2.py

# 使用命令行指定代理
python gmgn_crawler_v2.py --proxy http://127.0.0.1:7890

# 查看帮助
python gmgn_crawler_v2.py --help
```

**新特性：**
- ✅ 使用响应监听模式，不拦截请求
- ✅ 页面加载流畅，不会卡顿
- ✅ 代理配置更可靠
- ✅ 自动去重、断点续传

**配置代理（重要）：**
如果你访问 gmgn.ai 需要代理，编辑 `config.py` 文件：
```python
PROXY = "http://127.0.0.1:7890"  # 改为你的代理地址
```

### 方式二：高级版爬虫（支持代理和配置）⭐⭐
```bash
# 使用默认配置
python gmgn_crawler_advanced.py

# 使用命令行代理
python gmgn_crawler_advanced.py --proxy http://127.0.0.1:7890

# 自定义输出文件
python gmgn_crawler_advanced.py --output my_data.json

# 查看帮助
python gmgn_crawler_advanced.py --help
```

### 方式三：去重版爬虫⭐
```bash
python gmgn_crawler_dedup.py
```
输出文件：`gmgn_users_dedup.json`
- ✅ 自动去重（根据 user_id）
- ✅ 支持断点续传
- ✅ 按粉丝数排序

### 方式四：基础版爬虫
```bash
python gmgn_crawler.py
```
输出文件：`gmgn_users.json`

### 使用流程
1. 运行脚本后，会自动打开浏览器（显示空白页）
2. **手动在浏览器地址栏输入并访问: https://gmgn.ai/**
3. 在浏览器中正常操作页面（搜索、浏览等）
4. 爬虫会自动在后台捕获所有 Twitter 用户搜索的 API 响应
5. 数据会实时保存到 JSON 文件中
6. 按 `Ctrl+C` 停止爬虫

### 数据分析
```bash
# 查看数据统计
python analyze_data.py analyze

# 按标签导出数据到单独文件
python analyze_data.py export

# 分析指定文件
python analyze_data.py analyze gmgn_users.json
```

### 目标 API
爬虫会监控以下 API：
```
https://gmgn.ai/vas/api/v1/twitter/user/search?d*
```

## 输出文件

### gmgn_users.json
爬虫会将所有捕获的用户数据保存到这个文件中，格式如下：

```json
{
  "total_users": 100,
  "last_updated": "2025-12-19T12:00:00",
  "users": [
    {
      "handle": "whitehouse",
      "user_id": "1879644163769335808",
      "user_tags": ["politics"],
      "platform": 0,
      "followers": 1910,
      "followed": false
    },
    ...
  ]
}
```

## 特点
- ✅ 自动监控网络请求
- ✅ 实时保存数据
- ✅ 自动去重和累加用户
- ✅ 显示捕获进度
- ✅ 支持手动停止（Ctrl+C）

## 注意事项
1. 需要保持浏览器窗口打开
2. 必须手动在浏览器中访问 gmgn.ai（不会自动跳转）
3. 数据会实时保存，不用担心丢失
4. 可以多次运行，去重版会自动合并数据

## 常见问题排查

### ❌ 问题：连接超时 `ETIMEDOUT`
**现象：** 报错 `Route.fetch: connect ETIMEDOUT` 或 `connect ETIMEDOUT 202.160.128.14:443`

**原因：** 网络无法直接访问 gmgn.ai，需要使用代理

**解决方案：**
1. **使用 v2 版本（推荐）：**
   ```bash
   python gmgn_crawler_v2.py --proxy http://127.0.0.1:7890
   ```

2. **配置代理文件：**
   编辑 `config.py`，修改代理地址：
   ```python
   PROXY = "http://127.0.0.1:7890"  # 改为你的代理
   ```
   然后运行：
   ```bash
   python gmgn_crawler_v2.py
   ```

3. **确认代理地址：**
   - Clash 默认: `http://127.0.0.1:7890`
   - v2ray 默认: `socks5://127.0.0.1:1080`
   - 检查你的代理软件确认端口号

### ❌ 问题：运行时报错 `net::ERR_ABORTED`
**解决方案：**
- 现在脚本会打开空白页，需要你**手动访问** `https://gmgn.ai/`
- 不要关闭或刷新浏览器，让它保持打开状态

### ❌ 问题：无法访问 gmgn.ai 网站
**解决方案：**
1. 使用高级版爬虫并配置代理：
   ```bash
   python gmgn_crawler_advanced.py --proxy http://127.0.0.1:7890
   ```
2. 或者编辑 `config.py` 文件设置代理

### ❌ 问题：没有捕获到任何数据
**原因分析：**
- 你可能没有在页面上触发用户搜索功能
- 需要在 gmgn.ai 网站上进行搜索、浏览用户等操作

**解决方案：**
1. 确保在浏览器中访问了 https://gmgn.ai/
2. 在页面上搜索用户或浏览用户列表
3. 观察终端输出，看是否有 "捕获到请求" 的提示

### ❌ 问题：Playwright 安装失败
**解决方案：**
```bash
# 重新安装
pip install playwright
playwright install chromium

# 如果还是失败，尝试
python -m playwright install chromium
```

### 💡 使用技巧
1. **如何高效抓取：** 在 gmgn.ai 页面上多搜索、多翻页，爬虫会自动捕获所有请求
2. **断点续传：** 使用去重版或高级版，关闭后再运行会继续累加数据
3. **查看进度：** 终端会实时显示捕获到的请求数和用户数
4. **数据分析：** 运行 `python analyze_data.py analyze` 可以查看详细统计