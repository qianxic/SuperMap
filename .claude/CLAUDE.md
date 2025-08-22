# CLAUDE.md

这个文件为 Claude Code (claude.ai/code) 在此代码库中的工作提供指导。

## 项目概览

这是一个基于 SuperMap 技术的现代化城市仪表板系统，采用前后端分离架构。项目主要包含：

### 技术架构总览
- **前端**: Vue 3 + TypeScript + OpenLayers + SuperMap iClient
- **后端**: Node.js + Express + TypeScript + Prisma ORM (计划中)
- **数据库**: PostgreSQL + PostGIS (计划中)
- **GIS服务**: SuperMap iServer

### 项目结构
```
SuperMap/
├── Frontend/           # Vue 3 前端应用 (主要开发)
│   ├── src/           # 源代码
│   ├── public/        # 静态资源 (包含大量 SuperMap 示例)
│   └── package.json   # 依赖配置
├── Backend/           # Node.js 后端API (框架已搭建，内容为空)
│   ├── src/          # 源代码目录 (空)
│   ├── prisma/       # 数据库模型
│   └── package.json  # 后端依赖配置
└── README.md         # 项目文档
```

## 开发命令

### 前端开发
```bash
# 进入前端目录
cd Frontend

# 安装依赖
npm install

# 启动开发服务器 (支持热重载)
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 后端开发 (计划中，目前为空)
```bash
# 进入后端目录
cd Backend

# 安装依赝
npm install

# 数据库操作
npm run prisma:generate
npm run prisma:push
npm run prisma:migrate

# 启动开发服务器
npm run dev

# 构建和启动
npm run build
npm run start
```

## 核心架构特点

### 1. 服务器资源连接架构

#### SuperMap 服务集成模式
项目采用直连 SuperMap iServer 的架构模式：

```typescript
// 配置化服务连接 - Frontend/src/utils/config.ts
export const createAPIConfig = (): APIConfig => {
  return {
    baseUrl: 'http://localhost:8090',  // SuperMap iServer 地址
    mapService: 'iserver/services/map-WuHan/rest',      // 地图服务端点
    dataService: 'iserver/services/data-WuHan/rest/data', // 数据服务端点
    timeout: 10000,        // 请求超时配置
    retryCount: 3,         // 失败重试次数
    // 武汉数据图层完整配置
    wuhanLayers: [ /* 详细的图层配置... */ ]
  }
}
```

#### 统一API客户端设计
```typescript
// 健壮的服务客户端 - Frontend/src/api/supermap.ts
export class SuperMapClient {
  // 服务健康检查
  async checkServiceHealth(): Promise<ServiceResponse<boolean>>
  
  // 指数退避重试机制
  private async executeWithRetry<T>(operation: () => Promise<T>): Promise<T>
  
