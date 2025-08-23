# 基于LLM的智能化城市管理平台

基于Vue 3 + TypeScript构建的现代化城市管理平台，集成SuperMap GIS功能和LLM智能助手，提供地图展示、空间分析、智能问答等功能。采用模块化架构设计，支持双模式操作（传统模式/LLM模式），具备完整的主题系统和响应式布局。

## 🏗️ 项目架构

### 核心技术栈
- **前端框架**: Vue 3 + Composition API + TypeScript
- **状态管理**: Pinia stores (响应式状态管理)
- **样式方案**: CSS自定义属性 + 明暗主题自动切换
- **UI组件**: Ant Design Vue + 自定义组件库
- **地图引擎**: OpenLayers + SuperMap iServer集成
- **布局组件**: Splitpanes可拖拽分割面板
- **构建工具**: Vite (快速构建和热重载)
- **网络通信**: 统一API客户端 + 错误处理机制
- **配置管理**: 环境变量 + 动态配置加载

### 架构特点
- 🎯 **双模式设计**: 传统GIS操作模式 + LLM智能助手模式
- 🔒 **类型安全**: 完整的TypeScript类型系统
- 🌐 **环境隔离**: 开发/生产环境自动配置切换
- 🚨 **健壮通信**: 重试机制、超时处理、错误恢复
- 📊 **状态监控**: 统一的加载状态和错误反馈
- 🎨 **主题系统**: CSS变量驱动的明暗主题自动切换
- 🤖 **AI集成**: 内置LLM智能助手，支持自然语言交互
- 🏗️ **分层架构**: 清晰的分层设计，职责分离明确
- 🔧 **模块化**: 按功能领域组织的组件架构

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
cd SuperMap/Frontend

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
VITE_SUPERMAP_MAP_SERVICE=iserver/services/map-WuHan/rest
VITE_SUPERMAP_DATA_SERVICE=iserver/services/data-WuHan/rest/data
VITE_SUPERMAP_DATASET_NAME=武汉_县级@wuhan@@武汉

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
├── main.js                    # 应用入口文件
├── App.vue                    # 根组件
├── vite-env.d.ts             # Vite环境类型声明
├── views/                     # 页面视图层
│   ├── Dashboard.vue         # 主仪表板页面
│   ├── Login.vue             # 登录页面 (10KB, 433行)
│   └── Register.vue          # 注册页面 (11KB, 458行)
├── router/                    # 路由管理层
│   └── index.ts              # 路由配置 (1.8KB, 74行)
├── components/                # 组件层
│   ├── Layout/               # 布局组件
│   │   ├── DashboardLayout.vue    # 主布局容器 (2.5KB, 134行)
│   │   ├── DashboardHeader.vue    # 顶部导航栏 (9.3KB, 420行)
│   │   └── RightPanel.vue         # 右侧面板 (8.3KB, 299行)
│   ├── Map/                  # 地图功能组件
│   │   ├── SuperMapViewer.vue     # 核心地图视图 (1.2KB, 58行)
│   │   ├── LayerManager.vue       # 图层管理器 (6.6KB, 283行)
│   │   ├── EditTools.vue          # 编辑工具 (35KB, 1148行)
│   │   ├── ChatAssistant.vue      # AI聊天助手 (8.8KB, 396行)
│   │   ├── FeatureQueryPanel.vue  # 要素查询面板 (6.5KB, 258行)
│   │   ├── BufferAnalysisPanel.vue # 缓冲区分析 (4.4KB, 192行)
│   │   ├── DistanceAnalysisPanel.vue # 距离分析 (6.9KB, 291行)
│   │   ├── AccessibilityAnalysisPanel.vue # 可达性分析 (6.1KB, 261行)
│   │   ├── FeaturePopup.vue       # 要素弹窗 (4.4KB, 193行)
│   │   ├── ZoomControls.vue       # 缩放控件 (2.1KB, 106行)
│   │   ├── ScaleBar.vue          # 比例尺 (3.5KB, 161行)
│   │   └── CoordinateDisplay.vue  # 坐标显示 (445B, 24行)
│   └── UI/                   # 可复用UI组件库
│       ├── NotificationManager.vue # 通知管理器 (2.1KB, 105行)
│       ├── NotificationToast.vue   # 通知提示 (4.7KB, 215行)
│       ├── ButtonGroup.vue         # 按钮组 (997B, 59行)
│       ├── IconButton.vue          # 图标按钮 (2.2KB, 133行)
│       ├── SplitPanel.vue          # 分割面板 (4.2KB, 192行)
│       ├── PrimaryButton.vue       # 主要按钮 (1.5KB, 98行)
│       ├── SecondaryButton.vue     # 次要按钮 (2KB, 106行)
│       ├── TipWindow.vue           # 提示窗口 (2.2KB, 116行)
│       ├── PanelWindow.vue         # 面板窗口 (5.6KB, 257行)
│       ├── LLMInputGroup.vue       # LLM输入组 (2.8KB, 119行)
│       ├── DropdownSelect.vue      # 下拉选择 (5.2KB, 256行)
│       ├── TraditionalInputGroup.vue # 传统输入组 (2.5KB, 113行)
│       └── PanelContainer.vue      # 面板容器 (1KB, 60行)
├── stores/                    # 状态管理层
│   ├── mapStore.ts           # 地图状态管理 (9KB, 294行)
│   ├── themeStore.ts         # 主题状态管理 (2KB, 72行)
│   ├── loadingStore.ts       # 加载状态管理 (1.4KB, 54行)
│   ├── analysisStore.ts      # 分析工具状态 (1.6KB, 71行)
│   ├── userStore.ts          # 用户状态管理 (1.3KB, 60行)
│   └── layerStore.ts         # 图层状态管理 (256B, 13行)
├── composables/               # 业务逻辑组合函数
│   ├── useMap.ts             # 地图核心逻辑 (54KB, 1291行)
│   ├── useLayerManager.ts    # 图层管理逻辑 (2.2KB, 76行)
│   ├── useFeatureQuery.ts    # 要素查询逻辑 (2.8KB, 105行)
│   ├── useBufferAnalysis.ts  # 缓冲区分析 (2.2KB, 79行)
│   ├── useDistanceAnalysis.ts # 距离分析 (4.4KB, 157行)
│   └── useAccessibilityAnalysis.ts # 可达性分析 (3.2KB, 106行)
├── api/                       # API接口层
│   ├── supermap.ts           # SuperMap服务客户端 (6.8KB, 223行)
│   ├── analysis.ts           # 分析功能API (3.1KB, 131行)
│   └── config.ts             # API配置 (1KB, 47行)
├── types/                     # TypeScript类型定义
│   ├── map.ts                # 地图相关接口 (1.5KB, 75行)
│   ├── splitpanes.d.ts       # 分割面板类型声明 (468B, 20行)
│   └── supermap.d.ts         # SuperMap类型声明 (106B, 10行)
├── utils/                     # 工具函数
│   ├── config.ts             # 配置管理工具 (7.6KB, 231行)
│   └── notification.ts       # 通知系统 (2.5KB, 108行)
└── styles/                    # 全局样式
    └── theme.css             # 主题样式定义 (5.7KB, 249行)
