import { ref, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'

interface PointInfo {
  name: string
  coordinates: string
  geometry: any
}

interface PathResult {
  distance: number
  duration: number
  pathType: string
}

export function useDistanceAnalysis() {
  const analysisStore = useAnalysisStore()
  
  const startPoint = ref<any>(null) // ol.Feature
  const endPoint = ref<any>(null) // ol.Feature
  const pathType = ref<'shortest' | 'fastest' | 'scenic'>('shortest')
  const transportMode = ref<'walking' | 'cycling' | 'driving' | 'transit'>('walking')
  const analysisResult = ref<PathResult | null>(null)
  
  const startPointInfo = computed<PointInfo | null>(() => {
    if (!startPoint.value) return null
    
    const geometry = startPoint.value.getGeometry()
    const coords = geometry?.getCoordinates()
    
    return {
      name: '起始点',
      coordinates: coords ? `${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}` : '未知坐标',
      geometry: geometry
    }
  })
  
  const endPointInfo = computed<PointInfo | null>(() => {
    if (!endPoint.value) return null
    
    const geometry = endPoint.value.getGeometry()
    const coords = geometry?.getCoordinates()
    
    return {
      name: '目标点',
      coordinates: coords ? `${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}` : '未知坐标',
      geometry: geometry
    }
  })
  
  const setStartPoint = (feature: any | null): void => {
    startPoint.value = feature
    if (feature) {
      analysisStore.setAnalysisStatus('起始点已选择，请选择目标点')
    } else {
      analysisStore.setAnalysisStatus('请选择起始点')
    }
  }
  
  const setEndPoint = (feature: any | null): void => {
    endPoint.value = feature
    if (feature) {
      analysisStore.setAnalysisStatus('目标点已选择，可以计算最优路径')
    } else {
      analysisStore.setAnalysisStatus('请选择目标点')
    }
  }
  
  const executePathAnalysis = async (): Promise<void> => {
    if (!startPoint.value || !endPoint.value) {
      analysisStore.setAnalysisStatus('请先选择起始点和目标点')
      return
    }
    
    // 模拟路径计算
    const startCoords = startPoint.value.getGeometry().getCoordinates()
    const endCoords = endPoint.value.getGeometry().getCoordinates()
    
    // 基础距离计算
    const dx = endCoords[0] - startCoords[0]
    const dy = endCoords[1] - startCoords[1]
    let baseDistance = Math.sqrt(dx * dx + dy * dy) * 111000 // 转换为米
    
    let distance = 0
    let duration = 0
    let pathTypeName = ''
    
    switch (pathType.value) {
      case 'shortest':
        distance = baseDistance
        pathTypeName = '最短路径'
        break
      case 'fastest':
        distance = baseDistance * 1.2 // 可能绕行
        pathTypeName = '最快路径'
        break
      case 'scenic':
        distance = baseDistance * 1.5 // 风景路线更长
        pathTypeName = '风景路径'
        break
    }
    
    // 根据交通方式调整时间
    switch (transportMode.value) {
      case 'walking':
        duration = Math.round(distance / 1000 * 20) // 20分钟/公里
        break
      case 'cycling':
        duration = Math.round(distance / 1000 * 8) // 8分钟/公里
        break
      case 'driving':
        duration = Math.round(distance / 1000 * 2) // 2分钟/公里
        break
      case 'transit':
        duration = Math.round(distance / 1000 * 15) // 15分钟/公里
        break
    }
    
    analysisResult.value = {
      distance: Math.round(distance),
      duration: duration,
      pathType: pathTypeName
    }
    
    analysisStore.setAnalysisStatus(`路径分析完成: ${distance.toFixed(0)}米，预计耗时${duration}分钟`)
  }
  
  const selectStartPoint = (): void => {
    analysisStore.setAnalysisStatus('请在地图上点击选择起始点（功能已禁用，仅UI演示）')
  }
  
  const selectEndPoint = (): void => {
    analysisStore.setAnalysisStatus('请在地图上点击选择目标点（功能已禁用，仅UI演示）')
  }
  
  const clearSelection = (): void => {
    startPoint.value = null
    endPoint.value = null
    analysisResult.value = null
    analysisStore.setAnalysisStatus('')
  }
  
  return {
    startPointInfo,
    endPointInfo,
    pathType,
    transportMode,
    analysisResult,
    setStartPoint,
    setEndPoint,
    selectStartPoint,
    selectEndPoint,
    clearSelection,
    executePathAnalysis
  }
}