  // 错误分类处理
  private shouldRetry(error: SuperMapError): boolean
}
```

#### 数据图层体系架构
系统预配置完整的武汉市地理数据图层体系：

**行政区划层级**
- `武汉_县级@wuhan@@武汉` - 县级行政区边界

**城市基础信息分组**
- `公路@wuhan@@武汉` - 城市道路网络 (线要素)
- `铁路@wuhan@@武汉` - 轨道交通网络 (线要素) 
- `水系线@wuhan@@武汉` - 河流水道 (线要素)
- `水系面@wuhan@@武汉` - 湖泊水体 (面要素)
- `建筑物面@wuhan@@武汉` - 建筑轮廓 (面要素)

**基础设施点位分组**
- `学校@wuhan@@武汉` - 教育设施分布 (点要素)
- `医院@wuhan@@武汉` - 医疗设施分布 (点要素)
- `居民地地名点@wuhan@@武汉` - 重要地标 (点要素)

### 2. 前端实现架构深度分析

#### 响应式状态管理架构
```typescript
// 核心地图状态 - Frontend/src/stores/mapStore.ts
const useMapStore = defineStore('map', () => {
  // 地图核心实例
  const map = ref<any>(null)              // OpenLayers Map 实例
  const isMapReady = ref<boolean>(false)  // 地图初始化状态
  
  // 分层图层管理
  const baseLayer = ref<any>(null)        // 基础底图图层
  const hoverLayer = ref<any>(null)       // 悬停交互图层
  const selectLayer = ref<any>(null)      // 选择交互图层
  const vectorLayers = ref<MapLayer[]>([])  // 矢量数据图层数组
  const customLayers = ref<MapLayer[]>([]) // 用户自定义图层
  
  // 交互状态管理
  const hoveredFeature = ref<any>(null)   // 当前悬停要素
  const selectedFeature = ref<any>(null)  // 当前选中要素
  const currentCoordinate = ref<Coordinate>({}) // 鼠标坐标
  
  // 弹窗状态控制
  const popupVisible = ref<boolean>(false)
  const popupPosition = ref<{x: number, y: number}>({})
  const popupContent = ref<string>('')
  
  // 动态配置生成
  const createMapConfig = (): MapConfig => { /* 配置生成逻辑 */ }
  
  return { /* 导出响应式状态和方法 */ }
})
```

#### 组件化功能模块设计

**布局层组件架构**
```
Layout/
├── DashboardLayout.vue      # 主容器 (Splitpanes 75%/25% 布局)
├── DashboardHeader.vue      # 顶部导航 (主题切换 + 标题)
└── RightPanel.vue           # 右侧工具面板 (分析工具容器)
```

**地图功能组件架构**
```
Map/
├── SuperMapViewer.vue       # 核心地图视图 (OpenLayers 集成)
├── LayerManager.vue         # 图层管理器 (显示/隐藏/分组)
├── DrawTools.vue            # 绘制工具栏 (点/线/面绘制)
├── EditTools.vue            # 编辑工具 (节点编辑/属性编辑)
├── *AnalysisPanel.vue       # 分析面板系列:
│   ├── BufferAnalysisPanel.vue      # 缓冲区分析
│   ├── DistanceAnalysisPanel.vue    # 距离测量分析
│   └── AccessibilityAnalysisPanel.vue # 可达性分析
├── FeaturePopup.vue         # 要素信息弹窗
├── CoordinateDisplay.vue    # 实时坐标显示
├── ZoomControls.vue         # 缩放控制器
├── ScaleBar.vue            # 比例尺显示
└── ChatAssistant.vue       # AI聊天助手 (计划中)
```

**通用UI组件库**
```
UI/
├── PanelWindow.vue          # 通用窗口面板组件
├── ButtonGroup.vue          # 按钮组组件
├── SplitPanel.vue           # 分割面板组件
├── PrimaryButton.vue        # 主要按钮
├── SecondaryButton.vue      # 次要按钮
├── DropdownSelect.vue       # 下拉选择器
├── LLMInputGroup.vue        # LLM输入组件
└── TraditionalInputGroup.vue # 传统输入组件
```

#### 业务逻辑组合函数架构
```typescript
// 地图核心逻辑 - Frontend/src/composables/useMap.ts
export function useMap() {
  const mapStore = useMapStore()
  
  // 地图初始化与服务连接
  const initializeMap = async () => { /* SuperMap + OpenLayers 初始化 */ }
  
  // 事件处理系统
  const setupMapEvents = () => { /* 鼠标交互、要素选择事件 */ }
  
  return { initializeMap, setupMapEvents, /* 其他地图方法 */ }
}

// 图层管理逻辑 - Frontend/src/composables/useLayerManager.ts  
export function useLayerManager() {
  // 图层加载与样式配置
  const loadVectorLayer = async (layerConfig: WuhanLayer) => { /* 加载逻辑 */ }
  
  // 图层显示控制
  const toggleLayerVisibility = (layerName: string, visible: boolean) => { }
  
  return { loadVectorLayer, toggleLayerVisibility }
}

// 空间分析组合函数系列
// - useBufferAnalysis.ts     # 缓冲区分析业务逻辑
// - useDistanceAnalysis.ts   # 距离测量业务逻辑  
// - useAccessibilityAnalysis.ts # 可达性分析业务逻辑
```

### 3. 主题系统深度实现

#### CSS 变量驱动的主题切换
```css
/* Frontend/src/styles/theme.css */
:root {
  /* 基础色彩变量 */
  --bg: #ffffff;                    /* 主背景色 */
  --text: #000000;                  /* 主文本色 */
  --border: #e0e0e0;                /* 边框色 */
  --primary: #007bff;               /* 主题色 */
  --secondary: #6c757d;             /* 次要色 */
  
  /* 功能色彩变量 */
  --success: #28a745;               /* 成功色 */
  --warning: #ffc107;               /* 警告色 */
  --error: #dc3545;                 /* 错误色 */
  
  /* 地图特定变量 */
  --map-control-bg: rgba(255, 255, 255, 0.9);
  --popup-bg: #ffffff;
  --popup-shadow: rgba(0, 0, 0, 0.15);
}

