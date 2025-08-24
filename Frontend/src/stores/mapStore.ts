import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MapConfig, Coordinate, MapLayer, VectorLayerConfig } from '@/types/map'
import { createAPIConfig, getFullUrl } from '@/utils/config'

const useMapStore = defineStore('map', () => {
  // 地图实例
  const map = ref<any>(null) // ol.Map
  const isMapReady = ref<boolean>(false)
  
  // 图层管理
  const baseLayer = ref<any>(null) // ol.layer.Tile
  const hoverLayer = ref<any>(null) // ol.layer.Vector
  const selectLayer = ref<any>(null) // ol.layer.Vector
  const vectorLayers = ref<MapLayer[]>([])

  const customLayers = ref<MapLayer[]>([])
  
  // 悬停和选中要素
  const hoveredFeature = ref<any>(null) // ol.Feature
  const selectedFeature = ref<any>(null) // ol.Feature
  
  // 持久化的批量选择状态
  const persistentSelectedFeatures = ref<any[]>([]) // 保持选择状态的要素数组
  const selectedFeatureIndex = ref<number>(-1) // 当前选中要素的索引
  
  // 鼠标坐标
  const currentCoordinate = ref<Coordinate>({ lon: null, lat: null })
  
  // 弹窗状态
  const popupVisible = ref<boolean>(false)
  const popupPosition = ref<{ x: number, y: number }>({ x: 0, y: 0 })
  const popupContent = ref<string>('')
  
  const popupFeature = ref<any>(null) // ol.Feature
  const popupCoordinate = ref<number[] | null>(null) // [lon, lat]
  
  // 计算属性
  const formattedCoordinate = computed(() => {
    if (!currentCoordinate.value.lon || !currentCoordinate.value.lat) {
      return '经度: -, 纬度: -'
    }
    return `经度: ${currentCoordinate.value.lon.toFixed(6)}, 纬度: ${currentCoordinate.value.lat.toFixed(6)}`
  })

  const hasMapDiff = computed(() => {
    const hasCustomLayers = customLayers.value.length > 0
    const hasSelections = selectLayer.value && selectLayer.value.getSource() && selectLayer.value.getSource().getFeatures().length > 0
    const hasPersistentSelections = persistentSelectedFeatures.value.length > 0
    return hasCustomLayers || !!hasSelections || hasPersistentSelections
  })
  
  const createMapConfig = (): MapConfig => {
    const apiConfig = createAPIConfig()
    
    // 根据图层类型创建不同的样式配置
    const vectorLayerConfigs: VectorLayerConfig[] = apiConfig.wuhanLayers
      .filter(layer => layer.type !== 'raster') // 过滤掉栅格图层
      .map(layer => {
        const baseStyle = {
          stroke: { width: 1.5, color: '#007bff' },
          fill: { color: 'rgba(0, 123, 255, 0.1)' }
        }
        
        // 特殊处理县级图层，设置为透明显示
        const layerName = layer.name.split('@')[0] || layer.name
        if (layerName === '武汉_县级') {
          return {
            name: layer.name,
            style: {
              stroke: { width: 1.5, color: 'var(--accent)' },
              fill: { color: 'rgba(0, 0, 0, 0)' } // 完全透明
            }
          }
        }
        
        // 根据图层类型调整样式
        switch (layer.type) {
          case 'point':
            return {
              name: layer.name,
              style: {
                ...baseStyle,
                fill: { color: 'rgba(255, 0, 0, 0.6)' } // 点要素用红色
              }
            }
          case 'line':
            return {
              name: layer.name,
              style: {
                ...baseStyle,
                stroke: { width: 2, color: '#28a745' }, // 线要素用绿色
                fill: { color: 'rgba(0, 0, 0, 0)' }
              }
            }
          case 'polygon':
            return {
              name: layer.name,
              style: {
                ...baseStyle,
                stroke: { width: 1.5, color: '#007bff' },
                fill: { color: 'rgba(0, 123, 255, 0.1)' }
              }
            }
          default:
            return {
              name: layer.name,
              style: baseStyle
            }
        }
      })
    
    return {
      baseUrl: getFullUrl('map'),
      dataUrl: getFullUrl('data'),
      datasetName: apiConfig.datasetName,
      vectorLayers: vectorLayerConfigs,
      center: [114.37, 30.69],
      zoom: 8,
      projection: 'EPSG:4326',
      extent: [113.7, 29.97, 115.08, 31.36]
    }
  }
  
  const mapConfig = ref<MapConfig>(createMapConfig())
  
  // Actions
  function setMap(mapInstance: any) { // ol.Map
    map.value = mapInstance
    isMapReady.value = true
  }
  
  function setLayers(layers: { base: any, hover: any, select: any }) {
    baseLayer.value = layers.base
    hoverLayer.value = layers.hover
    selectLayer.value = layers.select
  }
  
  function updateCoordinate(coordinate: number[]) {
    currentCoordinate.value = {
      lon: coordinate[0],
      lat: coordinate[1]
    }
  }
  
  function setHoveredFeature(feature: any | null) { // ol.Feature
    hoveredFeature.value = feature
  }
  
  function setSelectedFeature(feature: any | null) { // ol.Feature
    selectedFeature.value = feature
  }
  
  function showPopup(position: {x: number, y: number}, content: string, feature: any | null = null, coordinate: number[] | null = null) {
    popupPosition.value = position
    popupContent.value = content
    popupFeature.value = feature
    popupCoordinate.value = coordinate
    popupVisible.value = true
  }
  
  function hidePopup() {
    popupVisible.value = false
    popupContent.value = ''
    popupFeature.value = null
    popupCoordinate.value = null
  }
  
  function updatePopupPosition() {
    if (popupVisible.value && popupCoordinate.value && map.value) {
      const pixel = map.value.getPixelFromCoordinate(popupCoordinate.value)
      if (pixel) {
        popupPosition.value = { x: pixel[0], y: pixel[1] }
      }
    }
  }
  
  function clearSelection() {
    selectedFeature.value = null
    // 普通点击选择：清除所有选择，不保留几何选择
    if (selectLayer.value && selectLayer.value.getSource()) {
      const source = selectLayer.value.getSource()
      source.clear()
    }
    hidePopup()
  }

  // 管理持久化选择状态的函数
  function setPersistentSelectedFeatures(features: any[]) {
    persistentSelectedFeatures.value = features
  }

  function getPersistentSelectedFeatures(): any[] {
    return persistentSelectedFeatures.value
  }

  function clearPersistentSelection() {
    persistentSelectedFeatures.value = []
    selectedFeatureIndex.value = -1
    clearSelection()
  }

  function setSelectedFeatureIndex(index: number) {
    selectedFeatureIndex.value = index
  }

  function getSelectedFeatures(): any[] { // ol.Feature[]
    if (selectLayer.value && selectLayer.value.getSource) {
      const source = selectLayer.value.getSource()
      return source ? source.getFeatures() : []
    }
    return []
  }

  function clearAllLayers() {
    if (map.value) {
      customLayers.value.forEach(item => {
        try { map.value.removeLayer(item.layer) } catch (_) { /* noop */ }
      })
      vectorLayers.value.forEach(item => {
        try { map.value.removeLayer(item.layer) } catch (_) { /* noop */ }
      })
    }
    customLayers.value = []
    vectorLayers.value = []
    if (selectLayer.value && selectLayer.value.getSource()) {
      selectLayer.value.getSource().clear()
    }
    hoveredFeature.value = null
    selectedFeature.value = null
    hidePopup()
  }

  function reloadConfig() {
    mapConfig.value = createMapConfig()
  }

  return {
    map,
    isMapReady,
    baseLayer,
    hoverLayer,
    selectLayer,
    vectorLayers,
    hoveredFeature,
    selectedFeature,
    currentCoordinate,
    customLayers,
    popupVisible,
    popupPosition,
    popupContent,
    popupFeature,
    popupCoordinate,
    mapConfig,
    formattedCoordinate,
    hasMapDiff,
    // 持久化选择状态
    persistentSelectedFeatures,
    selectedFeatureIndex,
    setMap,
    setLayers,
    updateCoordinate,
    setHoveredFeature,
    setSelectedFeature,
    showPopup,
    hidePopup,
    updatePopupPosition,
    clearSelection,
    getSelectedFeatures,
    clearAllLayers,
    reloadConfig,
    // 持久化选择状态管理
    setPersistentSelectedFeatures,
    getPersistentSelectedFeatures,
    clearPersistentSelection,
    setSelectedFeatureIndex
  }
})

export { useMapStore }
export default useMapStore
