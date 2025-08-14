<template>
  <PanelWindow 
    :visible="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'bianji'"
    :embed="true"
    :width="'100%'"
    :height="'100%'"
    class="edit-tools-panel"
  >
    <!-- 图层选择 -->
    <div class="analysis-section">
      <div class="section-title">在地图中选择要编辑的要素</div>
      <!-- 显示选中要素信息 -->
      <div v-if="selectedFeatureInfo.length" class="feature-info">
        <div 
          v-for="(item, index) in selectedFeatureInfo" 
          :key="index"
          class="info-item"
        >
          <span class="info-label">{{ item.label }}</span>
          <span class="info-value">{{ item.value }}</span>
        </div>
      </div>
      <div v-else class="tip">
        请在地图上点击一个要素来开始编辑
      </div>
    </div>
      
    <!-- 编辑操作 -->
    <div class="analysis-section">
      <div class="section-title">编辑操作</div>
      <div class="button-column">
        <SecondaryButton 
          text="回退上一步编辑"
          @click="undoEdit"
        />
        <SecondaryButton 
          text="完成编辑"
          @click="finishEdit"
        />
      </div>
    </div>
    
  </PanelWindow>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore.ts'
import { useMapStore } from '@/stores/mapStore.ts'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import PanelWindow from '@/components/UI/PanelWindow.vue'

const analysisStore = useAnalysisStore()
const mapStore = useMapStore()

// 状态管理
const editHistory = ref<any[]>([]) // 编辑历史记录

// 选中要素的详细信息
const selectedFeatureInfo = computed(() => {
  const feature = mapStore.selectedFeature
  if (!feature) return []
  
  const properties = feature.getProperties()
  const info: { label: string, value: any }[] = []
  
  const fieldsToShow: { key: string, label: string }[] = [
    { key: 'PAC_1', label: '邮编' },
    { key: 'NAME_1', label: '区名称' }
  ]

  fieldsToShow.forEach(field => {
    if (properties[field.key]) {
      info.push({ label: field.label, value: properties[field.key] })
    }
  })
  
  return info
})


// 回退编辑
const undoEdit = () => {
  if (editHistory.value.length > 0) {
    editHistory.value.pop()
    analysisStore.setAnalysisStatus('已回退上一步编辑操作')
  } else {
    analysisStore.setAnalysisStatus('没有可回退的编辑操作')
  }
}

// 完成编辑
const finishEdit = () => {
  if (!analysisStore.drawMode) {
    analysisStore.setAnalysisStatus('请先选择编辑模式')
    return
  }
  
  try {
    // 这里应该保存编辑结果
    analysisStore.setAnalysisStatus(`图层编辑已完成`)
    
    // 清理状态
    editHistory.value = []
    
  } catch (error) {
    console.error('完成编辑时出错:', error)
    analysisStore.setAnalysisStatus('完成编辑时出错，请重试')
  }
}

// 监听编辑工具关闭
watch(() => analysisStore.toolPanel?.activeTool, (tool) => {
  if (tool !== 'bianji') {
    analysisStore.setDrawMode('')
    editHistory.value = []
  }
})

defineExpose({
})
</script>

<style scoped>
.edit-tools-panel {
  height: 100%;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  /* 使用全局滚动条样式 */
}

.analysis-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px;
  transition: all 0.3s ease;
  animation: fadeIn 0.3s ease-out;
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
  font-size: 12px;
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
  display: flex;
  flex-direction: column;
  gap: 8px;
  animation: fadeIn 0.3s ease-out;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.info-label {
  color: var(--sub);
  min-width: 72px;
}

.info-value {
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.form-select {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--border);
  border-radius: 12px;
  color: var(--text);
  font-size: 13px;
  outline: none;
  transition: all 0.3s ease;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2366b3ff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6,9 12,15 18,9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px;
  padding-right: 40px;
}

.form-select:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(66, 165, 245, 0.2);
}

/* 下拉选项的圆角样式 */
.form-select option {
  background: var(--panel);
  color: var(--text);
  padding: 10px 16px;
  border-radius: 8px;
  margin: 2px 0;
}

.button-column {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.layer-info {
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

.tip { 
  margin-top: 8px; 
  font-size: 12px; 
  color: var(--sub);
  padding: 12px;
  background: rgba(66,165,245,0.08);
  border-radius: 12px;
  border-left: 4px solid var(--accent);
  animation: fadeIn 0.3s ease-out;
}
</style>
