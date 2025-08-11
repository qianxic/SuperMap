import { ref, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import type { FeatureInfo } from '@/types/map'

type GeometryType = 'Point' | 'LineString' | 'Polygon' | 'MultiPoint' | 'MultiLineString' | 'MultiPolygon' | string;

export function useBufferAnalysis() {
  const analysisStore = useAnalysisStore()
  
  const selectedFeature = ref<any>(null) // ol.Feature
  const bufferDistance = ref<number>(100)
  
  const featureInfo = computed<FeatureInfo | null>(() => {
    if (!selectedFeature.value) return null
    
    const props = selectedFeature.value.getProperties()
    const geometry = selectedFeature.value.getGeometry()
    
    return {
      id: props.id || '未知',
      name: props.name || '未命名要素',
      type: getGeometryType(geometry?.getType()),
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
    featureInfo,
    setSelectedFeature,
    selectFeatureFromMap,
    clearMapSelection,
    executeBufferAnalysis
  }
}
