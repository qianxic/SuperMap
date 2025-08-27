# SuperMap Frontend - 主题切换系统文档

## 📖 概述

本项目实现了完整的主题切换系统，支持浅色和深色两种主题模式，通过CSS变量统一管理所有颜色，确保整个应用界面的一致性和可维护性。

## 🎨 主题切换机制

### 核心原理
- 通过修改 `document.documentElement.setAttribute('data-theme', theme)` 触发主题切换
- 使用CSS变量（CSS Custom Properties）统一管理颜色
- 支持系统主题自动检测和手动切换

### 主题存储
- 使用 `localStorage` 持久化主题设置
- 支持系统主题偏好自动检测
- 默认主题：深色模式

## 🌈 颜色变量系统

### 基础颜色变量

#### 浅色主题 (`:root`)
```css
--bg: #f8f9fa                    /* 主背景色 */
--panel: #ffffff                 /* 面板背景色 */
--border: #dee2e6               /* 边框颜色 */
--text: #212529                 /* 主文本颜色 */
--sub: #6c757d                  /* 次要文本颜色 */
--accent: #212529               /* 强调色 */
--accent-rgb: 33, 37, 41       /* 强调色RGB值 */
--glow: 0 2px 8px rgba(0, 0, 0, 0.08)  /* 阴影效果 */
--radius: 10px                  /* 圆角半径 */
```

#### 深色主题 (`[data-theme="dark"]`)
```css
--bg: #1e1e1e                   /* 主背景色 */
--panel: #2d2d30                /* 面板背景色 */
--border: #3c3c3c               /* 边框颜色 */
--text: #ffffff                 /* 主文本颜色 */
--sub: #cccccc                  /* 次要文本颜色 */
--accent: #666666               /* 强调色 */
--accent-rgb: 102, 102, 102    /* 强调色RGB值 */
--glow: 0 2px 8px rgba(0, 0, 0, 0.4)   /* 阴影效果 */
```

### 按钮颜色系统

#### 浅色主题
```css
--btn-primary-bg: #212529       /* 主按钮背景 */
--btn-primary-color: #ffffff    /* 主按钮文字 */
--btn-secondary-bg: #e9ecef     /* 次按钮背景 */
--btn-secondary-color: #212529  /* 次按钮文字 */
```

#### 深色主题
```css
--btn-primary-bg: #000000       /* 主按钮背景 */
--btn-primary-color: #ffffff    /* 主按钮文字 */
--btn-secondary-bg: #373737     /* 次按钮背景 */
--btn-secondary-color: #ffffff  /* 次按钮文字 */
```

### 交互颜色系统

#### 浅色主题
```css
--surface: rgba(0, 0, 0, 0.03)           /* 表面色 */
--surface-hover: rgba(0, 0, 0, 0.06)     /* 悬停表面色 */
--divider: #dee2e6                       /* 分割线颜色 */
--selection-bg: rgba(33, 37, 41, 0.1)    /* 选择背景色 */
```

#### 深色主题
```css
--surface: rgba(255, 255, 255, 0.03)     /* 表面色 */
--surface-hover: rgba(255, 255, 255, 0.06) /* 悬停表面色 */
--divider: #484848                       /* 分割线颜色 */
--selection-bg: rgba(255, 255, 255, 0.15) /* 选择背景色 */
```

### 地图相关颜色

#### 浅色主题
```css
--map-hover-fill: rgba(0, 0, 0, 0.06)        /* 地图悬停填充 */
--map-select-fill: rgba(33, 37, 41, 0.15)    /* 地图选择填充 */
--map-highlight-color: #000000                /* 地图高亮边界色 */
--measure-line-color: #212529                 /* 测量线颜色 */
--measure-line-rgb: 33, 37, 41               /* 测量线RGB值 */
--overview-extent-color: #000000              /* 鹰眼视口框颜色 */
--overview-extent-rgb: 0, 0, 0               /* 鹰眼视口框RGB值 */
```

#### 深色主题
```css
--map-hover-fill: rgba(255, 255, 255, 0.06)  /* 地图悬停填充 */
--map-select-fill: rgba(255, 255, 255, 0.15) /* 地图选择填充 */
--map-highlight-color: #ffffff                /* 地图高亮边界色 */
--measure-line-color: #ffffff                 /* 测量线颜色 */
--measure-line-rgb: 255, 255, 255            /* 测量线RGB值 */
--overview-extent-color: #cccccc              /* 鹰眼视口框颜色 */
--overview-extent-rgb: 204, 204, 204         /* 鹰眼视口框RGB值 */
```

