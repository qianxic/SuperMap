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

This is a Vue 3 + TypeScript city dashboard application built with Vite, featuring SuperMap integration for GIS mapping functionality.

### Technology Stack
- **Frontend**: Vue 3 with Composition API and TypeScript
- **State Management**: Pinia stores
- **Styling**: CSS custom properties with dark theme support
- **UI Components**: Ant Design Vue, custom component library
- **Mapping**: SuperMap/OpenLayers integration via external libs
- **Layout**: Splitpanes for resizable panels
- **Build Tool**: Vite

### File Organization Design

The project follows a **domain-driven modular architecture** with clear separation of concerns:

```
src/
├── components/          # 按功能领域组织的组件
│   ├── Layout/         # 布局层组件
│   │   ├── DashboardLayout.vue    # 主布局容器
│   │   ├── DashboardHeader.vue    # 顶部导航
│   │   └── RightPanel.vue         # 右侧面板
│   ├── Map/            # 地图功能组件
│   │   ├── SuperMapViewer.vue     # 核心地图视图
│   │   ├── LayerManager.vue       # 图层管理
│   │   ├── DrawTools.vue          # 绘制工具
│   │   ├── BufferAnalysisPanel.vue # 缓冲区分析
│   │   ├── FeaturePopup.vue       # 要素弹窗
│   │   └── CoordinateDisplay.vue   # 坐标显示
│   ├── UI/             # 可复用UI组件库
│   │   ├── ButtonGroup.vue        # 按钮组
│   │   ├── PanelWindow.vue        # 面板窗口
│   │   ├── SplitPanel.vue         # 分割面板
│   │   └── FormInput.vue          # 表单输入
│   └── LLM/            # AI助手组件
│       └── ChatAssistant.vue      # 聊天助手
├── composables/        # 业务逻辑组合函数
├── stores/             # 状态管理
├── types/              # TypeScript类型定义
├── styles/             # 全局样式
├── models/             # 数据模型
└── api/                # API接口层
```

### Core Architecture Patterns

1. **按功能领域分组**: 组件按业务职责划分，便于团队协作和功能迭代
2. **关注点分离**: 
   - 视图层（components）专注UI渲染
   - 业务逻辑抽取到composables
   - 状态管理集中在stores
   - 类型定义统一管理

3. **Component Structure**: 
   - **Layout层**: 负责整体布局和导航结构
   - **Map层**: 所有GIS相关功能组件  
   - **UI层**: 可复用的通用组件库
   - **LLM层**: AI功能相关组件

4. **State Management**: 
   - `mapStore.ts`: Map instance, layers, coordinates, popup state
   - `layerStore.ts`: Layer management functionality  
   - `analysisStore.ts`: GIS analysis operations

5. **Composables**: Business logic extracted to reusable composables
   - `useMap.ts`: Core map initialization and interaction
   - `useDraw.ts`: Drawing tools functionality
   - `useLayerManager.ts`: Layer management operations
   - `useBufferAnalysis.ts`: Buffer analysis tools

6. **Types**: TypeScript definitions in `src/types/`
   - `map.ts`: Map-related interfaces
   - `supermap.d.ts`: SuperMap global declarations

### Key Implementation Details

- **Map Integration**: Uses SuperMap/OpenLayers loaded as external scripts via window.ol
- **Layout**: Split-pane layout with 75% map view and 25% right panel
- **Theming**: CSS custom properties for consistent dark theme styling
- **Responsive Design**: Mobile-friendly responsive breakpoints
- **External Dependencies**: SuperMap libraries loaded externally, not bundled

### Data Flow

1. Map instance managed in mapStore with reactive state
2. User interactions trigger composable functions
3. Store mutations update UI components reactively
4. Map layers and features managed through OpenLayers API

### External Library Integration

The application relies on SuperMap libraries loaded externally:
- Must ensure `window.ol` and `window.ol.supermap` are available before map initialization
- Uses fallback timeout if libraries aren't immediately ready
- No bundled GIS dependencies - all loaded at runtime

### Development Notes

- Uses Vite with Vue plugin and TypeScript support
- Path aliases configured: `@/*` points to `src/*`
- CSS custom properties provide consistent theming
- Component composition follows Vue 3 best practices with setup script syntax

### Architectural Benefits

1. **Maintainability**: Clear functional separation makes code easy to locate and modify
2. **Scalability**: New features can be added to appropriate domain directories
3. **Reusability**: UI components and composables support cross-module reuse
4. **Type Safety**: Centralized TypeScript definitions prevent duplicate types
5. **Team Collaboration**: Domain-based organization enables parallel development