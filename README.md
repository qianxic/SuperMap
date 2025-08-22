# SuperMap 城市仪表板系统

基于 SuperMap 技术的现代化城市地理信息系统（GIS）仪表板，提供完整的空间数据管理、可视化与分析功能。

## 项目概览

这是一个全栈GIS应用系统，采用前后端分离架构，主要用于城市地理空间数据的展示、管理和分析。系统以武汉市地理数据为示例，展示了完整的城市基础信息管理和空间分析能力。

### 核心特性

- 🗺️ **交互式地图展示** - 基于 SuperMap 和 OpenLayers 的高性能地图显示
- 📊 **多维数据可视化** - 支持点、线、面等多种几何要素的样式化展示
- 🔍 **空间分析工具** - 缓冲区分析、距离分析、可达性分析等
- 🎨 **主题切换系统** - 支持明暗主题无缝切换
- 📱 **响应式设计** - 适配桌面端和移动端
- ⚡ **高性能架构** - 异步加载、错误重试、智能缓存

## 技术架构

### 整体架构图
```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐
│   前端应用       │    │    后端API       │    │  SuperMap服务   │
│  Vue 3 + TS     │◄──►│  Express + TS    │◄──►│   iServer      │
│  OpenLayers     │    │  Prisma ORM      │    │   地图/数据服务  │
│  Ant Design     │    │  PostgreSQL      │    │                │
└─────────────────┘    └──────────────────┘    └────────────────┘
```

### 前端技术栈

#### 核心框架
- **Vue 3** - 现代化组件式前端框架，使用 Composition API
- **TypeScript** - 强类型支持，提供更好的开发体验
- **Vite** - 快速构建工具，支持热更新

#### 地图与可视化
- **OpenLayers** - 开源 WebGIS 库，处理地图交互和渲染
- **SuperMap iClient** - SuperMap 官方 JavaScript 客户端库
- **PostGIS** - 空间数据库扩展，存储地理空间数据

#### UI 组件与样式
- **Ant Design Vue** - 企业级UI组件库
- **CSS Custom Properties** - 支持主题切换的CSS变量系统
- **Splitpanes** - 可调整大小的面板布局

#### 状态管理与工具
- **Pinia** - Vue 3 官方推荐的状态管理库
- **响应式数据流** - 基于 Vue 3 响应式系统的数据管理

### 后端技术栈

#### 核心框架（计划中）
- **Express.js** - 轻量级 Node.js Web 框架
- **TypeScript** - 提供类型安全的服务端开发
- **Prisma** - 现代化 ORM，支持 PostgreSQL

#### 数据库与存储
- **PostgreSQL** - 主数据库
- **PostGIS** - 地理空间数据扩展
- **几何数据支持** - 点、线、面等空间几何类型

#### API 与服务
- **RESTful API** - 标准化的 API 设计
- **Swagger/OpenAPI** - 自动生成 API 文档
- **CORS** - 跨域资源共享支持

### 服务器资源连接架构

#### SuperMap 服务连接
```typescript
// 配置化的服务连接管理
const apiConfig = {
  baseUrl: 'http://localhost:8090', // SuperMap iServer 地址
  mapService: 'iserver/services/map-WuHan/rest', // 地图服务
  dataService: 'iserver/services/data-WuHan/rest/data', // 数据服务
  timeout: 10000, // 请求超时时间
  retryCount: 3 // 重试次数
}

// 统一的服务客户端
export class SuperMapClient {
  // 健康检查
  async checkServiceHealth(): Promise<ServiceResponse<boolean>>
  
  // 带重试机制的请求执行
  private async executeWithRetry<T>(operation: () => Promise<T>): Promise<T>
  
  // 指数退避重试策略
  private shouldRetry(error: any): boolean
}
```

#### 数据图层管理
系统预配置了完整的武汉市地理数据图层：

**行政区划图层**
- 武汉_县级 - 县级行政区边界

**城市基础信息**
- 公路网络 - 城市交通干道
- 铁路网络 - 轨道交通线路
- 水系线 - 河流水道
- 水系面 - 湖泊水体
- 建筑物面 - 城市建筑轮廓

**基础设施点位**
- 学校分布 - 教育设施点位
- 医院分布 - 医疗设施点位
- 居民地地名点 - 重要地名标注

#### 错误处理与恢复机制
```typescript
// 分层错误处理策略
export class SuperMapError extends Error {
  constructor(
    message: string,
    public code?: number,
    public type: 'network' | 'service' | 'timeout' = 'service'
  )
}

// 错误恢复机制
- 网络错误：自动重试（指数退避）
- 服务错误：用户通知 + 降级处理
- 超时错误：重试 + 用户反馈
```

