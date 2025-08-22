# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Install dependencies
npm install

# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Architecture

This is a Vue 3 + TypeScript city dashboard application built with Vite, featuring SuperMap integration for GIS mapping functionality with enhanced architecture for production-ready deployment.

### Technology Stack
- **Frontend**: Vue 3 with Composition API and TypeScript
- **State Management**: Pinia stores with reactive state management
- **Styling**: CSS custom properties with dark/light theme support
- **UI Components**: Ant Design Vue + custom component library
- **Mapping**: SuperMap/OpenLayers integration via external libs
- **Layout**: Splitpanes for resizable panels
- **Build Tool**: Vite with fast HMR
- **Network**: Unified API client with error handling and retry mechanism
- **Configuration**: Environment variables with multi-environment support

### Enhanced Architecture Features (v2.0)

#### 🔧 **Configuration Management**
- **Environment Variables**: `.env` and `.env.production` for different deployment environments
- **Dynamic Configuration**: Runtime configuration loading with `createAPIConfig()`
- **Service URLs**: Configurable SuperMap service endpoints
- **API Settings**: Timeout, retry count, and development mode configuration

#### 🚨 **Error Handling & Resilience**
- **Unified Error Handling**: Global error catching with user-friendly notifications
- **Retry Mechanism**: Exponential backoff for network failures
- **Timeout Protection**: Configurable request timeouts
- **Service Health Check**: Automatic service availability validation
- **Loading States**: Centralized loading state management

#### 🌐 **API Communication**
- **SuperMapClient**: Unified API client for all SuperMap service calls
- **Type Safety**: Complete TypeScript interfaces for service responses
- **Error Classification**: Network, service, and timeout error differentiation
- **Promise-based**: Modern async/await patterns throughout

### File Organization Design (Updated)

The project follows a **domain-driven modular architecture** with enhanced infrastructure:

```
src/
├── api/                    # 🆕 API客户端层
│   └── supermap.ts        # SuperMap统一客户端，支持重试和错误处理
├── components/            # 按功能领域组织的组件
│   ├── Layout/           # 布局层组件
│   │   ├── DashboardLayout.vue    # 主布局容器
│   │   ├── DashboardHeader.vue    # 顶部导航
│   │   └── RightPanel.vue         # 右侧面板
│   ├── Map/              # 地图功能组件
│   │   ├── SuperMapViewer.vue     # 核心地图视图
│   │   ├── LayerManager.vue       # 图层管理
│   │   ├── DrawTools.vue          # 绘制工具
│   │   ├── BufferAnalysisPanel.vue # 缓冲区分析
│   │   ├── DistanceAnalysisPanel.vue # 距离分析
│   │   ├── AccessibilityAnalysisPanel.vue # 可达性分析
│   │   ├── FeaturePopup.vue       # 要素弹窗
│   │   ├── CoordinateDisplay.vue   # 坐标显示
│   │   ├── ZoomControls.vue       # 缩放控件
│   │   ├── ScaleBar.vue          # 比例尺
│   │   ├── EditTools.vue         # 编辑工具
│   │   └── ChatAssistant.vue     # AI聊天助手
│   └── UI/               # 可复用UI组件库
│       ├── ButtonGroup.vue        # 按钮组
│       ├── PanelWindow.vue        # 面板窗口
│       ├── SplitPanel.vue         # 分割面板
│       ├── PrimaryButton.vue      # 主要按钮
│       ├── SecondaryButton.vue    # 次要按钮
│       ├── DropdownSelect.vue     # 下拉选择
│       ├── LLMInputGroup.vue      # LLM输入组
│       └── TraditionalInputGroup.vue # 传统输入组
├── composables/          # 业务逻辑组合函数
│   ├── useMap.ts         # 🔄 地图核心逻辑 (enhanced with error handling)
│   ├── useDraw.ts        # 绘制工具逻辑
│   ├── useLayerManager.ts # 图层管理逻辑
│   ├── useBufferAnalysis.ts # 缓冲区分析
│   ├── useDistanceAnalysis.ts # 距离分析
│   └── useAccessibilityAnalysis.ts # 可达性分析
├── stores/               # Pinia状态管理
│   ├── mapStore.ts       # 🔄 地图状态 (enhanced with config management)
│   ├── layerStore.ts     # 图层状态管理
│   ├── analysisStore.ts  # 分析工具状态
│   ├── themeStore.ts     # 主题状态管理
│   └── loadingStore.ts   # 🆕 加载状态管理
├── types/                # TypeScript类型定义
│   ├── map.ts            # 🔄 地图相关接口 (enhanced with API types)
│   ├── supermap.d.ts     # SuperMap全局声明
│   └── splitpanes.d.ts   # 分割面板类型
├── utils/                # 🆕 工具函数
│   ├── config.ts         # 配置管理工具
│   └── notification.ts   # 通知系统
├── styles/               # 全局样式
│   └── theme.css         # 主题样式定义
└── docs/                 # 🆕 项目文档
    └── api-optimization.md # API优化方案文档
```

### Core Architecture Patterns (Enhanced)

1. **Configuration-Driven Development**:
   - Environment-specific configurations using Vite env variables
   - Runtime configuration loading and validation
   - Service endpoint management and health checking

