<template>
  <div class="area-measure-panel" v-if="mapStore.areaMeasureMode">
    <div class="panel-content">
      <div class="measure-instructions">
        <p>请在地图上绘制多边形进行面积量算</p>
        <p>双击结束绘制</p>
      </div>
      
      <div class="measure-result" v-if="mapStore.areaMeasureResult">
        <div class="result-item">
          <span class="label">面积:</span>
          <span class="value">{{ formatArea(mapStore.areaMeasureResult.area, mapStore.areaMeasureResult.unit).value }} {{ formatArea(mapStore.areaMeasureResult.area, mapStore.areaMeasureResult.unit).unit }}</span>
        </div>
      </div>
      
      <div class="measure-actions">
        <button @click="clearMeasure" class="action-btn clear-btn">
          清除量算
        </button>
        <button @click="stopMeasure" class="action-btn stop-btn">
          停止量算
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMapStore } from '@/stores/mapStore'

const mapStore = useMapStore()

const stopMeasure = () => {
  mapStore.stopAreaMeasure()
}

const clearMeasure = () => {
  mapStore.clearAreaMeasure()
}

const formatArea = (area: number, unit: string): { value: string; unit: string } => {
  return {
    value: area.toFixed(4),
    unit: '平方千米'
  }
}
</script>

<style scoped>
.area-measure-panel {
  position: absolute;
  top: 164px;
  left: 56px;
  width: 200px;
  background: var(--panel);
  border-radius: var(--radius);
  box-shadow: var(--glow);
  z-index: 1000;
  border: 1px solid var(--border);
}

.panel-content {
  padding: 12px;
}

.measure-instructions {
  margin-bottom: 12px;
  padding: 8px;
  background: var(--surface);
  border-radius: 6px;
  border-left: 4px solid var(--accent);
}

.measure-instructions p {
  margin: 0 0 6px 0;
  font-size: 12px;
  color: var(--sub);
}

.measure-instructions p:last-child {
  margin-bottom: 0;
}

.measure-result {
  margin-bottom: 8px;
  padding: 6px;
  background: rgba(var(--accent-rgb), 0.1);
  border-radius: 4px;
  border: 1px solid rgba(var(--accent-rgb), 0.2);
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
}

.value {
  font-size: 12px;
  font-weight: 700;
  color: var(--text);
}

.measure-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s;
}

.clear-btn {
  background: var(--btn-secondary-bg);
  color: var(--btn-secondary-color);
  border: 1px solid var(--border);
}

.clear-btn:hover {
  background: var(--surface-hover);
}

.stop-btn {
  background: var(--btn-secondary-bg);
  color: var(--btn-secondary-color);
  border: 1px solid var(--border);
}

.stop-btn:hover {
  background: var(--surface-hover);
}
</style>
