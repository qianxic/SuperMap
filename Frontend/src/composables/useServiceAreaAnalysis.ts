import { ref, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import { analysisAPI } from '@/api/analysis'

interface CenterPointInfo {
  id: string
  coordinates: string
  radius: number
}

interface GeoJSONFeatureCollection {
  type: 'FeatureCollection'
  features: any[]
}

export function useServiceAreaAnalysis() {
  const analysisStore = useAnalysisStore()

  const selectedCenters = ref<any[]>([])
  const baseRadius = ref<number>(400)
  const radiusStep = ref<number>(100)
  const serviceAreaResult = ref<GeoJSONFeatureCollection | null>(null)

  const centersInfo = computed<CenterPointInfo[]>(() => {
    return selectedCenters.value.map((feature: any, index: number) => {
      const geometry = feature?.getGeometry?.()
      const coords = geometry?.getCoordinates?.()
      const radius = baseRadius.value + index * radiusStep.value
      return {
        id: `center-${index + 1}`,
        coordinates: Array.isArray(coords) ? `${coords[0]}, ${coords[1]}` : '',
        radius
      }
    })
  })

  function selectCenters(): void {
    analysisStore.setAnalysisStatus('请在地图上依次选择服务中心点')
  }

  function setCenters(features: any[]): void {
    selectedCenters.value = features
    analysisStore.setAnalysisStatus('服务中心点已更新')
  }

  function clearSelection(): void {
    selectedCenters.value = []
    serviceAreaResult.value = null
    analysisStore.setAnalysisStatus('')
  }

  async function executeServiceArea(): Promise<void> {
    const buffers = [] as any[]
    for (let i = 0; i < selectedCenters.value.length; i += 1) {
      const center = selectedCenters.value[i]
      const coords = center.getGeometry().getCoordinates()
      const distance = baseRadius.value + i * radiusStep.value
      const response = await analysisAPI.bufferAnalysis({
        geometry: { type: 'Point', coordinates: coords },
        distance,
        unit: 'meters'
      })
      if (response.success && response.data) {
        buffers.push(response.data)
      }
    }

    serviceAreaResult.value = {
      type: 'FeatureCollection',
      features: buffers as any[]
    }
    analysisStore.setAnalysisStatus('服务区分析已生成')
  }

  return {
    centersInfo,
    serviceAreaResult,
    baseRadius,
    radiusStep,
    selectCenters,
    setCenters,
    clearSelection,
    executeServiceArea
  }
}