## 项目结构

### 根目录结构
```
SuperMap/
├── README.md                 # 项目说明文档
├── Frontend/                 # 前端应用
│   ├── src/                  # 源代码
│   ├── public/               # 静态资源
│   ├── package.json          # 前端依赖配置
│   └── vite.config.js        # 构建配置
├── Backend/                  # 后端API（开发中）
│   ├── src/                  # 源代码
│   ├── prisma/               # 数据库模型
│   └── package.json          # 后端依赖配置
└── .claude/                  # Claude AI 助手配置
```

### 前端详细结构
```
Frontend/src/
├── api/                      # API 客户端层
│   ├── supermap.ts          # SuperMap 统一客户端
│   ├── analysis.ts          # 空间分析 API
│   └── config.ts            # API 配置管理
├── components/              # 组件库
│   ├── Layout/              # 布局组件
│   │   ├── DashboardLayout.vue      # 主布局容器
│   │   ├── DashboardHeader.vue      # 顶部导航栏
│   │   └── RightPanel.vue           # 右侧工具面板
│   ├── Map/                 # 地图功能组件
│   │   ├── SuperMapViewer.vue       # 核心地图组件
│   │   ├── LayerManager.vue         # 图层管理器
│   │   ├── DrawTools.vue            # 绘制工具栏
│   │   ├── BufferAnalysisPanel.vue  # 缓冲区分析面板
│   │   ├── DistanceAnalysisPanel.vue # 距离分析面板
│   │   ├── AccessibilityAnalysisPanel.vue # 可达性分析面板
│   │   ├── FeaturePopup.vue         # 要素信息弹窗
│   │   ├── CoordinateDisplay.vue    # 坐标显示组件
│   │   ├── ZoomControls.vue         # 缩放控件
│   │   ├── ScaleBar.vue            # 比例尺显示
│   │   ├── EditTools.vue           # 要素编辑工具
│   │   └── ChatAssistant.vue       # AI 聊天助手
│   └── UI/                  # 通用UI组件
│       ├── ButtonGroup.vue          # 按钮组
│       ├── PanelWindow.vue          # 窗口面板
│       ├── SplitPanel.vue           # 分割面板
│       └── [其他UI组件...]
├── composables/             # 业务逻辑组合函数
│   ├── useMap.ts            # 地图核心逻辑
│   ├── useLayerManager.ts   # 图层管理逻辑
│   ├── useDraw.ts           # 绘制工具逻辑
│   ├── useBufferAnalysis.ts # 缓冲区分析
│   ├── useDistanceAnalysis.ts # 距离分析
│   └── useAccessibilityAnalysis.ts # 可达性分析
├── stores/                  # 状态管理
│   ├── mapStore.ts          # 地图状态管理
│   ├── layerStore.ts        # 图层状态管理
│   ├── analysisStore.ts     # 分析工具状态
│   ├── themeStore.ts        # 主题状态管理
│   └── loadingStore.ts      # 加载状态管理
├── types/                   # TypeScript 类型定义
│   ├── map.ts               # 地图相关接口
│   ├── supermap.d.ts        # SuperMap 类型声明
│   └── splitpanes.d.ts      # UI组件类型
├── utils/                   # 工具函数库
│   ├── config.ts            # 配置管理工具
│   └── notification.ts      # 通知系统
└── styles/                  # 样式文件
    └── theme.css            # 主题样式定义
```

### 后端结构（计划）
```
Backend/src/
├── config/                  # 配置文件
├── controllers/            # 控制器层
├── middleware/             # 中间件
├── models/                 # 数据模型
├── routes/                 # 路由定义
├── services/              # 业务逻辑层
├── types/                 # 类型定义
└── utils/                 # 工具函数
```

## 快速开始

### 环境要求

- **Node.js** >= 20.0.0
- **npm** >= 8.0.0
- **SuperMap iServer** (可选，用于完整功能)

### 前端开发

```bash
# 进入前端目录
cd Frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 后端开发（计划中）

```bash
# 进入后端目录
cd Backend

# 安装依赖
npm install

# 数据库初始化
npm run prisma:generate
npm run prisma:push

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 启动生产服务器
npm run start
```

### 环境配置

#### 前端环境变量
创建 `.env` 文件配置开发环境：

```env
# SuperMap 服务配置
VITE_SUPERMAP_BASE_URL=http://localhost:8090
VITE_SUPERMAP_MAP_SERVICE=iserver/services/map-WuHan/rest
VITE_SUPERMAP_DATA_SERVICE=iserver/services/data-WuHan/rest/data
VITE_SUPERMAP_DATASET_NAME=武汉_县级@wuhan@@武汉

