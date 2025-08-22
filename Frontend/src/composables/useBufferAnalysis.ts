import { ref, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import type { FeatureInfo } from '@/types/map'

type GeometryType = 'Point' | 'LineString' | 'Polygon' | 'MultiPoint' | 'MultiLineString' | 'MultiPolygon' | string;

export function useBufferAnalysis() {
  const analysisStore = useAnalysisStore()
  
  const selectedFeature = ref<any>(null) // ol.Feature
  const bufferDistance = ref<number>(100)
  
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
  
  const executeBufferAnalysis = async (): Promise<void> => {
    if (!selectedFeature.value) {
      analysisStore.setAnalysisStatus('请先选择要素')
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
  
  return {
    selectedFeature,
    bufferDistance,
    selectedFeatureInfo,
    setSelectedFeature,
    selectFeatureFromMap,
    clearMapSelection,
    executeBufferAnalysis
  }
}
