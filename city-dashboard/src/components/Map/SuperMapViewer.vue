<template>
  <div class="map-container">
    <div ref="mapContainer" class="map-view"></div>
    <!-- 要素弹窗 -->
    <FeaturePopup />
    <!-- 坐标显示（左下角） -->
    <CoordinateDisplay />
    <!-- 比例尺显示（右下角） -->
    <ScaleBar />

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMap } from '@/composables/useMap'
import FeaturePopup from './FeaturePopup.vue'
import CoordinateDisplay from './CoordinateDisplay.vue'
import ScaleBar from './ScaleBar.vue'


// 组合式函数
const { mapContainer, initMap } = useMap()

// 生命周期
onMounted(() => {
  // 确保外部库已加载
  if (window.ol && window.ol.supermap) {
    initMap()
  } else {
    // 如果库还未加载，等待一下再初始化
    setTimeout(initMap, 500)
  }
})
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.map-view {
  position: absolute;
  inset: 0;
  border-radius: 8px;
}
</style>
