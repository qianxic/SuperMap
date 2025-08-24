<template>
  <PanelWindow 
    :visible="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'bianji'"
    :embed="true"
    :width="'100%'"
    :height="'100%'"
    class="edit-tools-panel"
  >
    <!-- 已选中要素列表 -->
    <div class="analysis-section">
      <div class="section-title">已选中要素列表 ({{ selectedFeatures.length }})</div>
      <div class="layer-list" v-if="selectedFeatures.length > 0">
        <div 
          v-for="(feature, index) in selectedFeatures" 
          :key="feature.id || index"
          class="layer-item"
          :class="{ 'active': selectedFeatureIndex === index }"
          @click="handleSelectFeature(index)"
        >
          <div class="layer-info">
            <div class="layer-name">要素 {{ index + 1 }} - {{ getFeatureType(feature) }}</div>
            <div class="layer-desc">{{ feature.layerName || '未知图层' }} | {{ getFeatureGeometryInfo(feature) }}</div>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <div class="empty-text">未选中要素</div>
        <div class="empty-desc">请在地图上框选要素</div>
      </div>
    </div>

    <!-- 要素详细信息 -->
    <div class="analysis-section" v-if="selectedFeatureIndex !== -1 && selectedFeatures[selectedFeatureIndex]">
      <div class="section-title">要素详细信息</div>
      <div class="feature-details">
        <div 
          v-for="(item, index) in selectedFeatureInfo" 
          :key="index"
          class="info-item"
        >
          <span class="info-label">{{ item.label }}</span>
          <span class="info-value">{{ item.value }}</span>
        </div>
      </div>
    </div>

    <!-- 选择操作 -->
    <div class="analysis-section">
      <div class="section-title">选择操作</div>
      <div class="button-column">
        <SecondaryButton 
          text="清除选择"
          variant="danger"
          @click="clearSelection"
        />
      </div>
    </div>

    <!-- 提示信息 -->
    <div class="analysis-section">
      <TipWindow text="在地图上按住左键拖拽鼠标进行框选要素，框选完成后松开左键" />
    </div>
    
  </PanelWindow>
</template>

<script setup lang="ts">
import { watch, computed, onMounted, onUnmounted } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore.ts'
import { useMapStore } from '@/stores/mapStore.ts'
import { useFeatureSelection } from '@/composables/useFeatureSelection'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import PanelWindow from '@/components/UI/PanelWindow.vue'
import TipWindow from '@/components/UI/TipWindow.vue'

const analysisStore = useAnalysisStore()
const mapStore = useMapStore()

// 使用要素选择 hook
const {
  selectedFeatures,
  selectedFeatureIndex,
  clearSelection,
  handleSelectFeature,
  setupSelectionInteractions,
  clearSelectionInteractions,
  getFeatureType,
  getFeatureCoords,
  getFeatureGeometryInfo
} = useFeatureSelection()

// 选中要素的详细信息
const selectedFeatureInfo = computed(() => {
  if (selectedFeatureIndex.value === -1 || !selectedFeatures.value[selectedFeatureIndex.value]) {
    return []
  }
  
  const feature = selectedFeatures.value[selectedFeatureIndex.value]
  const properties = feature.properties || feature.getProperties?.() || {}
  
  const info = [
    { label: '要素ID', value: feature.getId?.() || feature.id || '无' },
    { label: '图层名称', value: feature.layerName || '未知图层' },
    { label: '几何类型', value: getFeatureType(feature) },
    { label: '几何信息', value: getFeatureCoords(feature) }
  ]
  
  // 添加属性字段计数
  const attributeCount = Object.keys(properties).filter(key => key !== 'geometry').length
  info.push({ label: '属性字段数', value: `${attributeCount}个` })
  
  // 添加所有属性字段，包括空值 - 与useMap中的显示逻辑一致
  Object.keys(properties).forEach(key => {
    if (key !== 'geometry') {
      const value = properties[key]
      const displayValue = value !== undefined && value !== null ? value : '(空值)'
      info.push({ label: key, value: displayValue })
    }
  })
  
  return info
})

// 监听编辑工具关闭 - 不清除已选择的要素，只清除交互
watch(() => analysisStore.toolPanel?.activeTool, (tool) => {
  if (tool !== 'bianji') {
    // 只清除交互，不清除已选择的要素
    clearSelectionInteractions()
  }
})

// 组件挂载时设置交互
onMounted(() => {
  setupSelectionInteractions()
})

// 组件卸载时清理 - 只清除交互，保持要素选择
onUnmounted(() => {
  clearSelectionInteractions()
})

defineExpose({
  selectedFeatures,
  selectedFeatureIndex,
  clearSelection
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

.selection-info {
  margin-bottom: 12px;
  padding: 12px;
  background: var(--btn-secondary-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  animation: fadeIn 0.3s ease-out;
}

.info-text {
  font-size: 12px;
  color: var(--text);
  margin-bottom: 4px;
}

.info-text:last-child {
  margin-bottom: 0;
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  color: var(--sub);
}

.empty-text {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text);
}

.empty-desc {
  font-size: 14px;
  opacity: 0.8;
}

.feature-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 4px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  padding: 6px 0;
  border-bottom: 1px solid var(--border);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  color: var(--sub);
  min-width: 80px;
  font-weight: 500;
}

.info-value {
  color: var(--text);
  text-align: right;
  word-break: break-word;
  max-width: 200px;
  font-size: 11px;
}
</style>
