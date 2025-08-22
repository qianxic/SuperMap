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
  </PanelWindow>
  
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useAnalysisStore } from '@/stores/analysisStore'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import { useLayerManager } from '@/composables/useLayerManager'
import PanelWindow from '@/components/UI/PanelWindow.vue'

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
  
  // 按图层类型分组显示
  const layerGroups = {
    '行政区划': ['武汉_县级'],
    '交通设施': ['公路', '铁路'],
    '水系': ['水系线', '水系面'],
    '建筑物': ['建筑物面'],
    '地名点': ['居民地地名点'],
    '公共服务': ['学校', '医院']
  }
  
  mapStore.vectorLayers.forEach(vl => {
    const layerName = vl.name
    let groupName = '其他'
    let desc = '矢量数据'
    
    // 根据图层名称确定分组和描述
    for (const [group, layers] of Object.entries(layerGroups)) {
      if (layers.includes(layerName)) {
        groupName = group
        break
      }
    }
    
    // 根据图层类型设置描述
    if (vl.type === 'raster') {
      desc = '栅格数据 (DEM)'
    } else if (layerName.includes('点')) {
      desc = '点要素'
    } else if (layerName.includes('线')) {
      desc = '线要素'
    } else if (layerName.includes('面')) {
      desc = '面要素'
    }
    
    items.push({
      key: vl.id,
      name: `${groupName} - ${layerName}`,
      desc: desc,
      visible: vl.layer.getVisible(),
      isVector: vl.type === 'vector'
    });
  });
  
  // 按分组排序
  return items.sort((a, b) => {
    const groupOrder = ['行政区划', '交通设施', '水系', '建筑物', '地名点', '公共服务', '其他']
    const aGroup = a.name.split(' - ')[0]
    const bGroup = b.name.split(' - ')[0]
    return groupOrder.indexOf(aGroup) - groupOrder.indexOf(bGroup)
  })
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
.layer-list { display: flex; flex-direction: column; gap: 8px; }
.layer-list.empty { color: var(--sub); font-size: 12px; padding: 12px; background: rgba(255,255,255,0.04); border-radius: 12px; }

.layer-container { display: flex; flex-direction: column; }

.layer-item {
  display: flex; align-items: center; justify-content: space-between;
  background: var(--surface, rgba(255,255,255,0.06));
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px 14px;
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
  background: var(--surface, rgba(255,255,255,0.03));
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  animation: fadeIn 0.3s ease-out;
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