# API 配置
VITE_API_TIMEOUT=10000
VITE_API_RETRY_COUNT=3
VITE_DEV_MODE=true
```

生产环境使用 `.env.production`：
```env
VITE_SUPERMAP_BASE_URL=https://your-production-server.com
VITE_DEV_MODE=false
```

#### 后端环境变量（计划）
```env
# 数据库配置
DATABASE_URL=postgresql://username:password@localhost:5432/supermap_db

# 服务配置
PORT=3000
NODE_ENV=development

# SuperMap 服务配置
SUPERMAP_SERVER_URL=http://localhost:8090
```

## 功能特性详解

### 核心地图功能

#### 1. 地图显示与交互
- **多图层支持** - 支持矢量图层、栅格图层的叠加显示
- **缩放控制** - 鼠标滚轮、双击、拖拽等多种缩放方式
- **平移导航** - 流畅的地图拖拽导航体验
- **坐标显示** - 实时显示鼠标位置的经纬度坐标

#### 2. 图层管理系统
- **图层切换** - 可视化控制各图层的显示/隐藏
- **图层分组** - 按功能域对图层进行逻辑分组
- **样式配置** - 支持点、线、面要素的样式自定义
- **透明度控制** - 调整图层透明度以便叠加显示

#### 3. 要素交互功能
- **悬停高亮** - 鼠标悬停自动高亮要素
- **点击选择** - 点击要素显示详细信息弹窗
- **属性查看** - 查看要素的完整属性信息
- **几何信息** - 显示要素的几何类型和坐标信息

### 空间分析工具

#### 1. 缓冲区分析
```typescript
// 缓冲区分析功能
interface BufferAnalysisParams {
  geometry: any        // 输入几何体
  distance: number     // 缓冲距离（米）
  unit: 'meter' | 'km' // 距离单位
}
```

#### 2. 距离分析
```typescript
// 距离测量功能
interface DistanceAnalysisParams {
  startPoint: [number, number]  // 起点坐标
  endPoint: [number, number]    // 终点坐标
  unit: 'meter' | 'km'         // 测量单位
}
```

#### 3. 可达性分析
```typescript
// 可达性分析参数
interface AccessibilityParams {
  center: [number, number]     // 中心点
  radius: number              // 分析半径
  travelMode: string         // 出行方式
}
```

### 绘制与编辑工具

#### 绘制功能
- **点绘制** - 在地图上标注点要素
- **线绘制** - 绘制路径、边界线等线要素
- **面绘制** - 绘制区域、缓冲区等面要素
- **自由绘制** - 支持复杂几何体的自由绘制

#### 编辑功能
- **要素选择** - 选择已存在的要素进行编辑
- **节点编辑** - 修改几何体的节点位置
- **属性编辑** - 编辑要素的属性信息
- **删除要素** - 删除不需要的要素

### 主题系统

#### 主题切换机制
```css
/* CSS 变量系统支持主题切换 */
:root {
  --bg: #ffffff;           /* 背景色 */
  --text: #000000;         /* 文字色 */
  --border: #e0e0e0;       /* 边框色 */
  --primary: #007bff;      /* 主题色 */
}

[data-theme='dark'] {
  --bg: #1a1a1a;
  --text: #ffffff;
  --border: #404040;
  --primary: #4dabf7;
}
```

#### 自适应主题
- **系统主题检测** - 自动检测用户系统主题偏好
- **手动切换** - 提供主题切换按钮供用户选择
- **持久化存储** - 记住用户的主题选择偏好

## 部署方案

### 开发环境部署

#### 1. SuperMap 服务准备
```bash
# 启动 SuperMap iServer
# 确保以下服务可访问：
# - 地图服务: http://localhost:8090/iserver/services/map-WuHan/rest
# - 数据服务: http://localhost:8090/iserver/services/data-WuHan/rest/data
```

#### 2. 前端开发服务器
```bash
cd Frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### 生产环境部署

#### 1. 前端构建与部署
```bash
# 构建生产版本
npm run build

# 部署到 Web 服务器
# 将 dist 目录内容部署到 Nginx/Apache 等服务器
```