```

## 🏗️ 分层架构设计

### 1. **应用入口层 (Entry Layer)**
- **main.js**: 应用启动入口，集成Pinia、Router、全局样式
- **App.vue**: 根组件，全局主题初始化、通知事件监听
- **vite-env.d.ts**: Vite环境类型声明

### 2. **页面视图层 (Views Layer)**
- **Dashboard.vue**: 主仪表板页面，集成DashboardLayout布局
- **Login.vue**: 用户登录页面，包含表单验证和状态管理
- **Register.vue**: 用户注册页面，包含表单验证和状态管理

### 3. **路由管理层 (Router Layer)**
- **index.ts**: 路由配置，包含路由守卫、权限控制、页面重定向

### 4. **组件层 (Components Layer)**
- **Layout组件组**: 布局相关组件，负责整体页面结构
- **Map组件组**: 地图功能组件，负责地图交互和分析功能
- **UI组件组**: 可复用UI组件库，提供统一的界面元素

### 5. **状态管理层 (Stores Layer)**
- **mapStore.ts**: 地图实例、图层、交互状态管理
- **themeStore.ts**: 主题切换、系统主题检测、主题持久化
- **loadingStore.ts**: 多任务加载状态、进度跟踪、全局状态
- **analysisStore.ts**: 分析工具状态、分析结果存储
- **userStore.ts**: 用户信息、登录状态、权限管理
- **layerStore.ts**: 图层状态、图层配置存储

### 6. **业务逻辑层 (Composables Layer)**
- **useMap.ts**: 地图初始化、图层管理、交互处理、空间分析
- **useLayerManager.ts**: 图层显示控制、分组管理、样式管理
- **useFeatureQuery.ts**: 属性查询、空间查询、SQL查询
- **useBufferAnalysis.ts**: 缓冲区分析逻辑、参数配置
- **useDistanceAnalysis.ts**: 距离计算、最优路径分析
- **useAccessibilityAnalysis.ts**: 可达性分析、服务范围计算

### 7. **API接口层 (API Layer)**
- **supermap.ts**: 统一SuperMap API客户端，重试机制、错误处理
- **analysis.ts**: 空间分析API，缓冲区、距离、可达性分析
- **config.ts**: API配置管理、环境变量处理

### 8. **类型定义层 (Types Layer)**
- **map.ts**: 地图相关接口定义，图层配置、坐标、要素信息
- **splitpanes.d.ts**: 分割面板组件类型声明
- **supermap.d.ts**: SuperMap SDK类型声明

### 9. **工具函数层 (Utils Layer)**
- **config.ts**: 环境配置创建、图层配置管理、URL构建工具
- **notification.ts**: 通知管理器、全局错误处理、网络错误处理

### 10. **样式层 (Styles Layer)**
- **theme.css**: CSS变量定义、明暗主题样式、组件样式变量

## 🎯 核心特性

### 双模式操作
- **LLM模式**: 智能聊天助手，支持自然语言交互
- **传统模式**: 经典GIS操作界面，功能按钮化操作
- **模式切换**: 顶部导航栏一键切换，状态保持

### 地图功能
- **响应式布局**: 70%地图视图 + 30%右侧面板的可拖拽分割布局
- **多图层管理**: 支持矢量图层(点/线/面)、栅格图层的动态加载和管理
- **图层分组**: 县级行政区、城市基本信息、基础设施等分组管理
- **交互绘制**: 点、线、面几何要素绘制工具
- **空间分析**: 缓冲区分析、距离分析(最优路径)、可达性分析
- **要素查询**: 属性查询、空间查询、SQL查询
- **地图控件**: 缩放、比例尺、坐标显示、图层切换
- **要素交互**: 点击查询、悬停高亮、弹窗显示

### 智能助手功能
- **自然语言交互**: 支持中文自然语言描述需求
- **地图操作**: 通过对话控制地图显示、图层管理
- **空间分析**: 智能分析建议和结果解释
- **上下文理解**: 保持对话上下文，支持连续对话
- **Markdown渲染**: 支持富文本格式的消息显示

### 系统架构
- **模块化设计**: 按功能领域组织的组件架构
- **类型安全**: 完整的TypeScript类型系统覆盖
- **状态管理**: 基于Pinia的响应式状态管理
- **配置管理**: 环境变量驱动的多环境配置
- **错误处理**: 统一的错误捕获、重试和用户反馈机制
- **主题系统**: CSS变量驱动的明暗主题自动切换
- **性能优化**: 分页加载、缓存策略、异步处理

### 开发体验
- **热重载**: Vite驱动的快速开发体验
- **代码规范**: TypeScript严格模式开发
- **组件复用**: 可复用的UI组件库
- **API统一**: 标准化的SuperMap服务调用接口
- **调试工具**: 完整的开发调试和错误追踪

## 🔧 技术实现

### 双模式架构
```typescript
// 模式管理 - 全局状态
const activeMode = ref<'traditional' | 'llm'>('llm')

