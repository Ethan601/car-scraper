# Canadian Used Car Listing Scraper - Deployment Guide

这是一个完整的部署指南，将教你如何把这个应用部署到免费的云服务上，然后在手机上使用。

## 目录
1. [快速开始](#快速开始)
2. [部署到Render（推荐）](#部署到render推荐)
3. [部署到Railway](#部署到railway)
4. [部署到Heroku](#部署到heroku)
5. [本地测试](#本地测试)
6. [使用指南](#使用指南)
7. [常见问题](#常见问题)

---

## 快速开始

### 你需要的东西：
- GitHub账户（免费）
- 云服务账户（Render、Railway或Heroku，都是免费的）
- OpenAI API密钥（用于AI总结功能，可选）

### 应用包含什么：
- **Kijiji爬虫**：从Kijiji抓取二手车信息
- **AutoTrader爬虫**：从AutoTrader抓取二手车信息
- **AI总结功能**：用OpenAI自动总结车辆描述
- **手机友好界面**：可以在手机浏览器直接使用

---

## 部署到Render（推荐）

Render是最简单的选择，完全免费，而且部署过程最简单。

### 步骤1：准备代码（GitHub）

1. 创建GitHub账户（如果还没有）：https://github.com/signup
2. 创建一个新的仓库：
   - 点击右上角的 `+` → `New repository`
   - 仓库名称：`car-scraper`
   - 选择 `Public`
   - 点击 `Create repository`

3. 上传代码到GitHub：
   ```bash
   # 在你的电脑上，进入项目文件夹
   cd /path/to/car_scraper
   
   # 初始化git
   git init
   git add .
   git commit -m "Initial commit"
   
   # 添加远程仓库（替换USERNAME为你的GitHub用户名）
   git branch -M main
   git remote add origin https://github.com/USERNAME/car-scraper.git
   git push -u origin main
   ```

### 步骤2：在Render上部署

1. 访问 https://render.com 并注册（可以用GitHub账户直接登录）

2. 点击 `New +` → `Web Service`

3. 选择 `Deploy an existing Git repository`
   - 点击 `Connect account` 连接你的GitHub
   - 选择 `car-scraper` 仓库

4. 填写部署配置：
   - **Name**: `car-scraper`（或任何你喜欢的名字）
   - **Environment**: `Python 3`
   - **Region**: 选择离你最近的（例如 `Oregon` 或 `Frankfurt`）
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

5. 在 `Environment` 部分添加环境变量：
   - 点击 `Add Environment Variable`
   - 如果你想使用AI总结功能，添加：
     - **Key**: `OPENAI_API_KEY`
     - **Value**: 你的OpenAI API密钥（从 https://platform.openai.com/api-keys 获取）
   - 如果不需要AI功能，可以跳过这一步

6. 点击 `Create Web Service`

7. 等待部署完成（通常需要2-5分钟）

8. 部署完成后，你会看到一个URL，例如：`https://car-scraper-xxxx.onrender.com`

9. **在手机上打开这个URL**，就可以使用应用了！

---

## 部署到Railway

Railway也是一个很好的免费选择。

### 步骤1：准备代码（同上）

按照"部署到Render"中的步骤1上传代码到GitHub。

### 步骤2：在Railway上部署

1. 访问 https://railway.app 并注册（可以用GitHub账户直接登录）

2. 点击 `New Project` → `Deploy from GitHub repo`

3. 选择 `car-scraper` 仓库

4. Railway会自动检测这是一个Python项目并配置部署

5. 添加环境变量：
   - 点击 `Variables`
   - 如果需要AI功能，添加：
     - **OPENAI_API_KEY**: 你的OpenAI API密钥

6. 点击 `Deploy`

7. 等待部署完成，然后点击生成的URL访问应用

---

## 部署到Heroku

Heroku的免费层已经改变，但仍然可以部署。

### 步骤1：准备代码（同上）

按照"部署到Render"中的步骤1上传代码到GitHub。

### 步骤2：在Heroku上部署

1. 访问 https://www.heroku.com 并注册

2. 点击 `New` → `Create new app`
   - 输入应用名称：`car-scraper-yourname`
   - 选择地区：`United States` 或 `Europe`
   - 点击 `Create app`

3. 在 `Deployment method` 中选择 `GitHub`
   - 连接你的GitHub账户
   - 搜索并选择 `car-scraper` 仓库

4. 在 `Config Vars` 中添加环境变量：
   - 点击 `Reveal Config Vars`
   - 如果需要AI功能，添加：
     - **Key**: `OPENAI_API_KEY`
     - **Value**: 你的OpenAI API密钥

5. 点击 `Deploy Branch`

6. 等待部署完成，点击 `View` 打开应用

---

## 本地测试

如果你想在部署前在自己的电脑上测试应用：

### 步骤1：安装Python

确保你的电脑上安装了Python 3.8或更高版本。

### 步骤2：安装依赖

```bash
cd /path/to/car_scraper
pip install -r requirements.txt
```

### 步骤3：运行应用

```bash
python app.py
```

### 步骤4：访问应用

打开浏览器，访问：`http://localhost:5000`

你应该会看到应用的界面。

### 步骤5：停止应用

在终端中按 `Ctrl+C` 停止应用。

---

## 使用指南

### 在手机上使用应用

1. 打开手机浏览器（Safari、Chrome等）
2. 输入你的应用URL（例如：`https://car-scraper-xxxx.onrender.com`）
3. 你会看到一个搜索表单

### 搜索车辆

1. **输入车型**：例如 "Honda Civic"、"Toyota Camry"、"Ford Focus"
2. **选择地区**：选择你想搜索的加拿大地区
3. **选择平台**：勾选想搜索的平台（Kijiji、AutoTrader等）
4. **启用AI总结**（可选）：如果勾选，应用会用AI总结每个车辆的描述
5. **点击搜索**：应用会从选定的平台抓取数据

### 查看结果

- 每个车辆显示为一张卡片
- 显示信息包括：价格、年份、里程、位置、描述
- 点击 "View on [Platform]" 可以在原网站查看完整信息

---

## 常见问题

### Q1: 应用显示"No listings found"

**原因**：可能是网站结构改变了，或者搜索参数不正确。

**解决方案**：
- 尝试用不同的车型搜索
- 尝试不同的地区
- 检查应用的日志（在Render/Railway/Heroku的仪表板中）

### Q2: AI总结功能不工作

**原因**：可能是没有设置OpenAI API密钥，或者密钥无效。

**解决方案**：
1. 获取OpenAI API密钥：https://platform.openai.com/api-keys
2. 在你的云服务仪表板中添加环境变量
3. 重新部署应用

### Q3: 应用很慢

**原因**：爬虫需要时间从网站抓取数据。

**解决方案**：
- 这是正常的，第一次搜索可能需要30-60秒
- 如果超过2分钟还没有结果，可能是网络问题

### Q4: 我想修改应用

**解决方案**：
1. 编辑你GitHub仓库中的文件
2. 提交更改（`git commit` 和 `git push`）
3. 云服务会自动重新部署

### Q5: 如何在手机上添加到主屏幕

**iPhone**：
1. 打开Safari浏览器
2. 点击分享按钮
3. 选择"添加到主屏幕"

**Android**：
1. 打开Chrome浏览器
2. 点击右上角的菜单（三个点）
3. 选择"安装应用"或"添加到主屏幕"

---

## 获取OpenAI API密钥（用于AI总结功能）

1. 访问 https://platform.openai.com/api-keys
2. 登录或创建OpenAI账户
3. 点击 `Create new secret key`
4. 复制密钥
5. 在你的云服务中添加为环境变量 `OPENAI_API_KEY`

**注意**：OpenAI API不是完全免费的，但有免费额度。检查他们的定价页面了解详情。

---

## 支持和反馈

如果遇到问题：
1. 检查应用的日志（在云服务仪表板中）
2. 确保所有环境变量都正确设置
3. 尝试重新部署应用

---

## 应用架构简介

**给初学者的简单解释**：

这个应用分为两部分：

1. **后端（Backend）**：运行在云服务器上的Python代码
   - 从Kijiji和AutoTrader抓取数据
   - 用OpenAI API总结描述
   - 返回数据给前端

2. **前端（Frontend）**：运行在你手机浏览器中的HTML/CSS/JavaScript
   - 显示搜索表单
   - 显示搜索结果
   - 和后端通信

当你在手机上点击"搜索"时：
1. 前端发送请求到后端
2. 后端从网站抓取数据
3. 后端处理数据（提取信息、总结描述）
4. 后端返回数据给前端
5. 前端显示结果

---

祝你使用愉快！有任何问题，随时问我。