/* 暗色主题覆盖 */
[data-theme='dark'] {
  --bg: #1a1a1a;
  --text: #ffffff; 
  --border: #404040;
  --primary: #4dabf7;
  --map-control-bg: rgba(26, 26, 26, 0.9);
  --popup-bg: #2d2d2d;
}
```

#### 响应式主题管理
```typescript
// Frontend/src/stores/themeStore.ts
export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref<'light' | 'dark' | 'auto'>('auto')
  
  // 系统主题检测
  const applySystemTheme = () => {
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    document.documentElement.setAttribute('data-theme', systemPrefersDark ? 'dark' : 'light')
  }
  
  // 主题切换监听
  const setupSystemThemeListener = () => {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applySystemTheme)
  }
  
  return { currentTheme, applySystemTheme, setupSystemThemeListener }
})
```

## 项目当前状态

### ✅ 已完成的核心功能

#### 1. 基础架构完成度: 90%
- ✅ Vue 3 + TypeScript 项目框架
- ✅ Vite 构建系统配置 
- ✅ Pinia 状态管理集成
- ✅ 路径别名和TypeScript配置

#### 2. 地图核心功能完成度: 85%  
- ✅ SuperMap + OpenLayers 集成
- ✅ 武汉市多图层数据展示
- ✅ 地图交互 (缩放/平移/坐标显示)
- ✅ 要素悬停和选择交互
- ✅ 弹窗信息显示系统

#### 3. 图层管理完成度: 80%
- ✅ 图层显示/隐藏控制
- ✅ 按组分类的图层管理
- ✅ 图层样式配置系统  
- ✅ 矢量要素样式渲染

#### 4. 空间分析工具完成度: 70%
- ✅ 缓冲区分析面板UI
- ✅ 距离分析面板UI  
- ✅ 可达性分析面板UI
- ⚠️ 分析功能后端集成待完善

#### 5. 绘制编辑功能完成度: 65%
- ✅ 点/线/面绘制工具
- ✅ 绘制结果显示
- ⚠️ 要素编辑功能部分完成
- ❌ 属性编辑功能待开发

#### 6. UI系统完成度: 90%
- ✅ 响应式布局 (75%地图 + 25%工具面板)
- ✅ 主题切换系统 (明暗主题)
- ✅ 通用UI组件库
- ✅ 移动端适配

### 🚧 开发中的功能

#### 1. 后端API系统 (0% - 框架已搭建但无实现)
- 📦 Express + TypeScript 框架已配置
- 📦 Prisma ORM 数据模型已定义
- ❌ 控制器和服务层代码为空
- ❌ 数据库连接和API端点未实现

#### 2. 高级分析功能 (30%)
- ⚠️ 分析参数验证逻辑
- ⚠️ 分析结果可视化
- ❌ 复杂几何运算集成

#### 3. AI聊天助手 (10%)
- ✅ ChatAssistant 组件框架
- ❌ AI集成和对话逻辑

### 📋 计划中的功能

#### 1. 数据管理系统
- 📋 要素数据CRUD操作
- 📋 数据导入/导出功能
- 📋 数据格式转换 (GeoJSON/Shapefile)

#### 2. 用户系统
- 📋 用户认证和权限管理
- 📋 个人工作空间
- 📋 项目和图层共享

#### 3. 高级可视化
- 📋 数据图表集成
- 📋 时态数据动画
- 📋 3D可视化扩展

## 关键实现细节

### 错误处理和恢复机制

#### 分层错误处理策略
```typescript
// 错误分类系统
export class SuperMapError extends Error {
  constructor(
    message: string,
    public code?: number,
    public type: 'network' | 'service' | 'timeout' = 'service'
  ) { super(message) }
}