// 模式切换事件
window.dispatchEvent(new CustomEvent('modeChanged', { detail: modeId }))

// 组件监听模式变化
window.addEventListener('modeChanged', handleModeChange)
```

### 地图服务集成
```typescript
// 统一的API客户端
const superMapClient = new SuperMapClient()

// 支持重试和错误处理的服务调用
const result = await superMapClient.getFeaturesBySQL({
  datasetName: '武汉_县级@wuhan@@武汉',
  attributeFilter: '1=1'
})
```

### 主题系统
```css
/* CSS变量驱动的主题切换 */
:root {
  --bg: #f8f9fa;
  --panel: #ffffff;
  --text: #212529;
  --accent: #007bff;
}

[data-theme="dark"] {
  --bg: #1e1e1e;
  --panel: #2d2d30;
  --text: #ffffff;
  --accent: #0078d4;
}
```

### 配置管理系统
```typescript
// 动态配置加载
const config = createAPIConfig()
const mapUrl = getFullUrl('map')  // 自动拼接完整URL

// 武汉图层配置
wuhanLayers: [
  { name: '武汉_县级@wuhan@@武汉', type: 'polygon', group: '县级行政区' },
  { name: '公路@wuhan@@武汉', type: 'line', group: '城市基本信息' },
  { name: '学校@wuhan@@武汉', type: 'point', group: '基础设施' }
]
```

### 状态管理模式
```typescript
// 响应式状态管理
const mapStore = useMapStore()
const loadingStore = useLoadingStore()

