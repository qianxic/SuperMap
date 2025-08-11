import { computed } from 'vue'
import { useLayerStore } from '@/stores/layerStore'
import type { MapLayer } from '@/types/map';

export function useLayerManager() {
  const layerStore = useLayerStore()

  // 所有图层操作功能已禁用
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

  const toggleFeatureVisibility = (_layerId: string, _featureId: string): boolean => {
    console.log('要素可见性切换功能已禁用')
    return false
  }

  const removeFeature = (_layerId: string, _featureId: string): boolean => {
    console.log('要素删除功能已禁用')
    return false
  }

  return {
    // 数据视图 (直接从 store 获取)
    managedDrawLayers: computed(() => layerStore.managedDrawLayers),

    // 所有操作已禁用
    acceptDrawLayer,
    toggleDrawLayerVisibility,
    removeDrawLayer,
    updateLayerProperties,
    findFeatureAtCoordinate,
    toggleFeatureVisibility,
    removeFeature
  }
}