2. **Resilient Communication**:
   - Unified API client with built-in retry logic
   - Error classification and appropriate handling
   - User feedback through notification system

3. **Enhanced Component Structure**: 
   - **Layout层**: Responsible for overall layout and navigation structure
   - **Map层**: All GIS-related functional components with enhanced error handling
   - **UI层**: Reusable component library with consistent styling
   - **API层**: Centralized service communication layer

4. **Robust State Management**: 
   - `mapStore.ts`: Map instance, layers, coordinates, popup state with config management
   - `loadingStore.ts`: Centralized loading state management
   - `analysisStore.ts`: GIS analysis operations with enhanced error states

5. **Type-Safe Development**: 
   - Complete TypeScript coverage including API responses
   - Service interfaces and error type definitions
   - Runtime type validation for critical operations

### Key Implementation Details (Updated)

- **Map Integration**: Uses SuperMap/OpenLayers with health checking before initialization
- **Layout**: Split-pane layout (75% map, 25% right panel) with responsive design
- **Theming**: CSS custom properties for consistent dark/light theme styling
- **Responsive Design**: Mobile-friendly responsive breakpoints with touch support
- **External Dependencies**: SuperMap libraries loaded externally with fallback handling
- **Error Recovery**: Graceful degradation when services are unavailable
- **Performance**: Optimized loading with progress feedback and lazy loading

### Enhanced Data Flow

1. **Configuration Loading**: Environment-based configuration with validation
2. **Service Health Check**: Automatic service availability validation
3. **Map Initialization**: Enhanced with error handling and loading states
4. **User Interactions**: Trigger composable functions with proper error boundaries
5. **State Updates**: Reactive store mutations with error state management
6. **User Feedback**: Comprehensive notification system for all operations

### Development Guidelines

#### Error Handling Best Practices
```typescript
// Always use the unified error handling
import { handleError, notificationManager } from '@/utils/notification'

try {
  const result = await superMapClient.getFeaturesBySQL(params)
  if (result.success) {
    // Handle success
  } else {
    handleError(result.error, 'Feature Loading')
  }
} catch (error) {
  handleError(error, 'API Call')
}
```

#### Configuration Usage
```typescript
// Use dynamic configuration instead of hardcoded values
import { createAPIConfig, getFullUrl } from '@/utils/config'

const config = createAPIConfig()
const serviceUrl = getFullUrl('data')
```

#### Loading State Management
```typescript
// Use centralized loading states
import { useLoadingStore } from '@/stores/loadingStore'

const loadingStore = useLoadingStore()
loadingStore.startLoading('operation-id', 'Processing...')
// ... perform operation
loadingStore.stopLoading('operation-id')
```

### Development Status & Progress

#### ✅ **Completed Features**
- Core map display and interaction
- Layer management (show/hide/remove)
- Drawing tools (point/line/polygon)
- Spatial analysis panels (buffer/distance/accessibility)
- Feature interaction (hover/click/popup)
- Theme switching (dark/light)
- Responsive layout with splitpanes
- **🆕 Environment configuration management**
- **🆕 Unified API client with retry mechanism**
- **🆕 Comprehensive error handling system**
- **🆕 Loading state management**
- **🆕 Type-safe API communication**

#### 🚧 **In Development**
- AI chat assistant functionality
- Feature editing capabilities
- Data import/export features
- Enhanced mobile support

#### 📋 **Planned Features**
- User authentication and permissions
- Data visualization charts
- Multiple basemap support
- Offline capabilities
- Advanced spatial analysis tools

### Architectural Benefits (Enhanced)

1. **Maintainability**: Clear functional separation with robust error handling
2. **Scalability**: Environment-driven configuration supports multiple deployments
3. **Reliability**: Built-in retry mechanisms and graceful error recovery
4. **Developer Experience**: Comprehensive error feedback and loading states
5. **Production Ready**: Full configuration management and deployment support
6. **Type Safety**: Complete TypeScript coverage prevents runtime errors

### Backend Integration Requirements

When developing the backend, ensure compatibility with:

1. **Service Endpoints**: Match the configured service paths in environment variables
2. **Error Response Format**: Follow the standardized error response format
3. **CORS Configuration**: Allow requests from configured frontend domains
4. **Health Check Endpoints**: Provide service availability endpoints
5. **Timeout Handling**: Configure appropriate server-side timeouts

### External Library Integration (Enhanced)

The application relies on SuperMap libraries with enhanced loading:
- **Dependency Check**: Ensures `window.ol` and `window.ol.supermap` availability
- **Health Monitoring**: Validates service connectivity before operations
- **Graceful Degradation**: Handles library loading failures appropriately
- **Performance Optimization**: Excludes GIS libraries from bundle to reduce size

### Development Notes (Updated)

- Uses Vite with Vue plugin and TypeScript support with enhanced configuration
- Path aliases configured: `@/*` points to `src/*`
- CSS custom properties provide consistent theming with theme switching
- Component composition follows Vue 3 best practices with setup script syntax
- **Enhanced error boundaries protect against runtime failures**
- **Centralized configuration management supports multi-environment deployment**
- **Unified API client ensures consistent service communication patterns**

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

IMPORTANT: this context may be updated as the project evolves. Always refer to the actual file structure and implementation for the most current information.