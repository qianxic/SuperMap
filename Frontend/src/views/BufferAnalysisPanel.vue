<template>
  <PanelWindow 
    :visible="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'buffer'"
    :embed="true"
    :width="'100%'"
    :height="'100%'"
    class="buffer-analysis-panel"
  >
    <!-- 选择分析区域 -->
    <div class="analysis-section">
      <div class="section-title">选择分析区域</div>
      <SecondaryButton 
        text="选择分析区域"
        @click="selectFeatureFromMap"
        :active="isSelectingFeature"
      />
      
      <!-- 显示选中要素信息 -->
      <div v-if="featureInfo" class="feature-info">
        <div class="info-item">
          <span class="info-label">要素类型:</span>
          <span class="info-value">{{ featureInfo.type }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">要素名称:</span>
          <span class="info-value">{{ featureInfo.name }}</span>
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
import { watch, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useBufferAnalysis } from '@/composables/useBufferAnalysis'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import TraditionalInputGroup from '@/components/UI/TraditionalInputGroup.vue'
import PanelWindow from '@/components/UI/PanelWindow.vue'

const analysisStore = useAnalysisStore()

const {
  selectedFeature,
  bufferDistance,
  featureInfo,
  setSelectedFeature,
  selectFeatureFromMap,
  clearMapSelection,
  executeBufferAnalysis
} = useBufferAnalysis()

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
    setSelectedFeature(null)
    clearMapSelection()
  }
}, { immediate: true }) // 立即执行，确保初始状态正确
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