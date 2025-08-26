# GIS 空间分析实现文档

## 概述

本系统已完整实现基于 SuperMap iServer 的三大空间分析功能：
- 缓冲区分析 (Buffer Analysis)
- 最佳路径分析 (Shortest Path Analysis)  
- 等时圈分析 (Isochrone Analysis)

## 架构设计

### 数据流架构
```
前端请求 → API → UseCase → Domain Service → SuperMap Client → SuperMap iServer
                ↓
            数据库存储 ← Repository ← 结果转换 ← SuperMap Response
```

### 核心组件

1. **几何转换器** (`geometry_converter.py`)
   - GeoJSON ↔ SuperMap 格式双向转换
   - 支持点、线、面、多点、多线、多面几何类型

2. **SuperMap 客户端** (`analysis_client.py`)
   - 统一的 HTTP 请求处理
   - 缓冲区、路径、服务区分析 API 调用

3. **领域服务** (`services.py`)
   - 集成 SuperMap 客户端
   - 异常处理和降级策略
   - 结果格式标准化

4. **数据持久化** (`repositories.py`)
   - PostGIS 几何入库
   - JSONB 原始数据存储
   - 结构化属性字段

## API 接口

### 1. 缓冲区分析
```bash
POST /api/v1/gis/analysis/buffer
Content-Type: application/json

{
  "input": {
    "type": "Feature",
    "geometry": {
      "type": "Point", 
      "coordinates": [114.37, 30.69]
    },
    "properties": {}
  },
  "distance_m": 1000,
  "cap_style": "round",
  "dissolve": true
}
```

**响应格式**：
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[...]]
      },
      "properties": {
        "area_km2": 3.14159,
        "buffer_m": 1000,
        "cap_style": "round",
        "dissolved": true,
        "source": "supermap",
        "record_id": 123
      }
    }
  ]
}
```

### 2. 最佳路径分析
```bash
POST /api/v1/gis/analysis/shortest-path
Content-Type: application/json

{
  "start": {
    "type": "Feature",
    "geometry": {
      "type": "Point",
      "coordinates": [114.37, 30.69]
    }
  },
  "end": {
    "type": "Feature", 
    "geometry": {
      "type": "Point",
      "coordinates": [114.40, 30.70]
    }
  },
  "profile": "drive",
  "weight": "time"
}
```

**响应格式**：
```json
{
  "type": "Feature",
  "geometry": {
    "type": "LineString",
    "coordinates": [[...]]
  },
  "properties": {
    "length_km": 5.2,
    "duration_min": 12.5,
    "profile": "drive",
    "weight": "time",
    "source": "supermap",
    "record_id": 124
  }
}
```

### 3. 等时圈分析
```bash
POST /api/v1/gis/analysis/accessibility
Content-Type: application/json

{
  "origin": {
    "type": "Feature",
    "geometry": {
      "type": "Point",
      "coordinates": [114.37, 30.69]
    }
  },
  "mode": "walk",
  "cutoff_min": 15,
  "bands": [5, 10, 15]
}
```

**响应格式**：
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[...]]
      },
      "properties": {
        "band_min": 5,
        "area_km2": 0.785,
        "mode": "walk"
      }
    }
  ],
  "summary": {
    "total_area_km2": 2.356,
    "bands": [5, 10, 15],
    "origin": [114.37, 30.69],
    "source": "supermap",
    "record_id": 125
  }
}
```

## 配置说明

### 环境变量
```env
# SuperMap 服务配置
SUPERMAP_ISERVER_URL=http://localhost:8090/iserver
SUPERMAP_USERNAME=admin
SUPERMAP_PASSWORD=admin
SUPERMAP_NETWORK_SERVICE=NetworkAnalyst@Changchun
SUPERMAP_SPATIAL_SERVICE=SpatialAnalyst@Changchun
```

