import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MapConfig, Coordinate, MapLayer, VectorLayerConfig } from '@/types/map'
import { createAPIConfig, getFullUrl } from '@/utils/config'
import { useAnalysisStore } from '@/stores/analysisStore'

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
  
  // 鼠标坐标
  const currentCoordinate = ref<Coordinate>({ lon: null, lat: null })
  
  // 距离量算相关状态
  const distanceMeasureMode = ref<boolean>(false)
  const distanceMeasureResult = ref<{ distance: number; unit: string } | null>(null)
  const measureLayer = ref<any>(null) // 量算图层
  const measureInteraction = ref<any>(null) // 量算交互
  
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
  }

  function reloadConfig() {
    mapConfig.value = createMapConfig()
  }

  // 距离量算功能 - 直接使用SuperMap iClient API
  function startDistanceMeasure() {
    if (!map.value) return
    
    const ol = window.ol
    
    // 创建量算图层
    const measureSource = new ol.source.Vector({ wrapX: false })
    measureLayer.value = new ol.layer.Vector({
      source: measureSource,
      style: new ol.style.Style({
        stroke: new ol.style.Stroke({
          color: '#ff0000',
          width: 2
        }),
        fill: new ol.style.Fill({
          color: 'rgba(255, 0, 0, 0.1)'
        })
      })
    })
    
    map.value.addLayer(measureLayer.value)
    
    // 创建量算交互 - 直接使用SuperMap官方示例的方式
    measureInteraction.value = new ol.interaction.Draw({
      source: measureSource,
      type: 'LineString',
      snapTolerance: 20
    })
    
    // 监听绘制完成事件
    measureInteraction.value.on('drawend', (event: any) => {
      const feature = event.feature
      const geometry = feature.getGeometry()
      
      // 打印几何信息
      console.log('=== 距离量测API调用信息 ===')
      console.log('绘制要素:', feature)
      console.log('几何对象:', geometry)
      console.log('几何类型:', geometry.getType())
      console.log('几何坐标:', geometry.getCoordinates())
      
      // 尝试使用SuperMap MeasureService进行距离量算
      try {
        const distanceMeasureParam = new ol.supermap.MeasureParameters(geometry)
        console.log('MeasureParameters对象:', distanceMeasureParam)
        
        // 获取地图服务URL - 直接使用正确的URL
        const url = 'http://localhost:8090/iserver/services/map-WuHan/rest/maps/武汉'
        console.log('SuperMap服务URL:', url)
        
        // 直接调用SuperMap MeasureService API
        const measureService = new ol.supermap.MeasureService(url, { measureMode: 'distance' })
        console.log('MeasureService对象:', measureService)
        
        console.log('开始调用measureDistance API...')
        measureService.measureDistance(distanceMeasureParam)
          .then((serviceResult: any) => {
            console.log('SuperMap MeasureService返回结果:', serviceResult)
            if (serviceResult && serviceResult.result) {
              const result = serviceResult.result
              distanceMeasureResult.value = {
                distance: result.distance,
                unit: result.unit || '米'
              }
            }
          })
          .catch((error: any) => {
            console.error('SuperMap服务距离量算失败:', error)
            console.error('错误详情:', error?.message)
            console.error('错误堆栈:', error?.stack)
          })
      } catch (error: any) {
        console.error('SuperMap MeasureService初始化失败:', error)
        console.error('错误详情:', error?.message)
        console.error('错误堆栈:', error?.stack)
      }
    })
    
    map.value.addInteraction(measureInteraction.value)
    distanceMeasureMode.value = true
    
    // 同步分析状态
    const analysisStore = useAnalysisStore()
    analysisStore.setDistanceMeasureMode(true)
  }
  
  function stopDistanceMeasure() {
    if (measureInteraction.value && map.value) {
      map.value.removeInteraction(measureInteraction.value)
      measureInteraction.value = null
    }
    
    if (measureLayer.value && map.value) {
      map.value.removeLayer(measureLayer.value)
      measureLayer.value = null
    }
    
    distanceMeasureMode.value = false
    distanceMeasureResult.value = null
    
    // 同步分析状态
    const analysisStore = useAnalysisStore()
    analysisStore.setDistanceMeasureMode(false)
  }
  
  function clearDistanceMeasure() {
    if (measureLayer.value && measureLayer.value.getSource()) {
      measureLayer.value.getSource().clear()
    }
    distanceMeasureResult.value = null
  }
  

  return {
    map,
    isMapReady,
    baseLayer,
    hoverLayer,
    selectLayer,
    vectorLayers,
    currentCoordinate,
    customLayers,
    mapConfig,
    formattedCoordinate,
    hasMapDiff,
    // 距离量算相关
    distanceMeasureMode,
    distanceMeasureResult,
    measureLayer,
    measureInteraction,
    setMap,
    setLayers,
    updateCoordinate,
    getSelectedFeatures,
    clearAllLayers,
    reloadConfig,
    // 距离量算方法
    startDistanceMeasure,
    stopDistanceMeasure,
    clearDistanceMeasure
  }
})

export { useMapStore }
export default useMapStore
