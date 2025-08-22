<template>
  <PanelWindow
    :visible="mapStore.popupVisible"
    title="要素信息"
    :width="175"
    :height="popupHeight"
    position="absolute"
    :left="adjustedPosition.x"
    :top="adjustedPosition.y"
    :z-index="1000"
    :focusable="true"
    :closeable="true"
    :resizable="true"
    @close="mapStore.hidePopup"
  >
    <div class="popup-body" v-html="mapStore.popupContent"></div>
  </PanelWindow>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useMapStore } from '@/stores/mapStore.ts'
import PanelWindow from '@/components/UI/PanelWindow.vue'

const mapStore = useMapStore()

// 计算弹窗高度为屏幕高度的1/4（缩小一半）
const popupHeight = computed(() => {
  return Math.floor(window.innerHeight / 4)
})

// 计算调整后的位置，使弹窗显示在鼠标位置的右侧，高度为屏幕高度的1/4
const adjustedPosition = computed(() => {
  const windowWidth = window.innerWidth
  const windowHeight = window.innerHeight
  const popupWidth = 175 // 宽度缩小一半
  
  // 将弹窗放在鼠标位置的右侧
  let x = mapStore.popupPosition.x + 10 // 鼠标位置右侧，留10px间距
  let y = mapStore.popupPosition.y - popupHeight.value / 2 // 垂直居中于鼠标位置
  
  // 确保弹窗不会超出屏幕边界
  if (x + popupWidth > windowWidth) x = mapStore.popupPosition.x - popupWidth - 10 // 如果右侧放不下，放在左侧
  if (x < 0) x = 0
  if (y < 0) y = 0
  if (y + popupHeight.value > windowHeight) y = windowHeight - popupHeight.value
  
  return { x, y }
})
</script>

<style scoped>
.popup-body {
  padding: 0;
  margin: 0;
}

.popup-body :deep(.kv) {
  display: flex;
  gap: 12px;
  align-items: baseline;
  font-size: 12px;
  line-height: 20px;
  margin-bottom: 6px;
  padding: 4px 0;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.popup-body :deep(.kv:hover) {
  background: var(--surface-hover);
  padding: 4px 6px;
  margin: 0 -6px 6px -6px;
}

.popup-body :deep(.k) {
  color: var(--sub);
  min-width: 80px;
  font-weight: 500;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  flex-shrink: 0;
}

.popup-body :deep(.v) {
  color: var(--text);
  text-overflow: unset;
  white-space: nowrap;
  flex: 1;
  font-weight: 400;
  font-size: 12px;
  word-break: keep-all;
}

.popup-body :deep(.section-title) {
  font-size: 11px;
  color: var(--accent);
  font-weight: 600;
  margin: 16px 0 8px 0;
  padding: 6px 0;
  border-bottom: 2px solid var(--accent);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  position: relative;
}

.popup-body :deep(.section-title:first-child) {
  margin-top: 0;
}

.popup-body :deep(.section-title::before) {
  content: '';
  position: absolute;
  left: 0;
  bottom: -2px;
  width: 20px;
  height: 2px;
  background: var(--accent);
  border-radius: 1px;
}

/* 新增：支持显示所有字段的样式 */
.popup-body :deep(.field-row) {
  display: flex;
  gap: 12px;
  align-items: baseline;
  font-size: 12px;
  line-height: 20px;
  margin-bottom: 6px;
  padding: 4px 0;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.popup-body :deep(.field-row:hover) {
  background: var(--surface-hover);
  padding: 4px 6px;
  margin: 0 -6px 6px -6px;
}

.popup-body :deep(.field-label) {
  color: var(--sub);
  min-width: 80px;
  font-weight: 500;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  flex-shrink: 0;
}

.popup-body :deep(.field-value) {
  color: var(--text);
  text-overflow: unset;
  white-space: nowrap;
  flex: 1;
  font-weight: 400;
  font-size: 12px;
  word-break: keep-all;
}

/* 多要素信息样式 */
.popup-body :deep(.multi-feature-info) {
  /* 移除所有可能导致滚动条的样式 */
}

.popup-body :deep(.feature-count) {
  font-size: 13px;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}

.popup-body :deep(.feature-item) {
  margin-bottom: 16px;
  padding: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
}

.popup-body :deep(.feature-header) {
  font-size: 12px;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--border);
}
</style>
