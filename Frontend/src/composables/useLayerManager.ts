import { computed } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useSelectionStore } from '@/stores/selectionStore'
import { usePopupStore } from '@/stores/popupStore'
import type { MapLayer } from '@/types/map';

export function useLayerManager() {
  const mapStore = useMapStore()
  const selectionStore = useSelectionStore()
  const popupStore = usePopupStore()

  // 清除特定图层的选择高亮
  const clearLayerSelection = (layerName: string) => {
    console.log(`清除图层 ${layerName} 的选择高亮和组件状态`)
    
    if (!mapStore.selectLayer || !mapStore.selectLayer.getSource()) return

    const source = mapStore.selectLayer.getSource()
    const features = source.getFeatures()
    
    // 找出属于该图层的选择要素并移除
    const featuresToRemove = features.filter((feature: any) => {
      // 通过多种方式判断要素是否属于该图层
      const layerId = feature.get('layerName') || 
                     (feature.getProperties ? feature.getProperties().layerName : null) ||
                     (feature.properties ? feature.properties.layerName : null)
      
      // 如果没有layerName属性，尝试通过图层ID匹配
      if (!layerId) {
        // 检查要素是否来自当前隐藏的图层
        const layerInfo = mapStore.vectorLayers.find(l => l.name === layerName)
        if (layerInfo && layerInfo.layer) {
          const layerSource = layerInfo.layer.getSource()
          if (layerSource) {
            const layerFeatures = layerSource.getFeatures()
            return layerFeatures.some((lf: any) => {
              // 通过几何坐标比较来判断是否为同一要素
              const lfGeom = lf.getGeometry()
              const featureGeom = feature.getGeometry()
              if (lfGeom && featureGeom) {
                const lfCoords = JSON.stringify(lfGeom.getCoordinates())
                const featureCoords = JSON.stringify(featureGeom.getCoordinates())
                return lfCoords === featureCoords
              }
              return false
            })
          }
        }
      }
      
      return layerId === layerName
    })

    console.log(`找到 ${featuresToRemove.length} 个属于图层 ${layerName} 的选择要素，准备移除`)

    // 从选择图层中移除这些要素
    featuresToRemove.forEach((feature: any) => {
      source.removeFeature(feature)
    })

    // 检查当前选中的要素是否属于被隐藏的图层
    const currentSelectedFeature = selectionStore.currentSelectedFeature
    if (currentSelectedFeature) {
      const currentLayerName = currentSelectedFeature.get('layerName') || 
                              (currentSelectedFeature.getProperties ? currentSelectedFeature.getProperties().layerName : null) ||
                              (currentSelectedFeature.properties ? currentSelectedFeature.properties.layerName : null)
      if (currentLayerName === layerName) {
        console.log(`当前选中的要素属于被隐藏的图层 ${layerName}，清除选择状态`)
        // 清除当前选中的要素
        selectionStore.clearSelection()
        // 隐藏弹窗 - 结束要素信息组件的生命周期
        popupStore.hidePopup()
      }
    }

    // 从持久化选择列表中移除相关要素
    const updatedFeatures = selectionStore.selectedFeatures.filter((feature: any) => {
      return feature.layerName !== layerName
    })
    selectionStore.setSelectedFeatures(updatedFeatures)

    // 如果当前选中的要素被移除，重置选中索引
    if (selectionStore.selectedFeatureIndex >= updatedFeatures.length) {
      selectionStore.setSelectedFeatureIndex(-1)
    }

    // 强制刷新选择图层以确保高亮效果立即消失
    if (mapStore.selectLayer) {
      mapStore.selectLayer.changed()
    }

    console.log(`图层 ${layerName} 的选择状态清除完成`)
  }

  const toggleLayerVisibility = async (layerId: string) => {
    const layerInfo = mapStore.vectorLayers.find(l => l.id === layerId)
    if (layerInfo && layerInfo.layer) {
      const currentVisibility = layerInfo.layer.getVisible()
      const newVisibility = !currentVisibility
      
      console.log(`切换图层 ${layerInfo.name} 可见性: ${currentVisibility} -> ${newVisibility}`)
      
      // 如果图层被隐藏，立即清除该图层的选择高亮和组件状态
      if (!newVisibility) {
        console.log(`图层 ${layerInfo.name} 被隐藏，立即清除相关选择状态`)
        clearLayerSelection(layerInfo.name)
        
        // 强制清除所有选择状态，确保完全清除
        if (mapStore.selectLayer && mapStore.selectLayer.getSource()) {
          mapStore.selectLayer.getSource().clear()
        }
        selectionStore.clearSelection()
        
        // 清除查询结果（如果当前在查询工具中）
        const { useFeatureQuery } = await import('@/composables/useFeatureQuery')
        const featureQuery = useFeatureQuery()
        if (featureQuery.queryResults && featureQuery.queryResults.value) {
          featureQuery.queryResults.value = []
        }
        
        // 重置选中要素索引
        if (featureQuery.selectedFeatureIndex) {
          featureQuery.selectedFeatureIndex.value = -1
        }
      }
      
      // 设置图层可见性
      layerInfo.layer.setVisible(newVisibility)
      
      // 确保响应式更新 - 使用数组索引直接更新
      const layerIndex = mapStore.vectorLayers.findIndex(l => l.id === layerId)
      if (layerIndex > -1) {
        // 创建新的对象来触发响应式更新
        mapStore.vectorLayers[layerIndex] = {
          ...mapStore.vectorLayers[layerIndex],
          visible: newVisibility
        }
      }
      
      console.log(`图层 ${layerInfo.name} 可见性切换完成`)
    }
  }

  const removeLayer = (layerId: string) => {
    const index = mapStore.vectorLayers.findIndex(l => l.id === layerId)
    if (index > -1) {
      const layerInfo = mapStore.vectorLayers[index]
      if (layerInfo.layer && mapStore.map) {
        // 移除图层前，清除该图层的选择高亮
        clearLayerSelection(layerInfo.name)
        
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
    clearLayerSelection,

    // 旧的禁用功能
    managedDrawLayers: computed(() => []),
    acceptDrawLayer,
    toggleDrawLayerVisibility,
    removeDrawLayer,
    updateLayerProperties,
    findFeatureAtCoordinate,
    toggleFeatureVisibility,
    removeFeature,

  }
}
