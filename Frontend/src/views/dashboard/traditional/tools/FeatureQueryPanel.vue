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
      <div class="section-title">选择查询图层</div>
      <DropdownSelect 
        v-model="selectedLayerId"
        :options="layerOptions"
        placeholder="请选择要查询的图层"
      />
    </div>
    
    <!-- 要素查询 -->
    <div class="analysis-section">
      <div class="section-title">要素查询（关键字）</div>
      <TraditionalInputGroup 
        v-model="queryKeyword" 
        label="查询关键字" 
        placeholder="请输入查询关键字"
      />
    </div>

    <!-- 查询结果 -->
    <div class="analysis-section" v-if="queryResults.length > 0">
      <div class="section-title">查询结果 ({{ queryResults.length }}个要素)</div>
      <div class="query-results">
        <div 
          v-for="(feature, index) in queryResults" 
          :key="feature.getId?.() || index"
          class="result-item"
          @click="selectFeature(feature)"
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
        />
        <SecondaryButton 
          text="反选当前图层"
          @click="invertSelectedLayer"
        />
        <SecondaryButton 
          text="清空查询结果"
          variant="danger"
          @click="clearQueryResults"
        />
      </div>
    </div>
    
    <TipWindow v-if="selectedLayerId" :text="`已选择图层: ${getSelectedLayerName()}`" />
  </PanelWindow>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore.ts'
import { useFeatureQuery } from '@/composables/useFeatureQuery.ts'
import { useModeStateStore } from '@/stores/modeStateStore.ts'
import DropdownSelect from '@/components/UI/DropdownSelect.vue'
import TraditionalInputGroup from '@/components/UI/TraditionalInputGroup.vue'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import PanelWindow from '@/components/UI/PanelWindow.vue'
import TipWindow from '@/components/UI/TipWindow.vue'

const analysisStore = useAnalysisStore()
const featureQuery = useFeatureQuery()
const modeStateStore = useModeStateStore()

// 状态管理
const selectedLayerId = ref('')
const queryKeyword = ref('')
const queryResults = ref<any[]>([])

// 工具状态管理
const toolId = 'query'

// 保存工具状态
const saveToolState = () => {
  modeStateStore.saveToolState(toolId, {
    selectedLayerId: selectedLayerId.value,
    queryKeyword: queryKeyword.value,
    queryResults: queryResults.value
  })
}

// 恢复工具状态
const restoreToolState = () => {
  const state = modeStateStore.getToolState(toolId)
  if (state.selectedLayerId) {
    selectedLayerId.value = state.selectedLayerId
  }
  if (state.queryKeyword) {
    queryKeyword.value = state.queryKeyword
  }
  if (state.queryResults) {
    queryResults.value = state.queryResults
  }
}

// 组件生命周期管理
onMounted(() => {
  restoreToolState()
})

onUnmounted(() => {
  saveToolState()
})

// 监听状态变化，自动保存
watch([selectedLayerId, queryKeyword, queryResults], () => {
  saveToolState()
}, { deep: true })

// 图层选项
const layerOptions = computed(() => featureQuery.getLayerOptions())

// 获取选中图层名称
const getSelectedLayerName = () => {
  return featureQuery.getSelectedLayerName(selectedLayerId.value)
}

// 执行查询
const executeQuery = () => {
  if (!selectedLayerId.value || !queryKeyword.value.trim()) {
    analysisStore.setAnalysisStatus('请选择图层并输入查询关键字')
    return
  }
  
  try {
    const results = featureQuery.queryFeatures(selectedLayerId.value, queryKeyword.value)
    queryResults.value = results
    analysisStore.setAnalysisStatus(`查询完成，找到 ${results.length} 个要素`)
  } catch (error) {
    console.error('执行查询时出错:', error)
    analysisStore.setAnalysisStatus('查询执行失败，请重试')
  }
}

// 选择要素
const selectFeature = (feature: any) => {
  try {
    // 这里可以添加选择要素的逻辑
    // 例如在地图上高亮显示选中的要素
    console.log('选择要素:', feature)
    analysisStore.setAnalysisStatus('已选择要素并在地图上高亮显示')
  } catch (error) {
    console.error('选择要素时出错:', error)
    analysisStore.setAnalysisStatus('选择要素失败，请重试')
  }
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

// 反选当前图层
const invertSelectedLayer = () => {
  if (!selectedLayerId.value) {
    analysisStore.setAnalysisStatus('请先选择要操作的图层')
    return
  }
  
  try {
    featureQuery.invertSelectedLayer(selectedLayerId.value)
    analysisStore.setAnalysisStatus(`已反选图层 "${getSelectedLayerName()}"`)
  } catch (error) {
    console.error('反选图层时出错:', error)
    analysisStore.setAnalysisStatus('反选图层时出错，请重试')
  }
}

// 清空查询结果
const clearQueryResults = () => {
  queryResults.value = []
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
  /* 使用全局滚动条样式 */
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
</style>
