<template>
  <PanelWindow 
    :visible="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'buffer'"
    :embed="true"
    :width="'100%'"
    :height="'100%'"
    class="buffer-analysis-panel"
  >
    <!-- 选择分析区域和图层 -->
    <div class="analysis-section">
      <div class="section-title">选择分析区域</div>
      <div class="button-row">
        <SecondaryButton 
          text="选择分析区域"
          @click="selectFeatureFromMap"
          :active="isSelectingFeature"
        />
        <SecondaryButton 
          text="选择分析图层"
          @click="showLayerSelector = true"
          :active="showLayerSelector"
        />
      </div>
      
      <!-- 图层选择下拉框 -->
      <div v-if="showLayerSelector" class="layer-selector">
        <DropdownSelect 
          v-model="selectedAnalysisLayerId"
          :options="layerOptionsWithNone"
          placeholder="请选择分析图层"
        />
      </div>
      
      <!-- 显示选中要素信息 -->
      <div v-if="selectedFeatureInfo" class="feature-info">
        <div class="info-item">
          <span class="info-label">要素名称:</span>
          <span class="info-value">{{ selectedFeatureInfo?.name }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">坐标:</span>
          <span class="info-value">{{ selectedFeatureInfo?.coordinates }}</span>
        </div>
      </div>
      

    </div>
    
    <!-- 缓冲区参数 -->
    <div class="analysis-section">
      <div class="section-title">缓冲距离参数</div>
      <div class="form-item">
        <label class="form-label">距离 (米)</label>
        <TraditionalInputGroup
          v-model.number="bufferDistance" 
          type="number" 
          :min="1" 
          :step="10"
          placeholder="请输入缓冲距离"
          @input="onDistanceChange"
        />
      </div>
    </div>

    <!-- 分析操作 -->
    <div class="analysis-section">
      <SecondaryButton 
        text="执行缓冲区分析"
        @click="executeBufferAnalysis"
      />
    </div>
  </PanelWindow>
</template>

<script setup lang="ts">
import { watch, computed, ref } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useMapStore } from '@/stores/mapStore'
import { useBufferAnalysis } from '@/composables/useBufferAnalysis'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import TraditionalInputGroup from '@/components/UI/TraditionalInputGroup.vue'
import DropdownSelect from '@/components/UI/DropdownSelect.vue'
import PanelWindow from '@/components/UI/PanelWindow.vue'

const analysisStore = useAnalysisStore()

const {
  selectedFeature,
  bufferDistance,
  selectedAnalysisLayerId,
  selectedFeatureInfo,
  layerOptions,
  setSelectedAnalysisLayer,
  selectFeatureFromMap,
  clearMapSelection,
  clearAllSelections,
  executeBufferAnalysis
} = useBufferAnalysis()

// 图层选择相关状态
const showLayerSelector = ref(false)

// 包含"无"选项的图层选项
const layerOptionsWithNone = computed(() => {
  return [
    { value: '', label: '无', disabled: false },
    ...layerOptions.value
  ]
})

// 是否正在选择要素
const isSelectingFeature = computed(() => {
  return analysisStore.toolPanel.activeTool === 'buffer' && !selectedFeature.value
})



// 距离变化时的处理（可以添加实时预览等功能）
const onDistanceChange = () => {
  // 这里可以添加实时预览逻辑
  if (bufferDistance.value <= 0) {
    analysisStore.setAnalysisStatus('缓冲距离必须大于0')
  } else {
    analysisStore.setAnalysisStatus(`缓冲距离: ${bufferDistance.value}米`)
  }
}

// 监听工具面板变化，自动激活地图选择模式
watch(() => analysisStore.toolPanel.activeTool, (tool) => {
  if (tool === 'buffer') {
    // 当进入缓冲区分析时，自动激活地图选择模式
    selectFeatureFromMap()
  } else {
    // 当离开缓冲区分析时，清除选中状态和监听器
    clearAllSelections()
    clearMapSelection()
    showLayerSelector.value = false
  }
}, { immediate: true }) // 立即执行，确保初始状态正确

// 监听图层选择变化
watch(selectedAnalysisLayerId, (newLayerId) => {
  if (newLayerId) {
    setSelectedAnalysisLayer(newLayerId)
  }
})
</script>

<style scoped>
.buffer-analysis-panel {
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
  /* 禁用动画，防止主题切换闪烁 */
  animation: none !important;
  margin-bottom: 16px;
}

/* 保留fadeIn动画定义但不使用 */
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

.button-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.button-row .secondary-button {
  flex: 1;
}

.layer-selector {
  margin-bottom: 12px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 12px;
  color: var(--sub);
  font-weight: 500;
}

.feature-info {
  margin-top: 12px;
  padding: 16px;
  background: rgba(66, 165, 245, 0.08);
  border: 1px solid rgba(66, 165, 245, 0.2);
  border-radius: 12px;
  animation: fadeIn 0.3s ease-out;
}



.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-label {
  font-size: 11px;
  color: var(--sub);
  font-weight: 500;
}

.info-value {
  font-size: 11px;
  color: var(--accent);
  font-weight: 600;
}

</style>