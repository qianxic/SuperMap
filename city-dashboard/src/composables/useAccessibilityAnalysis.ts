import { ref, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'

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
    
    const props = centerPoint.value.getProperties()
    const geometry = centerPoint.value.getGeometry()
    const coords = geometry?.getCoordinates()
    
    return {
      name: props.name || '中心点',
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
    
    // 模拟可达性分析 - 计算从中心点能到达的范围
    const centerCoords = centerPoint.value.getGeometry().getCoordinates()
    
    // 根据交通方式和时间限制计算可达范围
    let speedFactor = 1 // 速度因子（米/分钟）
    switch (transportMode.value) {
      case 'walking':
        speedFactor = 50 // 50米/分钟
        break
      case 'cycling':
        speedFactor = 125 // 125米/分钟
        break
      case 'driving':
        speedFactor = 500 // 500米/分钟
        break
      case 'transit':
        speedFactor = 200 // 200米/分钟
        break
    }
    
    // 计算最大可达距离（取距离限制和时间限制的较小值）
    const timeBasedDistance = speedFactor * timeLimit.value
    const maxReachDistance = Math.min(maxDistance.value, timeBasedDistance)
    
    // 模拟可达性分析结果
    const coverageArea = Math.PI * Math.pow(maxReachDistance / 1000, 2) // 覆盖面积（平方公里）
    const reachablePoints = Math.round(coverageArea * 1000) // 可达点数量（假设每平方公里1000个点）
    const averageDistance = maxReachDistance * 0.7 // 平均距离
    
    analysisResult.value = {
      coverageArea: Math.round(coverageArea * 100) / 100,
      reachablePoints,
      averageDistance: Math.round(averageDistance),
      maxReachDistance: Math.round(maxReachDistance)
    }
    
    analysisStore.setAnalysisStatus(`可达性分析完成: 覆盖面积${coverageArea.toFixed(2)}平方公里，可达${reachablePoints}个点，最大距离${maxReachDistance.toFixed(0)}米`)
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
