import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const useAreaSelectionStore = defineStore('areaSelection', () => {
  const selectedFeatures = ref<any[]>([])
  const selectedFeatureIndex = ref<number>(-1)
  const highlightedFeature = ref<any>(null)

  const hasSelected = computed(() => selectedFeatures.value.length > 0)
  const current = computed(() => {
    if (selectedFeatureIndex.value >= 0 && selectedFeatureIndex.value < selectedFeatures.value.length) {
      return selectedFeatures.value[selectedFeatureIndex.value]
    }
    return null
  })

  function setSelectedFeatures(features: any[]) {
    selectedFeatures.value = features
  }

  function setSelectedFeatureIndex(index: number) {
    selectedFeatureIndex.value = index
  }

  function setHighlightedFeature(feature: any) {
    highlightedFeature.value = feature
  }

  function clear() {
    selectedFeatures.value = []
    selectedFeatureIndex.value = -1
    highlightedFeature.value = null
  }

  return {
    selectedFeatures,
    selectedFeatureIndex,
    highlightedFeature,
    hasSelected,
    current,
    setSelectedFeatures,
    setSelectedFeatureIndex,
    setHighlightedFeature,
    clear
  }
})

export { useAreaSelectionStore }
export default useAreaSelectionStore


