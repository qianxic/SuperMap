import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { MapLayer } from '@/types/map'

export const useLayerStore = defineStore('layer', () => {
  const managedDrawLayers = ref<MapLayer[]>([])

  return {
    managedDrawLayers,
  }
})

