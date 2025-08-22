# 城市仪表板 (City Dashboard)

基于Vue 3 + TypeScript构建的现代化城市仪表板应用，集成SuperMap GIS功能，提供地图展示、图层管理、空间分析等功能。采用模块化架构设计，支持环境配置管理、统一错误处理、类型安全的API通信。

## 🏗️ 项目架构

### 核心技术栈
- **前端框架**: Vue 3 + Composition API + TypeScript
- **状态管理**: Pinia stores (响应式状态管理)
- **样式方案**: CSS自定义属性 + 深色主题支持
- **UI组件**: Ant Design Vue + 自定义组件库
- **地图引擎**: SuperMap/OpenLayers集成
- **布局组件**: Splitpanes可调整面板
- **构建工具**: Vite (快速构建和热重载)
- **网络通信**: 统一API客户端 + 错误处理机制
- **配置管理**: 环境变量 + 动态配置加载

### 架构特点
- 🎯 **领域驱动设计**: 按业务功能模块化组织代码
- 🔒 **类型安全**: 完整的TypeScript类型系统
- 🌐 **环境隔离**: 开发/生产环境自动配置切换
- 🚨 **健壮通信**: 重试机制、超时处理、错误恢复
- 📊 **状态监控**: 统一的加载状态和错误反馈
- 🎨 **主题系统**: CSS变量驱动的主题切换

## 环境要求

- **Node.js**: v20.19.0+ 或 v22.12.0+
- **npm**: 建议 8.0+
- **SuperMap**: iServer GIS服务(需单独部署)

## 🚀 快速开始

### 1. 环境准备 (Windows系统)
```bash
# 1. 安装 Git for Windows
# 下载地址: https://git-scm.com/download/win

# 2. 安装 Node.js LTS版本  
# 下载地址: https://nodejs.org/

# 3. 验证安装
node --version
npm --version
git --version
```

### 2. 项目配置
```bash
# 克隆项目
git clone [项目地址]
cd city-dashboard

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置SuperMap服务地址
```

### 3. 环境变量配置
在项目根目录创建 `.env` 文件：
```env
# SuperMap服务配置
VITE_SUPERMAP_BASE_URL=http://localhost:8090
VITE_SUPERMAP_MAP_SERVICE=iserver/services/map-WuHan/rest/maps/武汉_市级
VITE_SUPERMAP_DATA_SERVICE=iserver/services/data-WuHan/rest/data
VITE_SUPERMAP_DATASET_NAME=wuhan:武汉_县级

# API配置
VITE_API_TIMEOUT=10000
VITE_API_RETRY_COUNT=3
VITE_DEV_MODE=true
```

