<div align="center">

# XinchenAOI

**Universal AI Visual Inspection Platform for Manufacturing**

通用工业视觉质检平台 · 配置驱动 · 多品类一套代码

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF?logo=yolo&logoColor=white)](https://ultralytics.com)
[![ONNX Runtime](https://img.shields.io/badge/ONNX_Runtime-Web-FF6F00?logo=onnx&logoColor=white)](https://onnxruntime.ai)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

</div>

---

## 概述

XinchenAOI 是鑫晨科技自研的**通用工业视觉质检平台**。它把过去专门为键盘瑕疵检测构建的多路融合 pipeline，抽象成了**配置驱动的产品无关流水线**——一套代码、一套部署、通过 YAML 配置就能切换检测对象（键盘 / 连接器 / 充电器 / 五金件 / 注塑件 / 玩具 / ...）。

### 核心特性

- **配置驱动**：新增品类 = 写一份 YAML profile，不动 Python 代码
- **多路融合检测**：CNN 分类 + 金样对比 + OpenCV 形态学 + 高通边缘，任一路阳性则判 NG
- **三阶段流水线**：产品定位 → ROI 切分 → 瑕疵判定
- **Web/Edge 部署**：ONNX Runtime Web，浏览器即可运行，免服务器
- **批量+单张**：单张 ~3 秒，批量 100 张 ~5 分钟（CPU）
- **多语种报告**：中/英/西/葡，外贸品牌方可读

---

## 架构

```
                  ┌──────────────────────────────────────────┐
                  │          Product Profile (YAML)          │
                  │  - 定位策略 / ROI 模型 / 缺陷分类 / 路由 │
                  └──────────────────┬───────────────────────┘
                                     │
                                     ▼
   Input ──► Stage1: Localizer ──► Stage2: ROIDetector ──► Stage3: Multi-Route Inspector
                                                                │
                                            ┌───────────────────┼───────────────────┬─────────────────────┐
                                            ▼                   ▼                   ▼                     ▼
                                      Route A: CNN       Route B: Golden      Route C: OpenCV       Route D: Highpass
                                      (YOLOv8-cls)       Reference Match      Anomaly Detect        + Edge Density
                                            │                   │                   │                     │
                                            └───────────────────┴────────┬──────────┴─────────────────────┘
                                                                         ▼
                                                            Fusion → OK / NG + Defect Type
```

---

## 快速开始

### 安装
```bash
pip install -r requirements.txt
pip install -e .
```

### 命令行
```bash
# 用 keyboard profile 检测
yueshang-aoi inspect --profile keyboard --input ./samples/kb_001.tif --output ./out/

# 用 connector profile 批量检测
yueshang-aoi inspect --profile connector --input ./batch/ --output ./out/ --report-lang en

# 列出所有内置 profile
yueshang-aoi list-profiles
```

### Python API
```python
from yueshang_aoi import InspectionPipeline, load_profile

profile = load_profile("connector")           # 内置 profile，或传 yaml 路径
pipeline = InspectionPipeline(profile)
result = pipeline.run("photo.jpg")

print(result.overall_status)                  # "OK" / "NG"
print(result.defect_summary)                  # {"scratch": 2, "burr": 1}
result.save_report("./out/", lang="en")       # 多语种报告
```

---

## 内置 Profile

| Profile | 适用品类 | 定位方式 | 主路由 |
|---------|---------|---------|--------|
| `keyboard` | 键盘 / 键帽阵列 | OpenCV 透视矫正 | CNN + Golden + OpenCV + Highpass |
| `connector` | USB / 排针 / 端子 | 边缘检测 + ROI 模板 | CNN + Highpass |
| `charger` | 充电器外壳 / 接口 | YOLO 物体检测 | CNN + Golden |
| `plastic_part` | 注塑件 / 模具件 | 阈值分割 | OpenCV + Highpass |
| `metal_part` | 五金 / 冲压件 | 反射剥离 + 边缘 | OpenCV + Edge |
| `pcb` | PCBA / 焊点 | 模板匹配 | Golden + Highpass |
| `toy` | 玩具表面 | YOLO + 颜色聚类 | CNN + Golden |

新增品类只需 `configs/profiles/<your_product>.yaml`。详见 `docs/adding-a-product.md`。

---

## 项目结构

```
aoi-platform/
├── configs/
│   ├── defaults.yaml              # 全局默认参数
│   └── profiles/                  # 各品类 profile
│       ├── keyboard.yaml
│       ├── connector.yaml
│       └── ...
├── src/yueshang_aoi/
│   ├── core/                      # 核心抽象
│   │   ├── pipeline.py            # 主流水线
│   │   ├── product.py             # 产品抽象
│   │   ├── result.py              # 结果数据类
│   │   └── config.py              # 配置加载
│   ├── stages/                    # 三阶段流水线
│   │   ├── localizer.py           # Stage 1: 产品定位
│   │   ├── roi_detector.py        # Stage 2: 部件/ROI 检测
│   │   └── classifier.py          # Stage 3: 瑕疵判定
│   ├── routes/                    # 检测路由
│   │   ├── base.py                # Route 接口
│   │   ├── yolo_cls.py            # Route A
│   │   ├── golden_match.py        # Route B
│   │   ├── opencv_anomaly.py      # Route C
│   │   └── highpass_edge.py       # Route D
│   ├── reporting/                 # 报告生成（多语种）
│   └── cli/                       # 命令行入口
├── examples/
└── tests/
```

---

## 商业模式

XinchenAOI 提供三种交付形态：

| 形态 | 适用客户 | 价格区间 |
|------|---------|---------|
| **AOI-as-a-Service** | 中小工厂、外贸厂 | 499–2999 元/工位/月 |
| **AOI Edge Box** | 中型工厂、海外仓 | 18,000–48,000 元/台 + 服务费 |
| **AOI Enterprise** | 大型代工厂、品牌方 | 项目制定价 |

---

## License

Proprietary © 2026 鑫晨科技有限公司. All rights reserved.

