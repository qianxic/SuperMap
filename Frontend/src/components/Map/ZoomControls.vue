<template>
  <div class="zoom-controls">
    <button 
      class="zoom-btn zoom-in" 
      @click="zoomIn"
      title="放大"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
        <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
      </svg>
    </button>
    <button 
      class="zoom-btn zoom-out" 
      @click="zoomOut"
      title="缩小"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
        <path d="M19 13H5v-2h14v2z"/>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { useMapStore } from '@/stores/mapStore'

const mapStore = useMapStore()

const zoomIn = () => {
  if (mapStore.map) {
    const view = mapStore.map.getView()
    const zoom = view.getZoom()
    view.animate({
      zoom: zoom + 1,
      duration: 250
    })
  }
}

const zoomOut = () => {
  if (mapStore.map) {
    const view = mapStore.map.getView()
    const zoom = view.getZoom()
    view.animate({
      zoom: zoom - 1,
      duration: 250
    })
  }
}
</script>

<style scoped>
.zoom-controls {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--glow);
  padding: 4px;
}

.zoom-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: var(--panel);
  color: var(--text);
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
}

.zoom-btn:hover {
  background: var(--accent);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.zoom-btn:active {
  transform: translateY(0);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.zoom-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.zoom-btn:disabled:hover {
  background: var(--panel);
  color: var(--text);
  box-shadow: none;
}
</style>