### 4. 开发运行
```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 📁 项目结构

### 整体架构
```
src/
├── api/                    # API客户端层
│   └── supermap.ts        # SuperMap服务统一客户端
├── components/            # 按功能领域组织的组件
│   ├── Layout/           # 布局层组件
│   │   ├── DashboardLayout.vue    # 主布局容器
│   │   ├── DashboardHeader.vue    # 顶部导航栏
│   │   └── RightPanel.vue         # 右侧面板
│   ├── Map/              # 地图功能组件
│   │   ├── SuperMapViewer.vue     # 核心地图视图
│   │   ├── LayerManager.vue       # 图层管理器
│   │   ├── DrawTools.vue          # 绘制工具
│   │   ├── BufferAnalysisPanel.vue # 缓冲区分析
│   │   ├── DistanceAnalysisPanel.vue # 距离分析
│   │   ├── AccessibilityAnalysisPanel.vue # 可达性分析
│   │   ├── FeaturePopup.vue       # 要素弹窗
│   │   ├── CoordinateDisplay.vue  # 坐标显示
│   │   ├── ZoomControls.vue       # 缩放控件
│   │   ├── ScaleBar.vue          # 比例尺
│   │   ├── EditTools.vue         # 编辑工具
│   │   └── ChatAssistant.vue     # AI聊天助手
│   └── UI/               # 可复用UI组件库
│       ├── ButtonGroup.vue       # 按钮组
│       ├── PanelWindow.vue       # 面板窗口
│       ├── SplitPanel.vue        # 分割面板
│       ├── PrimaryButton.vue     # 主要按钮
│       ├── SecondaryButton.vue   # 次要按钮
│       ├── DropdownSelect.vue    # 下拉选择
│       ├── LLMInputGroup.vue     # LLM输入组
│       └── TraditionalInputGroup.vue # 传统输入组
├── composables/          # 业务逻辑组合函数
│   ├── useMap.ts         # 地图核心逻辑
│   ├── useDraw.ts        # 绘制工具逻辑
│   ├── useLayerManager.ts # 图层管理逻辑
│   ├── useBufferAnalysis.ts # 缓冲区分析
│   ├── useDistanceAnalysis.ts # 距离分析
│   └── useAccessibilityAnalysis.ts # 可达性分析
├── stores/               # Pinia状态管理
│   ├── mapStore.ts       # 地图状态管理
│   ├── layerStore.ts     # 图层状态管理
│   ├── analysisStore.ts  # 分析工具状态
│   ├── themeStore.ts     # 主题状态管理
│   └── loadingStore.ts   # 加载状态管理
├── types/                # TypeScript类型定义
│   ├── map.ts            # 地图相关接口
│   ├── supermap.d.ts     # SuperMap类型声明
│   └── splitpanes.d.ts   # 分割面板类型
├── utils/                # 工具函数
│   ├── config.ts         # 配置管理工具
│   └── notification.ts   # 通知系统
├── styles/               # 全局样式
│   └── theme.css         # 主题样式定义
├── App.vue               # 根组件
└── main.js               # 应用入口
```

## 🎯 核心特性

### 地图功能
- **响应式布局**: 75%地图视图 + 25%右侧面板的分割布局
- **多图层管理**: 支持矢量图层、栅格图层的动态加载和管理
- **交互绘制**: 点、线、面几何要素绘制工具
- **空间分析**: 缓冲区分析、距离分析、可达性分析
- **要素查询**: 属性查询、空间查询、SQL查询
- **地图控件**: 缩放、比例尺、坐标显示、图层切换
- **AI助手**: 集成LLM的智能地图分析助手

### 系统架构
- **模块化设计**: 按功能领域组织的组件架构
- **类型安全**: 完整的TypeScript类型系统覆盖
- **状态管理**: 基于Pinia的响应式状态管理
- **配置管理**: 环境变量驱动的多环境配置
- **错误处理**: 统一的错误捕获、重试和用户反馈机制
- **主题系统**: CSS变量驱动的深色/浅色主题切换
- **性能优化**: 分页加载、缓存策略、异步处理

### 开发体验
- **热重载**: Vite驱动的快速开发体验
- **代码规范**: ESLint + Prettier统一代码风格
- **组件复用**: 可复用的UI组件库
- **API统一**: 标准化的SuperMap服务调用接口
- **调试工具**: 完整的开发调试和错误追踪

## 🔧 技术实现

### 网络通信架构
```typescript
// 统一的API客户端
const superMapClient = new SuperMapClient()

// 支持重试和错误处理的服务调用
const result = await superMapClient.getFeaturesBySQL({
  datasetName: 'wuhan:武汉_县级',
  attributeFilter: '1=1'
})
```

### 基于 features.json 的分页驱动读取（推荐）
为确保与服务器分页保持一致，先预读 `features.json` 获取分页元数据，再把 `fromIndex`/`toIndex` 注入到要素查询参数中：

```typescript
// 以 wuhan:武汉_县级 为例
const base = 'http://localhost:8090/iserver/services/data-WuHan/rest/data'
const datasource = 'wuhan'
const dataset = '武汉_县级'

// 1) 预读分页元数据（GET features.json）
const metaUrl = `${base}/datasources/${datasource}/datasets/${dataset}/features.json`
const meta = await (await fetch(metaUrl)).json()

// 2) 按 JSON 中字段严格取值
const startIndex: number = typeof meta.startIndex === 'number' ? meta.startIndex : 0
const featureCount: number = typeof meta.featureCount === 'number' ? meta.featureCount : 20
const fromIndex = startIndex
const toIndex = startIndex + featureCount - 1

// 3) 应用于范围查询（Bounds）
const boundsParams = new ol.supermap.GetFeaturesByBoundsParameters({
  datasetNames: [`${datasource}:${dataset}`],
  bounds: ol.extent.boundingExtent([[113.7, 29.97], [115.08, 31.36]]),
  returnContent: true,
  returnFeaturesOnly: true,
  maxFeatures: -1,
  fromIndex,
  toIndex
})
new ol.supermap.FeatureService(base).getFeaturesByBounds(boundsParams, (res: any) => {
  // 处理要素
})