### 滚动条颜色（深色主题特有）
```css
--scrollbar-track: rgba(255, 255, 255, 0.1)      /* 滚动条轨道 */
--scrollbar-thumb: rgba(255, 255, 255, 0.3)      /* 滚动条滑块 */
--scrollbar-thumb-hover: rgba(255, 255, 255, 0.5) /* 滚动条滑块悬停 */
```

### 分割面板颜色

#### 浅色主题
```css
--splitter-bg: rgba(0, 0, 0, 0.1)    /* 分割器背景 */
--splitter-hover: #212529             /* 分割器悬停 */
```

#### 深色主题
```css
--splitter-bg: rgba(255, 255, 255, 0.1) /* 分割器背景 */
--splitter-hover: #000000                /* 分割器悬停 */
```

### 弹窗和字段颜色

#### 浅色主题
```css
--field-label-color: #6c757d    /* 字段标签颜色 */
--field-value-color: #212529    /* 字段值颜色 */
```

#### 深色主题
```css
--field-label-color: #cccccc    /* 字段标签颜色 */
--field-value-color: #ffffff    /* 字段值颜色 */
```

### 图层颜色（动态）

#### 武汉市县级图层（动态主题适配）
```css
/* 浅色主题 */
--layer-stroke-武汉_县级: #000000    /* 黑色边界 */
--layer-fill-武汉_县级: rgba(0, 0, 0, 0.1)  /* 半透明黑色填充 */

/* 深色主题 */
--layer-stroke-武汉_县级: #ffffff    /* 白色边界 */
--layer-fill-武汉_县级: rgba(255, 255, 255, 0.1)  /* 半透明白色填充 */
```

**注意**：武汉市县级图层会根据主题自动切换颜色，确保在不同主题下都有良好的可见性。

**修复说明**：之前存在主题监听器配置错误的问题，`MutationObserver` 监听的是 `['class', 'style']` 属性，但主题切换时修改的是 `data-theme` 属性。现已修复为正确监听 `['data-theme']` 属性。

#### 固定图层颜色（不受主题影响）
```css
/* 交通设施 - 公路 */
--layer-stroke-公路: #f39c12
--layer-fill-公路: rgba(243, 156, 18, 0.08)

/* 交通设施 - 铁路 */
--layer-stroke-铁路: #8e44ad
--layer-fill-铁路: rgba(142, 68, 173, 0.08)

/* 水系 - 水系面 */
--layer-stroke-水系面: #2980b9
--layer-fill-水系面: rgba(41, 128, 185, 0.18)

/* 水系 - 水系线 */
--layer-stroke-水系线: #3498db
--layer-fill-水系线: rgba(52, 152, 219, 0.10)

/* 建筑物 - 建筑物面 */
--layer-stroke-建筑物面: #7f8c8d
--layer-fill-建筑物面: rgba(127, 140, 141, 0.20)

/* 地名点 - 居民地地名点 */
--layer-stroke-居民地地名点: #e74c3c
--layer-fill-居民地地名点: rgba(231, 76, 60, 0.35)

/* 公共服务 - 学校 */
--layer-stroke-学校: #27ae60
--layer-fill-学校: rgba(39, 174, 96, 0.35)

/* 公共服务 - 医院 */
--layer-stroke-医院: #c0392b
--layer-fill-医院: rgba(192, 57, 43, 0.35)
```

## 🔧 技术实现

### 主题存储 (themeStore.ts)
```typescript
export const useThemeStore = defineStore('theme', () => {
  const theme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'dark')
  
  // 切换主题
  const toggleTheme = () => {
    const newTheme = theme.value === 'light' ? 'dark' : 'light'
    theme.value = newTheme
  }
  
  // 监听主题变化，自动应用到DOM和localStorage
  watch(theme, (newTheme) => {
    applyTheme(newTheme)
    localStorage.setItem('theme', newTheme)
  }, { immediate: true })
})
```

### 主题切换触发
```typescript
// 应用主题到DOM
const applyTheme = (newTheme: Theme) => {
  document.documentElement.setAttribute('data-theme', newTheme)
}
```

### 系统主题检测
```typescript
// 检测系统主题偏好
const detectSystemTheme = (): Theme => {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

// 监听系统主题变化
const setupSystemThemeListener = () => {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
      setTheme(e.matches ? 'dark' : 'light')
    }
  })
}
```

## 📱 应用范围

### 布局组件
- `DashboardLayout.vue` - 主布局容器
- `DashboardHeader.vue` - 顶部导航栏
- `RightPanel.vue` - 右侧面板

