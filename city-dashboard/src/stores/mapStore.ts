import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MapConfig, Coordinate, MapLayer } from '@/types/map'

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
    return hasCustomLayers || !!hasSelections
  })
  
  const mapConfig = ref<MapConfig>({
    baseUrl: "http://localhost:8090/iserver/services/map-WuHan/rest/maps/武汉_市级",
    dataUrl: 'http://localhost:8090/iserver/services/data-WuHan/rest/data',
    datasetName: 'wuhan:武汉_县级',
    vectorLayers: [
      { 
        name: '武汉_县级@wuhan',
        style: {
          stroke: { width: 1.5 }, // 移除 color 属性
          fill: { color: 'rgba(0, 0, 255, 0)' }
        }
      }
    ],
    center: [114.37, 30.69],
    zoom: 8,
    projection: 'EPSG:4326',
    extent: [113.7, 29.97, 115.08, 31.36]
  })
  
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
    if (selectLayer.value && selectLayer.value.getSource()) {
      selectLayer.value.getSource().clear()
    }
    hidePopup()
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
    clearAllLayers
  }
})

export { useMapStore }
export default useMapStore
