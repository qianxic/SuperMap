<template>
  <div 
    v-show="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'buffer'"
    class="buffer-analysis-panel"
  >
    <!-- 缓冲区参数 -->
    <div class="section-title">缓冲距离(米)</div>
    
    <div class="form-item">
      <input 
        v-model.number="bufferDistance" 
        type="number" 
        min="1" 
        step="10"
        class="form-input"
        @input="onDistanceChange"
      />
    </div>

    <!-- 分析操作 -->
    <ButtonGroup :columns="1">
      <SecondaryButton 
        text="执行缓冲区分析"
        @click="executeBufferAnalysis"
      />
    </ButtonGroup>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useBufferAnalysis } from '@/composables/useBufferAnalysis'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import ButtonGroup from '@/components/UI/ButtonGroup.vue'

const analysisStore = useAnalysisStore()

const {
  selectedFeature,
  bufferDistance,
  featureInfo,
  isAnalyzing,
  setSelectedFeature,
  selectFeatureFromMap,
  clearMapSelection,
  executeBufferAnalysis
} = useBufferAnalysis()

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
    setSelectedFeature(null)
    clearMapSelection()
  }
}, { immediate: true }) // 立即执行，确保初始状态正确
</script>

<style scoped>
.buffer-analysis-panel {
  height: 100%;
  overflow-y: auto;
  padding: 0 4px;
}



.section-title {
  font-size: 12px;
  color: var(--sub);
  margin-bottom: 8px;
  font-weight: 500;
}





.parameter-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.form-item label {
  font-size: 12px;
  color: var(--sub);
  font-weight: 500;
}

.form-input {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text);
  font-size: 13px;
  outline: none;
  transition: all 0.2s ease;
}

.form-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(66, 165, 245, 0.2);
}

/* 隐藏数字输入框的上下箭头 */
.form-input[type="number"]::-webkit-outer-spin-button,
.form-input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.form-input[type="number"] {
  -moz-appearance: textfield;
  appearance: textfield;
}




</style>