#### 2. Nginx 配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/dist;
    index index.html;
    
    # 处理单页应用路由
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # SuperMap 服务代理
    location /api/ {
        proxy_pass http://supermap-server:8090/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 3. 后端服务部署（计划）
```bash
# 使用 PM2 部署 Node.js 服务
pm2 start dist/app.js --name "supermap-api"
pm2 startup
pm2 save
```

## 开发指南

### 添加新的空间分析功能

1. **创建分析组合函数**
```typescript
// src/composables/useCustomAnalysis.ts
export function useCustomAnalysis() {
  const analysisStore = useAnalysisStore()
  
  const performAnalysis = async (params: CustomAnalysisParams) => {
    // 实现分析逻辑
  }
  
  return { performAnalysis }
}
```

2. **添加分析面板组件**
```vue
<!-- src/components/Map/CustomAnalysisPanel.vue -->
<template>
  <PanelWindow title="自定义分析">
    <!-- 分析参数输入界面 -->
  </PanelWindow>
</template>
```

3. **注册到分析工具栏**
```typescript
// 在相关组件中添加新的分析工具按钮
```

### 添加新的数据图层

1. **更新配置文件**
```typescript
// src/utils/config.ts
export const createAPIConfig = (): APIConfig => {
  return {
    // ... 现有配置
    wuhanLayers: [
      // ... 现有图层
      {
        name: '新图层@wuhan@@武汉',
        type: 'polygon',
        visible: true,
        group: '新分组',
        datasetName: '新数据集',
        dataService: 'iserver/services/map-WuHan/rest/maps/武汉'
      }
    ]
  }
}
```

2. **更新类型定义**
```typescript
// src/types/map.ts - 如需要添加新的属性类型
```

### 自定义主题样式

1. **扩展CSS变量**
```css
/* src/styles/theme.css */
:root {
  --custom-color: #your-color;
}

[data-theme='dark'] {
  --custom-color: #your-dark-color;
}
```

2. **在组件中使用**
```vue
<style scoped>
.custom-element {
  background-color: var(--custom-color);
}
</style>
```

## 性能优化

### 地图性能优化

- **图层懒加载** - 按需加载图层数据
- **要素简化** - 根据缩放级别简化几何体
- **缓存策略** - 缓存已加载的地图瓦片
- **视口裁剪** - 只渲染可见区域的要素

### 前端性能优化

- **代码分割** - 按路由分割代码包
- **组件懒加载** - 大型组件按需加载
- **图片优化** - 使用WebP格式，实现响应式图片
- **CDN加速** - 静态资源使用CDN分发

## 故障排除

### 常见问题

#### 1. SuperMap 服务连接失败
```
错误: 无法连接到 SuperMap 服务
解决: 
- 检查 SuperMap iServer 是否运行
- 确认服务地址配置正确
- 检查网络防火墙设置
```

#### 2. 地图无法显示
```
错误: 地图容器空白
解决:
- 检查浏览器控制台错误信息
- 确认 OpenLayers 库加载成功
- 检查地图服务URL是否可访问
```

#### 3. 图层加载失败
```
错误: 特定图层无法显示
解决:
- 确认数据集名称正确
- 检查图层配置参数
- 验证数据服务权限
```

### 调试技巧

#### 1. 开启开发模式
```typescript
// 在配置中启用调试
const config = createAPIConfig()
console.log('当前配置:', config)
```

#### 2. 网络请求调试
```typescript
// 使用浏览器开发者工具 Network 标签
// 检查 SuperMap 服务请求和响应
```

#### 3. 地图实例调试
```typescript
// 在浏览器控制台访问地图实例
window.debugMap = mapInstance
```

## 贡献指南

### 代码规范

- **TypeScript** - 使用严格的类型检查
- **ESLint** - 遵循 Vue/TypeScript 编码规范
- **Prettier** - 统一代码格式化
- **注释规范** - 为复杂逻辑添加中文注释

### 提交规范

```bash
# 功能添加
git commit -m "feat: 添加缓冲区分析功能"

# 错误修复
git commit -m "fix: 修复图层加载失败问题"

# 文档更新
git commit -m "docs: 更新API使用文档"

# 样式调整
git commit -m "style: 优化主题切换动画效果"
```

### 发布流程

1. **开发分支** - 在功能分支上开发新特性
2. **测试验证** - 确保功能正常运行
3. **代码审查** - 进行代码质量检查
4. **合并主分支** - 合并到主分支
5. **版本发布** - 创建版本标签并部署

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详细信息。

## 联系方式

- **项目维护者**: [您的姓名]
- **邮箱**: [您的邮箱]
- **GitHub**: [项目GitHub地址]

---

> 本项目基于 SuperMap 技术构建，为现代化城市地理信息系统提供完整解决方案。