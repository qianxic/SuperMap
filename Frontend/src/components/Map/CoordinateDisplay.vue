<template>
  <div class="coordinate-text">{{ mapStore.formattedCoordinate }}</div>
  
</template>

<script setup lang="ts">
import { useMapStore } from '@/stores/mapStore'

const mapStore = useMapStore()
</script>

<style scoped>
.coordinate-text {
  position: absolute;
  right: 16px;
  bottom: 50px;
  z-index: 1000;
  font-family: monospace;
  font-size: 12px;
  color: var(--accent);
  text-shadow: 0 0 8px rgba(66,165,245,0.35);
}
</style>
