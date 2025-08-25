# 基于LLM的A2A智慧城市管理分析平台

基于Vue 3 + TypeScript构建的现代化城市管理平台，集成SuperMap GIS功能和LLM智能助手，提供地图展示、空间分析、智能问答等功能。采用模块化架构设计，支持双模式操作（传统模式/LLM模式），具备完整的主题系统和响应式布局。

## 🏗️ 项目架构

### 核心技术栈
- **前端框架**: Vue 3 + Composition API + TypeScript
- **状态管理**: Pinia stores (响应式状态管理)
- **路由管理**: Vue Router 4 (嵌套路由 + 路由守卫)
- **样式方案**: CSS自定义属性 + 明暗主题自动切换
- **UI组件**: Ant Design Vue + 自定义组件库
- **地图引擎**: OpenLayers + SuperMap iServer集成
- **布局组件**: Splitpanes可拖拽分割面板
- **构建工具**: Vite (快速构建和热重载)
- **网络通信**: 统一API客户端 + 错误处理机制
- **配置管理**: 环境变量 + 动态配置加载

### 架构特点
- 🎯 **双模式设计**: 传统GIS操作模式 + LLM智能助手模式
- 🛣️ **路由化架构**: 基于Vue Router的嵌套路由管理
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

```text
src/
├── main.js                    # 应用入口文件
├── App.vue                    # 根组件
├── vite-env.d.ts             # Vite环境类型声明
├── views/                     # 页面视图层
│   ├── Dashboard.vue         # 主仪表板页面
│   ├── auth/
│   │   ├── Login.vue         # 登录页面
│   │   └── Register.vue      # 注册页面
│   ├── dashboard/
│   │   ├── LLM/LLMMode.vue   # LLM 模式
│   │   └── traditional/      # 传统模式
│   │       ├── TraditionalMode.vue
│   │       └── tools/        # 二级工具路由组件
│   │           ├── LayerManager.vue
│   │           ├── FeatureQueryPanel.vue
│   │           ├── EditTools.vue
│   │           ├── BufferAnalysisPanel.vue
│   │           ├── DistanceAnalysisPanel.vue
│   │           └── AccessibilityAnalysisPanel.vue
│   ├── management/AIManagement.vue
│   └── profile/UserProfile.vue
├── router/                    # 路由管理层
│   └── index.ts              # 路由配置
├── components/                # 组件层
│   ├── Layout/
│   │   ├── DashboardLayout.vue
│   │   ├── DashboardHeader.vue
│   │   └── RightPanel.vue
│   ├── Map/
│   │   ├── SuperMapViewer.vue
│   │   ├── FeaturePopup.vue
│   │   ├── ZoomControls.vue
│   │   ├── ScaleBar.vue
│   │   └── CoordinateDisplay.vue
│   └── UI/
│       ├── NotificationManager.vue
│       ├── NotificationToast.vue
│       ├── ButtonGroup.vue
│       ├── IconButton.vue
│       ├── SplitPanel.vue
│       ├── PrimaryButton.vue
│       ├── SecondaryButton.vue
│       ├── TipWindow.vue
│       ├── PanelWindow.vue
│       ├── LLMInputGroup.vue
│       ├── DropdownSelect.vue
│       ├── TraditionalInputGroup.vue
│       └── PanelContainer.vue
├── stores/                    # 状态管理层
│   ├── analysisStore.ts
│   ├── featureQueryStore.ts
│   ├── interactionStore.ts
│   ├── loadingStore.ts
│   ├── mapStore.ts
│   ├── modeStateStore.ts
│   ├── popupStore.ts
│   ├── selectionStore.ts
│   ├── themeStore.ts
│   └── userStore.ts
├── composables/               # 业务逻辑组合函数
│   ├── useMap.ts
│   ├── useLayerManager.ts
│   ├── useFeatureQuery.ts
│   ├── useBufferAnalysis.ts
│   ├── useDistanceAnalysis.ts
│   └── useAccessibilityAnalysis.ts
├── api/                       # API接口层
│   ├── supermap.ts
│   ├── analysis.ts
│   └── config.ts
├── types/                     # TypeScript类型定义
│   ├── map.ts
│   ├── query.ts
│   ├── splitpanes.d.ts
│   └── supermap.d.ts
├── utils/                     # 工具函数
│   ├── config.ts
│   └── notification.ts
└── styles/                    # 全局样式
    └── theme.css
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
- **路由结构**:
  - `/dashboard/llm` - LLM模式（AI助手）
  - `/dashboard/traditional` - 传统模式（功能按钮）

### 4. **组件层 (Components Layer)**
- **Layout组件组**: 布局相关组件，负责整体页面结构
  - **DashboardLayout.vue**: 主布局容器，包含标题栏、地图区域、右侧面板
  - **DashboardHeader.vue**: 顶部导航栏，包含模式切换、主题切换、用户管理
  - **RightPanel.vue**: 右侧面板容器，使用router-view渲染模式组件
- **Modes组件组**: 模式相关组件，负责不同操作模式的内容
  - **LLMMode.vue**: LLM模式内容，集成ChatAssistant组件
  - **TraditionalMode.vue**: 传统模式内容，包含功能按钮和工具面板
- **Map组件组**: 地图功能组件，负责地图交互和分析功能
- **UI组件组**: 可复用UI组件库，提供统一的界面元素

### 5. **状态管理层 (Stores Layer)**
- **mapStore.ts**: 地图实例、图层、交互状态
- **themeStore.ts**: 主题切换、系统主题检测、主题持久化
- **loadingStore.ts**: 多任务加载状态与进度
- **analysisStore.ts**: 空间分析参数与结果
- **userStore.ts**: 用户信息、登录态、权限
- **featureQueryStore.ts**: 要素查询条件、结果、分页
- **selectionStore.ts**: 地图选中要素、集与高亮
- **interactionStore.ts**: 绘制/修改/选择等交互模式
- **modeStateStore.ts**: 模式/工具的当前选择与持久化
- **popupStore.ts**: 要素弹窗内容与显隐

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
- **路由管理**: 基于Vue Router的嵌套路由，支持URL直接访问

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
- **路由管理**: Vue Router 4的嵌套路由和路由守卫
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

### 路由化架构
```typescript
// 路由配置 - 嵌套路由结构
{
  path: '/dashboard',
  component: Dashboard,
  children: [
    { path: '', redirect: '/dashboard/llm' },
    { path: 'llm', component: LLMMode },
    { path: 'traditional', component: TraditionalMode }
  ]
}