// 重试策略配置
class SuperMapClient {
  private async executeWithRetry<T>(operation: () => Promise<T>, retries = 3): Promise<T> {
    try {
      return await operation()
    } catch (error) {
      if (retries > 0 && this.shouldRetry(error)) {
        await this.delay(Math.pow(2, 3 - retries) * 1000) // 指数退避
        return this.executeWithRetry(operation, retries - 1)
      }
      throw error
    }
  }
}
```

#### 用户反馈系统
```typescript
// Frontend/src/utils/notification.ts
export const handleError = (error: Error, context: string) => {
  // 错误分类和用户友好的提示
  if (error instanceof SuperMapError) {
    switch (error.type) {
      case 'network':
        showNotification('网络连接失败，请检查网络设置', 'error')
        break
      case 'timeout': 
        showNotification('请求超时，服务可能繁忙', 'warning')
        break
      case 'service':
        showNotification(`服务错误: ${error.message}`, 'error')
        break
    }
  }
}
```

### 性能优化实现

#### 1. 地图渲染优化
```typescript
// 图层懒加载策略
const loadVectorLayer = async (layerConfig: WuhanLayer) => {
  // 视口范围检测
  const viewExtent = map.getView().calculateExtent()
  
  // 只加载可视区域内的要素
  const features = await fetchFeaturesInExtent(layerConfig, viewExtent)
  
  // 几何体简化 (根据缩放级别)
  const simplifiedFeatures = simplifyFeaturesByZoom(features, map.getView().getZoom())
  
  return simplifiedFeatures
}
```

#### 2. 状态管理优化
```typescript
// 响应式数据的计算属性缓存
const formattedCoordinate = computed(() => {
  // 避免频繁的字符串格式化
  const { lon, lat } = currentCoordinate.value
  if (!lon || !lat) return '经度: -, 纬度: -'
  return `经度: ${lon.toFixed(6)}, 纬度: ${lat.toFixed(6)}`
})
```

## 开发工作流程

### 添加新的空间分析功能

#### 1. 创建分析组合函数
```typescript
// src/composables/useNewAnalysis.ts
import { ref } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'

export function useNewAnalysis() {
  const analysisStore = useAnalysisStore()
  const isAnalyzing = ref(false)
  
  const performAnalysis = async (params: NewAnalysisParams) => {
    isAnalyzing.value = true
    try {
      // 1. 参数验证
      validateAnalysisParams(params)
      
      // 2. 调用分析服务
      const result = await superMapClient.newAnalysis(params)
      
      // 3. 结果处理和可视化
      analysisStore.setAnalysisResult('new-analysis', result)
      
      // 4. 在地图上显示结果
      displayAnalysisResult(result)
      
    } catch (error) {
      handleError(error, '新分析功能')
    } finally {
      isAnalyzing.value = false
    }
  }
  
  return { performAnalysis, isAnalyzing }
}
```

#### 2. 创建分析面板组件
```vue
<!-- src/components/Map/NewAnalysisPanel.vue -->
<template>
  <PanelWindow title="新分析功能" :loading="isAnalyzing">
    <div class="analysis-form">
      <!-- 参数输入表单 -->
      <TraditionalInputGroup 
        label="分析参数"
        v-model="analysisParams.value"
        @change="onParamChange"
      />
      
      <!-- 执行按钮 -->
      <PrimaryButton 
        @click="runAnalysis"
        :disabled="!isParamsValid"
      >
        开始分析
      </PrimaryButton>
    </div>
  </PanelWindow>
</template>

<script setup lang="ts">
import { useNewAnalysis } from '@/composables/useNewAnalysis'
// 组件逻辑...
</script>
```

#### 3. 集成到主界面
```vue
<!-- src/components/Layout/RightPanel.vue -->
<template>
  <div class="right-panel">
    <!-- 其他分析面板 -->
    <NewAnalysisPanel v-if="activeAnalysis === 'new-analysis'" />
  </div>
</template>
```

### 添加新的数据图层

#### 1. 更新图层配置
```typescript
// src/utils/config.ts
export const createAPIConfig = (): APIConfig => {
  return {
    // ... 现有配置
    wuhanLayers: [
      // ... 现有图层
      {
        name: '新数据图层@wuhan@@武汉',
        type: 'polygon',  // 或 'point', 'line'
        visible: true,
        group: '新功能分组',
        datasetName: '新数据集名称',
        dataService: 'iserver/services/map-WuHan/rest/maps/武汉'
      }
    ]
  }
}
```

#### 2. 添加样式配置
```typescript
// 在 mapStore.ts 的 createMapConfig 中添加样式
const vectorLayerConfigs: VectorLayerConfig[] = apiConfig.wuhanLayers
  .map(layer => {
    // 为新图层添加专门的样式配置
    if (layer.name.includes('新数据图层')) {
      return {
        name: layer.name,
        style: {
          stroke: { width: 2, color: '#ff6600' },
          fill: { color: 'rgba(255, 102, 0, 0.2)' }
        }
      }
    }
    // ... 其他图层样式
  })
