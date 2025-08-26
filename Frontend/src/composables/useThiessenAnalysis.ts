import { ref, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import { analysisAPI, type ThiessenParams } from '@/api/analysis'

interface PointInfo {
  id: string
  coordinates: string
}

interface GeoJSONFeatureCollection {
  type: 'FeatureCollection'
  features: any[]
}

export function useThiessenAnalysis() {
  const analysisStore = useAnalysisStore()

  const selectedPoints = ref<any[]>([])
  const extent = ref<[number, number, number, number] | undefined>(undefined)
  const thiessenResult = ref<GeoJSONFeatureCollection | null>(null)

  const pointsInfo = computed<PointInfo[]>(() => {
    return selectedPoints.value.map((feature: any, index: number) => {
      const geometry = feature?.getGeometry?.()
      const coords = geometry?.getCoordinates?.()
      return {
        id: `pt-${index + 1}`,
        coordinates: Array.isArray(coords) ? `${coords[0]}, ${coords[1]}` : ''
      }
    })
  })

  function setExtentFromText(text: string): void {
    const parts = text.split(',').map((t) => Number(t.trim()))
    extent.value = [parts[0], parts[1], parts[2], parts[3]] as [number, number, number, number]
  }

  function selectPoints(): void {
    analysisStore.setAnalysisStatus('请在地图上点选多个点（功能演示）')
  }

  function setPoints(features: any[]): void {
    selectedPoints.value = features
    analysisStore.setAnalysisStatus('点要素已更新')
  }

  function clearSelection(): void {
    selectedPoints.value = []
    thiessenResult.value = null
    analysisStore.setAnalysisStatus('')
  }

  async function executeThiessen(): Promise<void> {
    const pointsGeo = selectedPoints.value.map((feature: any) => {
      const coords = feature.getGeometry().getCoordinates()
      return { type: 'Point', coordinates: coords }
    })

    const params: ThiessenParams = { points: pointsGeo, extent: extent.value }
    const response = await analysisAPI.thiessenAnalysis(params)
    thiessenResult.value = response.data as GeoJSONFeatureCollection
    analysisStore.setAnalysisStatus('泰森多边形已生成')
  }

  return {
    pointsInfo,
    thiessenResult,
    selectPoints,
    setPoints,
    clearSelection,
    executeThiessen,
    setExtentFromText
  }
}