// 4) 应用于几何查询（Geometry）
const geometryParams = new ol.supermap.GetFeaturesByGeometryParameters({
  datasetNames: [`${datasource}:${dataset}`],
  geometry: new ol.geom.Point([114.3, 30.6]).buffer(0.001),
  spatialQueryMode: ol.supermap.SpatialQueryMode.INTERSECT,
  returnContent: true,
  returnFeaturesOnly: true,
  attributeFilter: '',
  fields: ['*'],
  fromIndex,
  toIndex
})
new ol.supermap.FeatureService(base).getFeaturesByGeometry(geometryParams, (res: any) => {
  // 处理要素
})
```

说明：
- 严格使用 `features.json` 中的 `startIndex`（起始索引）与 `featureCount`（要素数量）计算分页范围：`fromIndex = startIndex`，`toIndex = startIndex + featureCount - 1`。
- 如需核对服务返回数据，可在请求回调中打印 `res.result.startIndex` 与 `res.result.featureCount`。
- 当前项目在 `useMap.ts` 已实现上述流程，并在控制台打印完整的“服务器地址”“请求参数”“分页参数”与“完整API响应JSON”。

### 配置管理系统
```typescript
// 动态配置加载
const config = createAPIConfig()
const mapUrl = getFullUrl('map')  // 自动拼接完整URL
```

### 状态管理模式
```typescript
// 响应式状态管理
const mapStore = useMapStore()
const loadingStore = useLoadingStore()

// 统一的加载状态控制
loadingStore.startLoading('operation', '正在处理...')
```

## 🛠️ 开发指南

### 推荐开发环境
- **IDE**: [VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (禁用Vetur)
- **Node.js**: 使用 LTS 版本
- **包管理器**: npm (推荐) 或 yarn

### 开发规范
- 遵循Vue 3 Composition API最佳实践
- 使用 `<script setup>` 语法糖
- TypeScript严格模式开发
- 按功能领域组织代码结构
- 统一的错误处理和状态管理模式

### 外部依赖集成
- **SuperMap SDK**: 通过外部脚本加载，需确保 `window.ol` 和 `window.ol.supermap` 可用
- **运行时加载**: GIS依赖不打包进bundle，减小包体积
- **健康检查**: 内置服务可用性检测

## 📋 功能模块

### 已实现功能
- ✅ **地图展示**: 基于SuperMap/OpenLayers的地图渲染
- ✅ **图层管理**: 动态图层加载、显示/隐藏、删除
- ✅ **绘制工具**: 点、线、面要素绘制
- ✅ **空间分析**: 缓冲区分析、距离分析、可达性分析
- ✅ **要素交互**: 点击查询、悬停高亮、弹窗显示
- ✅ **主题切换**: 深色/浅色主题支持
- ✅ **响应式布局**: 分割面板、移动端适配
- ✅ **配置管理**: 环境变量配置、多环境支持
- ✅ **错误处理**: 统一错误捕获和用户反馈
- ✅ **加载状态**: 操作进度显示和状态管理
- ✅ **AI聊天助手**: LLM集成和智能对话界面
- ✅ **性能优化**: 分页加载、缓存策略、异步处理

### 开发中功能
- 🚧 **图层编辑**: 要素编辑和属性修改
- 🚧 **数据导入**: 文件上传和数据格式支持
- 🚧 **高级分析**: 网络分析、3D可视化

### 计划功能
- 📋 **用户权限**: 登录认证和权限控制
- 📋 **数据可视化**: 图表集成和数据展示
- 📋 **地图服务**: 更多地图底图和服务支持
- 📋 **移动端优化**: 触摸交互和手势支持
- 📋 **实时数据**: 实时数据流和动态更新

## 🚀 部署指南

### 开发环境部署
```bash
npm run dev  # 启动开发服务器，支持热重载
```

### 生产环境构建
```bash
npm run build  # 构建生产版本到 dist/ 目录
npm run preview  # 预览生产构建结果
```

### 环境配置
- **开发环境**: 使用 `.env` 文件配置
- **生产环境**: 使用 `.env.production` 或CI/CD传入环境变量
- **服务部署**: 需要同步部署SuperMap iServer服务
- **性能监控**: 集成错误追踪和性能监控

### 部署检查清单
- [ ] SuperMap iServer服务正常运行
- [ ] 环境变量配置正确
- [ ] 静态资源CDN配置
- [ ] 错误监控和日志收集
- [ ] 性能优化和缓存策略

## 📚 相关文档

- [Vite配置文档](https://vite.dev/config/)
- [Vue 3官方文档](https://vuejs.org/)
- [Pinia状态管理](https://pinia.vuejs.org/)
- [SuperMap iClient](https://iclient.supermap.io/)
- [API优化方案](./docs/api-optimization.md)

## 🤝 贡献指南

1. Fork 项目仓库
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建 Pull Request

## 📄 许可证

本项目采用 [MIT许可证](LICENSE)