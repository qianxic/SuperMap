# 前后端通信优化方案实施指南

## 概述
本方案解决了原项目中硬编码服务地址、缺少错误处理、类型安全等问题，建立了完整的前后端通信架构。

## 核心改进

### 1. 环境配置管理
- ✅ 使用 `.env` 文件管理不同环境的配置
- ✅ 支持开发/生产环境自动切换
- ✅ 动态配置 SuperMap 服务地址

### 2. 统一API客户端
- ✅ 创建 `SuperMapClient` 统一管理所有 SuperMap 服务调用
- ✅ 内置重试机制和超时处理
- ✅ 指数退避策略处理网络错误

### 3. 错误处理机制
- ✅ 全局错误处理和用户通知系统
- ✅ 区分网络错误、服务错误和超时错误
- ✅ 友好的错误提示和恢复建议

### 4. 类型安全
- ✅ 完善的 TypeScript 接口定义
- ✅ 服务响应类型检查
- ✅ 编译时错误检测

### 5. 加载状态管理
- ✅ 统一的加载状态显示
- ✅ 支持进度更新和分步骤加载

## 使用方法

### 配置环境变量
在项目根目录创建 `.env` 文件：
\`\`\`env
VITE_SUPERMAP_BASE_URL=http://localhost:8090
VITE_SUPERMAP_MAP_SERVICE=iserver/services/map-WuHan/rest/maps/武汉_市级
VITE_SUPERMAP_DATA_SERVICE=iserver/services/data-WuHan/rest/data
VITE_SUPERMAP_DATASET_NAME=wuhan:武汉_县级
VITE_API_TIMEOUT=10000
VITE_API_RETRY_COUNT=3
\`\`\`

### 在组件中使用新的API客户端
\`\`\`typescript
import { superMapClient } from '@/api/supermap'
import { handleError, notificationManager } from '@/utils/notification'

// 获取要素数据
const loadFeatures = async () => {
  try {
    const result = await superMapClient.getFeaturesBySQL({
      datasetName: 'wuhan:武汉_县级',
      attributeFilter: '1=1'
    })
    
    if (result.success) {
      // 处理成功数据
      console.log('Features:', result.data)
    } else {
      handleError(result.error, '加载要素')
    }
  } catch (error) {
    handleError(error, '要素查询')
  }
}
\`\`\`

### 使用加载状态
\`\`\`typescript
import { useLoadingStore } from '@/stores/loadingStore'

const loadingStore = useLoadingStore()

const doSomething = async () => {
  loadingStore.startLoading('operation-id', '正在执行操作...')
  try {
    // 执行操作
    await someAsyncOperation()
    notificationManager.success('操作成功', '操作已完成')
  } catch (error) {
    handleError(error, '操作')
  } finally {
    loadingStore.stopLoading('operation-id')
  }
}
\`\`\`

## 后端开发建议

### 1. API 端点设计
确保后端提供的端点与前端配置匹配：
- 地图服务：`{BASE_URL}/iserver/services/map-WuHan/rest/maps/武汉_市级`
- 数据服务：`{BASE_URL}/iserver/services/data-WuHan/rest/data`

### 2. 错误响应格式
建议统一错误响应格式：
\`\`\`json
{
  "error": {
    "code": 400,
    "errorMsg": "具体错误信息",
    "details": "详细错误说明"
  }
}
\`\`\`

### 3. 健康检查端点
考虑提供服务健康检查端点：
- `GET /health` - 返回服务状态
- `GET /api/health` - 返回API服务状态

### 4. CORS 配置
确保跨域配置正确，允许前端域名访问。

### 5. 超时设置
建议服务端超时时间略小于前端超时时间（前端默认10秒）。

## 部署配置

### 开发环境
使用 `.env` 文件配置本地开发服务器地址。

### 生产环境
使用 `.env.production` 文件配置生产服务器地址，或通过构建工具传入环境变量。

### 构建命令
\`\`\`bash
# 开发模式
npm run dev

# 生产构建
npm run build

# 预览生产构建
npm run preview
\`\`\`

## 监控和调试

### 错误监控
- 所有错误都会在控制台输出详细信息
- 用户友好的错误提示通过通知系统显示
- 可以集成第三方错误监控服务

### 网络请求调试
- 开发模式下，API调用会有详细日志
- 可以通过浏览器开发工具查看网络请求
- 支持服务健康检查

## 性能优化

### 重试机制
- 网络错误和超时自动重试
- 指数退避避免服务过载
- 可配置重试次数

### 缓存策略
- 图层数据使用 OpenLayers 内置缓存
- 可以根据需要添加应用层缓存

### 加载优化
- 分步骤加载，提供用户反馈
- 支持并发加载多个图层
- 错误隔离，单个图层失败不影响其他图层

## 扩展性

### 添加新的API服务
1. 在 `supermap.ts` 中添加新的方法
2. 定义相应的 TypeScript 接口
3. 添加错误处理逻辑

### 集成其他地图服务
1. 创建新的客户端类
2. 实现统一的服务接口
3. 在配置文件中添加相关配置

这个优化方案为前后端通信提供了完整、健壮、可扩展的解决方案。