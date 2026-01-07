# 工具目录说明

本目录包含各种辅助工具，用于管理项目和维护系统。

## Cookies管理工具

### 1. manual_login.py
使用Selenium自动化浏览器登录抖音并获取cookies。

**使用方法：**
```bash
python tools/manual_login.py
```

**依赖：**
- selenium
- webdriver-manager

**注意：** 如果遇到网络问题，请使用Playwright版本。

---

### 2. manual_login_playwright.py
使用Playwright自动化浏览器登录抖音并获取cookies（推荐）。

**使用方法：**
```bash
python tools/manual_login_playwright.py
```

**依赖：**
- playwright

**优势：** 比Selenium更稳定，网络问题更少。

---

### 3. cookies_helper.html
手动获取cookies的HTML工具。

**使用方法：**
1. 在浏览器中打开 `tools/cookies_helper.html`
2. 按照页面说明操作
3. 从浏览器开发者工具复制cookies
4. 粘贴到工具中并保存

**优势：** 不需要安装任何Python依赖，最简单的方法。

---

### 4. convert_cookies.py
将表格格式的cookies转换为JSON格式。

**使用方法：**
1. 从浏览器开发者工具复制cookies（表格格式）
2. 编辑 `tools/convert_cookies.py`，将cookies粘贴到 `cookies_text` 变量
3. 运行脚本：
```bash
python tools/convert_cookies.py
```

**输出：** `douyin_cookies.json`

---

### 5. fix_cookies.py
修复cookies格式问题（如sameSite字段）。

**使用方法：**
```bash
python tools/fix_cookies.py
```

**功能：**
- 修复 `sameSite` 字段中的特殊字符
- 验证关键登录cookies是否存在
- 生成格式正确的cookies文件

---

## 数据库管理工具

### 6. rebuild_fts.py
重建全文搜索索引。

**使用方法：**
```bash
python tools/rebuild_fts.py
```

**用途：** 当全文搜索功能异常时使用。

---

### 7. reinit_db.py
重新初始化数据库结构（保留数据）。

**使用方法：**
```bash
python tools/reinit_db.py
```

**用途：** 当数据库结构需要更新时使用。

---

### 8. reset_db.py
重置数据库（删除所有数据）。

**使用方法：**
```bash
python tools/reset_db.py
```

**⚠️ 警告：** 此操作会删除所有数据，请谨慎使用！

---

## Cookies使用流程

### 推荐流程（使用Playwright）：

1. 运行登录工具：
   ```bash
   python tools/manual_login_playwright.py
   ```

2. 在浏览器中完成登录

3. 按回车键保存cookies

4. Cookies会自动保存到 `douyin_cookies.json`

### 备选流程（手动方式）：

1. 在浏览器中访问 https://www.douyin.com/

2. 完成登录

3. 按 F12 打开开发者工具

4. 复制cookies（使用 cookies_helper.html 或直接复制）

5. 如果是表格格式，运行：
   ```bash
   python tools/convert_cookies.py
   ```

6. 如果格式有问题，运行：
   ```bash
   python tools/fix_cookies.py
   ```

---

## Cookies验证

确保cookies包含以下关键信息：

- ✅ `sessionid` - 会话ID
- ✅ `sessionid_ss` - 安全会话ID
- ✅ `sid_guard` - 会话保护
- ✅ `sid_tt` - TikTok会话ID

如果缺少这些cookies，yt-dlp会返回"Fresh cookies are needed"错误。

---

## 常见问题

### Q: Cookies过期了怎么办？
A: 重新运行登录工具获取新的cookies。

### Q: 为什么还是提示"Fresh cookies are needed"？
A: 检查cookies是否包含关键登录cookies（sessionid、sid_guard等）。

### Q: Playwright/Selenium无法下载驱动怎么办？
A: 使用手动方式（cookies_helper.html）获取cookies。

### Q: 如何检查cookies是否有效？
A: 运行 `python tools/fix_cookies.py`，它会检查关键cookies。

---

## 注意事项

1. **Cookies安全：** Cookies包含敏感信息，不要分享给他人
2. **定期更新：** Cookies会过期，需要定期重新获取
3. **备份：** 建议备份有效的cookies文件
4. **网络问题：** 如果自动化工具遇到网络问题，使用手动方式

---

## 开发者信息

- 项目：短视频知识提炼工具
- 版本：1.0.0
- 最后更新：2026-01-07