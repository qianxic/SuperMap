<template>
  <div class="distance-measure-button">
    <button 
      @click="toggleDistanceMeasure" 
      :class="['measure-btn', { active: mapStore.distanceMeasureMode }]"
      :title="mapStore.distanceMeasureMode ? '停止距离量算' : '开始距离量算'"
    >
      <svg class="measure-icon" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { useMapStore } from '@/stores/mapStore'
import { useAnalysisStore } from '@/stores/analysisStore'

const mapStore = useMapStore()
const analysisStore = useAnalysisStore()

const toggleDistanceMeasure = () => {
  if (mapStore.distanceMeasureMode) {
    mapStore.stopDistanceMeasure()
    analysisStore.setDistanceMeasureMode(false)
  } else {
    mapStore.startDistanceMeasure()
    analysisStore.setDistanceMeasureMode(true)
  }
}
</script>

<style scoped>
.distance-measure-button {
  position: absolute;
  top: 120px;
  left: 20px;
  z-index: 1000;
}

.measure-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  background: white;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #24292f;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.measure-btn:hover {
  background: #f6f8fa;
  border-color: #0969da;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.15);
}

.measure-btn.active {
  background: #0969da;
  border-color: #0969da;
  color: white;
}

.measure-btn.active:hover {
  background: #0858b9;
}

.measure-icon {
  width: 20px;
  height: 20px;
}
</style>
