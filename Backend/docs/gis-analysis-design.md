## GIS 空间分析设计方案（对齐前端 analysis-integration.md）

### 1. 目标与范围
- 实现三大空间分析：缓冲区、最优路径、可达性（等时圈/服务区）。
- 与前端 `Frontend/docs/analysis-integration.md` 的请求/响应格式严格对齐。
- 按项目 DDD + 清洁架构分层：API → 应用用例 → 领域服务 → 基础设施。
- 结果除返回给前端外，同步保存至数据库（PostgreSQL + PostGIS），面积单位 km²。

### 2. 分层与文件位置
- API 层：`app/api/v1/gis/analysis.py`
  - POST `/analysis/buffer`
  - POST `/analysis/shortest-path`
  - POST `/analysis/accessibility`
- 应用层：`app/application/use_cases/gis/analysis_use_case.py`
  - `run_buffer` / `run_shortest_path` / `run_accessibility`
  - 解析与校验 DTO、统一坐标投影、执行业务流程、调用仓储写库
- DTO：`app/application/dto/gis_dto.py`
  - `BufferRequest`、`ShortestPathRequest`、`AccessibilityRequest`
  - `GeoJSONFeature`、`GeoJSONFC`
- 领域层：`app/domains/gis/services.py`
  - `GeometryProjector`（4326 ↔ 米制、质心、面积km²）
  - `BufferService`、`RoutingService`、`IsochroneService`
- 基础设施层：
  - 外部服务集成：`app/infrastructure/external/supermap/`（可替换为 osmnx/networkx）
  - 数据访问：`app/infrastructure/database/postgres/`（models.py、repositories.py）

### 3. 前后端接口契约
- 输入坐标系：EPSG:4326；内部计算：UTM/3857；输出回投影 4326。
- 面积单位：平方千米（km²）。
- 点需求接口：非点几何统一取质心。
- 返回几何：严格遵循 `analysis-integration.md` 示例结构。

#### 3.1 缓冲区 API
- URL：POST `/analysis/buffer`
- 请求体：
  {
    "input": Feature 或 FeatureCollection,
    "distance_m": number,
    "cap_style": "round" | "flat" | "square",
    "dissolve": boolean
  }
- 处理流程：GeoJSON → 投影至米制 → buffer(distance_m, cap_style) → 可选溶解 → 面积 km² → 回投影 4326。
- 响应：FeatureCollection；每个 Feature.properties 至少包含：`area_km2`, `buffer_m`, `cap_style`, `dissolved`。

#### 3.2 最优路径 API
- URL：POST `/analysis/shortest-path`
- 请求体：
  {
    "start": Feature,
    "end": Feature,
    "profile": "walk" | "bike" | "drive",
    "weight": "time" | "distance"
  }
- 处理流程：start/end 非点取质心 → 路网最短路（OSRM/GraphHopper/SuperMap 或 osmnx+networkx）→ 回投影 4326。
- 响应：Feature(LineString)；properties：`length_km`, `duration_min`, `profile`, `weight`, `source`。

#### 3.3 可达性（等时圈）API
- URL：POST `/analysis/accessibility`
- 请求体：
  {
    "origin": Feature,
    "mode": "walk" | "bike" | "drive",
    "cutoff_min": int,
    "bands": int[] 可选
  }
- 处理流程：origin 非点取质心 → 可达子图 → 等时圈构面（外部服务或 concave-hull/alpha-shape）→ 回投影 4326。
- 响应：FeatureCollection；每个 band 的 Feature.properties：`band_min`, `area_km2`, `mode`；`summary` 含 `total_area_km2`, `bands`, `origin`, `source`。

### 4. DTO 规范
- `GeoJSONFeature`：`{"type":"Feature","geometry":{...},"properties":{...}}`
- `GeoJSONFC`：`{"type":"FeatureCollection","features":[...]}`
- `BufferRequest`：`input`, `distance_m>0`, `cap_style`, `dissolve`
- `ShortestPathRequest`：`start`, `end`, `profile`, `weight`
- `AccessibilityRequest`：`origin`, `mode`, `cutoff_min>0`, `bands?`

