<template>
  <div 
    v-show="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'layer'"
    class="layer-manager-panel"
  >
    <div class="layer-manager-content">
      <div class="section">
        <div class="section-title">地图图层</div>
        <div class="layer-list">
          <div class="layer-item" v-for="item in mapLayers" :key="item.key">
            <div class="meta">
              <div class="name">{{ item.name }}</div>
              <div class="sub">{{ item.desc }}</div>
            </div>
            <div class="ops">
              <SecondaryButton
                :text="item.visible ? '隐藏' : '显示'"
                @click="handleToggleVisibility({ kind: 'map-layer', item })"
              />
              <SecondaryButton
                text="移除"
                variant="danger"
                @click="handleRemove({ kind: 'map-layer', item })"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-title">绘制图层 ({{ drawLayers.length }})</div>
        <div class="layer-list empty" v-if="!drawLayers.length">暂无绘制图层</div>
        <div class="layer-list" v-else>
          <div v-for="dl in drawLayers" :key="dl.id" class="layer-container">
            <div class="layer-item">
              <div class="meta">
                <div class="name">{{ dl.name }}</div>
                <div class="sub">要素数量：{{ dl.features?.length ?? 0 }}</div>
              </div>
              <div class="ops">
                <SecondaryButton
                  :text="expandedLayerId === dl.id ? '收起' : '详情'"
                  @click="toggleExpanded(dl.id)"
                />
                <SecondaryButton
                  :text="dl.visible ? '隐藏' : '显示'"
                  @click="handleToggleVisibility({ kind: 'draw-layer', layer: dl })"
                />
                <SecondaryButton
                  text="移除"
                  variant="danger"
                  @click="handleRemove({ kind: 'draw-layer', layer: dl })"
                />
              </div>
            </div>
            
            <!-- 展开的要素列表 -->
            <div v-if="expandedLayerId === dl.id" class="feature-list">
              <div class="feature-header">要素列表</div>
              <div v-if="!dl.features?.length" class="feature-empty">此图层暂无要素</div>
              <div v-else class="feature-items">
                <div v-for="feature in dl.features" :key="feature.id" class="feature-item">
                  <div class="feature-content">
                    <div class="feature-meta">
                      <div class="feature-name">{{ feature.name }}</div>
                      <div class="feature-type">{{ getFeatureTypeLabel(feature.type) }}</div>
                    </div>
                    <div class="feature-props">
                      <span v-if="feature.type === 'point'">
                        经度: {{ feature.longitude?.toFixed(6) }}, 纬度: {{ feature.latitude?.toFixed(6) }}
                      </span>
                      <span v-else-if="feature.type === 'line'">
                        长度: {{ feature.length?.toFixed(2) }}米
                      </span>
                      <span v-else-if="feature.type === 'polygon'">
                        面积: {{ feature.area?.toFixed(2) }}平方米
                      </span>
                      <span v-else-if="feature.type === 'buffer'">
                        缓冲距离: {{ feature.bufferDistance }}米, 面积: {{ feature.area?.toFixed(2) }}平方米
                      </span>
                    </div>
                  </div>
                  <!-- 移除要素操作按钮 -->
                  <div class="feature-ops">
                    <SecondaryButton
                      :text="feature.visible ? '隐藏' : '显示'"
                      @click.stop="handleToggleVisibility({ kind: 'feature', layerId: dl.id, feature })"
                    />
                    <SecondaryButton
                      text="移除"
                      variant="danger"
                      @click.stop="handleRemove({ kind: 'feature', layerId: dl.id, feature })"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useLayerStore } from '@/stores/layerStore'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import { useLayerManager } from '@/composables/useLayerManager'
import type { MapLayer, FeatureInfo } from '@/types/map'

// Define a more specific type for your drawn layers, assuming it has a features array
interface DrawnLayer extends MapLayer {
  features?: FeatureInfo[];
}
interface MapLayerItem {
  key: string;
  name: string;
  desc: string;
  visible: boolean;
}
type Payload = {
  kind: 'map-layer';
  item: MapLayerItem;
} | {
  kind: 'draw-layer';
  layer: DrawnLayer;
} | {
  kind: 'feature';
  layerId: string;
  feature: FeatureInfo;
};


const mapStore = useMapStore()
const analysisStore = useAnalysisStore()
const layerStore = useLayerStore()
const {
  toggleDrawLayerVisibility,
  removeDrawLayer,
  removeFeature: removeFeatureFromLayer,
  toggleFeatureVisibility
} = useLayerManager()

