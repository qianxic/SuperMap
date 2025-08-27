<template>
  <PanelWindow 
    :visible="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'distance'"
    :embed="true"
    :width="'100%'"
    :height="'100%'"
    class="distance-analysis-panel"
  >
    <!-- 选择起点和终点 -->
    <div class="analysis-section">
      <div class="section-title">选择起点和终点</div>
      <div class="point-selection-container">
        <div class="point-selection-item">
          <SecondaryButton 
            text="选择起始点"
            @click="selectStartPoint"
            :active="isSelectingStartPoint"
          />
          
          <!-- 显示起始点信息 -->
          <div v-if="startPointInfo" class="feature-info">
            <div class="info-item">
              <span class="info-label">起始点:</span>
              <span class="info-value">{{ startPointInfo.name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">坐标:</span>
              <span class="info-value">{{ startPointInfo.coordinates }}</span>
            </div>
          </div>
        </div>
        
        <div class="point-selection-item">
          <SecondaryButton 
            text="选择目标点"
            @click="selectEndPoint"
            :active="isSelectingEndPoint ?? undefined"
          />
          
          <!-- 显示目标点信息 -->
          <div v-if="endPointInfo" class="feature-info">
            <div class="info-item">
              <span class="info-label">目标点:</span>
              <span class="info-value">{{ endPointInfo.name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">坐标:</span>
              <span class="info-value">{{ endPointInfo.coordinates }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 路径参数 -->
    <div class="analysis-section">
      <div class="section-title">路径参数</div>
      <div class="form-item">
        <label class="form-label">路径类型</label>
        <DropdownSelect 
          v-model="pathType" 
          placeholder="请选择路径类型"
          :options="[
            { value: 'shortest', label: '最短路径' },
            { value: 'fastest', label: '最快路径' },
            { value: 'scenic', label: '风景路径' }
          ]"
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
        text="计算最优路径"
        @click="executePathAnalysis"
      />
      
      <!-- 显示分析结果 -->
      <div v-if="analysisResult" class="result-section">
        <div class="result-title">路径分析结果</div>
        <div class="result-item">
          <span class="result-label">路径长度:</span>
          <span class="result-value">{{ analysisResult.distance }} 米</span>
        </div>
        <div class="result-item">
          <span class="result-label">预计时间:</span>
          <span class="result-value">{{ analysisResult.duration }} 分钟</span>
        </div>
        <div class="result-item">
          <span class="result-label">路径类型:</span>
          <span class="result-value">{{ analysisResult.pathType }}</span>
        </div>
      </div>
    </div>
  </PanelWindow>
</template>

<script setup lang="ts">
import { watch, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useDistanceAnalysis } from '@/composables/useDistanceAnalysis'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import DropdownSelect from '@/components/UI/DropdownSelect.vue'
import PanelWindow from '@/components/UI/PanelWindow.vue'

const analysisStore = useAnalysisStore()

const {
  startPointInfo,
  endPointInfo,
  pathType,
  transportMode,
  analysisResult,
  selectStartPoint,
  selectEndPoint,
  clearSelection,
  executePathAnalysis
} = useDistanceAnalysis()

// 是否正在选择起始点
const isSelectingStartPoint = computed(() => {
  return analysisStore.toolPanel.activeTool === 'distance' && !startPointInfo.value
})

// 是否正在选择目标点
const isSelectingEndPoint = computed(() => {
  return analysisStore.toolPanel.activeTool === 'distance' && startPointInfo.value && !endPointInfo.value
})

// 监听工具面板变化
watch(() => analysisStore.toolPanel.activeTool, (tool) => {
  if (tool === 'distance') {
    // 当进入路径分析时，自动激活起始点选择模式
    selectStartPoint()
  } else {
    // 当离开路径分析时，清除选中状态
    clearSelection()
  }
})
</script>

<style scoped>
.distance-analysis-panel {
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

.point-selection-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.point-selection-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
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
  color: var(--text);
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
</style>
