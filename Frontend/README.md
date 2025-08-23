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
├── api/                    # API客户端层
│   ├── supermap.ts        # SuperMap服务统一客户端
│   ├── analysis.ts        # 分析功能API
│   └── config.ts          # API配置
├── components/            # 按功能领域组织的组件
│   ├── Layout/           # 布局层组件
│   │   ├── DashboardLayout.vue    # 主布局容器(70%地图+30%面板)
│   │   ├── DashboardHeader.vue    # 顶部导航栏(模式切换+主题切换)
│   │   └── RightPanel.vue         # 右侧面板(传统/LLM模式)
│   ├── Map/              # 地图功能组件
│   │   ├── SuperMapViewer.vue     # 核心地图视图
│   │   ├── LayerManager.vue       # 图层管理器
│   │   ├── EditTools.vue          # 编辑工具(区域选择)
│   │   ├── BufferAnalysisPanel.vue # 缓冲区分析
│   │   ├── DistanceAnalysisPanel.vue # 距离分析(最优路径)
│   │   ├── AccessibilityAnalysisPanel.vue # 可达性分析
│   │   ├── FeatureQueryPanel.vue  # 要素查询面板
│   │   ├── FeaturePopup.vue       # 要素弹窗
│   │   ├── CoordinateDisplay.vue  # 坐标显示(左下角)
│   │   ├── ZoomControls.vue       # 缩放控件(左上角)
│   │   ├── ScaleBar.vue          # 比例尺(右下角)
│   │   └── ChatAssistant.vue     # AI聊天助手
│   └── UI/               # 可复用UI组件库
│       ├── ButtonGroup.vue       # 按钮组(模式切换)
│       ├── PanelWindow.vue       # 面板窗口
│       ├── PanelContainer.vue    # 面板容器
│       ├── PrimaryButton.vue     # 主要按钮
│       ├── SecondaryButton.vue   # 次要按钮
│       ├── DropdownSelect.vue    # 下拉选择
│       ├── LLMInputGroup.vue     # LLM输入组
│       ├── TraditionalInputGroup.vue # 传统输入组
│       ├── SplitPanel.vue        # 分割面板
│       └── TipWindow.vue         # 提示窗口
├── composables/          # 业务逻辑组合函数
│   ├── useMap.ts         # 地图核心逻辑(1394行)
│   ├── useLayerManager.ts # 图层管理逻辑
│   ├── useFeatureQuery.ts # 要素查询逻辑
│   ├── useBufferAnalysis.ts # 缓冲区分析
│   ├── useDistanceAnalysis.ts # 距离分析
│   └── useAccessibilityAnalysis.ts # 可达性分析
├── stores/               # Pinia状态管理
│   ├── mapStore.ts       # 地图状态管理(294行)
│   ├── layerStore.ts     # 图层状态管理
│   ├── analysisStore.ts  # 分析工具状态
│   ├── themeStore.ts     # 主题状态管理
│   └── loadingStore.ts   # 加载状态管理
├── types/                # TypeScript类型定义
│   ├── map.ts            # 地图相关接口
│   ├── supermap.d.ts     # SuperMap类型声明
│   └── splitpanes.d.ts   # 分割面板类型
├── utils/                # 工具函数
│   ├── config.ts         # 配置管理工具(231行)
│   └── notification.ts   # 通知系统
├── styles/               # 全局样式
│   └── theme.css         # 主题样式定义(249行)
├── App.vue               # 根组件
└── main.js               # 应用入口
```

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