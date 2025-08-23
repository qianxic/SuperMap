import { computed } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import type { MapLayer } from '@/types/map';

export function useLayerManager() {
  const mapStore = useMapStore()

  const toggleLayerVisibility = (layerId: string) => {
    const layerInfo = mapStore.vectorLayers.find(l => l.id === layerId)
    if (layerInfo && layerInfo.layer) {
      const currentVisibility = layerInfo.layer.getVisible()
      layerInfo.layer.setVisible(!currentVisibility)
      // 可选：更新 store 中的状态，如果需要的话
      layerInfo.visible = !currentVisibility
    }
  }

  const removeLayer = (layerId: string) => {
    const index = mapStore.vectorLayers.findIndex(l => l.id === layerId)
    if (index > -1) {
      const layerInfo = mapStore.vectorLayers[index]
      if (layerInfo.layer && mapStore.map) {
        mapStore.map.removeLayer(layerInfo.layer)
        mapStore.vectorLayers.splice(index, 1)
        return true
      }
    }
    return false
  }

  // 保留原有的被禁用的函数，以防其他地方有依赖
  const acceptDrawLayer = (_layerData: MapLayer): boolean => {
    console.log('图层管理功能已禁用')
    return false
  }

  const toggleDrawLayerVisibility = (_layerId: string): boolean => {
    console.log('图层可见性切换功能已禁用')
    return false
  }

  const removeDrawLayer = (_layerId: string): boolean => {
    console.log('图层删除功能已禁用')
    return false
  }

  const updateLayerProperties = (_layerId: string, _properties: Partial<MapLayer>): boolean => {
    console.log('图层属性更新功能已禁用')
    return false
  }

  const findFeatureAtCoordinate = (_coordinate: number[]): any | null => {
    return null
  }

  const toggleFeatureVisibility = (_layerId:string, _featureId: string): boolean => {
    console.log('要素可见性切换功能已禁用')
    return false
  }

  const removeFeature = (_layerId: string, _featureId: string): boolean => {
    console.log('要素删除功能已禁用')
    return false
  }

  return {
    // 激活新功能
    toggleLayerVisibility,
    removeLayer,

    // 旧的禁用功能
    managedDrawLayers: computed(() => []),

  }
}
