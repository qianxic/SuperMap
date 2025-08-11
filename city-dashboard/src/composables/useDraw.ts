import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useMapStore } from '@/stores/mapStore'

type DrawType = 'Point' | 'LineString' | 'Polygon';

export function useDraw() {
  const analysisStore = useAnalysisStore()
  const mapStore = useMapStore()
  
  const drawInteraction = ref<any>(null) // ol.interaction.Draw
  const drawSource = ref<any>(null) // ol.source.Vector
  
  const createDrawLayerStyle = (): any => { // ol.style.Style
    return new ol.style.Style({
      image: new ol.style.Circle({
        radius: 8,
        fill: new ol.style.Fill({ color: '#42a5f5' }),
        stroke: new ol.style.Stroke({ color: '#ffffff', width: 2 })
      }),
      stroke: new ol.style.Stroke({
        color: '#42a5f5',
        width: 3
      }),
      fill: new ol.style.Fill({
        color: 'rgba(66, 165, 245, 0.2)'
      })
    })
  }
  
  const initDrawLayer = (): void => {
    if (!mapStore.map) return
    
    const source = new ol.source.Vector()
    const layer = new ol.layer.Vector({
      source: source,
      style: createDrawLayerStyle(),
      zIndex: 1000
    })
    
    mapStore.map.addLayer(layer)
    drawSource.value = source
  }
  
  const setupDrawInteraction = (): void => {
    removeDrawInteraction()
    const map = mapStore.map
    if (!map || !drawSource.value) return
    
    const drawMode = analysisStore.drawMode
    
    let drawType: DrawType | undefined;
    if (drawMode === 'point') drawType = 'Point'
    else if (drawMode === 'line') drawType = 'LineString'
    else if (drawMode === 'polygon') drawType = 'Polygon'
    else return
    
    const draw = new ol.interaction.Draw({
      source: drawSource.value,
      type: drawType
    })
      
    draw.on('drawend', (event: any) => { // ol.interaction.DrawEvent
      setTimeout(() => {
        if (drawSource.value) {
          drawSource.value.removeFeature(event.feature)
        }
      }, 1000)
    })
      
    map.addInteraction(draw)
    drawInteraction.value = draw
  }
  
  const removeDrawInteraction = (): void => {
    const map = mapStore.map
    if (map && drawInteraction.value) {
      map.removeInteraction(drawInteraction.value)
      drawInteraction.value = null
    }
  }

  const clearDrawing = (): void => {
    if (drawSource.value) {
      drawSource.value.clear()
    }
  }

  watch(() => analysisStore.drawMode, (newMode) => {
    if (analysisStore.toolPanel?.activeTool === 'draw' && drawSource.value) {
      if (newMode) {
        setupDrawInteraction()
      } else {
        removeDrawInteraction()
      }
    }
  })
  
  watch(() => analysisStore.toolPanel?.activeTool, (tool) => {
    if (tool !== 'draw') {
      removeDrawInteraction()
    } else if (tool === 'draw') {
      initDrawLayer()
    }
  })
  
  onMounted(() => {
  })
  
  onUnmounted(() => {
    removeDrawInteraction()
  })
  
  return {
    drawInteraction,
    drawSource,
    setupDrawInteraction,
    removeDrawInteraction,
    initDrawLayer,
    clearDrawing
  }
}