### UI组件
- `PrimaryButton.vue` - 主按钮
- `SecondaryButton.vue` - 次按钮
- `IconButton.vue` - 图标按钮
- `ButtonGroup.vue` - 按钮组
- `PanelWindow.vue` - 面板窗口
- `PanelContainer.vue` - 面板容器
- `SplitPanel.vue` - 分割面板
- `TipWindow.vue` - 提示窗口
- `EditModal.vue` - 编辑模态框
- `DropdownSelect.vue` - 下拉选择器
- `AutoScrollContainer.vue` - 自动滚动容器

### 地图组件
- `AreaMeasurePanel.vue` - 面积测量面板
- `DistanceMeasureButton.vue` - 距离测量按钮
- `CoordinateDisplay.vue` - 坐标显示
- `OverviewMap.vue` - 鹰眼地图
- `LayerAssistant.vue` - 图层助手
- `ScaleBar.vue` - 比例尺

### 页面组件
- `Login.vue` - 登录页面
- `Register.vue` - 注册页面
- `UserProfile.vue` - 用户资料页面
- `Dashboard.vue` - 仪表板页面

### 功能组件
- `LLMInputGroup.vue` - LLM输入组

## 🎯 特殊样式覆盖

### 深色主题强制样式
```css
/* 确保黑色主题下所有弹出窗口使用浅色字体 */
[data-theme="dark"] .panel-window,
[data-theme="dark"] .confirm-dialog,
[data-theme="dark"] .notification-toast,
[data-theme="dark"] .popup-body,
[data-theme="dark"] .feature-info,
[data-theme="dark"] .multi-feature-info {
  color: #ffffff !important;
}

/* 确保黑色主题下标题、坐标、比例尺等使用浅色字体 */
[data-theme="dark"] .screen-title,
[data-theme="dark"] .coordinate-text,
[data-theme="dark"] .scale-text {
  color: #ffffff !important;
}
```

### 防闪烁样式
```css
/* 全局防闪烁样式 - 防止主题切换时的颜色闪烁 */
.no-theme-flicker,
.no-theme-flicker *,
.no-theme-flicker *::before,
.no-theme-flicker *::after {
  transition: none !important;
  animation: none !important;
}
```

## 🚀 使用方法

### 1. 手动切换主题
```typescript
import { useThemeStore } from '@/stores/themeStore'

const themeStore = useThemeStore()

// 切换主题
themeStore.toggleTheme()

// 设置指定主题
themeStore.setTheme('light') // 或 'dark'
```

### 2. 在组件中使用主题
```vue
<template>
  <div class="my-component">
    <button class="btn-primary">按钮</button>
  </div>
</template>

<style scoped>
.my-component {
  background: var(--panel);
  color: var(--text);
  border: 1px solid var(--border);
}

.btn-primary {
  background: var(--btn-primary-bg);
  color: var(--btn-primary-color);
}
</style>
```

### 3. 在JavaScript中获取主题颜色
```typescript
// 获取CSS变量值
const getComputedStyle = (element: HTMLElement, property: string) => {
  return getComputedStyle(element).getPropertyValue(property).trim()
}

// 使用示例
const accentColor = getComputedStyle(document.documentElement, '--accent')
const textColor = getComputedStyle(document.documentElement, '--text')
```

## 📋 最佳实践

### 1. 颜色使用规范
- ✅ 使用CSS变量：`color: var(--text)`
- ❌ 避免硬编码：`color: #212529`

### 2. 组件设计原则
- 所有颜色都应该通过CSS变量定义
- 支持主题切换的组件应该使用相对颜色值
- 避免使用固定的颜色值

### 3. 性能优化
- 使用防闪烁样式避免主题切换时的视觉闪烁
- 合理使用CSS变量的回退值
- 避免在主题切换时进行复杂的DOM操作

### 4. 可访问性
- 确保颜色对比度符合WCAG标准
- 深色主题下使用足够的对比度
- 支持系统主题偏好设置

## 🔍 调试和测试

### 1. 检查主题状态
```javascript
// 检查当前主题
console.log(document.documentElement.getAttribute('data-theme'))

// 检查CSS变量值
console.log(getComputedStyle(document.documentElement, '--text'))
```

### 2. 主题切换测试
- 测试手动切换功能
- 测试系统主题自动检测
- 测试localStorage持久化
- 测试所有组件的颜色适配

### 3. 兼容性测试
- 测试不同浏览器的CSS变量支持
- 测试系统主题检测的兼容性
- 测试localStorage的可用性

## 📝 更新日志

### v1.0.0
- 实现基础的主题切换系统
- 支持浅色和深色两种主题
- 添加系统主题自动检测
- 实现localStorage持久化

### 未来计划
- 支持自定义主题色
- 添加更多主题预设
- 优化主题切换动画
- 增强可访问性支持

---

**注意**：本文档描述了完整的主题切换系统实现。所有颜色都应该通过CSS变量使用，确保主题切换的一致性和可维护性。
