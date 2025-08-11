import { ref, onMounted, onUnmounted } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useLayerManager } from '@/composables/useLayerManager'

const ol = window.ol;

export function useMap() {
  let mapStore = useMapStore()
  const analysisStore = useAnalysisStore()
  const layerManager = useLayerManager()
  const mapContainer = ref<HTMLElement | null>(null)
  const hoverTimer = ref<number | null>(null)
  const selectSourceRef = ref<any>(null) // ol.source.Vector

  const initMap = (): void => {
    mapStore = useMapStore()
    
    try {
      if (!window.ol || !mapContainer.value) return
      
      const resolutions: number[] = [];
      for (let i = 0; i < 19; i++) {
          resolutions[i] = 180 / 256 / Math.pow(2, i);
      }

      const map = new ol.Map({
        target: mapContainer.value,
        controls: new ol.Collection([
          new ol.supermap.control.Logo({ link: "https://iclient.supermap.io" })
        ]),
        view: new ol.View({
          projection: mapStore.mapConfig.projection,
          resolutions: resolutions,
          center: mapStore.mapConfig.center,
          zoom: mapStore.mapConfig.zoom
        })
      })
      
      const projectionExtent = mapStore.mapConfig.extent;

      const tileGrid = new ol.tilegrid.TileGrid({
          extent: projectionExtent,
          origin: ol.extent.getTopLeft(projectionExtent),
          resolutions: resolutions
      });

      const baseLayer = new ol.layer.Tile({
        source: new ol.source.TileSuperMapRest({
          url: mapStore.mapConfig.baseUrl,
          tileGrid: tileGrid
        }),
      })
      map.addLayer(baseLayer)
      
      const hoverSource = new ol.source.Vector()
      const hoverLayer = new ol.layer.Vector({
        source: hoverSource,
        style: new ol.style.Style({
          image: new ol.style.Circle({ 
            radius: 8, 
            stroke: new ol.style.Stroke({color:'#42a5f5', width:2}), 
            fill: new ol.style.Fill({color:'rgba(66,165,245,0.25)'}) 
          }),
          stroke: new ol.style.Stroke({color:'#42a5f5', width:2}),
          fill: new ol.style.Fill({color:'rgba(66,165,245,0.15)'})
        })
      })
      map.addLayer(hoverLayer)
        
      const selectSource = new ol.source.Vector()
      const selectLayer = new ol.layer.Vector({
        source: selectSource,
        style: new ol.style.Style({
          image: new ol.style.Circle({ 
            radius: 5, 
            stroke: new ol.style.Stroke({color:'#ffca28', width:1.5}), 
            fill: new ol.style.Fill({color:'rgba(255,202,40,0.15)'}) 
          }),
          stroke: new ol.style.Stroke({color:'#ffca28', width:1.5}),
          fill: new ol.style.Fill({color:'rgba(255,202,40,0.08)'})
        })
      })
      map.addLayer(selectLayer)
      selectSourceRef.value = selectSource
        
      mapStore.setMap(map)
      mapStore.setLayers({
        base: baseLayer,
        hover: hoverLayer,
        select: selectLayer
      })
        
      setupMapEvents(map, hoverSource, selectSource)
        
      setTimeout(() => {
        map.updateSize()
      }, 100)

      const handleDrawLayerCompleted = (event: Event) => {
        layerManager.acceptDrawLayer((event as CustomEvent).detail)
      }
      window.addEventListener('drawLayerCompleted', handleDrawLayerCompleted)
        
      console.log('地图初始化完成')
    } catch (error) {
      console.error('地图初始化失败:', error)
    }
  }
  
  const setupMapEvents = (map: any, hoverSource: any, selectSource: any): void => {
    const view = map.getView()
    view.on('change:center', () => {
      mapStore.updatePopupPosition()
    })
    view.on('change:resolution', () => {
      mapStore.updatePopupPosition()
    })
    
    map.on('pointermove', (evt: any) => {
      mapStore.updateCoordinate(evt.coordinate)
      if (hoverTimer.value) clearTimeout(hoverTimer.value)
      hoverTimer.value = window.setTimeout(() => {
        handleFeatureHover(hoverSource)
      }, 120)
      console.log(evt)
    })
    
    map.on('click', (evt: any) => {
      handleMapClick(evt, selectSource)
    })
    
    const resizeHandler = () => map.updateSize()
    window.addEventListener('resize', resizeHandler)
    
    onUnmounted(() => {
      window.removeEventListener('resize', resizeHandler)
    })
  }
  
  const handleFeatureHover = async (hoverSource: any): Promise<void> => {
    hoverSource.clear()
    if (mapStore.map) {
      mapStore.map.getTargetElement().style.cursor = 'default'
    }
  }
  
  const handleMapClick = async (evt: any, selectSource: any): Promise<void> => {
    if (analysisStore.toolPanel?.activeTool === 'draw' && analysisStore.drawMode === 'point') {
      const coord = mapStore.map.getCoordinateFromPixel(evt.pixel)
      if (coord) {
        window.dispatchEvent(new CustomEvent('drawPointClick', { 
          detail: { coordinate: coord, pixel: evt.pixel } 
        }))
      }
      return
    }
    
    await handleNormalClick(selectSource)
  }

  const handleNormalClick = async (selectSource: any): Promise<void> => {
    selectSource.clear()
    mapStore.setSelectedFeature(null)
    mapStore.hidePopup()
  }

  const cleanup = (): void => {
    if (hoverTimer.value) {
      clearTimeout(hoverTimer.value)
    }
  }
  
  onUnmounted(cleanup)

  onMounted(() => {
    const drawCompleteHandler = (e: Event) => {
      console.log('useMap 收到绘制完成事件:', (e as CustomEvent).detail)
      layerManager.acceptDrawLayer((e as CustomEvent).detail)
    }
    
    const removeLayerHandler = (e: Event) => {
      console.log('useMap 收到移除图层事件:', (e as CustomEvent).detail)
      const { layer } = (e as CustomEvent).detail
      if (layer && mapStore.map) {
        try {
          mapStore.map.removeLayer(layer)
          console.log('图层已从地图中移除')
        } catch (error) {
          console.error('移除图层时出错:', error)
        }
      }
    }
    
    window.addEventListener('drawLayerCompleted', drawCompleteHandler)
    window.addEventListener('removeLayerRequested', removeLayerHandler)
    
    onUnmounted(() => {
      window.removeEventListener('drawLayerCompleted', drawCompleteHandler)
      window.removeEventListener('removeLayerRequested', removeLayerHandler)
    })
  })
  
  return {
    mapContainer,
    initMap,
    cleanup
  }
}
