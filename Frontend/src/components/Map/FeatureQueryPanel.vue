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

    <!-- 查询操作 -->
    <div class="analysis-section">
      <div class="section-title">查询操作</div>
      <div class="button-column">
        <SecondaryButton 
          text="清空当前选中图层"
          @click="clearSelectedLayer"
        />
        <SecondaryButton 
          text="反选当前图层"
          @click="invertSelectedLayer"
        />
      </div>
    </div>
    
    <TipWindow v-if="selectedLayerId" :text="`已选择图层: ${getSelectedLayerName()}`" />
  </PanelWindow>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore.ts'
import { useMapStore } from '@/stores/mapStore.ts'
import { useFeatureQuery } from '@/composables/useFeatureQuery.ts'
import DropdownSelect from '@/components/UI/DropdownSelect.vue'
import TraditionalInputGroup from '@/components/UI/TraditionalInputGroup.vue'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import PanelWindow from '@/components/UI/PanelWindow.vue'
import TipWindow from '@/components/UI/TipWindow.vue'

const analysisStore = useAnalysisStore()
const mapStore = useMapStore()
const featureQuery = useFeatureQuery()

// 状态管理
const selectedLayerId = ref('')
const queryKeyword = ref('')

// 图层选项
const layerOptions = computed(() => featureQuery.getLayerOptions())

// 获取选中图层名称
const getSelectedLayerName = () => {
  return featureQuery.getSelectedLayerName(selectedLayerId.value)
}

// 清空当前选中图层
const clearSelectedLayer = () => {
  if (!selectedLayerId.value) {
    analysisStore.setAnalysisStatus('请先选择要操作的图层')
    return
  }
  
  try {
    featureQuery.clearSelectedLayer(selectedLayerId.value)
    analysisStore.setAnalysisStatus(`已清空图层 "${getSelectedLayerName()}" 的选中状态`)
  } catch (error) {
    console.error('清空选中图层时出错:', error)
    analysisStore.setAnalysisStatus('清空选中图层时出错，请重试')
  }
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


</style>
