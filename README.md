# JoyRent

JoyRent 是一个面向游戏租赁场景的多端项目，包含 Java 后端、管理端前端、uni-app 小程序端，以及若干 AI 能力服务（RAG / 评论分析 / 人脸识别 / Agent）。

## 项目结构

- `switch-rent-common`: 公共实体、DTO、工具类
- `switch-rent-mapper`: MyBatis-Plus Mapper 与 XML
- `switch-rent-service`: 业务服务层
- `switch-rent-controller`: Spring Boot 启动与接口层
- `rent-vue`: 管理后台（Vue3 + Vite + Element Plus）
- `switchRentApp`: uni-app 客户端
- `rent-agent`: LangGraph 工作流 Agent（独立 Python 服务）
- `rag_llm_engine` / `RAG_search` / `RAG_Intend_Bert`: RAG 与意图识别实验模块
- `comment-analysis`: 评论分析服务
- `face`: 人脸识别服务

## 技术栈

- Backend: Java 8, Spring Boot 2.7, MyBatis-Plus, MySQL, Redis
- Admin Web: Vue 3, Vite, Element Plus
- Client: uni-app (Vue2)
- AI Services: Python (RAG, NLP, Face, Agent)

## 环境要求

- JDK 8+
- Maven 3.8+
- Node.js 18+
- Python 3.10+
- MySQL 8+
- Redis 6+

## 快速启动

### 1. 启动后端

1) 创建数据库并导入表结构（参考 `db_schema.md`）

2) 按需修改配置：

- `switch-rent-controller/src/main/resources/application.yml`
- 主要包含 MySQL、Redis、Python 服务地址等

3) 启动 Spring Boot：

```bash
mvn -pl switch-rent-controller -am spring-boot:run
```

默认端口：`8080`

### 2. 启动管理端（rent-vue）

```bash
cd rent-vue
npm install
npm run dev
```

### 3. 启动 uni-app（switchRentApp）

- 使用 HBuilderX 打开 `switchRentApp` 目录
- 选择目标平台运行（如微信开发者工具）

### 4. 启动 Python 服务（按需）

不同目录是独立服务，请分别安装依赖后运行。
例如：

```bash
cd rent-agent
pip install -e .
python -m rent_agent.main
```

其他模块请参考各自目录下 `README.md` / `requirements.txt`。

## 模型与大文件说明

仓库默认不提交模型权重与缓存文件（如 `*.pt`, `*.bin`, `*.safetensors`, `*.h5`, `__pycache__` 等）。

如需运行 AI 模块，请在本地自行准备模型文件，并放入对应目录（这些目录通常已被 `.gitignore` 忽略）。

## 分支说明

当前默认分支为 `main`。

## 备注

- 本仓库为多模块聚合项目，建议按“后端 -> 前端 -> AI 服务”顺序逐步联调。
- 若接口联调失败，先检查后端数据库连接、Redis 与 Python 服务地址配置。
