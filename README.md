<div align="center">

# 悦尚科技有限公司
**Yueshang Technology Co., Ltd.**

让中国工厂也用得起的 AI 工厂大脑 · AI for Cross-Border Manufacturing

[![Live Demo](https://img.shields.io/badge/Live%20Demo-supergokou.github.io%2Fyueshang-7C3AED?style=for-the-badge&logo=github&logoColor=white)](https://supergokou.github.io/yueshang/)
[![Copilot Demo](https://img.shields.io/badge/Copilot%20Demo-yuechangcopilot-06B6D4?style=for-the-badge&logo=githubpages&logoColor=white)](https://supergokou.github.io/yuechangcopilot/)
[![Stack](https://img.shields.io/badge/Stack-Python%20%7C%20FastAPI%20%7C%20YOLOv8%20%7C%20RAG-F59E0B?style=for-the-badge)](#)
[![License](https://img.shields.io/badge/License-Proprietary-DC2626?style=for-the-badge)](#)

**[在线官网 →](https://supergokou.github.io/yueshang/)**  ·  **[作品集 →](https://supergokou.github.io/yueshang/works.html)**  ·  **[公司彩页 →](https://supergokou.github.io/yueshang/brochure.html)**

</div>

---

## 仓库一览

```
Yueshang/
├── README.md                       ← 你正在看的文件
├── docs/
│   ├── product-matrix.md           ← 产品矩阵
│   └── business-plan.md            ← 商业计划单页
│
├── aoi-platform/                   ← 产品 1: 通用工业视觉质检平台
│   ├── README.md
│   ├── src/yueshang_aoi/           ← Python 包
│   │   ├── core/                   ← Pipeline / Profile / Result
│   │   ├── stages/                 ← Localizer + ROIDetector
│   │   ├── routes/                 ← 4 路检测：CNN/Golden/OpenCV/Highpass
│   │   ├── reporting/              ← 多语种 HTML/JSON 报告
│   │   └── cli/                    ← yueshang-aoi CLI
│   ├── configs/
│   │   ├── defaults.yaml
│   │   └── profiles/               ← 7 个内置品类
│   │       ├── keyboard.yaml
│   │       ├── connector.yaml
│   │       ├── charger.yaml
│   │       ├── plastic_part.yaml
│   │       ├── metal_part.yaml
│   │       ├── pcb.yaml
│   │       └── toy.yaml
│   ├── examples/
│   ├── tests/
│   └── docs/adding-a-product.md
│
├── trade-copilot/                  ← 产品 2: 出海 AI Copilot
│   ├── README.md
│   ├── .env.example
│   ├── src/yueshang_copilot/
│   │   ├── core/                   ← Settings + Schemas
│   │   ├── llm/                    ← Claude/Qwen/DeepSeek/Local 路由
│   │   ├── rag/                    ← Embed/Store/Retrieve/QA
│   │   ├── agents/                 ← 6 大 Agent
│   │   │   ├── hscode.py
│   │   │   ├── inquiry_reply.py
│   │   │   ├── compliance.py
│   │   │   ├── product_page.py
│   │   │   └── buyer_profile.py
│   │   └── api/                    ← FastAPI Gateway
│   ├── data/seed/                  ← HS Code / 合规 / 询盘模板种子
│   └── tests/
│
├── index.html                      ← 产品 3: 官网首页 (GH Pages 入口)
├── styles.css
├── app.js
├── works.html                      ← 作品集页面
├── works.css
├── brochure.html                   ← 公司彩页 (20 页, A4 横版, 可打印)
├── brochure.css
├── public/                         ← 图片素材 (logo, screenshots, university logos)
├── logo/                           ← brochure 用的 logo 副本
└── universities/                   ← brochure 用的大学 logo
```

---

## 快速启动

### 1) AOI 平台（单图烟雾测试）
```bash
cd aoi-platform
pip install -r requirements.txt
pip install -e .
yueshang-aoi list-profiles
yueshang-aoi inspect --profile plastic_part --input some_image.jpg --output ./out --report-lang en
```

### 2) Trade Copilot（API 服务）
```bash
cd trade-copilot
pip install -r requirements.txt
cp .env.example .env       # 填入 ANTHROPIC_API_KEY
python -m yueshang_copilot.rag.ingest data/seed/  --collection demo
uvicorn yueshang_copilot.api.main:app --reload --port 8000
# Swagger: http://localhost:8000/docs
```

### 3) 官方网站 + 彩页（本地预览）
```bash
python -m http.server 8080
# 打开 http://localhost:8080/index.html
# 打开 http://localhost:8080/works.html
# 打开 http://localhost:8080/brochure.html (20 页, 浏览器打印即得 PDF)
```

部署: GitHub Pages 直接服务于仓库根目录,Settings → Pages → Source: `main` → `/ (root)`。

---

## 三大交付一览

| 交付 | 形态 | 状态 |
|------|------|------|
| **YueshangAOI** | Python 包 + CLI + 7 个内置 Profile | ✅ 7/7 profile 烟雾测试通过 |
| **YueshangCopilot** | FastAPI 服务 + 6 大 Agent + 多语种 RAG | ✅ Schema/Config 通过，需 API Key 才能跑 LLM |
| **官方网站** | 单页站 (HTML/CSS/JS) | ✅ 可直接 `python -m http.server` 预览 |
| **公司彩页** | 20 页 A4 横版 HTML，可打印为 PDF | ✅ 浏览器 `Ctrl+P` 即得 PDF |
| **商业文档** | 产品矩阵 + 商业计划单页 | ✅ Markdown，可直接发投资人 |

---

## 公司信息

- **名称**: 悦尚科技有限公司 / Yueshang Technology Co., Ltd.
- **总部**: 浙江·杭州
- **成立**: 2026
- **创始团队**: AI 视觉算法工程师 + 资深外贸运营人
- **业务**: 工业视觉质检 · 出海 AI Copilot · 跨境数据中台

---

© 2026 悦尚科技有限公司 · All rights reserved.
