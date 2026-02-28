---
name: Premium UI/UX Design (Pro Edition)
description: 拒绝平庸！专注于打造具有“高级感”和“游戏品牌质感”的 JoyRent 界面，通过精密的数学间距和光影模拟，摆脱廉价的 AI 生成感。
---

# JoyRent 视觉与交互实战守则

当你为本项目编写前端代码时，必须遵守以下这些**硬核设计约束**：

## 1. 色彩与光效 (Lighting & Color)
- **禁止纯黑与纯白**：背景禁止使用 `#000`，应使用深板岩蓝（如 `#0B1120`）；文字禁止全白 `#FFF`，应使用 `#F8FAFC`（降低视觉疲劳）。
- **品牌渐变 (Brand Identity)**：JoyRent 核心按钮统一种子色：
  - `linear-gradient(135deg, #FF3D00 0%, #FF8A00 100%)` (活力红橙)
- **卡片深度 (Z-Axis)**：不要用浅灰色边框，要用微弱的外发光模拟物理层级：
  ```css
  box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(255, 255, 255, 0.05);
  ```

## 2. 动效曲线 (Motion Physics)
- **拒绝线性动画**：禁止使用 `transition: 0.3s` 这种生硬的 AI 风格，必须指定具体的贝塞尔曲线。
  - 标准反馈：`cubic-bezier(0.34, 1.56, 0.64, 1)` (带有轻微 Q 弹感的物理效果)。
- **微交互**：所有 Click 事件必须配合 `scale(0.97)` 的即时下沉反馈，模拟物理按钮压力。

## 3. 布局逻辑 (Grid System)
- **8px 黄金法则**：所有 padding/margin 必须是 8 的倍数。禁止出现 `15px`, `10px` 这种随意数值。
- **排版节奏**：
  - 标题：`font-weight: 700; letter-spacing: -0.02em;` (更有力量感)
  - 正文：`line-height: 1.6; color: rgba(255,255,255,0.7);`

## 4. 前端工程化与 API 范式 (API & Engineering Paradigm)
- **禁止硬编码 URL**：严禁在 `.vue` 或组件文件中直接使用 `uni.request` 或硬编码路径。所有接口必须按业务模块封装在 `api/*.js` 中。
- **模块化职责**：
  - `api/` 目录：仅负责定义接口路径、方法及数据解构。
  - `utils/request.js`：负责处理 BaseURL、Token 注入、统一错误拦截及 `200` 状态码校验。
- **语义化命名**：接口函数应使用 `getXxxList`, `saveXxx`, `deleteXxxById` 等动宾短语命名，确保开发者看一眼 API 定义就知道业务功能。

## 5. 业务场景特定设计 (Gaming Context)
- **卡片稀缺度表示**：
  - 普通卡：纯色背景。
  - 热门卡：边框自带流光效果 (`animation: linear-gradient-move`)。
- **库存状态**：
  - 缺货：灰度滤镜 + `opacity: 0.6;`。