### 数据库配置
```sql
-- 启用 PostGIS 扩展
CREATE EXTENSION IF NOT EXISTS postgis;

-- 创建分析结果表
CREATE TABLE analysis_buffer_results (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT now(),
  user_id BIGINT NULL,
  source_tag VARCHAR(16) NULL,
  input_json JSONB NOT NULL,
  result_fc_json JSONB NOT NULL,
  buffer_m DOUBLE PRECISION NOT NULL,
  cap_style VARCHAR(8) NOT NULL,
  dissolved BOOLEAN NOT NULL,
  geom geometry(MultiPolygon, 4326) NULL,
  area_km2 DOUBLE PRECISION NOT NULL
);

CREATE TABLE analysis_route_results (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT now(),
  user_id BIGINT NULL,
  source_tag VARCHAR(16) NULL,
  input_json JSONB NOT NULL,
  result_feature_json JSONB NOT NULL,
  profile VARCHAR(16) NOT NULL,
  weight VARCHAR(16) NOT NULL,
  length_km DOUBLE PRECISION NULL,
  duration_min DOUBLE PRECISION NULL,
  geom geometry(LineString, 4326) NULL
);

CREATE TABLE analysis_accessibility_results (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT now(),
  user_id BIGINT NULL,
  source_tag VARCHAR(16) NULL,
  input_json JSONB NOT NULL,
  result_fc_json JSONB NOT NULL,
  mode VARCHAR(16) NOT NULL,
  cutoff_min INT NOT NULL,
  bands INT[] NULL,
  total_area_km2 DOUBLE PRECISION NULL,
  geoms geometry(MultiPolygon, 4326) NULL
);
```

## 部署步骤

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置 SuperMap iServer
- 部署 SuperMap iServer 服务
- 发布网络分析服务 (NetworkAnalyst)
- 发布空间分析服务 (SpatialAnalyst)
- 配置路网数据集

### 3. 启动服务
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 验证部署
```bash
# 健康检查
curl http://localhost:8000/health

# API 文档
open http://localhost:8000/docs
```

## 异常处理

### 降级策略
- SuperMap 服务不可用时，返回占位结果
- 几何转换失败时，跳过 PostGIS 入库
- 网络超时时，返回错误信息

### 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": "ANALYSIS_SERVICE_ERROR",
    "message": "SuperMap 服务调用失败: Connection timeout"
  }
}
```

## 性能优化

### 缓存策略
- 路网数据缓存
- 分析结果缓存
- 几何转换缓存

### 并发处理
- 异步 API 调用
- 数据库连接池
- 请求超时控制

## 监控指标

### 关键指标
- API 响应时间
- SuperMap 服务可用性
- 数据库写入成功率
- 几何转换成功率

### 日志记录
- 分析请求日志
- 服务调用日志
- 错误异常日志

## 扩展功能

### 支持的分析类型
- 叠加分析 (Overlay Analysis)
- 泰森多边形 (Voronoi Diagram)
- 核密度分析 (Kernel Density)
- 插值分析 (Interpolation)

### 数据源扩展
- 支持多种数据源
- 动态数据加载
- 实时数据更新

## 测试用例

### 单元测试
```bash
pytest app/tests/unit/test_gis_services.py
```

### 集成测试
```bash
pytest app/tests/integration/test_analysis_api.py
```

### 性能测试
```bash
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

## 常见问题

### Q: SuperMap 服务连接失败
A: 检查 iServer 服务状态、网络连接、认证信息

### Q: 几何转换错误
A: 检查输入 GeoJSON 格式、坐标系设置

### Q: 数据库写入失败
A: 检查 PostGIS 扩展、表结构、权限设置

### Q: 分析结果为空
A: 检查路网数据、起终点位置、分析参数

## 技术支持

- 文档：`docs/gis-analysis-design.md`
- 代码：`app/domains/gis/services.py`
- 配置：`app/core/config.py`
- 测试：`app/tests/`