### 5. 领域服务职责
- GeometryProjector：
  - `to_metric(geojson)`：4326→米制；`to_wgs84(geojson)`：米制→4326
  - `centroid_point(feature)`：任意几何→点 Feature
  - `area_km2(geojson)`：几何面积换算 km²
- BufferService：
  - `buffer_geojson(input, distance_m, cap_style, dissolve)`：返回 FC，属性含 `area_km2`、参数回填
- RoutingService：
  - `shortest_path(start, end, profile, weight)`：返回 LineString Feature，属性含长度/时间/来源
- IsochroneService：
  - `isochrones(origin, mode, cutoff_min, bands)`：返回 FC，分 band 要素与 summary

### 6. 数据库持久化设计（PostgreSQL + PostGIS）
#### 6.1 表结构
- `analysis_buffer_results`
  - id, created_at, user_id?, source_tag?, input_json jsonb, result_fc_json jsonb,
  - buffer_m, cap_style, dissolved, geom MultiPolygon(4326), area_km2
- `analysis_route_results`
  - id, created_at, user_id?, source_tag?, input_json jsonb, result_feature_json jsonb,
  - profile, weight, length_km, duration_min?, geom LineString(4326)
- `analysis_accessibility_results`
  - id, created_at, user_id?, source_tag?, input_json jsonb, result_fc_json jsonb,
  - mode, cutoff_min, bands int[], total_area_km2?, geoms MultiPolygon(4326)
- 可选 `analysis_accessibility_bands`
  - id, result_id fk, band_min, area_km2, geom Polygon/MultiPolygon(4326)

#### 6.2 迁移 SQL（节选）
-- 需启用 PostGIS：CREATE EXTENSION IF NOT EXISTS postgis;
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
  geom geometry(MultiPolygon, 4326) NOT NULL,
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
  length_km DOUBLE PRECISION NOT NULL,
  duration_min DOUBLE PRECISION NULL,
  geom geometry(LineString, 4326) NOT NULL
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
  geoms geometry(MultiPolygon, 4326) NOT NULL
);

CREATE TABLE analysis_accessibility_bands (
  id BIGSERIAL PRIMARY KEY,
  result_id BIGINT NOT NULL REFERENCES analysis_accessibility_results(id) ON DELETE CASCADE,
  band_min INT NOT NULL,
  area_km2 DOUBLE PRECISION NOT NULL,
  geom geometry(MultiPolygon, 4326) NOT NULL
);

### 7. 仓储保存策略
- 写入时同时保存：
  - 结构化属性（距离、cap_style、profile、weight、bands 等）
  - 几何（geometry，SRID=4326）
  - 原始请求/完整结果体（jsonb），方便追溯与重放
- `AnalysisResultRepository` 提供：
  - `save_buffer_result(req, fc)` 返回 record_id
  - `save_route_result(req, feature)` 返回 record_id
  - `save_accessibility_result(req, fc)` 返回 record_id

### 8. 误差与性能
- 大范围缓冲与等时圈：优先分块或外部服务；必要时开启简化（Douglas-Peucker）。
- 路网计算：缓存路网子图；OSRM/GraphHopper/SuperMap 优先，osmnx 兜底。
- 投影：优先 UTM 区带；退化用 EPSG:3857；确保面积与长度在米制空间计算。

### 9. 返回体一致性
- 缓冲区：FC，Feature.properties 含 `area_km2`, `buffer_m`, `cap_style`, `dissolved`。
- 最优路径：Feature(LineString)，properties 含 `length_km`, `duration_min`, `profile`, `weight`, `source`。
- 可达性：FC，features 带 `band_min`, `area_km2`, `mode`；`summary` 含 `total_area_km2`, `bands`, `origin`, `source`。

### 10. 开发顺序建议（对应 TODO）
1) DTO 定义 → 2) 领域服务接口 → 3) 用例流程 → 4) API 端点 → 5) 数据库/模型/仓储 → 6) 依赖装配 → 7) 测试示例。


