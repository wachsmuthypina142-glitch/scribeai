# ScribeAI - 个人知识管理AI助手（最终版）

## 产品定位

> 一个开源的个人知识管理AI助手，帮助用户把碎片化的链接收藏变成结构化的知识。

## 目标用户

- **学习者**：收藏了大量教程/文章，但消化不了
- **研究者**：需要管理论文、笔记、想法
- **创作者**：需要积累素材、建立知识体系

## 核心功能

| 功能 | 描述 | 用户价值 |
|------|------|---------|
| 链接收藏 | 粘贴URL / 浏览器插件一键收藏 | 随时随地收藏 |
| AI消化 | 自动总结 + 关键要点 + 实体提取 | 快速获取精华 |
| 知识图谱 | 标签聚合 + 相关主题推荐 | 发现知识关联 |
| 知识问答 | 基于收藏内容回答问题 | 深度理解知识 |

## 用户流程

```
1. 收藏内容
   ├── 方式A: 粘贴URL到网页输入框
   └── 方式B: 浏览器插件一键收藏

2. AI自动处理
   ├── 抓取网页内容
   ├── 生成总结
   ├── 提取关键要点
   └── 提取标签/实体

3. 知识管理
   ├── 查看收藏列表
   ├── 按标签筛选
   └── 查看知识图谱

4. 知识问答
   └── 用自己的知识回答问题
```

## 技术栈

- **后端**: FastAPI + SQLAlchemy
- **前端**: Next.js 14 + TailwindCSS + shadcn/ui
- **数据库**: SQLite（简化版）
- **AI**: DeepSeek (API: https://api.deepseek.com)
- **浏览器插件**: Chrome Extension (Manifest V3)
- **Python**: 3.12+

## 项目结构

```
scribeai/
├── backend/
│   ├── main.py              # FastAPI入口
│   ├── database.py          # SQLite连接
│   ├── requirements.txt     # 依赖
│   ├── routers/
│   │   ├── collect.py       # 收藏API
│   │   ├── knowledge.py     # 知识图谱API
│   │   └── search.py        # 问答API
│   └── services/
│       ├── parser.py        # 内容解析器
│       └── llm.py           # LLM服务
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # 首页
│   │   ├── collection/      # 收藏页面
│   │   ├── knowledge/       # 知识图谱页面
│   │   └── search/          # 问答页面
│   ├── components/          # UI组件
│   └── lib/
│       └── api.ts           # API调用
│
├── extension/
│   ├── manifest.json        # 插件配置
│   ├── popup.html           # 弹出窗口
│   └── popup.js             # 收藏逻辑
│
└── docker-compose.yml       # 部署配置
```

## 数据库设计

### contents 表（内容收藏）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 主键UUID |
| url | TEXT | 原始链接 |
| title | TEXT | 标题 |
| content | TEXT | 正文内容 |
| summary | TEXT | AI总结 |
| key_points | JSON | 关键要点列表 |
| tags | JSON | 提取的标签 |
| user_id | TEXT | 用户设备ID |
| created_at | DATETIME | 收藏时间 |

## API设计

### 收藏API

```
POST /api/collect
Body: { "url": "https://..." }
Response: {
  "success": true,
  "data": {
    "id": "xxx",
    "title": "文章标题",
    "summary": "AI总结...",
    "key_points": ["要点1", "要点2"],
    "tags": ["AI", "前端"]
  }
}
```

### 知识图谱API

```
GET /api/knowledge/tags
Response: {
  "success": true,
  "data": {
    "tags": [
      {"name": "AI", "count": 15},
      {"name": "前端", "count": 8}
    ]
  }
}

GET /api/knowledge/by-tag?tag=AI
Response: {
  "success": true,
  "data": {
    "contents": [...]
  }
}
```

### 问答API

```
POST /api/ask
Body: { "question": "xxx" }
Response: {
  "success": true,
  "data": {
    "answer": "AI回答...",
    "sources": [{"title": "...", "url": "..."}]
  }
}
```

## 浏览器插件功能

- 一键收藏当前网页
- 显示收藏状态
- 支持登录/匿名收藏

## 开发时间线

| 阶段 | 内容 | 预计时间 |
|------|------|---------|
| Phase 1 | 项目初始化 | Day 1 |
| Phase 2 | 后端核心 | Day 2-3 |
| Phase 3 | 前端界面 | Day 3-4 |
| Phase 4 | 浏览器插件 | Day 5 |

**总计：约5天可完成MVP**

## 面试可讲的亮点

1. **市场洞察**：信息过载时代，用户需要"知识消化"而非"更多收藏"
2. **产品设计**：简化不切实际的功能，聚焦可实现的价值
3. **技术深度**：
   - 网页内容解析（BeautifulSoup）
   - LLM调用（Anthropic SDK + DeepSeek API）
   - RAG问答（基于自有知识回答）
   - Chrome Extension开发
4. **全栈能力**：FastAPI + Next.js + SQLite