```

### 自定义主题扩展

#### 1. 添加新的CSS变量
```css
/* src/styles/theme.css */
:root {
  /* 新主题变量 */
  --new-feature-primary: #6366f1;
  --new-feature-secondary: #a5b4fc;
  --new-feature-bg: rgba(99, 102, 241, 0.1);
}

[data-theme='dark'] {
  --new-feature-primary: #818cf8;
  --new-feature-secondary: #6366f1;
  --new-feature-bg: rgba(129, 140, 248, 0.2);
}
```

#### 2. 在组件中应用主题
```vue
<style scoped>
.new-feature-panel {
  background: var(--new-feature-bg);
  border: 1px solid var(--new-feature-secondary);
}

.new-feature-button {
  background: var(--new-feature-primary);
  color: var(--text);
}
</style>
```

## 重要注意事项

### 1. SuperMap 服务依赖

系统严重依赖 SuperMap iServer 服务，开发时需要：

```bash
# 确保 SuperMap iServer 运行在 localhost:8090
# 主要服务端点:
# - 地图服务: http://localhost:8090/iserver/services/map-WuHan/rest
# - 数据服务: http://localhost:8090/iserver/services/data-WuHan/rest/data  

# 检查服务可用性
curl http://localhost:8090/iserver/services/map-WuHan/rest/maps/武汉
```

### 2. 外部库依赖管理

```html
<!-- public/index.html 中加载的外部库 -->
<script src="./libs/supermap/iclient-ol.min.js"></script>
<script src="./libs/openlayers/ol.js"></script>

<!-- 确保这些库在组件使用前已加载 -->
```

### 3. 类型安全开发

```typescript
// 始终使用 TypeScript 接口定义
interface WuhanLayer {
  name: string
  type: 'point' | 'line' | 'polygon' | 'raster'
  visible: boolean
  group?: string
  datasetName: string
  dataService: string
}

// 为 SuperMap 对象添加类型声明
declare global {
  interface Window {
    ol: any
    'ol.supermap': any
  }
}
```

### 4. 错误处理最佳实践

```typescript
// 总是使用统一的错误处理
try {
  const result = await superMapClient.someOperation()
  if (result.success) {
    // 处理成功结果
  } else {
    handleError(new Error(result.error), '操作名称')
  }
} catch (error) {
  handleError(error, '操作上下文')
}
```

### 5. 性能考虑

- **图层数量控制**: 避免同时显示过多图层
- **要素数量限制**: 大数据集使用分页或聚类
- **事件监听器清理**: 组件销毁时清理地图事件
- **内存泄漏预防**: 及时清理 OpenLayers 对象引用

## 故障排除指南

### 常见问题及解决方案

#### 1. SuperMap 服务连接失败
```
症状: 控制台报错 "无法连接到 SuperMap 服务"
原因: SuperMap iServer 未启动或端口配置错误
解决: 
- 检查 iServer 服务状态
- 确认端口 8090 可访问
- 检查防火墙设置
```

#### 2. 图层无法加载
```
症状: 特定图层在地图上不显示
原因: 数据集名称或服务路径配置错误
解决:
- 检查 wuhanLayers 配置中的 datasetName
- 验证 dataService 路径正确性
- 确认 SuperMap 中数据集存在
```

#### 3. 地图交互失效
```
症状: 鼠标悬停或点击无反应
原因: OpenLayers 事件监听器未正确绑定
解决:
- 检查 setupMapEvents 是否被调用
- 确认地图初始化完成后再绑定事件
- 查看浏览器控制台错误信息
```

#### 4. 主题切换异常
```
症状: 切换主题后部分元素样式异常
原因: CSS 变量未正确覆盖或组件未使用变量
解决:
- 检查 CSS 变量定义完整性
- 确保组件样式使用 var() 语法
- 验证主题属性正确设置到 document.documentElement
```

---

## 重要提醒

- **当前后端为空**: Backend 目录虽然有完整的包配置和数据模型，但 src 下的所有目录都是空的
- **主要开发在前端**: 目前所有功能都在 Frontend 中实现，直接连接 SuperMap 服务
- **生产环境考虑**: 需要实现后端API作为中间层，提供数据缓存、用户管理、权限控制等功能
- **数据安全**: 直连 SuperMap 服务不适合生产环境，需要后端API层进行安全控制