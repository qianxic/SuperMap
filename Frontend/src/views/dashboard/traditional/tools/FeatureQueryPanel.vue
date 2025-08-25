<template>
  <PanelWindow 
    :visible="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'query'"
    :embed="true"
    :width="'100%'"
    :height="'100%'"
    class="feature-query-panel"
    component-id="traditional-query-panel"
  >
    <!-- 图层选择 -->
    <div class="analysis-section">
      <div class="section-title">选择查询数据源</div>
      <DropdownSelect 
        v-model="selectedLayerId"
        :options="layerOptions"
        placeholder="无"
      />
    </div>
    
    <!-- 数据字段结构 -->
    <div class="analysis-section no-theme-flicker" v-if="layerFields.length > 0">
      <div class="section-title">
        数据字段结构 ({{ layerFields.length }}个字段)
      </div>
      <div class="fields-info">
        <div class="fields-header">
          <span class="field-name">字段名称</span>
          <span class="field-type">类型</span>
          <span class="field-sample">示例值</span>
          <span class="field-desc">描述</span>
        </div>
        <div class="fields-list">
          <div 
            v-for="field in layerFields" 
            :key="field.name"
            class="field-item"
            :class="{ active: selectedFieldName === field.name }"
            @click="selectFieldName(field.name)"
          >
            <span class="field-name">{{ field.name }}</span>
            <span class="field-type" :class="getFieldTypeClass(field.type)">{{ field.type }}</span>
            <span class="field-sample" :title="field.sampleValue">{{ field.sampleValue }}</span>
            <span class="field-desc">{{ field.description }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 查询条件设置 -->
    <div class="analysis-section">
      <div class="section-title">
        查询条件设置
        <span class="condition-hint"> 字段选择 | 比较操作符 | 值输入</span>
      </div>
      
      <!-- 查询条件 -->
      <div class="query-conditions">
        <QueryConditionRow
          :condition="queryConfig.condition || createDefaultCondition()"
          :fields="layerFields"
          :disabled="false"
          @update="updateCondition"
        />
      </div>
      

    </div>

    <!-- 查询结果 -->
    <div class="analysis-section" v-if="queryResults.length > 0">
      <div class="section-title">
        查询结果 ({{ queryResults.length }}个要素)
      </div>
      
      <div class="layer-list">
        <div 
          v-for="(feature, index) in queryResults" 
          :key="feature.getId?.() || index"
          class="layer-item"
          :class="{ 'active': selectedFeatureIndex === index }"
          @click="handleSelectFeature(index)"
        >
          <div class="layer-info">
            <div class="layer-name">要素 {{ index + 1 }} - {{ getFeatureType(feature) }}</div>
            <div class="layer-desc">{{ getSelectedLayerName() || '未知图层' }} | {{ getFeatureGeometryInfo(feature) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 查询操作 -->
    <div class="analysis-section">
      <div class="section-title">查询操作</div>
      <div class="button-column">
        <SecondaryButton 
          text="执行查询"
          variant="secondary"
          @click="executeQuery"
          :disabled="queryConfig.condition === null || queryConfig.condition.fieldName === '' || isQuerying"
          :loading="isQuerying"
        />
        <SecondaryButton 
          text="反选当前要素"
          @click="invertSelectedLayer"
          :disabled="isQuerying"
        />
        <SecondaryButton 
          text="清空查询结果"
          variant="danger"
          @click="clearQueryResults"
          :disabled="false"
        />
      </div>
    </div>
    
    <TipWindow v-if="selectedLayerId" :text="getTipText()" />
  </PanelWindow>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, watch, ref } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore.ts'
import { useFeatureQueryStore } from '@/stores/featureQueryStore.ts'
import { useModeStateStore } from '@/stores/modeStateStore.ts'
import DropdownSelect from '@/components/UI/DropdownSelect.vue'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import PanelWindow from '@/components/UI/PanelWindow.vue'
import TipWindow from '@/components/UI/TipWindow.vue'
import QueryConditionRow from '@/components/UI/QueryConditionRow.vue'
import type { QueryCondition } from '@/types/query'
 

const analysisStore = useAnalysisStore()
const featureQuery = useFeatureQueryStore()
const modeStateStore = useModeStateStore()
 

// 状态管理
const selectedLayerId = computed({
  get: () => featureQuery.selectedLayerId,
  set: (value) => featureQuery.selectedLayerId = value
})

const queryResults = computed(() => featureQuery.queryResults)
const layerFields = computed(() => featureQuery.layerFields)
const selectedFieldName = ref<string>('')
const queryConfig = computed(() => featureQuery.queryConfig)
const isQuerying = computed(() => featureQuery.isQuerying)
const selectedFeatureIndex = computed(() => featureQuery.selectedFeatureIndex)

// 工具状态管理
const toolId = 'query'

// 保存工具状态
const saveToolState = () => {
  const stateToSave = {
    selectedLayerId: selectedLayerId.value,
    queryConfig: queryConfig.value,
    queryResults: queryResults.value
  }
  console.log('保存查询工具状态:', stateToSave)
  modeStateStore.saveToolState(toolId, stateToSave)
}

// 恢复工具状态
const restoreToolState = () => {
  const state = modeStateStore.getToolState(toolId)
  console.log('恢复查询工具状态:', state)
  
  if (state.selectedLayerId) {
    selectedLayerId.value = state.selectedLayerId
  }
  if (state.queryConfig) {
    // 恢复查询配置
    Object.assign(featureQuery.queryConfig, state.queryConfig)
  }
  if (state.queryResults && state.queryResults.length > 0) {
    featureQuery.queryResults = state.queryResults
    // 恢复查询结果的高亮显示
    setTimeout(() => {
      featureQuery.highlightQueryResults()
    }, 100)
  }
  
  // 如果有选中的图层，确保字段结构也被恢复
  if (state.selectedLayerId) {
    setTimeout(async () => {
      await featureQuery.getLayerFields(state.selectedLayerId)
    }, 50)
  }
}

// 组件生命周期管理
onMounted(() => {
  // 立即恢复基本状态
  restoreToolState()
  
  // 延迟恢复完整状态，确保所有依赖都已准备好
  setTimeout(() => {
    restoreToolState()
  }, 200)
})

onUnmounted(() => {
  console.log('查询工具组件卸载，保存状态')
  saveToolState()
})

// 监听状态变化，自动保存
watch([selectedLayerId, queryConfig, queryResults], () => {
  saveToolState()
}, { deep: true })

// 监听工具面板状态变化，在面板关闭时保存状态
watch(() => analysisStore.toolPanel.visible, (newVisible, oldVisible) => {
  if (oldVisible && !newVisible && analysisStore.toolPanel.activeTool === 'query') {
    // 工具面板关闭时保存状态
    saveToolState()
  }
})

// 监听activeTool变化，在工具切换时保存状态
watch(() => analysisStore.toolPanel.activeTool, (newTool, oldTool) => {
  if (oldTool === 'query' && newTool !== 'query') {
    // 从查询工具切换到其他工具时，立即保存状态
    console.log('从查询工具切换到其他工具，保存状态')
    saveToolState()
  }
})

// 监听图层选择变化，自动获取字段结构
watch(selectedLayerId, async (newLayerId, oldLayerId) => {
  console.log('图层选择变化:', newLayerId, '从:', oldLayerId)
  
  // 只有在真正切换图层时才清空查询结果
  if (newLayerId && newLayerId !== oldLayerId) {
    // 清空查询结果
    featureQuery.queryResults = []
    
    // 重置查询条件
    Object.assign(featureQuery.queryConfig.condition, createDefaultCondition())
    
    // 获取新图层的字段结构
    await featureQuery.getLayerFields(newLayerId)
    analysisStore.setAnalysisStatus(`已选择图层: ${getSelectedLayerName()}`)
  } else if (newLayerId && newLayerId === oldLayerId) {
    // 如果是恢复状态时的相同图层，只获取字段结构
    await featureQuery.getLayerFields(newLayerId)
  } else if (!newLayerId) {
    // 选择“无”时清空字段与结果
    featureQuery.queryResults = []
    featureQuery.layerFields = []
    Object.assign(featureQuery.queryConfig.condition, createDefaultCondition())
    analysisStore.setAnalysisStatus('未选择查询图层')
  }
})

// 图层选项（首项为“无”）
const layerOptions = computed(() => [{ value: '', label: '无', disabled: false }, ...featureQuery.getLayerOptions()])

// 获取选中图层名称
const getSelectedLayerName = () => {
  return featureQuery.getSelectedLayerName(selectedLayerId.value)
}

// 获取TipWindow显示文本
const getTipText = () => {
  const layerName = getSelectedLayerName()
  const condition = queryConfig.value.condition
  
  // 获取图层要素数量
  const featureCount = featureQuery.getLayerFeatureCount(selectedLayerId.value)
  
  let tipText = `已选择图层: ${layerName}`
  
  if (featureCount > 0) {
    tipText += `，共${featureCount}个要素`
  }
  
  if (condition && condition.fieldName) {
    const operatorText = condition.operator ? ` (${getOperatorLabel(condition.operator)})` : ''
    tipText += `，查询字段: ${condition.fieldName}${operatorText}`
    
    if (condition.value) {
      tipText += `，查询值: ${condition.value}`
    }
  } else {
    tipText += `，请选择查询字段`
  }
  
  // 添加查询结果信息
  if (queryResults.value.length > 0) {
    tipText += `，找到${queryResults.value.length}个匹配要素`
  }
  
  return tipText
}

// 获取操作符标签
const getOperatorLabel = (operator: string) => {
  const operatorMap: { [key: string]: string } = {
    'eq': '=',
    'gt': '>',
    'lt': '<',
    'gte': '>=',
    'lte': '<=',
    'like': 'LIKE'
  }
  return operatorMap[operator] || operator
}

// 获取字段类型样式类
const getFieldTypeClass = (type: string): string => {
  const typeClasses: { [key: string]: string } = {
    '文本': 'type-text',
    '整数': 'type-number',
    '小数': 'type-number',
    '布尔值': 'type-boolean',
    '日期': 'type-date',
    '数组': 'type-array',
    '对象': 'type-object',
    '空值': 'type-null',
    '未知': 'type-unknown'
  }
  return typeClasses[type] || 'type-unknown'
}

// 复制字段名到剪贴板
const selectFieldName = (fieldName: string) => {
  selectedFieldName.value = fieldName
}

// 查询条件管理
const createDefaultCondition = (): QueryCondition => ({
  fieldName: '',
  operator: 'eq',
  value: ''
})

const updateCondition = (condition: QueryCondition) => {
  console.log('更新条件:', condition)
  // 直接更新查询条件
  Object.assign(featureQuery.queryConfig.condition, condition)
}



// 执行查询
const executeQuery = async () => {
  if (!selectedLayerId.value) {
    analysisStore.setAnalysisStatus('请选择查询图层')
    return
  }
  
  const condition = queryConfig.value.condition
  if (!condition || !condition.fieldName || !condition.value) {
    analysisStore.setAnalysisStatus('请填写完整的查询条件')
    return
  }
  
  try {
    const result = await featureQuery.executeQuery()
    
    if (result.success) {
      console.log('查询成功:', result)
      
      // 自动高亮显示查询结果
      if (result.data.length > 0) {
        featureQuery.highlightQueryResults()
      }
    } else {
      console.error('查询失败:', result.error)
    }
  } catch (error) {
    console.error('执行查询时出错:', error)
    analysisStore.setAnalysisStatus('查询执行失败，请重试')
  }
}

// 选择要素（在列表中点击）
const handleSelectFeature = (index: number) => {
  featureQuery.handleSelectFeature(index)
}



// 获取要素类型
const getFeatureType = (feature: any): string => {
  const geometry = feature.geometry || feature.getGeometry?.()
  if (!geometry) return '未知'
  
  // 直接返回几何类型，不进行映射
  const geometryType = geometry.getType?.() || geometry.type
  return geometryType || '未知'
}

// 获取要素几何信息
const getFeatureGeometryInfo = (feature: any): string => {
  const geometry = feature.geometry || feature.getGeometry?.()
  if (!geometry) return '未知坐标'
  
  try {
    const geometryType = geometry.getType?.() || geometry.type
    const coords = geometry.getCoordinates?.() || geometry.coordinates
    
    if (!coords) return '坐标解析失败'
    
    switch (geometryType) {
      case 'Point':
        // 点要素显示坐标
        if (Array.isArray(coords) && coords.length >= 2) {
          return `${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}`
        }
        return '点坐标解析失败'
      
      case 'LineString':
        // 线要素显示长度
        if (Array.isArray(coords) && coords.length >= 2) {
          const length = calculateLineLength(coords)
          return `长度: ${length.toFixed(4)}千米`
        }
        return '线长度计算失败'
      
      case 'Polygon':
        // 面要素显示面积
        if (Array.isArray(coords) && coords.length > 0) {
          const area = calculatePolygonArea(coords[0]) // 使用外环计算面积
          return `面积: ${area.toFixed(4)}平方千米`
        }
        return '面积计算失败'
      
      case 'MultiPoint':
        // 多点显示点数和第一个点的坐标
        if (Array.isArray(coords) && coords.length > 0) {
          const firstPoint = coords[0]
          if (Array.isArray(firstPoint) && firstPoint.length >= 2) {
            return `${coords.length}个点, 起始: ${firstPoint[0].toFixed(6)}, ${firstPoint[1].toFixed(6)}`
          }
        }
        return '多点坐标解析失败'
      
      case 'MultiLineString':
        // 多线显示总长度
        if (Array.isArray(coords) && coords.length > 0) {
          let totalLength = 0
          coords.forEach((lineCoords: number[][]) => {
            if (Array.isArray(lineCoords)) {
              totalLength += calculateLineLength(lineCoords)
            }
          })
          return `总长度: ${totalLength.toFixed(4)}千米`
        }
        return '多线长度计算失败'
      
      case 'MultiPolygon':
        // 多面显示总面积
        if (Array.isArray(coords) && coords.length > 0) {
          let totalArea = 0
          coords.forEach((polygonCoords: number[][][]) => {
            if (Array.isArray(polygonCoords) && polygonCoords.length > 0) {
              totalArea += calculatePolygonArea(polygonCoords[0]) // 使用外环
            }
          })
          return `总面积: ${totalArea.toFixed(4)}平方千米`
        }
        return '多面面积计算失败'
      
      default:
        // 未知类型，尝试显示第一个坐标
        if (Array.isArray(coords) && coords.length >= 2 && typeof coords[0] === 'number') {
          return `${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}`
        }
        return `${geometryType || '未知类型'}`
    }
  } catch (error) {
    console.error('几何信息解析错误:', error)
    return '几何信息解析失败'
  }
}

// 几何计算函数
const calculateLineLength = (coordinates: number[][]): number => {
  if (!coordinates || coordinates.length < 2) return 0
  
  let totalLength = 0
  for (let i = 1; i < coordinates.length; i++) {
    const [lon1, lat1] = coordinates[i - 1]
    const [lon2, lat2] = coordinates[i]
    totalLength += haversineDistance(lat1, lon1, lat2, lon2)
  }
  return totalLength
}

const calculatePolygonArea = (coordinates: number[][]): number => {
  if (!coordinates || coordinates.length < 3) return 0
  
  // 简化的球面面积计算（适用于小区域）
  let area = 0
  const n = coordinates.length
  
  for (let i = 0; i < n - 1; i++) {
    const [x1, y1] = coordinates[i]
    const [x2, y2] = coordinates[i + 1]
    area += x1 * y2 - x2 * y1
  }
  
  // 将度转换为平方千米（近似）
  const earthRadius = 6371 // 地球半径（千米）
  const latRad = coordinates[0][1] * Math.PI / 180
  const kmPerDegLat = earthRadius * Math.PI / 180
  const kmPerDegLon = kmPerDegLat * Math.cos(latRad)
  
  return Math.abs(area * kmPerDegLat * kmPerDegLon / 2)
}

const haversineDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
  const R = 6371 // 地球半径（千米）
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

// 反选当前已选中的要素
const invertSelectedLayer = () => {
  if (!selectedLayerId.value) {
    analysisStore.setAnalysisStatus('请先选择要操作的数据')
    return
  }
  
  try {
    featureQuery.invertSelectedLayer(selectedLayerId.value)
    analysisStore.setAnalysisStatus(`已反选图层 "${getSelectedLayerName()}"，更新查询结果列表`)
  } catch (error) {
    console.error('反选要素时出错:', error)
    analysisStore.setAnalysisStatus('反选要素时出错，请重试')
  }
}

// 清空查询结果（统一清除）
const clearQueryResults = () => {
  featureQuery.clearQuerySelection()
}


</script>

<style scoped>
.feature-query-panel {
  height: 100%;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.analysis-section {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px;
  animation: fadeIn 0.3s ease-out;
  margin-bottom: 16px;
}

/* 避免主题切换时该区域闪烁：禁用动画与过渡 */
.no-theme-flicker {
  animation: none !important;
}

.no-theme-flicker *,
.no-theme-flicker *::before,
.no-theme-flicker *::after {
  transition: none !important;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-title {
  font-size: 13px;
  color: var(--text);
  margin-bottom: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.field-hint,
.condition-hint {
  font-size: 11px;
  color: var(--sub);
  font-weight: normal;
}

.button-column {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 使用图层管理的列表样式 */
.layer-list { 
  display: flex; 
  flex-direction: column; 
  gap: 8px;
  max-height: 180px; /* 约3个项目的高度 */
  overflow-y: auto;
  padding-right: 4px; /* 为滚动条预留空间 */
}

.layer-item {
  display: flex; 
  align-items: center; 
  justify-content: space-between;
  background: var(--btn-secondary-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px 14px;
  animation: fadeIn 0.3s ease-out;
  cursor: pointer;
  transition: all 0.2s ease;
}

.layer-item:hover {
  background: var(--surface-hover);
  border-color: var(--accent);
}

.layer-item.active {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}

.layer-info { 
  display: flex; 
  flex-direction: column; 
}

.layer-name { 
  font-size: 13px; 
  color: var(--text); 
  font-weight: 500; 
}

.layer-item.active .layer-name {
  color: white;
}

.layer-desc { 
  font-size: 11px; 
  color: var(--sub); 
  margin-top: 2px; 
}

.layer-item.active .layer-desc {
  color: rgba(255, 255, 255, 0.9);
}

/* 字段结构样式 */
.fields-info {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--glow);
}

.fields-header {
  display: grid;
  grid-template-columns: 2fr 1fr 2fr 2fr;
  gap: 12px;
  padding: 12px 16px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
}

.fields-list {
  max-height: 300px;
  overflow-y: auto;
}

.field-item {
  display: grid;
  grid-template-columns: 2fr 1fr 2fr 2fr;
  gap: 12px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--divider);
  cursor: pointer;
  font-size: 12px;
  background: var(--panel);
  transition: background-color 0.2s ease;
}

.field-item.active {
  background: var(--surface-hover);
  border-left: 2px solid var(--accent);
}

.field-item:hover {
  background: var(--surface-hover);
}

.field-item:last-child {
  border-bottom: none;
}

.field-name {
  font-weight: 500;
  color: var(--text);
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.field-type {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  text-align: center;
  min-width: 40px;
}

.type-text {
  background: var(--field-type-text-bg);
  color: var(--field-type-text-color);
}

.type-number {
  background: var(--field-type-number-bg);
  color: var(--field-type-number-color);
}

.type-boolean {
  background: var(--field-type-boolean-bg);
  color: var(--field-type-boolean-color);
}

.type-date {
  background: var(--field-type-date-bg);
  color: var(--field-type-date-color);
}

.type-array {
  background: var(--field-type-array-bg);
  color: var(--field-type-array-color);
}

.type-object {
  background: var(--field-type-object-bg);
  color: var(--field-type-object-color);
}

.type-null {
  background: var(--field-type-null-bg);
  color: var(--field-type-null-color);
}

.type-unknown {
  background: var(--field-type-unknown-bg);
  color: var(--field-type-unknown-color);
}

.field-sample {
  color: var(--sub);
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.field-desc {
  color: var(--sub);
  font-size: 11px;
}

/* 查询条件样式 */
.query-conditions {
  margin-bottom: 16px;
}







/* 滚动条样式 */
.fields-list::-webkit-scrollbar,
.layer-list::-webkit-scrollbar {
  width: 3px;
}

.fields-list::-webkit-scrollbar-track,
.layer-list::-webkit-scrollbar-track {
  background: var(--scrollbar-track, rgba(200, 200, 200, 0.1));
  border-radius: 1.5px;
}

.fields-list::-webkit-scrollbar-thumb,
.layer-list::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb, rgba(150, 150, 150, 0.3));
  border-radius: 1.5px;
}

.fields-list::-webkit-scrollbar-thumb:hover,
.layer-list::-webkit-scrollbar-thumb:hover {
  background: var(--scrollbar-thumb-hover, rgba(150, 150, 150, 0.5));
}
</style>
