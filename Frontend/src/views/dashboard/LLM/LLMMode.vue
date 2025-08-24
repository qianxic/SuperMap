<template>
  <PanelContainer class="llm-panel">
    <div class="chat-container">
      <ChatAssistant 
        :initial-layers="layersStatus" 
        :map-ready="mapStore.isMapReady"
        :selected-features="selectedFeaturesStatus"
      />
    </div>
  </PanelContainer>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useModeStateStore } from '@/stores/modeStateStore'
import ChatAssistant from './tools/ChatAssistant.vue'
import PanelContainer from '@/components/UI/PanelContainer.vue'

const mapStore = useMapStore()
const modeStateStore = useModeStateStore()

const layersStatus = computed(() => {
  return mapStore.vectorLayers.map(l => ({ name: l.name, visible: l.visible }))
})

// 新增：计算选中要素状态
const selectedFeaturesStatus = computed(() => {
  const features = mapStore.persistentSelectedFeatures.map(feature => {
    // 使用与EditTools.vue完全相同的几何类型获取逻辑
    const geometry = feature.geometry || feature.getGeometry?.();
    let geometryType = '未知';
    
    if (geometry) {
      // 直接返回几何类型，不进行映射 - 与EditTools.vue的getFeatureType函数保持一致
      geometryType = geometry.getType?.() || geometry.type || '未知';
    }
    
    return {
      id: feature.id || feature.getId?.() || null,
      properties: feature.properties || feature.getProperties?.() || {},
      geometry: {
        ...(feature.geometry || feature.getGeometry?.() || {}),
        type: geometryType // 确保几何类型正确传递
      },
      layerName: feature.layerName || '未知图层'
    };
  });
  
  return features;
})

// 组件生命周期管理
onMounted(() => {
  // 激活LLM模式，恢复状态
  modeStateStore.restoreModeState('llm')
})

onUnmounted(() => {
  // 组件卸载时保存状态（虽然通常不会卸载，但为了安全）
  // 状态保存由ChatAssistant组件内部处理
})
</script>

<style scoped>
.llm-panel {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
</style>