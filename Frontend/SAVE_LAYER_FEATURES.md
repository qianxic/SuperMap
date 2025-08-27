# 另存为图层功能实现总结

## 1. 通用插槽函数设计

### 功能概述
将原有的 `saveDrawAsLayer` 函数重构为通用的 `saveFeaturesAsLayer` 插槽函数，支持从不同来源保存要素为图层。

### API 设计

**输入数据格式**:
```typescript
saveFeaturesAsLayer(
  features: any[],           // ol.Feature[] 要素数组
  layerName: string,         // 图层名称
  sourceType: 'draw' | 'area' | 'query' = 'draw'  // 来源类型
)
```

**数据处理方法**:
1. 验证输入要素数组
2. 转换为GeoJSON格式，添加几何属性（长度、面积、坐标等）
3. 根据来源类型设置不同的样式颜色
4. 创建新的矢量图层并添加到地图
5. 更新图层管理列表

**输出数据格式**:
- 返回 `boolean` 表示保存成功或失败
- 创建新的 `ol.layer.Vector` 图层对象
- 自动添加到 `mapStore.vectorLayers` 管理列表

### 样式区分
- **绘制图层**: 红色样式 (`#ff0000`)
- **区域选择**: 红色样式 (`#ff0000`) 
- **属性查询**: 蓝色样式 (`#0000ff`)

## 2. 区域选择保存功能

### 实现位置
- **文件**: `src/views/dashboard/traditional/tools/EditTools.vue`
- **功能**: 在区域选择工具中添加"另存为图层"按钮

### UI 设计
```vue
<SecondaryButton 
  text="另存为图层"
  @click="saveSelectedAsLayer"
  :disabled="selectedFeatures.length === 0"
/>
```

### 功能实现
```typescript
const saveSelectedAsLayer = async () => {
  if (selectedFeatures.value.length === 0) {
    return
  }

  const layerName = `区域选择_${new Date().toLocaleString()}`
  await saveFeaturesAsLayer(selectedFeatures.value, layerName, 'area')
}
```

### 使用流程
1. 用户在地图上框选要素
2. 选中要素显示在列表中
3. 点击"另存为图层"按钮
4. 自动创建绿色样式的新图层
5. 图层名称格式: `区域选择_2024-01-01 12:00:00`

## 3. 属性查询保存功能

### 实现位置
- **文件**: `src/views/dashboard/traditional/tools/FeatureQueryPanel.vue`
- **功能**: 在属性查询工具中添加"另存为图层"按钮

### UI 设计
```vue
<SecondaryButton 
  text="另存为图层"
  @click="saveQueryResultsAsLayer"
  :disabled="queryResults.length === 0"
/>
```

### 功能实现
```typescript
// 生成基于SQL语句的图层名称
const generateLayerNameFromQuery = () => {
  const condition = queryConfig.value.condition
  if (!condition || !condition.fieldName || !condition.value) {
    return `属性查询_${new Date().toLocaleString()}`
  }

  // 获取图层名称
  const layerName = getSelectedLayerName()
  
  // 获取操作符标签
  const operatorLabel = getOperatorLabel(condition.operator)
  
  // 拼接图层名称：图层名称 字段 条件 值
  const sqlLayerName = `${layerName} ${condition.fieldName} ${operatorLabel} ${condition.value}`
  
  return sqlLayerName
}

const saveQueryResultsAsLayer = async () => {
  if (queryResults.value.length === 0) {
    return
  }

  const layerName = generateLayerNameFromQuery()
  await saveFeaturesAsLayer(queryResults.value, layerName, 'query')
}
```

### 使用流程
1. 用户选择图层和查询条件
2. 执行查询获得结果
3. 点击"保存为图层"按钮
4. 自动创建蓝色样式的新图层
5. 图层名称格式: `道路 length > 111` (基于SQL语句生成)

## 4. 技术特点

### 统一的数据处理
- 所有来源的要素都通过同一个插槽函数处理
- 保持一致的几何属性计算（长度、面积、坐标）
- 统一的错误处理和用户通知

### 样式区分
- 不同来源的图层使用不同颜色便于识别
- 支持主题色变量引用
- 保持与现有样式系统的一致性

### 向后兼容
- 保留原有的 `saveDrawAsLayer` 函数
- 绘制功能不受影响
- 现有代码无需修改

### 用户体验
- 按钮状态根据要素数量自动启用/禁用
- 保存成功后显示通知消息
- 图层自动添加到图层管理列表

## 5. 扩展性

### 支持新的来源类型
只需在 `sourceType` 参数中添加新的类型，并在 `getLayerStyle` 函数中添加对应的样式即可。

### 自定义图层名称
可以通过参数传入自定义的图层名称，支持更灵活的命名规则。

### 样式定制
可以根据需要修改不同来源类型的样式，支持更丰富的视觉效果。

## 6. 测试示例

### 区域选择测试
1. 打开"按区域选择要素"工具
2. 在地图上框选要素
3. 点击"保存为图层"按钮
4. 验证：新图层使用红色样式，名称格式为 `区域选择_时间戳`

### 属性查询测试
1. 打开"按属性选择要素"工具
2. 选择图层：`道路`
3. 设置查询条件：
   - 字段：`length`
   - 操作符：`>`
   - 值：`111`
4. 执行查询
5. 点击"保存为图层"按钮
6. 验证：新图层使用蓝色样式，名称格式为 `道路 length > 111`

### 操作符映射测试
- `eq` → `=`
- `gt` → `>`
- `lt` → `<`
- `gte` → `>=`
- `lte` → `<=`
- `like` → `LIKE`

### 图层名称示例
- `道路 length > 111`
- `建筑物 area >= 1000`
- `学校 name LIKE 小学`
- `医院 distance <= 500`
