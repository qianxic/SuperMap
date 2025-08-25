<template>
  <PanelWindow 
    :visible="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'query'"
    :embed="true"
    :width="'100%'"
    :height="'100%'"
    class="feature-query-panel"
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
    <div class="analysis-section" v-if="layerFields.length > 0">
      <div class="section-title">
        数据字段结构 ({{ layerFields.length }}个字段)
        <span class="field-hint">选择字段后将自动复制名称</span>
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
            @click="copyFieldName(field.name)"
            :title="`点击复制字段名: ${field.name}`"
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
      
      <div class="query-results">
        <div 
          v-for="(feature, index) in queryResults" 
          :key="feature.getId?.() || index"
          class="result-item"
          :class="{ 'active': selectedFeatureIndex === index }"
          @click="handleSelectFeature(index)"
        >
          <div class="result-info">
            <div class="result-name">要素 {{ index + 1 }}</div>
            <div class="result-desc">{{ getFeatureDescription(feature) }}</div>
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
import { computed, onMounted, onUnmounted, watch } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore.ts'
import { useFeatureQuery } from '@/composables/useFeatureQuery.ts'
import { useModeStateStore } from '@/stores/modeStateStore.ts'
import DropdownSelect from '@/components/UI/DropdownSelect.vue'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import PanelWindow from '@/components/UI/PanelWindow.vue'
import TipWindow from '@/components/UI/TipWindow.vue'
import QueryConditionRow from '@/components/UI/QueryConditionRow.vue'
import type { QueryCondition } from '@/types/query'
import { useMapStore } from '@/stores/mapStore.ts'

const analysisStore = useAnalysisStore()
const featureQuery = useFeatureQuery()
const modeStateStore = useModeStateStore()
const mapStore = useMapStore()

// 状态管理
const selectedLayerId = computed({
  get: () => featureQuery.selectedLayerId.value,
  set: (value) => featureQuery.selectedLayerId.value = value
})

const queryResults = computed(() => featureQuery.queryResults.value)
const layerFields = computed(() => featureQuery.layerFields.value)
const queryConfig = computed(() => featureQuery.queryConfig)
const isQuerying = computed(() => featureQuery.isQuerying.value)
const selectedFeatureIndex = computed(() => featureQuery.selectedFeatureIndex.value)

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
    featureQuery.queryResults.value = state.queryResults
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
    featureQuery.initAutoScroll()
  }, 200)
})

onUnmounted(() => {
  console.log('查询工具组件卸载，保存状态')
  saveToolState()
  // 清除点击事件监听
  featureQuery.clearSelectionInteractions()
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
    featureQuery.queryResults.value = []
    
    // 重置查询条件
    Object.assign(featureQuery.queryConfig.condition, createDefaultCondition())
    
    // 获取新图层的字段结构
    await featureQuery.getLayerFields(newLayerId)
    analysisStore.setAnalysisStatus(`已选择图层: ${getSelectedLayerName()}`)
  } else if (newLayerId && newLayerId === oldLayerId) {
    // 如果是恢复状态时的相同图层，只获取字段结构
    await featureQuery.getLayerFields(newLayerId)
  }
})

// 图层选项
const layerOptions = computed(() => featureQuery.getLayerOptions())

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
const copyFieldName = async (fieldName: string) => {
  try {
    await navigator.clipboard.writeText(fieldName)
    analysisStore.setAnalysisStatus(`已复制字段名: ${fieldName}`)
  } catch (error) {
    console.error('复制字段名失败:', error)
    analysisStore.setAnalysisStatus('复制字段名失败')
  }
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

// 获取要素描述
const getFeatureDescription = (feature: any) => {
  const properties = feature.getProperties?.() || feature.properties || {}
  const geometry = feature.getGeometry?.() || feature.geometry
  
  let desc = ''
  if (geometry) {
    const geometryType = geometry.getType?.() || geometry.type
    desc += `${geometryType} | `
  }
  
  // 显示前几个属性值
  const propertyValues = Object.values(properties).filter(v => v !== undefined && v !== null)
  if (propertyValues.length > 0) {
    desc += propertyValues.slice(0, 2).join(', ')
  }
  
  return desc || '无属性信息'
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

// 清空查询结果
const clearQueryResults = () => {
  // 清空查询结果数组
  featureQuery.queryResults.value = []
  
  // 同时清空地图上的高亮显示
  if (mapStore.selectLayer && mapStore.selectLayer.getSource()) {
    mapStore.selectLayer.getSource().clear()
  }
  
  // 清除点击事件监听
  featureQuery.clearSelectionInteractions()
  
  // 重置选中要素索引
  featureQuery.selectedFeatureIndex.value = -1
  
  // 清空选择状态
  if (featureQuery.highlightedFeature) {
    featureQuery.removeHighlightFeature()
  }
  
  analysisStore.setAnalysisStatus('已清空查询结果')
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

.query-results {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 4px;
}

.result-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--btn-secondary-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.result-item:hover {
  background: var(--surface-hover);
  border-color: var(--accent);
}

.result-item.active {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}

.result-item.active .result-name {
  color: white;
}

.result-item.active .result-desc {
  color: rgba(255, 255, 255, 0.9);
}

.result-info {
  display: flex;
  flex-direction: column;
}

.result-name {
  font-size: 13px;
  color: var(--text);
  font-weight: 500;
}

.result-desc {
  font-size: 11px;
  color: var(--sub);
  margin-top: 2px;
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
.query-results::-webkit-scrollbar {
  width: 3px;
}

.fields-list::-webkit-scrollbar-track,
.query-results::-webkit-scrollbar-track {
  background: var(--scrollbar-track, rgba(200, 200, 200, 0.1));
  border-radius: 1.5px;
}

.fields-list::-webkit-scrollbar-thumb,
.query-results::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb, rgba(150, 150, 150, 0.3));
  border-radius: 1.5px;
}

.fields-list::-webkit-scrollbar-thumb:hover,
.query-results::-webkit-scrollbar-thumb:hover {
  background: var(--scrollbar-thumb-hover, rgba(150, 150, 150, 0.5));
}
</style>
