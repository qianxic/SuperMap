# SuperMap GIS + AI Backend - 微服务架构系统

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue)
![Python](https://img.shields.io/badge/Python-3.11-yellow)
![DDD](https://img.shields.io/badge/DDD-Architecture-orange)
![Microservices](https://img.shields.io/badge/Microservices-3%20Services-blue)

*基于 FastAPI + DDD 的微服务架构系统 - 提供用户管理、空间分析、AI代理服务*

</div>

---

## 📋 目录

- [🏗️ 微服务架构](#-微服务架构)
- [🎯 DDD 架构详解](#-ddd-架构详解)
- [📚 API文档访问](#-api文档访问)
- [🚀 快速启动](#-快速启动)
- [⚙️ 配置](#-配置)
- [🔗 相关链接](#-相关链接)
- [👥 贡献指南](#-贡献指南)

---

## 🏗️ 微服务架构

### 服务概览

本系统采用微服务架构，包含三个核心服务：

| 服务名称 | 端口 | 主要功能 | 状态 |
|---------|------|----------|------|
| **user** | 8000 | 用户认证、授权、用户信息管理 | ✅ 已完成 |
| **analysis** | 8001 | 空间分析、地理数据处理 | 🚧 开发中 |
| **llmagent** | 8002 | AI代理、大语言模型集成 | 🚧 开发中 |

### 服务详细说明

#### 1. User Service (用户服务) - 端口 8000
- **职责**: 用户认证、授权、用户信息管理
- **核心功能**:
  - 用户注册/登录/登出
  - JWT Token 管理
  - 用户资料管理
  - 权限控制
- **技术栈**: FastAPI + PostgreSQL + Redis
- **状态**: ✅ 生产就绪

#### 2. Analysis Service (分析服务) - 端口 8001
- **职责**: 空间分析、地理数据处理
- **核心功能**:
  - 空间数据读取与处理
  - 地理空间分析算法
  - 地图数据转换
  - 空间统计计算
- **技术栈**: FastAPI + GDAL + PostgreSQL + PostGIS
- **状态**: 🚧 开发中

#### 3. LLM Agent Service (AI代理服务) - 端口 8002
- **职责**: AI代理、大语言模型集成
- **核心功能**:
  - 自然语言处理
  - 智能问答系统
  - 地理信息智能分析
  - 多模态数据处理
- **技术栈**: FastAPI + OpenAI/Claude + Vector DB
- **状态**: 🚧 开发中

### 服务间通信

- **同步通信**: HTTP REST API
- **异步通信**: Redis Pub/Sub (计划中)
- **服务发现**: 基于端口号直接访问
- **负载均衡**: Nginx (生产环境)

---

## 🎯 DDD 架构详解

### 什么是 DDD (领域驱动设计)？

DDD 是一种软件开发方法论，强调通过深入理解业务领域来指导软件设计。它帮助我们将复杂的业务逻辑组织成清晰、可维护的代码结构。

### DDD 分层架构

每个微服务都采用 DDD 分层架构，包含以下层次：

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (接口层)                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   HTTP Routes   │  │   DTOs          │  │  Middleware  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                Application Layer (应用层)                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Use Cases     │  │   DTOs          │  │  Validators  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   Domain Layer (领域层)                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Entities      │  │   Value Objects │  │  Services    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   Repositories  │  │   Domain Events │                   │
│  └─────────────────┘  └─────────────────┘                   │
├─────────────────────────────────────────────────────────────┤
│              Infrastructure Layer (基础设施层)               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Database      │  │   External APIs │  │  File System │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   Cache         │  │   Message Queue │                   │
│  └─────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

### 各层职责详解

#### 1. API Layer (接口层)
- **职责**: 对外提供 HTTP 接口，处理请求/响应
- **包含**:
  - HTTP 路由定义
  - 请求/响应 DTO
  - 中间件 (认证、日志、CORS)
  - 异常处理
- **特点**: 不包含业务逻辑，只负责协议转换

#### 2. Application Layer (应用层)
- **职责**: 编排业务用例，协调领域对象
- **包含**:
  - 用例 (Use Cases) - 具体的业务操作
  - 应用 DTO - 数据传输对象
  - 验证器 - 输入验证
  - 事务管理
- **特点**: 包含业务流程编排，但不包含核心业务规则

#### 3. Domain Layer (领域层)
- **职责**: 核心业务逻辑和规则
- **包含**:
  - **实体 (Entities)**: 有身份的业务对象
  - **值对象 (Value Objects)**: 无身份的业务概念
  - **领域服务 (Domain Services)**: 跨实体的业务逻辑
  - **仓储接口 (Repository Interfaces)**: 数据访问抽象
  - **领域事件 (Domain Events)**: 业务事件定义
- **特点**: 最核心的层，包含所有业务规则

#### 4. Infrastructure Layer (基础设施层)
- **职责**: 技术实现细节
- **包含**:
  - 数据库实现
  - 外部 API 调用
  - 文件系统操作
  - 缓存实现
  - 消息队列
- **特点**: 实现领域层定义的接口

### DDD 核心概念

#### 实体 (Entity)
- 有唯一标识的对象
- 例如: User (用户)、Order (订单)
- 通过 ID 区分不同实例

#### 值对象 (Value Object)
- 无身份的对象，通过属性值区分
- 例如: Email、Address、Money
- 不可变，可共享

#### 聚合 (Aggregate)
- 一组相关对象的集合
- 有聚合根 (Aggregate Root)
- 保证数据一致性

#### 领域服务 (Domain Service)
- 不属于特定实体的业务逻辑
- 协调多个实体或值对象
- 例如: 用户认证服务、订单计算服务

#### 仓储 (Repository)
- 数据访问的抽象
- 隐藏数据存储细节
- 提供领域对象查询接口

### 依赖方向

```
API Layer → Application Layer → Domain Layer ← Infrastructure Layer
     ↓              ↓              ↓                    ↑
  依赖注入容器 (Dependency Injection Container)
```

- **单向依赖**: 上层依赖下层，下层不依赖上层
- **依赖倒置**: 领域层定义接口，基础设施层实现
- **依赖注入**: 通过容器管理依赖关系

### 实际应用示例

以用户注册为例，展示 DDD 各层协作：

1. **API Layer**: 接收注册请求，验证 DTO
2. **Application Layer**: 调用注册用例，协调用户实体和领域服务
3. **Domain Layer**: 用户实体验证业务规则，领域服务检查唯一性
4. **Infrastructure Layer**: 仓储实现保存用户到数据库

### 架构优势

- **业务聚焦**: 代码结构反映业务概念
- **可维护性**: 清晰的层次和职责分离
- **可测试性**: 每层可独立测试
- **可扩展性**: 易于添加新功能
- **团队协作**: 不同团队可并行开发不同层

### 项目结构

```
SuperMap-Backend/
├── user/                          # 用户服务 (端口 8000)
│   ├── api/                       # API 层
│   │   └── v1/
│   │       ├── user/
│   │       │   ├── auth.py        # 认证 API
│   │       │   └── user_dto.py    # API DTO
│   │       └── __init__.py        # 路由汇总
│   ├── application/               # 应用层
│   │   ├── dto/
│   │   │   └── user_dto.py        # 应用 DTO
│   │   └── use_cases/
│   │       └── user/
│   │           └── auth_use_case.py # 认证用例
│   ├── domains/                   # 领域层
│   │   └── user/
│   │       ├── entities.py        # 用户实体
│   │       ├── repositories.py    # 仓储接口
│   │       ├── services.py        # 领域服务
│   │       └── value_objects.py   # 值对象
│   ├── infrastructure/            # 基础设施层
│   │   ├── database/
│   │   │   └── postgres/
│   │   │       ├── models.py      # SQLAlchemy 模型
│   │   │       └── repositories.py # PostgreSQL 实现
│   │   ├── cache/
│   │   │   └── redis/
│   │   │       └── cache_service.py # Redis 缓存
│   │   └── external/              # 外部服务
│   ├── core/                      # 核心横切
│   │   ├── config.py              # 配置管理
│   │   ├── database.py            # 数据库连接
│   │   ├── security.py            # 安全/JWT
│   │   └── container.py           # 依赖注入容器
│   ├── utils/                     # 工具脚本
│   │   ├── debug_server.py        # 调试工具
│   │   ├── start_server.py        # 启动脚本
│   │   ├── test_userapi.py        # API 测试
│   │   └── read_sdx_schema.py     # 数据库工具
│   └── main.py                    # 应用入口
├── analysis/                      # 分析服务 (端口 8001) - 🚧 开发中
│   ├── api/
│   ├── application/
│   ├── domains/
│   ├── infrastructure/
│   └── main.py
├── llmagent/                      # AI代理服务 (端口 8002) - 🚧 开发中
│   ├── api/
│   ├── application/
│   ├── domains/
│   ├── infrastructure/
│   └── main.py
├── shared/                        # 共享组件
│   ├── common/                    # 通用工具
│   ├── middleware/                # 中间件
│   └── utils/                     # 共享工具
├── docs/                          # 文档
│   ├── api/                       # API 文档
│   └── architecture/              # 架构文档
├── tests/                         # 测试
├── requirements.txt               # 依赖管理
└── README.md                      # 项目说明
```

---

## 📚 API文档访问

### 服务文档地址

| 服务 | Swagger UI | ReDoc | 健康检查 |
|------|------------|-------|----------|
| **User Service** | http://localhost:8000/docs | http://localhost:8000/redoc | http://localhost:8000/health |
| **Analysis Service** | http://localhost:8001/docs | http://localhost:8001/redoc | http://localhost:8001/health |
| **LLM Agent Service** | http://localhost:8002/docs | http://localhost:8002/redoc | http://localhost:8002/health |

### 📡 API 概览

#### User Service (用户服务) - 端口 8000
- `POST /api/v1/user/register` - 用户注册
- `POST /api/v1/user/login` - 用户登录
- `GET /api/v1/user/profile` - 获取用户资料
- `GET /api/v1/user/me` - 获取当前用户信息
- `GET /api/v1/user/stats` - 获取用户统计
- `POST /api/v1/user/update-profile` - 更新用户资料
- `POST /api/v1/user/change-password` - 修改密码
- `POST /api/v1/user/logout` - 用户登出

#### Analysis Service (分析服务) - 端口 8001 🚧
- `POST /api/v1/analysis/spatial-query` - 空间查询
- `POST /api/v1/analysis/buffer-analysis` - 缓冲区分析
- `POST /api/v1/analysis/intersection` - 空间相交分析
- `GET /api/v1/analysis/data-sources` - 获取数据源列表
- `POST /api/v1/analysis/upload-geodata` - 上传地理数据

#### LLM Agent Service (AI代理服务) - 端口 8002 🚧
- `POST /api/v1/llm/chat` - 智能对话
- `POST /api/v1/llm/analyze-geospatial` - 地理空间智能分析
- `POST /api/v1/llm/generate-report` - 生成分析报告
- `GET /api/v1/llm/models` - 获取可用模型列表
- `POST /api/v1/llm/vector-search` - 向量搜索

### 新功能开发流程

#### 1. 领域建模
- 在对应服务的 `domains/` 目录定义实体、值对象和领域服务
- 设计聚合边界和业务规则
- 定义仓储接口

#### 2. 用例实现
- 在 `application/use_cases/` 实现业务用例
- 定义应用层 DTO
- 实现业务流程编排

#### 3. 基础设施
- 在 `infrastructure/` 实现技术细节
- 数据库模型和仓储实现
- 外部服务集成

#### 4. API 接口
- 在 `api/` 暴露 HTTP 接口
- 定义 API DTO
- 实现中间件和异常处理

#### 5. 测试验证
- 编写单元测试
- 集成测试
- API 端到端测试

#### 6. 文档更新
- 更新 API 文档
- 更新架构文档
- 更新部署文档

### 🚀 快速启动

#### 环境准备

```bash
# 1. 激活环境
conda activate pyside6

# 2. 进入项目目录
cd Backend

# 3. 安装依赖
pip install -r requirements.txt
```

#### 启动服务

##### 启动 User Service (用户服务)
```bash
# 方式1: 直接启动
python -m uvicorn user.main:app --reload --host 0.0.0.0 --port 8000

# 方式2: 使用启动脚本
python user/utils/start_server.py
```

##### 启动 Analysis Service (分析服务) 🚧
```bash
# 开发中，待实现
python -m uvicorn analysis.main:app --reload --host 0.0.0.0 --port 8001
```

##### 启动 LLM Agent Service (AI代理服务) 🚧
```bash
# 开发中，待实现
python -m uvicorn llmagent.main:app --reload --host 0.0.0.0 --port 8002
```

#### 验证服务

```bash
# 测试用户服务
curl http://localhost:8000/health

# 测试分析服务
curl http://localhost:8001/health

# 测试AI代理服务
curl http://localhost:8002/health
```

### ⚙️ 配置

#### 环境变量配置

将必要配置写入系统环境变量或项目根目录 `.env` 文件（优先级：环境变量 > `.env` > 代码默认）：

##### 数据库配置
```bash
# PostgreSQL 配置
POSTGRES_USER=postgres
POSTGRES_PASSWORD=001117
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=supermap_gis

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

##### 安全配置
```bash
# JWT 配置
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

##### 服务配置
```bash
# 应用配置
APP_NAME=SuperMap GIS + AI Backend
ENVIRONMENT=development
DEBUG=true
API_V1_PREFIX=/api/v1

# CORS 配置
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

##### 外部服务配置
```bash
# SuperMap 配置
SUPERMAP_BASE_URL=http://localhost:8090
SUPERMAP_USERNAME=admin
SUPERMAP_PASSWORD=admin

# AI 服务配置 (LLM Agent Service)
OPENAI_API_KEY=your-openai-api-key
CLAUDE_API_KEY=your-claude-api-key
VECTOR_DB_URL=your-vector-db-url
```

#### 数据库连接

连接串格式：
```
postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}
```

#### 配置文件位置

- `user/core/config.py` - 用户服务配置
- `analysis/core/config.py` - 分析服务配置 (待创建)
- `llmagent/core/config.py` - AI代理服务配置 (待创建)

### 🔗 相关链接

#### 技术文档
- [FastAPI 文档](https://fastapi.tiangolo.com)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [Redis 文档](https://redis.io/documentation)
- [GDAL 文档](https://gdal.org/documentation/)

#### 架构参考
- [DDD (领域驱动设计)](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [微服务架构](https://microservices.io/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

#### 项目文档
- [API 文档](http://localhost:8000/docs) - User Service
- [架构设计文档](./docs/architecture/) - 详细架构说明
- [API 规范文档](./docs/api/) - API 设计规范

### 👥 贡献指南

#### 开发流程

1. **Fork 本仓库**
2. **创建特性分支** (`git checkout -b feature/AmazingFeature`)
3. **遵循 DDD 架构** 进行开发
4. **编写测试** 确保代码质量
5. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
6. **推送到分支** (`git push origin feature/AmazingFeature`)
7. **打开 Pull Request**

#### 开发规范

##### 代码规范
- 遵循 PEP 8 Python 代码规范
- 使用类型注解 (Type Hints)
- 编写详细的文档字符串
- 保持函数简洁，单一职责

##### 架构规范
- 严格遵循 DDD 分层架构
- 领域层不依赖基础设施层
- 使用依赖注入管理依赖关系
- 保持各层职责清晰

##### 测试规范
- 单元测试覆盖率 > 80%
- 编写集成测试
- API 端到端测试
- 性能测试 (关键路径)

##### 提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建过程或辅助工具的变动
```

#### 服务开发指南

##### 新增微服务
1. 在根目录创建服务目录 (如 `analysis/`)
2. 按照 DDD 架构创建分层目录
3. 实现核心业务逻辑
4. 编写 API 接口
5. 添加测试用例
6. 更新文档

##### 扩展现有服务
1. 在领域层定义新的实体/服务
2. 在应用层实现用例
3. 在基础设施层实现技术细节
4. 在 API 层暴露接口
5. 更新相关文档

## 📜 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
