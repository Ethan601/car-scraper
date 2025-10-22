# Canadian Used Car Listing Scraper

一个简单的网页应用，可以从Kijiji、AutoTrader和Facebook Marketplace上自动收集加拿大二手车信息。

## 功能

- 🔍 **多平台搜索**：同时从Kijiji、AutoTrader和Facebook Marketplace搜索
- 📱 **手机友好**：完全响应式设计，可以在手机上直接使用
- 🤖 **AI总结**：使用OpenAI自动总结车辆描述（可选）
- 💰 **价格、里程、年份**：自动提取关键信息
- 🌍 **地区选择**：支持加拿大所有省份

## 快速开始

### 本地运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
python app.py
```

3. 打开浏览器访问：`http://localhost:5000`

### 部署到云服务

详见 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

支持的云服务：
- **Render**（推荐）
- **Railway**
- **Heroku**

## 项目结构

```
car_scraper/
├── app.py                    # 主应用文件（Flask后端）
├── requirements.txt          # Python依赖
├── Procfile                  # Heroku配置
├── runtime.txt              # Python版本指定
├── templates/
│   └── index.html           # 前端HTML/CSS/JavaScript
├── DEPLOYMENT_GUIDE.md      # 详细部署指南
└── README.md                # 本文件
```

## 技术栈

- **后端**：Python Flask
- **爬虫**：BeautifulSoup + Requests
- **AI**：OpenAI API
- **前端**：HTML5 + CSS3 + JavaScript
- **部署**：Render / Railway / Heroku

## 环境变量

可选的环境变量：

- `OPENAI_API_KEY`：OpenAI API密钥（用于AI总结功能）
- `FLASK_ENV`：Flask环境（production或development）

## 使用示例

1. 打开应用
2. 输入车型（例如："Honda Civic"）
3. 选择地区
4. 选择要搜索的平台
5. 点击搜索
6. 查看结果

## 注意事项

- 首次搜索可能需要30-60秒，因为需要从网站抓取数据
- 网站结构改变时，爬虫可能需要更新
- 频繁搜索可能被网站限制，请合理使用

## 常见问题

**Q: 为什么搜索很慢？**
A: 爬虫需要从网站抓取数据，这需要时间。这是正常的。

**Q: AI总结功能需要付费吗？**
A: OpenAI API不是完全免费的，但有免费额度。查看他们的定价了解详情。

**Q: 可以修改应用吗？**
A: 可以！这是开源的，你可以随意修改。

## 许可证

MIT License

## 作者

Created with ❤️ for Canadian car hunters

---

更多信息请查看 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

