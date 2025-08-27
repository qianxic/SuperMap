import { ref, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useMapStore } from '@/stores/mapStore'
import type { FeatureInfo } from '@/types/map'

type GeometryType = 'Point' | 'LineString' | 'Polygon' | 'MultiPoint' | 'MultiLineString' | 'MultiPolygon' | string;

export function useBufferAnalysis() {
  const analysisStore = useAnalysisStore()
  const mapStore = useMapStore()
  
  const selectedFeature = ref<any>(null) // ol.Feature
  const bufferDistance = ref<number>(100)
  const selectedAnalysisLayerId = ref<string>('')
  
  const selectedFeatureInfo = computed<FeatureInfo | null>(() => {
    if (!selectedFeature.value) return null
    
    const geometry = selectedFeature.value.getGeometry()
    const coords = geometry?.getCoordinates()
    
    return {
      name: '选中要素',
      coordinates: coords ? `${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}` : '未知坐标',
      geometry: geometry
    }
  })
  
  // 选中图层信息
  const selectedAnalysisLayerInfo = computed(() => {
    if (!selectedAnalysisLayerId.value) return null
    
    const layer = mapStore.vectorLayers.find(l => l.id === selectedAnalysisLayerId.value)
    if (!layer) return null
    
    return {
      id: layer.id,
      name: layer.name,
      type: layer.type,
      layer: layer.layer
    }
  })
  
  // 图层选项
  const layerOptions = computed(() => {
    const visibleLayers = mapStore.vectorLayers.filter(layer => layer.layer && layer.layer.getVisible())
    return visibleLayers.map(layer => ({ 
      value: layer.id, 
      label: layer.name, 
      disabled: false 
    }))
  })
  
  const getGeometryType = (type: GeometryType): string => {
    const typeMap: Record<string, string> = {
      'Point': '点',
      'LineString': '线',
      'Polygon': '面',
      'MultiPoint': '多点',
      'MultiLineString': '多线',  
      'MultiPolygon': '多面'
    }
    return typeMap[type] || type || ''
  }
  
  const setSelectedFeature = (feature: any | null): void => { // ol.Feature
    selectedFeature.value = feature
    if (feature) {
      analysisStore.setAnalysisStatus('要素选择功能已禁用（仅UI演示）')
    } else {
      analysisStore.setAnalysisStatus('未选择要素')
    }
  }
  
  // 设置选中的分析图层
  const setSelectedAnalysisLayer = (layerId: string): void => {
    selectedAnalysisLayerId.value = layerId
    if (layerId) {
      const layer = mapStore.vectorLayers.find(l => l.id === layerId)
      if (layer) {
        analysisStore.setAnalysisStatus(`已选择分析图层: ${layer.name}`)
      }
    } else {
      analysisStore.setAnalysisStatus('未选择分析图层')
    }
  }
  
  const executeBufferAnalysis = async (): Promise<void> => {
    if (!selectedFeature.value) {
      analysisStore.setAnalysisStatus('请先选择要素')
      return
    }
    
    if (!selectedAnalysisLayerId.value) {
      analysisStore.setAnalysisStatus('请先选择分析图层')
      return
    }
    
    if (bufferDistance.value <= 0) {
      analysisStore.setAnalysisStatus('缓冲距离必须大于0')
      return
    }
    
    analysisStore.setAnalysisStatus('缓冲区分析功能已禁用（仅UI演示）')
  }
  
  const selectFeatureFromMap = (): void => {
    analysisStore.setAnalysisStatus('要素选择功能已禁用（仅UI演示）')
  }
  
  const clearMapSelection = (): void => {
    // 功能已禁用
  }
  
  // 清除所有选择状态
  const clearAllSelections = (): void => {
    selectedFeature.value = null
    selectedAnalysisLayerId.value = ''
    analysisStore.setAnalysisStatus('已清除所有选择')
  }
  
  return {
    selectedFeature,
    bufferDistance,
    selectedAnalysisLayerId,
    selectedFeatureInfo,
    selectedAnalysisLayerInfo,
    layerOptions,
    setSelectedFeature,
    setSelectedAnalysisLayer,
    selectFeatureFromMap,
    clearMapSelection,
    clearAllSelections,
    executeBufferAnalysis
  }
}
