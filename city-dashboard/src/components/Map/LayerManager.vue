<template>
  <div 
    v-show="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'layer'"
    class="layer-manager-panel"
  >
    <!-- 地图图层管理 -->
    <div class="analysis-section">
      <div class="section-title">地图图层管理</div>
      <div class="layer-list">
        <div class="layer-item" v-for="item in mapLayers" :key="item.key">
          <div class="layer-info">
            <div class="layer-name">{{ item.name }}</div>
            <div class="layer-desc">{{ item.desc }}</div>
          </div>
          <div class="layer-operations">
            <SecondaryButton
              :text="item.visible ? '隐藏' : '显示'"
              @click="handleToggleVisibility(item)"
            />
            <SecondaryButton
              text="移除"
              variant="danger"
              @click="handleRemove(item)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useAnalysisStore } from '@/stores/analysisStore'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import { useLayerManager } from '@/composables/useLayerManager'

interface MapLayerItem {
  key: string;
  name: string;
  desc: string;
  visible: boolean;
  isVector?: boolean; // 标识是否为矢量图层
}


const mapStore = useMapStore()
const analysisStore = useAnalysisStore()
const { toggleLayerVisibility, removeLayer } = useLayerManager()

const mapLayers = computed<MapLayerItem[]>(() => {
  const items: MapLayerItem[] = []
  mapStore.vectorLayers.forEach(vl => {
    items.push({
      key: vl.id,
      name: vl.name,
      desc: '矢量数据',
      visible: vl.layer.getVisible(),
      isVector: true
    });
  });
  return items
})

const handleToggleVisibility = (item: MapLayerItem) => {
  toggleLayerVisibility(item.key)
}

const handleRemove = (item: MapLayerItem) => {
  if (confirm(`确定要移除图层"${item.name}"吗？此操作不可撤销。`)) {
    removeLayer(item.key)
  }
}



</script>

<style scoped>
.layer-manager-panel {
  height: 100%;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.analysis-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px;
  transition: all 0.3s ease;
  animation: fadeIn 0.3s ease-out;
}

.analysis-section:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(66, 165, 245, 0.3);
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
.layer-list { display: flex; flex-direction: column; gap: 8px; }
.layer-list.empty { color: var(--sub); font-size: 12px; padding: 12px; background: rgba(255,255,255,0.04); border-radius: 12px; }

.layer-container { display: flex; flex-direction: column; }

.layer-item {
  display: flex; align-items: center; justify-content: space-between;
  background: rgba(255,255,255,0.06);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px 14px;
  transition: all 0.3s ease;
  animation: fadeIn 0.3s ease-out;
}
.layer-info { display: flex; flex-direction: column; }
.layer-name { font-size: 13px; color: var(--text); font-weight: 500; }
.layer-desc { font-size: 11px; color: var(--sub); margin-top: 2px; }
.layer-operations { display: flex; gap: 6px; }

/* 要素列表样式 */
.feature-list {
  margin-top: 8px;
  margin-left: 12px;
  padding-left: 12px;
  border-left: 2px solid var(--border);
}

.feature-header {
  font-size: 11px;
  color: var(--sub);
  margin-bottom: 6px;
  font-weight: 500;
}

.feature-empty {
  font-size: 11px;
  color: var(--sub);
  font-style: italic;
}

.feature-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.feature-item {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(66,165,245,0.15);
  border-radius: 12px;
  padding: 10px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
  cursor: pointer;
  animation: fadeIn 0.3s ease-out;
}

.feature-item:hover {
  background: rgba(255,255,255,0.08);
  border-color: rgba(66,165,245,0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(66,165,245,0.2);
}



.feature-content {
  flex: 1;
  min-width: 0;
}

.feature-ops {
  margin-left: 8px;
  flex-shrink: 0;
  display: flex;
  gap: 4px;
}

.feature-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2px;
}

.feature-name {
  font-size: 12px;
  color: var(--text);
}

.feature-type {
  font-size: 10px;
  color: var(--accent);
  background: rgba(66,165,245,0.15);
  padding: 2px 8px;
  border-radius: 8px;
}

.feature-props {
  font-size: 10px;
  color: var(--sub);
  line-height: 1.3;
}
</style>


