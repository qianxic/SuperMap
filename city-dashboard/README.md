# 城市仪表板 (City Dashboard)

基于Vue 3 + TypeScript构建的城市仪表板应用，集成SuperMap GIS功能，提供地图展示、图层管理、空间分析等功能。

# 环境配置
win 系统极客自己安装（安装懒人包就不需要安装这个）
安装nodejs和npm和git
1. 安装 git for windows，链接：git-scm.com/download/win，使用默认选项安装即可
2. 访问 Node.js 官网
3. 下载 LTS 版本的安装包
4. 运行安装程序，按照提示完成安装
5. 打开命令提示符或 PowerShell，验证安装：
node --version
npm --version


## 技术栈

- **前端框架**: Vue 3 + Composition API + TypeScript
- **状态管理**: Pinia stores
- **样式方案**: CSS自定义属性 + 深色主题支持
- **UI组件**: Ant Design Vue + 自定义组件库
- **地图引擎**: SuperMap/OpenLayers集成
- **布局组件**: Splitpanes可调整面板
- **构建工具**: Vite

## 环境要求

- **Node.js**: v20.19.0+ 或 v22.12.0+
- **npm**: 建议 8.0+

## 快速开始

### 1. 克隆项目
```bash
git clone [项目地址]
cd city-dashboard
```

### 2. 安装依赖
```bash
npm install
```

### 3. 启动开发服务器
```bash
npm run dev
```

### 4. 构建生产版本
```bash
npm run build
```

### 5. 预览生产版本
```bash
npm run preview
```

## 项目架构

### 文件组织结构
```
src/
├── components/          # 按功能领域组织的组件
│   ├── Layout/         # 布局层组件 (导航、面板)
│   ├── Map/            # 地图功能组件 (视图、图层、工具)
│   ├── UI/             # 可复用UI组件库
│   └── LLM/            # AI助手组件
├── composables/        # 业务逻辑组合函数
├── stores/             # Pinia状态管理
├── types/              # TypeScript类型定义
├── styles/             # 全局样式文件
└── api/                # API接口层
```

### 核心特性

- **响应式布局**: 75%地图视图 + 25%右侧面板的分割布局
- **GIS功能**: 地图展示、图层管理、绘制工具、缓冲区分析
- **主题支持**: 基于CSS变量的深色主题
- **组件化架构**: 按功能领域分组的模块化设计
- **类型安全**: 完整的TypeScript类型定义

### 外部库集成

项目依赖SuperMap库的外部加载:
- 需确保 `window.ol` 和 `window.ol.supermap` 在地图初始化前可用
- 运行时加载GIS依赖，不打包进bundle

## 开发指南

### 推荐IDE
[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (请禁用Vetur)

### 配置参考
详见 [Vite配置文档](https://vite.dev/config/)

### 开发规范
- 遵循Vue 3 Composition API最佳实践
- 使用setup语法糖
- 统一的代码风格和组件规范
- 按功能领域组织代码结构

## 功能模块

- **地图交互**: 基于SuperMap/OpenLayers的地图展示
- **图层管理**: 动态图层控制和管理
- **绘制工具**: 点、线、面等几何要素绘制
- **空间分析**: 缓冲区分析等GIS分析功能
- **AI助手**: 集成聊天助手功能
- **响应式设计**: 支持移动端适配
