<template>
  <PanelContainer class="llm-panel">
    <div class="chat-container">
      <ChatAssistant :initial-layers="layersStatus" :map-ready="mapStore.isMapReady" />
    </div>
  </PanelContainer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import ChatAssistant from '@/components/Map/ChatAssistant.vue'
import PanelContainer from '@/components/UI/PanelContainer.vue'

const mapStore = useMapStore()

const layersStatus = computed(() => {
  return mapStore.vectorLayers.map(l => ({ name: l.name, visible: l.visible }))
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