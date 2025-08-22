import { ref, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import { analysisAPI } from '@/api/analysis'

interface PointInfo {
  name: string
  coordinates: string
  geometry: any
}

interface AccessibilityResult {
  coverageArea: number // 覆盖面积（平方公里）
  reachablePoints: number // 可达点数量
  averageDistance: number // 平均距离
  maxReachDistance: number // 最大可达距离
}

export function useAccessibilityAnalysis() {
  const analysisStore = useAnalysisStore()
  
  const centerPoint = ref<any>(null) // ol.Feature
  const maxDistance = ref<number>(1000)
  const transportMode = ref<'walking' | 'cycling' | 'driving' | 'transit'>('walking')
  const timeLimit = ref<number>(30)
  const analysisResult = ref<AccessibilityResult | null>(null)
  
  const centerPointInfo = computed<PointInfo | null>(() => {
    if (!centerPoint.value) return null
    
    const geometry = centerPoint.value.getGeometry()
    const coords = geometry?.getCoordinates()
    
    return {
      name: '中心点',
      coordinates: coords ? `${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}` : '未知坐标',
      geometry: geometry
    }
  })
  
  const setCenterPoint = (feature: any | null): void => {
    centerPoint.value = feature
    if (feature) {
      analysisStore.setAnalysisStatus('中心点已选择，可以执行可达性分析')
    } else {
      analysisStore.setAnalysisStatus('请选择中心点')
    }
  }
  
  const executeAccessibilityAnalysis = async (): Promise<void> => {
    if (!centerPoint.value) {
      analysisStore.setAnalysisStatus('请先选择中心点')
      return
    }
    
    try {
      analysisStore.setAnalysisStatus('正在执行可达性分析...')
      
      // 准备API参数
      const centerCoords = centerPoint.value.getGeometry().getCoordinates()
      const params = {
        centerPoint: {
          type: 'Point',
          coordinates: centerCoords
        },
        maxDistance: maxDistance.value,
        transportMode: transportMode.value,
        timeLimit: timeLimit.value
      }
      
      // 调用后端API
      const response = await analysisAPI.accessibilityAnalysis(params)
      
      if (response.success && response.data) {
        analysisResult.value = response.data
        analysisStore.setAnalysisStatus(`可达性分析完成: 覆盖面积${response.data.coverageArea}平方公里，可达${response.data.reachablePoints}个点，最大距离${response.data.maxReachDistance}米`)
      } else {
        analysisStore.setAnalysisStatus(`分析失败: ${response.error}`)
      }
    } catch (error) {
      analysisStore.setAnalysisStatus(`分析失败: ${error instanceof Error ? error.message : '未知错误'}`)
    }
  }
  
  const selectCenterPoint = (): void => {
    analysisStore.setAnalysisStatus('请在地图上点击选择中心点（功能已禁用，仅UI演示）')
  }
  
  const clearSelection = (): void => {
    centerPoint.value = null
    analysisResult.value = null
    analysisStore.setAnalysisStatus('')
  }
  
  return {
    centerPointInfo,
    maxDistance,
    transportMode,
    timeLimit,
    analysisResult,
    setCenterPoint,
    selectCenterPoint,
    clearSelection,
    executeAccessibilityAnalysis
  }
}
