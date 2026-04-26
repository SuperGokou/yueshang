# 新增品类 Profile 指南

YueshangAOI 的核心理念：**新增品类 = 写一份 YAML，不动一行 Python 代码**。

## 步骤

### 1. 创建 profile 文件

在 `configs/profiles/` 下新建 `<your_product>.yaml`，例如 `lipstick.yaml`：

```yaml
name: lipstick
display_name_zh: 口红外壳
display_name_en: Lipstick Tube

defect_categories:
  - { id: 1, code: scratch,  label_zh: 划痕,  label_en: Scratch,  severity: major,    group: surface,    color: "#FF6600" }
  - { id: 2, code: dent,     label_zh: 凹痕,  label_en: Dent,     severity: critical, group: structural, color: "#CC0000" }
  - { id: 3, code: paint,    label_zh: 喷漆瑕疵, label_en: Paint Defect, severity: major, group: surface, color: "#FF9900" }

localizer:
  strategy: opencv_perspective    # 或 threshold / yolo_box / none

roi_detector:
  strategy: grid                  # 或 yolo_box / template_match
  params: { rows: 1, cols: 1 }

routes:
  - name: opencv_anomaly
    enabled: true
  - name: highpass_edge
    enabled: true
    params: { edge_density_threshold: 0.08 }

fusion:
  strategy: any_positive          # 或 majority / weighted
```

### 2. （可选）训练定制模型

如果默认 OpenCV 路由召回不够，可以训练 CNN 路由：

```bash
# 准备数据：data/lipstick/cls_dataset/{ok, scratch, dent, paint}/*.jpg
yolo classify train data=data/lipstick/cls_dataset model=yolov8n-cls.pt epochs=100 imgsz=224
# 训练完拿 best.pt 路径填入 profile.yaml
```

### 3. 立刻可用

```bash
yueshang-aoi inspect --profile lipstick --input ./photos --output ./out --report-lang en
```

## Profile 字段速查

| 字段 | 取值 | 说明 |
|------|------|------|
| `localizer.strategy` | `opencv_perspective` | 透视矫正，适合平面物体 |
| | `threshold` | 阈值定位，适合高对比度 |
| | `yolo_box` | YOLO 检测物体边界 |
| | `none` | 跳过定位 |
| `roi_detector.strategy` | `yolo_box` | YOLO 检测部件 |
| | `grid` | 网格切分，适合阵列产品 |
| | `template_match` | 模板匹配，适合 PCBA |
| `routes[].name` | `yolo_cls` | CNN 分类 |
| | `golden_match` | 金样对比 |
| | `opencv_anomaly` | 形态学异常检测 |
| | `highpass_edge` | 高通+边缘密度 |
| `fusion.strategy` | `any_positive` | 任一路阳性 → NG |
| | `majority` | 多数路阳性 → NG |
| | `weighted` | 置信度加权 |

## 自定义路由

需要写自己的检测算法？继承 `Route` 协议并注册：

```python
from yueshang_aoi.routes.base import Route
from yueshang_aoi.routes.registry import register_route
from yueshang_aoi.core.result import RouteVerdict

class MyCustomRoute:
    name = "my_custom"
    enabled = True

    def __init__(self, enabled=True, **params):
        self.enabled = enabled
        # ... your config

    def inspect(self, part_image, context) -> RouteVerdict:
        # ... your logic
        return RouteVerdict(self.name, is_defect=False)

register_route("my_custom", MyCustomRoute)
```

然后在 profile 里直接引用：

```yaml
routes:
  - name: my_custom
    params: { foo: bar }
```
