## 前后端一体化技术文档：要素选择与分析接口对接

### 1. 前端要素选择与数据来源
- 点击选择：`useMap.ts -> handleNormalClick`
  - 选中要素加入 `mapStore.selectLayer` 高亮，并写入 `selectionStore.selectedFeatures`
  - 标记来源：`feature.set('sourceTag','click')`
- 框选：`useFeatureSelection.ts -> selectFeaturesInExtent`
  - 选中要素写入 `areaSelectionStore.selectedFeatures`
  - 标记来源：`feature.set('sourceTag','area')`
- 属性查询：`featureQueryStore.executeQuery`
  - 结果写入 `featureQueryStore.queryResults`
  - 标记来源：`feature.set('sourceTag','query')`

说明：三个来源的要素均可作为分析输入。地图上渲染仅依赖 `mapStore.selectLayer`，分析数据应从各自 store 收集。

### 2. 前端提取当前选中数据（发送后端）
推荐直接将 OpenLayers Feature 转为 GeoJSON Feature/FeatureCollection 随请求发送。

```javascript
import { useSelectionStore } from '@/stores/selectionStore'
import { useAreaSelectionStore } from '@/stores/areaSelectionStore'
import { useFeatureQueryStore } from '@/stores/featureQueryStore'

const selectionStore = useSelectionStore()
const areaStore = useAreaSelectionStore()
const queryStore = useFeatureQueryStore()
const writer = new window.ol.format.GeoJSON()

function toGeoJSONFeature(f) {
  return writer.writeFeatureObject(f)
}

export function collectSelectedAsFeatureOrFC() {
  const all = [
    ...selectionStore.selectedFeatures,
    ...areaStore.selectedFeatures,
    ...queryStore.queryResults
  ]
  const features = all.map(toGeoJSONFeature).filter(Boolean)
  return features.length === 1
    ? features[0]
    : { type: 'FeatureCollection', features }
}
```

用法示例（缓冲区）：
```javascript
const payload = collectSelectedAsFeatureOrFC()
await fetch('/analysis/buffer?distance_m=500&cap_style=round&dissolve=true', {
  method: 'POST', headers: {'Content-Type':'application/json'},
  body: JSON.stringify(payload)
})
```

用法示例（最优路径，取前两个要素为起终点）：
```javascript
const payload = collectSelectedAsFeatureOrFC()
const features = payload.type === 'FeatureCollection' ? payload.features : [payload]
await fetch('/analysis/shortest-path?profile=drive&weight=time', {
  method: 'POST', headers: {'Content-Type':'application/json'},
  body: JSON.stringify({ start: features[0], end: features[1] })
})
```

用法示例（可达性，取第一个要素为中心）：
```javascript
const payload = collectSelectedAsFeatureOrFC()
const feature = payload.type === 'FeatureCollection' ? payload.features[0] : payload
await fetch('/analysis/accessibility?mode=walk&cutoff_min=15', {
  method: 'POST', headers: {'Content-Type':'application/json'},
  body: JSON.stringify({ origin: feature })
})
```

可选的“后端拉取”模式：若后端需从 iServer 拉权威数据，前端额外传 layer 标识与 featureIds，后端调用 FeatureService 获取。

### 3. 后端通用规范
- 输入坐标系：EPSG:4326（WGS84）
- 内部计算：投影到米制坐标系（优先 UTM，否则 EPSG:3857），完成计算后回投影 4326 输出
- 面积单位：平方千米（项目约定）
- 返回几何：GeoJSON `Feature` 或 `FeatureCollection`
- 点需求的接口：若输入为线/面/多面，取质心作为点参与计算

通用数据模型（示意）：
```json
// Feature
{
  "type": "Feature",
  "geometry": { "type": "MultiPolygon", "coordinates": [...] },
  "properties": { ... }
}

// FeatureCollection
{
  "type": "FeatureCollection",
  "features": [ {"type":"Feature", ...}, ... ]
}
```

### 4. 缓冲区分析 API
- URL: `POST /analysis/buffer`
- 请求体（支持 Feature 或 FeatureCollection）：
```json
{
  "input": { ... },
  "distance_m": 500,
  "cap_style": "round",
  "dissolve": true
}
```
- 处理：解析 GeoJSON → 投影至米制 → buffer(distance_m, cap_style) → 可选溶解 → 回投影 4326
- 返回：
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Polygon" , "coordinates": [...] },
      "properties": {
        "area_km2": 1.234567,
        "buffer_m": 500,
        "cap_style": "round",
        "dissolved": true
      }
    }
  ]
}
```

### 5. 最优路径分析 API
- URL: `POST /analysis/shortest-path`
- 请求体：
```json
{
  "start": { ... Feature ... },
  "end": { ... Feature ... },
  "profile": "drive",
  "weight": "time"
}
```
- 处理：start/end 若非点取质心 → 路网最短路（OSRM/GraphHopper/SuperMap 或 osmnx+networkx）→ 线路回投影 4326
- 返回：
```json
{
  "type": "Feature",
  "geometry": { "type": "LineString", "coordinates": [[lon,lat], ...] },
  "properties": {
    "length_km": 12.34,
    "duration_min": 28,
    "profile": "drive",
    "weight": "time",
    "source": "osrm"
  }
}
```

### 6. 可达性分析（等时圈/服务区）API
- URL: `POST /analysis/accessibility`
- 请求体：
```json
{
  "origin": { ... Feature ... },
  "mode": "walk",
  "cutoff_min": 15,
  "bands": [5,10,15]
}
```
- 处理：origin 非点取质心 → 路网可达子图（时间/距离阈值）→ 等时圈构面（外部服务或本地 alpha-shape/栅格等值面）→ 回投影 4326
- 返回：
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Polygon", "coordinates": [...] },
      "properties": { "band_min": 5, "area_km2": 3.21, "mode": "walk" }
    },
    { "type": "Feature", "geometry": { ... }, "properties": { "band_min": 10, "area_km2": 7.89, "mode": "walk" } }
  ],
  "summary": {
    "total_area_km2": 11.10,
    "bands": [5,10],
    "origin": { "lon": 114.37, "lat": 30.69 },
    "source": "graphhopper"
  }
}
```

### 7. 错误返回规范
```json
{
  "success": false,
  "error": { "code": "INVALID_INPUT", "message": "geometry is empty" }
}
```

### 8. 关键实现要点（后端）
- 投影转换：EPSG:4326 ↔ 米制（UTM/3857），面积/缓冲/长度/时间计算在米制完成
- 点需求接口：非点几何统一取质心
- 路网来源：优先外部服务（OSRM/GraphHopper/SuperMap），或本地 osmnx+networkx（需缓存路网）
- 精度与性能：大范围分析优先分块或使用服务端索引；对等时圈生成可采用 concave hull/alpha shape 调参


