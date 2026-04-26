# HS Code Reference (示例 / 种子数据)

> 这是为悦尚 Copilot HS Code 助手准备的示例参考。生产部署时应换上完整的中国海关税则 + 主要贸易国 (US HTS, EU TARIC) 数据。

## 第 39 章 塑料及其制品 (Plastics)

| HS6 | Description (EN) | 中文 |
|-----|-----------------|------|
| 3923.30 | Carboys, bottles, flasks of plastics | 塑料瓶、罐、烧瓶 |
| 3924.10 | Tableware and kitchenware of plastics | 塑料餐具厨具 |
| 3926.90 | Other articles of plastics | 其他塑料制品 |

## 第 73 章 钢铁制品 (Articles of Iron or Steel)

| HS6 | Description (EN) | 中文 |
|-----|-----------------|------|
| 7323.93 | Stainless steel kitchen / table articles | 不锈钢厨具/餐具 |
| 7326.90 | Other articles of iron or steel | 其他钢铁制品 |

## 第 84 章 机械器具 (Machinery)

| HS6 | Description (EN) | 中文 |
|-----|-----------------|------|
| 8471.30 | Portable automatic data processing machines (laptops) | 便携式数据处理设备（笔记本） |
| 8473.30 | Parts of computers (incl. keyboards) | 计算机零件（含键盘） |
| 8504.40 | Static converters (chargers, power adapters) | 静止式变流器（充电器、电源适配器） |
| 8523.51 | Solid-state non-volatile storage (SSD, USB drive) | 固态非易失存储设备 |

## 第 85 章 电子电气设备 (Electrical Machinery)

| HS6 | Description (EN) | 中文 |
|-----|-----------------|------|
| 8517.62 | Machines for reception/transmission of voice/data (routers) | 通信设备（路由器等） |
| 8518.30 | Headphones and earphones | 耳机 |
| 8528.72 | Reception apparatus for television (TV) | 电视接收设备 |
| 8536.69 | Plugs and sockets for voltage <= 1000V | 插头插座（≤1000V） |
| 8544.42 | Other electric conductors with connectors (USB cables) | 带连接器的电线（USB线） |

## 第 95 章 玩具 (Toys)

| HS6 | Description (EN) | 中文 |
|-----|-----------------|------|
| 9503.00 | Tricycles, scooters, dolls, and other toys | 三轮车、滑板车、玩偶等玩具 |
| 9504.50 | Video game consoles and machines | 电视游戏机 |

## 国别尾码示例

不同国家把 HS6 扩展到 8/10 位：
- **中国**：8 位（HS6 + 2 位国内子目）
- **美国 HTS**：10 位（HS6 + 4 位 HTS suffix）
- **欧盟 TARIC**：10 位（HS6 + CN 8 + TARIC 10）

例如不锈钢保温杯：
- HS6: 7323.93
- 中国: 7323.93.00
- 美国: 7323.93.00.45 (其他不锈钢厨房用具)
- 欧盟 (TARIC): 7323.93.00.20 (家用、餐桌、厨房用)

## 关税参考（示例 · 仅供参考，以现行公告为准）

| 商品 | 美国一般税率 | 美国 301 关税 | 欧盟一般税率 |
|------|-------------|--------------|-------------|
| 充电器 (8504.40) | 0% | 25% (List 3) | 0% |
| 蓝牙耳机 (8518.30) | 4.9% | 7.5% | 0% |
| 不锈钢保温杯 (7323.93) | 2% | 25% (List 4A) | 2.7% |
| USB 数据线 (8544.42) | 2.6% | 7.5% | 3.7% |
| 塑料瓶 (3923.30) | 3% | 25% | 6.5% |

## 常见易错品名

| 客户描述 | 正确归类 | 常见错误 |
|---------|---------|---------|
| "电脑键盘" | 8471.60 (输入设备) 或 8473.30 (计算机零件) | 误归 8517 通信设备 |
| "智能手表" | 8517.62 (有蜂窝功能) 或 9102.12 (纯计时) | 难点：是否有蜂窝/Wi-Fi |
| "GaN 充电器" | 8504.40 (静止变流器) | 误归 8504.31 (变压器) |
| "蓝牙音箱" | 8518.22 (有放大器扬声器) | 误归 8527 (无线电接收) |