const expandedLayerId = ref<string | null>(null)

const mapLayers = computed<MapLayerItem[]>(() => {
  const items: MapLayerItem[] = []
  if (mapStore.baseLayer) {
    items.push({ 
      key: 'base', 
      name: '底图图层', 
      desc: 'TileSuperMapRest', 
      visible: mapStore.baseLayer.getVisible?.() ?? true 
    })
  }
  return items
})

const drawLayers = computed<DrawnLayer[]>(() => {
  return layerStore.managedDrawLayers as DrawnLayer[]
})

const getFeatureTypeLabel = (type: string) => {
  const typeMap: Record<string, string> = { point: '点', line: '线', polygon: '面', buffer: '缓冲区' }
  return typeMap[type] || type
}

const toggleExpanded = (layerId: string) => {
  expandedLayerId.value = expandedLayerId.value === layerId ? null : layerId
}

const handleToggleVisibility = (payload: Payload) => {
  switch (payload.kind) {
    case 'map-layer': {
      const layer = getMapLayerById(payload.item.key)
      if (layer && layer.setVisible) {
        const newVisible = !payload.item.visible
        layer.setVisible(newVisible)
      }
      break
    }
    case 'draw-layer': {
      toggleDrawLayerVisibility(payload.layer.id)
      break
    }
    case 'feature': {
      toggleFeatureVisibility(payload.layerId, payload.feature.id)
      break
    }
  }
}

const handleRemove = (payload: Payload) => {
  switch (payload.kind) {
    case 'map-layer': {
      if (confirm(`确定要移除图层"${payload.item.name}"吗？此操作不可撤销。`)) {
        const layer = getMapLayerById(payload.item.key)
        if (layer && mapStore.map) {
          mapStore.map.removeLayer(layer)
        }
      }
      break
    }
    case 'draw-layer': {
      if (confirm(`确定要移除图层"${payload.layer.name}"吗？此操作不可撤销。`)) {
        const ok = removeDrawLayer(payload.layer.id)
        if (ok && expandedLayerId.value === payload.layer.id) {
          expandedLayerId.value = null
        }
      }
      break
    }
    case 'feature': {
      const displayName = payload.feature.name || payload.feature.id
      if (confirm(`确定要移除要素"${displayName}"吗？此操作不可撤销。`)) {
        removeFeatureFromLayer(payload.layerId, payload.feature.id)
      }
      break
    }
  }
}

const getMapLayerById = (key: string): any | null => {
  switch (key) {
    case 'base':
      return mapStore.baseLayer
    case 'hover':
      return mapStore.hoverLayer
    case 'select':
      return mapStore.selectLayer
    default:
      return null
  }
}

</script>

<style scoped>
/* 外层容器添加滚动支持 */
.layer-manager-content {
  max-height: 70vh;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 4px; /* 为滚动条留出空间 */
}

/* 自定义滚动条样式 */
.layer-manager-content::-webkit-scrollbar {
  width: 6px;
}

.layer-manager-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.layer-manager-content::-webkit-scrollbar-thumb {
  background: rgba(66, 165, 245, 0.4);
  border-radius: 3px;
}

.layer-manager-content::-webkit-scrollbar-thumb:hover {
  background: rgba(66, 165, 245, 0.6);
}

.section { margin-bottom: 12px; }
.section-title {
  font-size: 12px;
  color: var(--sub);
  margin: 4px 0 8px;
}
.layer-list { display: flex; flex-direction: column; gap: 8px; }
.layer-list.empty { color: var(--sub); font-size: 12px; padding: 8px; background: rgba(255,255,255,0.04); border-radius: 6px; }

.layer-container { display: flex; flex-direction: column; }

.layer-item {
  display: flex; align-items: center; justify-content: space-between;
  background: rgba(255,255,255,0.06);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 10px;
}
.meta { display: flex; flex-direction: column; }
.name { font-size: 13px; color: var(--text); }
.sub { font-size: 11px; color: var(--sub); margin-top: 2px; }
.ops { display: flex; gap: 6px; }

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
  border-radius: 6px;
  padding: 6px 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
  cursor: pointer;
}

.feature-item:hover {
  background: rgba(255,255,255,0.08);
  border-color: rgba(66,165,245,0.3);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(66,165,245,0.15);
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
  padding: 1px 4px;
  border-radius: 3px;
}

.feature-props {
  font-size: 10px;
  color: var(--sub);
  line-height: 1.3;
}
</style>


