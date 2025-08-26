# SuperMap GIS + AI 智能分析系统 - 后端

<div align="center">

![SuperMap](https://img.shields.io/badge/SuperMap-GIS-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![LangChain](https://img.shields.io/badge/LangChain-0.1-orange)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Python](https://img.shields.io/badge/Python-3.11-yellow)
![Progress](https://img.shields.io/badge/Progress-35%25-orange)

*基于多智能体协作的 GIS 智能分析平台后端服务*

**当前状态**: 🚧 Phase 1 开发中 | **完成度**: 35% | **总文件**: 94个

</div>

---

## 📋 目录
---

## 🏗️ 系统架构

### 分层与目录（按代码实际存在）
- 接口层 API
  - 路由与中间件：`app/api/v1/**`、`app/api/dependencies.py`、`app/api/middleware.py`
  - 启动与装配：`app/main.py`
- 应用层 Application（用例/DTO/事件处理）
  - 用例：`app/application/use_cases/**`
  - DTO：`app/application/dto/**`
  - 处理器：`app/application/handlers/**`
- 领域层 Domain（模型与抽象）
  - 实体/值对象/服务：`app/domains/*/(entities|value_objects|services).py`
  - 仓储接口：`app/domains/*/repositories.py`
- 基础设施层 Infrastructure（实现与外部适配）
  - 数据库：`app/infrastructure/database/postgres/*`、`app/infrastructure/database/redis/*`、`app/infrastructure/database/vector/*`
  - 外部客户端：`app/infrastructure/external/supermap/*`、`app/infrastructure/external/llm/*`
  - AI 组件：`app/infrastructure/ai/*`（`agent_hub.py`、`aggregator.py`、`coordinator.py`、`executor.py`、`prompts/**`、`tools/**`）
  - 监控：`app/infrastructure/monitoring/*`
- 核心横切 Core（技术基座）
  - 配置/日志/异常/安全/缓存/中间件/容器/数据库：`app/core/*`
- 工程配套
  - 迁移：`migrations/001_create_gis_tables.py`
  - 文档：`docs/**`
  - 脚本与测试：`start_server.py`、`curl_test.sh`、`read_sdx_schema.py`、`quick_test.py`、`test_userapi.py`、`TEST_GUIDE.md`
  - 依赖：`requirements.txt`

### 依赖方向（技术单向依赖）
- API → Application → Domain(抽象) → Infrastructure(实现)
- Core 为横切，被各层引用；不承载领域逻辑。

### 技术调用链（纯技术流水）
- HTTP 请求 → `app/api/v1/*`
- DTO 组装 → `app/application/dto/*`
- 用例编排 → `app/application/use_cases/*`
- 领域抽象 & 仓储接口 → `app/domains/*`
- 具体实现访问外部资源 → `app/infrastructure/**`
- 返回结果序列化 → API 层响应

### 🧱 架构现状总结（基于当前代码）
- API 层：专注 FastAPI 路由与聚合（`app/api/v1/**`、`app/main.py`）。
- Application 层：
  - DTO 定义与数据校验（`app/application/dto/**`）。
  - 用例负责编排，但存在框架/实现渗透（如 `Depends/HTTPException`、直依具体仓储、安全算法直用库）。
- Domain 层：
  - 用户领域实体与仓储接口健全（`app/domains/user/**`）。
  - GIS 领域服务存在占位（`NotImplemented`），且引用外部客户端与配置（分层上偏“实现向”）。
- Infrastructure 层：
  - Postgres 仓储实现完整（`app/infrastructure/database/postgres/repositories.py`）。
  - 几何转换、并集等“具体算法模型”与持久化逻辑实现到位（GeoJSON ↔ PostGIS）。
- Core 层：配置/安全/数据库等横切能力提供（`app/core/**`）。

### ✅ 已实现功能（以代码为准）
- 用户模块（应用层用例已实现）：
  - 注册、登录、获取资料、更新资料、修改密码、统计、登出（`app/application/use_cases/user/auth_use_case.py`、`profile_use_case.py`）。
  - 对应使用用户仓储实现进行持久化（`PostgreSQLUserRepository`）。
- GIS 分析链路（用例与入库实现）：
  - 请求 DTO 与用例编排（`Buffer/ShortestPath/Accessibility` 请求结构与用例方法）。
  - 分析结果入库与几何转换（`save_buffer_result/save_route_result/save_accessibility_result`）。
  - 说明：GIS 领域服务本身为占位（`NotImplemented`），实际分析算法未在仓库中提供实现。
- 基础设施与横切：
  - PostgreSQL/SQLAlchemy 异步会话、GeoAlchemy2/Shapely 转换、配置与安全基础设施。
- 健康检查：根级 `/health` 探活（`app/main.py`）。

### 🚀 快速启动

```bash
# 1. 激活环境
conda activate pyside6

# 2. 进入Backend目录
cd Backend

# 3. 启动服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 📚 API文档访问
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health




### 新功能开发流程

1. **领域建模**: 在 `app/domains/` 定义实体和服务
2. **用例实现**: 在 `app/application/use_cases/` 实现业务逻辑  
3. **基础设施**: 在 `app/infrastructure/` 实现技术细节
4. **API 接口**: 在 `app/api/` 暴露 HTTP 接口
5. **测试用例**: 编写单元和集成测试
6. **文档更新**: 更新 API 文档和部署文档

## 🔗 相关链接

- [API 文档](http://localhost:8000/docs)
- [SuperMap 官网](https://www.supermap.com)
- [LangChain 文档](https://python.langchain.com)
- [FastAPI 文档](https://fastapi.tiangolo.com)
- [PostGIS 文档](https://postgis.net)

## 👥 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)  
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📜 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如有问题或建议，请：

- 创建 [Issue](../../issues)
- 发送邮件至: [your-email@example.com](mailto:your-email@example.com)
- 加入我们的 [Discord](https://discord.gg/your-invite) 社区

---

<div align="center">
Made with ❤️ by SuperMap GIS Team
</div>