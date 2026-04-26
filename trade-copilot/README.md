<div align="center">

# YueshangCopilot

**AI Copilot for Foreign-Trade & Cross-Border Business**

外贸出海智能 Copilot · 多语种 RAG · 私域知识库 · HS Code · 合规 · 询盘速回

</div>

---

## 概述

YueshangCopilot 是悦尚科技为外贸/出海企业打造的 AI Copilot。它把企业的产品资料、SOP、海关编码库、合规要求等内化成一个可问可答的私域 RAG 知识库，并以**询盘速回 / HS Code / 合规雷达 / 详情页生成 / 买家背调**等开箱即用 Agent 暴露能力。

### 核心特性

- **多语种 RAG**：中 / 英 / 西 / 葡 / 阿，文档可任意语种入库，问答可任意语种输出
- **HS Code 助手**：6/8/10 位编码自动匹配，覆盖中国 + 主要贸易国
- **合规雷达**：根据目标市场（CE / FCC / RoHS / CCC / FDA / REACH）扫描产品资料
- **询盘速回**：邮件 → 报价 / 起草回复 / 跟进序列
- **详情页生成**：Amazon / Shopify / eBay / 阿里国际站，多语种 SEO
- **本地化部署**：可对接私有大模型（Qwen / DeepSeek），数据不出企业

---

## 架构

```
                                  ┌──────────────────┐
                                  │  Web UI (Next.js)│
                                  └────────┬─────────┘
                                           │
                                  ┌────────▼─────────┐
                                  │  FastAPI Gateway │
                                  └────────┬─────────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              ▼                            ▼                            ▼
       ┌─────────────┐            ┌─────────────────┐         ┌──────────────────┐
       │   Agents    │◄──────────►│   RAG Engine    │◄────────│  Vector Store    │
       │ Inquiry/HS/ │            │ Embed / Retrieve│         │  ChromaDB / pgv  │
       │ Compliance/ │            │ + Rerank        │         │                  │
       │ ProdPage/   │            └────────┬────────┘         └──────────────────┘
       │ BuyerProfile│                     │
       └──────┬──────┘                     ▼
              │                  ┌──────────────────┐
              ▼                  │  i18n Translator │
       ┌──────────────┐          │  zh/en/es/pt/ar  │
       │  LLM Router  │◄─────────┴──────────────────┘
       │ (Claude/Qwen │
       │  /DeepSeek)  │
       └──────────────┘
```

---

## 快速开始

### 安装
```bash
cd trade-copilot
pip install -r requirements.txt
cp .env.example .env       # 填入 ANTHROPIC_API_KEY 或 DASHSCOPE_API_KEY
```

### 一键索引种子文档
```bash
python -m yueshang_copilot.rag.ingest data/seed/  --collection demo
```

### 启动 API 服务
```bash
uvicorn yueshang_copilot.api.main:app --reload --port 8000
# Swagger: http://localhost:8000/docs
```

### 试一个 Agent
```bash
# HS Code Agent
curl -X POST http://localhost:8000/agents/hscode \
     -H "Content-Type: application/json" \
     -d '{"product_name_zh":"304 不锈钢保温杯","product_name_en":"304 stainless steel insulated bottle","target_country":"US"}'

# 询盘速回 Agent
curl -X POST http://localhost:8000/agents/inquiry-reply \
     -H "Content-Type: application/json" \
     -d '{"inquiry":"Hi, can you make 5000pcs custom-printed coffee mugs by Aug?", "lang":"en"}'
```

---

## 项目结构

```
trade-copilot/
├── README.md
├── requirements.txt
├── .env.example
├── src/yueshang_copilot/
│   ├── api/                # FastAPI app
│   │   ├── main.py
│   │   └── routes/
│   ├── rag/                # 文档索引 / 检索 / rerank
│   │   ├── ingest.py
│   │   ├── retriever.py
│   │   └── store.py
│   ├── agents/             # 高层 Agent
│   │   ├── inquiry_reply.py
│   │   ├── hscode.py
│   │   ├── compliance.py
│   │   ├── product_page.py
│   │   └── buyer_profile.py
│   ├── i18n/               # 多语种翻译
│   │   └── translate.py
│   ├── llm/                # 模型路由
│   │   └── router.py
│   └── core/
│       ├── config.py
│       └── schema.py
├── data/seed/              # 种子知识：HS Code 表、合规要求、详情页模板
└── tests/
```

---

## 可插拔大模型

通过 `LLM_PROVIDER` 环境变量切换：

| Provider | 模型 | 适用 |
|----------|-----|------|
| `anthropic` | claude-sonnet-4-6 | 默认，国际客户、英文场景 |
| `qwen` | qwen2.5-72b-instruct | 国内部署、中文场景 |
| `deepseek` | deepseek-v3 | 高性价比、批量场景 |
| `local` | 本地部署 (Ollama / vLLM) | 数据不出企业 |

---

## License

Proprietary © 2026 悦尚科技有限公司
