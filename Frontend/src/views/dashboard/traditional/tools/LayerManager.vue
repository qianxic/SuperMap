<template>
  <PanelWindow 
    :visible="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'layer'"
    :embed="true"
    :width="'100%'"
    :height="'100%'"
    class="layer-manager-panel"
  >
    <!-- 地图图层管理 -->
    <div class="analysis-section">
      <div class="section-title">地图图层管理</div>
      <div class="layer-list-container">
        <div class="layer-list" :class="{ empty: groupedLayers.length === 0 }">
          <div v-if="groupedLayers.length === 0" class="empty-state">
            <div class="empty-icon">🗺️</div>
            <div class="empty-text">暂无图层加载</div>
            <div class="empty-desc">地图图层正在加载中，请稍候...</div>
          </div>
          
          <!-- 按来源分类的图层组 -->
          <div class="layer-group" v-for="group in groupedLayers" :key="group.source">
            <div class="group-header" @click="toggleGroupCollapse(group.source)">
              <div class="group-title">
                <span class="collapse-icon" :class="{ collapsed: collapsedGroups[group.source] }">
                  ▼
                </span>
                {{ getSourceDisplayName(group.source) }}
                <span class="layer-count">({{ group.items.length }})</span>
              </div>
            </div>
            
            <!-- 可折叠的图层列表 -->
            <div class="group-items" v-show="!collapsedGroups[group.source]">
              <div class="layer-item" v-for="item in group.items" :key="item.key">
                <div class="layer-info">
                  <div class="layer-name">{{ item.displayName }}</div>
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
      </div>
    </div>
  </PanelWindow>
  
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useAnalysisStore } from '@/stores/analysisStore'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import { useLayerManager } from '@/composables/useLayerManager'
import PanelWindow from '@/components/UI/PanelWindow.vue'

interface MapLayerItem {
  key: string;
  name: string;
  displayName: string;
  desc: string;
  visible: boolean;
  source: string;
}

const mapStore = useMapStore()
const analysisStore = useAnalysisStore()
const { toggleLayerVisibility, removeLayer } = useLayerManager()

// 折叠状态管理
const collapsedGroups = ref<Record<string, boolean>>({
  supermap: false,
  local: false,
  external: false
})

// 切换分组折叠状态
const toggleGroupCollapse = (source: string) => {
  collapsedGroups.value[source] = !collapsedGroups.value[source]
}

// 获取来源显示名称
const getSourceDisplayName = (source: string): string => {
  const sourceNames: Record<string, string> = {
    supermap: 'SuperMap 服务图层',
    local: '本地绘制图层',
    external: '外部图层'
  }
  return sourceNames[source] || source
}

// 按来源分组的图层
const groupedLayers = computed(() => {
  const allLayers = mapStore.vectorLayers
  
  // 按来源分组
  const groupedBySource: Record<string, MapLayerItem[]> = {
    supermap: [],
    local: [],
    external: []
  }
  
  allLayers.forEach(vl => {
    const source = vl.source || 'external'
    const item: MapLayerItem = {
      key: vl.id,
      name: vl.name,
      displayName: vl.name,
      desc: inferDesc(vl.name, vl.type),
      visible: vl.layer.getVisible(),
      source: source
    }
    
    // 特殊处理本地图层的显示名称
    if (source === 'local') {
      const layerName = vl.layer.get('layerName') || vl.name
      const sourceType = vl.layer.get('sourceType') || 'draw'
      const sourceTypeNames: Record<string, string> = {
        draw: '绘制',
        area: '区域选择',
        query: '属性查询'
      }
      item.displayName = `${sourceTypeNames[sourceType] || '本地'}: ${layerName}`
      item.desc = '用户创建的图层'
    }
    
    if (groupedBySource[source]) {
      groupedBySource[source].push(item)
    } else {
      groupedBySource[source] = [item]
    }
  })
  
  // 转换为数组格式，只返回有图层的分组
  return Object.entries(groupedBySource)
    .filter(([_, items]) => items.length > 0)
    .map(([source, items]) => ({
      source,
      items
    }))
})

function inferDesc(name: string, type: string): string {
  if (type === 'raster') return '栅格数据 (DEM)'
  if (name.includes('点')) return '点要素'
  if (name.includes('线')) return '线要素'
  if (name.includes('面')) return '面要素'
  return '矢量数据'
}

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
  /* 确保内容可以滚动 */
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.layer-list-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
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

.layer-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
  /* 确保滚动条样式正确 */
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}

.layer-list::-webkit-scrollbar {
  width: 6px;
}

.layer-list::-webkit-scrollbar-track {
  background: transparent;
}

.layer-list::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 3px;
}

.layer-list::-webkit-scrollbar-thumb:hover {
  background: var(--accent);
}

.layer-list.empty {
  align-items: center;
  justify-content: center;
  min-height: 200px;
  overflow: hidden;
}

.empty-state {
  text-align: center;
  color: var(--sub);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-text {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.empty-desc {
  font-size: 12px;
  opacity: 0.8;
}

.layer-group {
  background: var(--btn-secondary-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
}

.group-header {
  padding: 12px 16px;
  background: var(--surface-hover);
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s ease;
}

.group-header:hover {
  background: var(--surface-hover);
}

.group-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 8px;
}

.collapse-icon {
  font-size: 10px;
  transition: transform 0.2s ease;
  color: var(--accent);
}

.collapse-icon.collapsed {
  transform: rotate(-90deg);
}

.layer-count {
  font-size: 11px;
  color: var(--sub);
  font-weight: normal;
}

.group-items {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.layer-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
  transition: all 0.2s ease;
}

.layer-item:hover {
  background: var(--surface-hover);
  border-color: var(--accent);
}

.layer-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.layer-name {
  font-size: 12px;
  color: var(--text);
  font-weight: 500;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.layer-desc {
  font-size: 10px;
  color: var(--sub);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.layer-operations {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.layer-operations :deep(.secondary-button) {
  font-size: 10px;
  padding: 4px 8px;
  min-width: auto;
}
</style>


