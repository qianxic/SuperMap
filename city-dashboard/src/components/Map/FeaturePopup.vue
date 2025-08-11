<template>
  <div 
    v-show="mapStore.popupVisible"
    class="popup"
    :style="popupStyle"
  >
    <div class="hd">要素信息</div>
    <div class="popup-body" v-html="mapStore.popupContent"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useMapStore } from '@/stores/mapStore.ts'

const mapStore = useMapStore()

// 弹窗位置样式
const popupStyle = computed(() => ({
  left: `${mapStore.popupPosition.x}px`,
  top: `${mapStore.popupPosition.y}px`,
  transform: 'translate(-50%, -100%)'
}))
</script>

<style scoped>
.popup {
  position: absolute;
  min-width: 220px;
  max-width: 320px;
  background: var(--panel);
  color: var(--text);
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--glow);
  pointer-events: none;
  z-index: 1000;
}

.hd {
  font-size: 12px;
  color: var(--sub);
  margin-bottom: 4px;
}

.popup-body :deep(.kv) {
  display: flex;
  gap: 8px;
  align-items: baseline;
  font-size: 12px;
  line-height: 18px;
}

.popup-body :deep(.k) {
  color: var(--sub);
  min-width: 72px;
}

.popup-body :deep(.v) {
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
