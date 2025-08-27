<template>
  <div class="scale-bar" v-if="scaleInfo.visible">
    <div class="scale-line" :style="{ width: scaleInfo.width + 'px' }"></div>
    <div class="scale-text">{{ scaleInfo.text }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted, watch } from 'vue'
import { useMapStore } from '@/stores/mapStore'

const mapStore = useMapStore()

// 比例尺信息
const scaleInfo = ref({
  visible: false,
  width: 100,
  text: '0 km'
})

// 计算比例尺
const calculateScale = () => {
  const map = mapStore.map
  if (!map) {
    scaleInfo.value.visible = false
    return
  }

  const view = map.getView()
  const resolution = view.getResolution()
  const projection = view.getProjection()
  
  if (!resolution || !projection) {
    scaleInfo.value.visible = false
    return
  }

  // 获取地图中心点的米/像素分辨率
  const center = view.getCenter()
  if (!center) {
    scaleInfo.value.visible = false
    return
  }
  const metersPerPixel = getMetersPerPixel(resolution, center[1])
  
  // 设置比例尺宽度（像素）
  const maxWidth = 200
  const targetWidths = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
  
  let bestWidth = 100 // 默认像素宽度
  let bestDistance = 0 // 对应的实际距离（米）
  
  // 找到最合适的比例尺
  for (const distance of targetWidths) {
    const pixelWidth = (distance * 1000) / metersPerPixel // 转换为像素
    if (pixelWidth <= maxWidth) {
      bestWidth = pixelWidth
      bestDistance = distance
    } else {
      break
    }
  }
  
  scaleInfo.value = {
    visible: true,
    width: Math.round(bestWidth),
    text: formatDistance(bestDistance)
  }
}

// 获取指定纬度的米/像素分辨率
const getMetersPerPixel = (resolution: number, latitude: number) => {
  // 对于EPSG:4326，resolution是度/像素
  // 在给定纬度处，1度经度对应的米数
  const metersPerDegree = 111320 * Math.cos(latitude * Math.PI / 180)
  return resolution * metersPerDegree
}

// 格式化距离显示
const formatDistance = (distanceKm: number) => {
  if (distanceKm < 1) {
    return `${(distanceKm * 1000).toFixed(0)} m`
  } else {
    return `${distanceKm} km`
  }
}

// 监听地图变化
watch(() => mapStore.isMapReady, (ready) => {
  if (ready) {
    const map = mapStore.map
    if (map) {
      const view = map.getView()
      
      // 监听地图缩放和移动
      view.on('change:resolution', calculateScale)
      view.on('change:center', calculateScale)
      
      // 初始计算
      calculateScale()
    }
  }
}, { immediate: true })

onUnmounted(() => {
  const map = mapStore.map
  if (map) {
    const view = map.getView()
    view.un('change:resolution', calculateScale)
    view.un('change:center', calculateScale)
  }
})
</script>

<style scoped>
.scale-bar {
  position: absolute;
  right: 16px;
  bottom: 16px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.scale-line {
  height: 3px;
  background: var(--text);
  border-radius: 2px;
  box-shadow: 0 0 8px rgba(66,165,245,0.35);
  margin-bottom: 4px;
  position: relative;
}

.scale-line::before,
.scale-line::after {
  content: '';
  position: absolute;
  top: -2px;
  bottom: -2px;
  width: 2px;
  background: var(--text);
  border-radius: 1px;
}

.scale-line::before {
  left: 0;
}

.scale-line::after {
  right: 0;
}

.scale-text {
  font-family: monospace;
  font-size: 12px;
  color: var(--text);
  text-shadow: 0 0 8px rgba(66,165,245,0.35);
  white-space: nowrap;
  background: transparent;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--border);
}
</style>