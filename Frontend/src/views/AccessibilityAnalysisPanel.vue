<template>
  <PanelWindow 
    :visible="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'gotowhere'"
    :embed="true"
    :width="'100%'"
    :height="'100%'"
    class="accessibility-analysis-panel"
  >
    <!-- 选择分析中心点 -->
    <div class="analysis-section">
      <div class="section-title">选择分析中心点</div>
      <SecondaryButton 
        text="选择分析位置"
        @click="selectCenterPoint"
        :active="isSelectingCenterPoint"
      />
      
      <!-- 显示中心点信息 -->
      <div v-if="centerPointInfo" class="feature-info">
        <div class="info-item">
          <span class="info-label">中心点:</span>
          <span class="info-value">{{ centerPointInfo.name }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">坐标:</span>
          <span class="info-value">{{ centerPointInfo.coordinates }}</span>
        </div>
      </div>
    </div>

    <!-- 可达性参数 -->
    <div class="analysis-section">
      <div class="section-title">可达性参数</div>
      <div class="form-item">
        <label class="form-label">最大距离 (米)</label>
        <TraditionalInputGroup
          v-model.number="maxDistance" 
          type="number" 
          :min="100" 
          :step="100"
          placeholder="请输入最大可达距离"
        />
      </div>
      <div class="form-item">
        <label class="form-label">交通方式</label>
        <DropdownSelect 
          v-model="transportMode" 
          placeholder="请选择交通方式"
          :options="[
            { value: 'walking', label: '步行' },
            { value: 'cycling', label: '骑行' },
            { value: 'driving', label: '驾车' },
            { value: 'transit', label: '公交' }
          ]"
        />
      </div>

    </div>

    <!-- 分析操作 -->
    <div class="analysis-section">
      <SecondaryButton 
        text="执行可达性分析"
        @click="executeAccessibilityAnalysis"
      />
      
      <!-- 显示分析结果 -->
      <div v-if="analysisResult" class="result-section">
        <div class="result-title">可达性分析结果</div>
        <div class="result-item">
          <span class="result-label">覆盖面积:</span>
          <span class="result-value">{{ analysisResult.coverageArea }} 平方公里</span>
        </div>
        <div class="result-item">
          <span class="result-label">可达点数量:</span>
          <span class="result-value">{{ analysisResult.reachablePoints }} 个</span>
        </div>
        <div class="result-item">
          <span class="result-label">平均距离:</span>
          <span class="result-value">{{ analysisResult.averageDistance }} 米</span>
        </div>
        <div class="result-item">
          <span class="result-label">最大可达距离:</span>
          <span class="result-value">{{ analysisResult.maxReachDistance }} 米</span>
        </div>
      </div>
    </div>
  </PanelWindow>
</template>

<script setup lang="ts">
import { watch, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useAccessibilityAnalysis } from '@/composables/useAccessibilityAnalysis'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import TraditionalInputGroup from '@/components/UI/TraditionalInputGroup.vue'
import DropdownSelect from '@/components/UI/DropdownSelect.vue'
import PanelWindow from '@/components/UI/PanelWindow.vue'
import TipWindow from '@/components/UI/TipWindow.vue'

const analysisStore = useAnalysisStore()

const {
  centerPointInfo,
  maxDistance,
  transportMode,
  analysisResult,
  selectCenterPoint,
  clearSelection,
  executeAccessibilityAnalysis
} = useAccessibilityAnalysis()

// 是否正在选择中心点
const isSelectingCenterPoint = computed(() => {
  return analysisStore.toolPanel.activeTool === 'gotowhere' && !centerPointInfo.value
})

// 监听工具面板变化
watch(() => analysisStore.toolPanel.activeTool, (tool) => {
  if (tool === 'gotowhere') {
    // 当进入可达性分析时，自动激活中心点选择模式
    selectCenterPoint()
  } else {
    // 当离开可达性分析时，清除选中状态
    clearSelection()
  }
})
</script>

<style scoped>
.accessibility-analysis-panel {
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



.result-section {
  margin-top: 16px;
  padding: 16px;
  background: rgba(40, 167, 69, 0.05);
  border: 1px solid rgba(40, 167, 69, 0.2);
  border-radius: 8px;
}

.result-title {
  font-size: 14px;
  font-weight: 600;
  color: #28a745;
  margin-bottom: 12px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.result-item:last-child {
  margin-bottom: 0;
}

.result-label {
  font-size: 13px;
  color: var(--sub);
  font-weight: 500;
}

.result-value {
  font-size: 13px;
  color: var(--text);
  font-weight: 600;
}

.accessible {
  color: #28a745;
}

.not-accessible {
  color: #dc3545;
}
</style>