// 统一的加载状态控制
loadingStore.startLoading('operation', '正在处理...')
```

### 错误处理机制
```typescript
// 统一的错误处理
export const handleError = (error: any, context: string = '操作'): void => {
  console.error(`${context}失败:`, error)
  
  let message = '未知错误'
  if (error instanceof Error) {
    message = error.message
  }
  
  notificationManager.error(`${context}失败`, message)
}
```

## 📋 功能模块

### 已实现功能
- ✅ **双模式操作**: LLM智能助手模式 + 传统GIS操作模式
- ✅ **地图展示**: 基于OpenLayers + SuperMap的地图渲染
- ✅ **图层管理**: 动态图层加载、显示/隐藏、分组管理
- ✅ **绘制工具**: 点、线、面要素绘制和区域选择
- ✅ **空间分析**: 缓冲区分析、距离分析(最优路径)、可达性分析
- ✅ **要素查询**: 属性查询、空间查询、SQL查询
- ✅ **要素交互**: 点击查询、悬停高亮、弹窗显示
- ✅ **主题切换**: 明暗主题自动切换，支持系统主题跟随
- ✅ **响应式布局**: 可拖拽分割面板、移动端适配
- ✅ **配置管理**: 环境变量配置、多环境支持
- ✅ **错误处理**: 统一错误捕获和用户反馈
- ✅ **加载状态**: 操作进度显示和状态管理
- ✅ **AI聊天助手**: LLM集成和智能对话界面
- ✅ **性能优化**: 分页加载、缓存策略、异步处理
- ✅ **用户认证**: 登录注册功能、路由守卫
- ✅ **通知系统**: 全局通知管理、错误提示

### 武汉地图数据
- **县级行政区**: 武汉_县级 (面要素)
- **交通设施**: 公路、铁路 (线要素)
- **水系信息**: 水系线、水系面 (线/面要素)
- **建筑信息**: 建筑物面 (面要素)
- **基础设施**: 居民地地名点、学校、医院 (点要素)

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
- [OpenLayers文档](https://openlayers.org/)
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