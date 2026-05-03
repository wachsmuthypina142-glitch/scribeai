# ScribeAI - 个人知识管理 AI 助手
<div align="center">
# scribeai
个人知识管理AI助手 - 收藏内容问答系统
帮你把碎片化的链接收藏，变成结构化的知识

## ✨ 功能特点
链接收藏：粘贴URL或浏览器插件一键收藏任意网页
文件上传：支持PDF、TXT、Markdown 本地文件
AI 智能分析：自动总结、提取要点、生成标签 
知识图谱：可视化知识网络，发现知识关联
知识问答：基于收藏内容进行智能问答
分类管理：灵活的分类和标签系统

## 🚀 快速开始

### 环境要求
Python: 3.12 或更高版本
操作系统: Windows / macOS / Linux

### 1. 安装依赖

**Windows:**
```bash
cd scribeai
start.bat
```

**macOS / Linux:**
```bash
cd scribeai
chmod +x start.sh
./start.sh
```

或手动安装：
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env` 文件，填入你的 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=你的API密钥
```

> 💡 获取 DeepSeek API Key:https://platform.deepseek.com/api_keys

### 3. 启动服务

```bash
cd backend
python main.py
```

启动成功后访问：**http://localhost:8000**

---

## 📖 使用指南

### 收藏网页内容

1. 在输入框粘贴网址
2. 点击「收藏」按钮
3. 等待 AI 自动分析（抓取内容 → 生成摘要 → 提取要点 → 打标签）
4. 查看生成的结果

### 上传本地文件

支持 **PDF**、**TXT**、**Markdown** 文件：

1. 拖拽文件到上传区域，或点击选择文件
2. AI 自动解析并分析内容

### 知识问答

1. 切换到「问答」页面
2. 输入你的问题
3. 基于你的知识库获得精准答案

### 知识图谱

1. 切换到「知识图谱」页面
2. 可视化查看所有收藏的关联
3. 点击节点查看详情

---

## 🛠️ 项目结构

```
scribeai/
├── backend/                      # FastAPI 后端服务
│   ├── main.py                  # 程序入口
│   ├── database.py              # SQLite 数据库
│   ├── requirements.txt        # Python 依赖
│   ├── .env.example            # 环境变量模板
│   ├── routers/                # API 路由
│   │   ├── __init__.py
│   │   ├── collect.py          # 收藏 API
│   │   ├── knowledge.py        # 知识图谱 API
│   │   └── search.py           # 问答 API
│   └── services/               # 服务层
│       ├── parser.py           # 内容解析
│       ├── pdf_parser.py       # PDF 解析
│       └── llm.py              # LLM 调用
│
├── frontend/                    # 前端界面
│   └── index.html              # 单页应用
│
├── browser-extension/          # Chrome 浏览器插件
│   ├── manifest.json          # 插件配置
│   ├── popup.html             # 弹窗界面
│   ├── popup.js               # 插件逻辑
│   ├── content.js             # 内容脚本
│   └── background.js          # 后台脚本
│
├── start.bat                   # Windows 启动脚本
├── start.sh                   # Linux/macOS 启动脚本
├── .gitignore                 # Git 忽略配置
├── README.md                  # 项目文档
└── PLAN.md                   # 项目计划
```

---

## 🔌 API 接口

启动后端后访问 **http://localhost:8000/docs** 查看完整 API 文档（Swagger UI）。

### 主要接口

| 方法 | 路径 | 描述 |
|------|------|------|
| `POST` | `/api/collect` | 收藏 URL |
| `POST` | `/api/upload` | 上传本地文件 |
| `GET` | `/api/contents` | 获取收藏列表 |
| `GET` | `/api/contents/{id}` | 获取单条详情 |
| `DELETE` | `/api/contents/{id}` | 删除收藏 |
| `PUT` | `/api/contents/{id}` | 更新收藏 |
| `POST` | `/api/categories` | 创建分类 |
| `GET` | `/api/knowledge/tags` | 获取所有标签 |
| `GET` | `/api/knowledge/by-tag` | 按标签查询 |
| `GET` | `/api/graph` | 获取知识图谱数据 |
| `POST` | `/api/ask` | 知识问答 |
| `GET` | `/api/search` | 搜索收藏内容 |

---

## 🧩 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | FastAPI + SQLAlchemy |
| 数据库 | SQLite |
| AI 服务 | DeepSeek API |
| 前端 | Vue 3 + TailwindCSS + vis-network |
| 浏览器插件 | Chrome Extension (Manifest V3) |
| 内容解析 | BeautifulSoup, Playwright |
| PDF 解析 | PyMuPDF (fitz) |

---

## 🌐 浏览器插件安装

1. 打开 Chrome，进入 `chrome://extensions/`
2. 开启右上角 **开发者模式**
3. 点击 **加载已解压的扩展程序**
4. 选择项目中的 `browser-extension` 文件夹

安装后点击插件图标即可一键收藏当前页面！

---

## 🐳 Docker 部署

```bash
# 构建镜像
docker build -t scribeai .

# 运行容器
docker run -d -p 8000:8000 \
  -e DEEPSEEK_API_KEY=你的API密钥 \
  scribeai
```

---

## ⚙️ 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 必填 |
| `DEEPSEEK_API_URL` | API 地址 | https://api.deepseek.com |
| `HOST` | 服务地址 | 0.0.0.0 |
| `PORT` | 服务端口 | 8000 |

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

如果你发现了 bug 或有新功能想法，请：

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

---

## 📄 许可证

本项目基于 MIT 许可证开源，详情见 [LICENSE](LICENSE) 文件。

<div align="center">

**如果这个项目对你有帮助，请给我一个 ⭐️**

</div>

