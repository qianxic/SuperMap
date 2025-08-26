<template>
  <div class="distance-measure-panel" v-if="mapStore.distanceMeasureMode">
    <div class="panel-content">
      <div class="measure-instructions">
        <p>请在地图上绘制线段进行距离量算</p>
        <p>双击结束绘制</p>
      </div>
      
      <div class="measure-result" v-if="mapStore.distanceMeasureResult">
        <div class="result-item">
          <span class="label">距离:</span>
          <span class="value">{{ formatDistance(mapStore.distanceMeasureResult.distance, mapStore.distanceMeasureResult.unit).value }} {{ formatDistance(mapStore.distanceMeasureResult.distance, mapStore.distanceMeasureResult.unit).unit }}</span>
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
  mapStore.stopDistanceMeasure()
}

const clearMeasure = () => {
  mapStore.clearDistanceMeasure()
}

const formatDistance = (distance: number, unit: string): { value: string; unit: string } => {
  if (unit === 'METER' && distance >= 1000) {
    return {
      value: (distance / 1000).toFixed(2),
      unit: '千米'
    }
  }
  return {
    value: distance.toFixed(2),
    unit: unit === 'METER' ? '米' : unit
  }
}
</script>

<style scoped>
.distance-measure-panel {
  position: absolute;
  top: 50%;
  right: 20px;
  transform: translateY(-50%);
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
  color: var(--accent);
}

.value {
  font-size: 12px;
  font-weight: 700;
  color: var(--accent);
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
  background: #dc3545;
  color: white;
}

.stop-btn:hover {
  background: #c82333;
}
</style>