// 模式切换 - 路由导航
const setMode = (modeId: 'traditional' | 'llm') => {
  router.push(`/dashboard/${modeId}`);
};

// 模式状态 - 基于路由计算
const activeMode = computed(() => {
  const currentRoute = router.currentRoute.value
  return currentRoute.path.includes('/traditional') ? 'traditional' : 'llm'
})
```

### 组件组织架构
```
components/
├── Layout/              # 布局组件
│   ├── DashboardLayout.vue    # 主布局容器
│   ├── DashboardHeader.vue    # 顶部导航栏
│   └── RightPanel.vue         # 右侧面板容器
├── Modes/               # 模式组件
│   ├── LLMMode.vue      # LLM模式内容
│   └── TraditionalMode.vue # 传统模式内容
├── Map/                 # 地图组件
└── UI/                  # UI组件
```

### 双模式架构
```typescript
// 模式管理 - 路由驱动
const activeMode = computed(() => {
  // 根据当前路由判断模式
  const currentRoute = router.currentRoute.value
  if (currentRoute.path.includes('/traditional')) {
    return 'traditional'
  }
  return 'llm'
})

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
:root[data-theme="light"] {
  --bg: #ffffff;
  --text: #333333;
  --accent: #007bff;
}

:root[data-theme="dark"] {
  --bg: #1a1a1a;
  --text: #ffffff;
  --accent: #4dabf7;
}
```

### 状态管理
```typescript
// Pinia Store - 响应式状态管理
export const useMapStore = defineStore('map', () => {
  const map = ref<any>(null)
  const vectorLayers = ref<MapLayer[]>([])
  
  const isMapReady = computed(() => !!map.value)
  
  return { map, vectorLayers, isMapReady }
})
```

### 组合函数 (Composables)
```typescript
// Vue 3 Composables - 业务逻辑封装
export function useMap() {
  const mapStore = useMapStore()
  
  const initMap = async () => {
    // 地图初始化逻辑
  }
  
  const loadVectorLayers = async () => {
    // 图层加载逻辑
  }
  
  return { initMap, loadVectorLayers }
}
```

## 🛣️ 路由配置

### 路由列表
| 路由路径 | 路由名称 | 组件 | 认证要求 | 标题 | 说明 |
|----------|----------|------|----------|------|------|
| `/` | - | - | - | - | 根路径重定向到 `/login` |
| `/login` | `login` | `views/auth/Login.vue` | ❌ 不需要 | 系统登录 | 登录页面 |
| `/register` | `register` | `views/auth/Register.vue` | ❌ 不需要 | 用户注册 | 注册页面 |
| `/dashboard` | `dashboard` | `views/Dashboard.vue` | ✅ 需要 | 地图系统 | 主应用页面 |
| `/dashboard/llm` | `llm-mode` | `views/dashboard/LLM/LLMMode.vue` | ✅ 需要 | AI助手 | LLM模式 |
| `/dashboard/traditional` | `traditional-mode` | `views/dashboard/traditional/TraditionalMode.vue` | ✅ 需要 | 传统模式 | 传统模式主页 |
| `/dashboard/traditional/layer` | `layer-management` | `.../tools/LayerManager.vue` | ✅ | 图层管理 | 二级工具 |
| `/dashboard/traditional/query` | `feature-query` | `.../tools/FeatureQueryPanel.vue` | ✅ | 要素查询 | 二级工具 |
| `/dashboard/traditional/edit` | `edit-tools` | `.../tools/EditTools.vue` | ✅ | 图层编辑 | 二级工具 |
| `/dashboard/traditional/buffer` | `buffer-analysis` | `.../tools/BufferAnalysisPanel.vue` | ✅ | 缓冲区分析 | 二级工具 |
| `/dashboard/traditional/distance` | `distance-analysis` | `.../tools/DistanceAnalysisPanel.vue` | ✅ | 距离分析 | 二级工具 |
| `/dashboard/traditional/accessibility` | `accessibility-analysis` | `.../tools/AccessibilityAnalysisPanel.vue` | ✅ | 可达性分析 | 二级工具 |

### 路由守卫
```typescript
// 全局前置守卫
router.beforeEach((to, from, next) => {
  const isLoggedIn = localStorage.getItem('authToken')
  
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')  // 未登录重定向到登录页
  } else if ((to.path === '/login' || to.path === '/register') && isLoggedIn) {
    next('/dashboard')  // 已登录用户重定向到仪表板
  } else {
    next()  // 正常跳转
  }
})
```

### 模式与工具的默认还原
- 访问 `/dashboard` 时，默认根据 `localStorage.currentMode` 重定向到 `/dashboard/llm` 或 `/dashboard/traditional`
- 访问 `/dashboard/traditional` 时，若存在 `localStorage.traditionalModeState.activeTool`，将重定向到对应二级工具路由

## 🎨 主题系统

### 支持的主题
- **浅色主题**: 明亮界面，适合白天使用
- **深色主题**: 暗色界面，适合夜间使用
- **系统主题**: 自动跟随系统主题偏好

### 主题切换
- 顶部导航栏主题切换按钮
- 自动检测系统主题偏好
- 主题设置持久化存储

### CSS变量系统
```css
/* 主题变量定义 */
:root {
  --bg: #ffffff;
  --text: #333333;
  --accent: #007bff;
  --border: #e0e0e0;
  --panel: #f8f9fa;
  --radius: 8px;
  --glow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
```

## 🔒 权限控制

### 认证机制
- 基于localStorage的token认证
- 路由级别的权限控制
- 自动重定向和状态保持

### 权限级别
- **公开访问**: 登录页、注册页
- **认证访问**: 主应用页面、所有功能模块

## 📱 响应式设计

### 布局适配
- 桌面端: 70%地图 + 30%面板的拖拽分割布局
- 移动端: 垂直堆叠布局，自适应屏幕尺寸
- 平板端: 混合布局，支持横竖屏切换

### 交互优化
- 触摸友好的操作界面
- 手势支持（缩放、平移）
- 自适应字体大小

## 🚀 性能优化

### 加载优化
- 路由懒加载
- 组件按需加载
- 图片懒加载和压缩

### 渲染优化
- Vue 3响应式系统
- 虚拟滚动
- 防抖和节流

### 缓存策略
- 浏览器缓存
- 状态持久化
- API响应缓存

## 🧪 开发调试

### 开发工具
- Vue DevTools支持
- TypeScript类型检查
- ESLint代码规范

### 调试功能
- 控制台日志
- 错误边界处理
- 性能监控

### 脚本与测试
- `npm run dev` 启动开发服务器 (Vite)
- `npm run build` 构建生产包
- `npm run preview` 预览生产包
- `npm run test:routing` 路由配置与重定向检查（见 `scripts/test-routing.js`）
- `npm run test:build` 构建连通性测试
- `npm run test:all` 综合测试（路由 + 构建）

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发流程
1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件
- 项目讨论区

---

**基于LLM的A2A智慧城市管理分析平台** - 让城市管理更智能、更高效！ 🚀

---

## 🛠️ 待办 / 已知问题

### 需更新：状态管理
- 现状：状态分散于多个 Pinia stores（如 `featureQueryStore`、`selectionStore`、`interactionStore`、`modeStateStore` 等），与路由状态（模式、工具）存在部分重复与耦合。
- 目标：
  - 统一模式/工具的单一信息源（建议由路由驱动 + 轻量 store 派生）。
  - 明确 store 职责边界：查询、选择、交互分别独立，避免交叉写入。
  - 提供跨模块的只读选择器（selectors）与事件编排，降低组件间耦合。
- 建议改造方向：
  1) 建立 `uiStateStore`（仅存 UI 可序列化状态，路由为真源）。
  2) 将 `modeStateStore` 收敛为路由派生的计算状态，减少冗余持久化。
  3) 规范 `selectionStore` 与 `featureQueryStore` 的输入输出，副作用沉到 composables。
  4) 引入统一事件/命令总线以协调地图交互与面板状态（避免组件直接相互依赖）。
- 影响面：`router/index.ts`、`components/Layout/DashboardLayout.vue`、传统模式工具组件、相关 composables。