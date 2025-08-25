import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export type SelectionMode = 'single' | 'area'

const useSelectionStore = defineStore('selection', () => {
  // 选择模式
  const selectionMode = ref<SelectionMode>('single')
  
  // 选择的要素
  const selectedFeatures = ref<any[]>([])
  const selectedFeatureIndex = ref<number>(-1)
  
  // 高亮要素
  const highlightedFeature = ref<any>(null)
  
  // 计算属性
  const hasSelectedFeatures = computed(() => selectedFeatures.value.length > 0)
  const currentSelectedFeature = computed(() => {
    if (selectedFeatureIndex.value >= 0 && selectedFeatureIndex.value < selectedFeatures.value.length) {
      return selectedFeatures.value[selectedFeatureIndex.value]
    }
    return null
  })
  
  // Actions
  function setSelectionMode(mode: SelectionMode) {
    selectionMode.value = mode
  }
  
  function addSelectedFeature(feature: any) {
    selectedFeatures.value.push(feature)
  }
  
  function setSelectedFeatures(features: any[]) {
    selectedFeatures.value = features
  }
  
  function setSelectedFeatureIndex(index: number) {
    selectedFeatureIndex.value = index
  }
  
  function setHighlightedFeature(feature: any) {
    highlightedFeature.value = feature
  }
  
  function clearSelection() {
    selectedFeatures.value = []
    selectedFeatureIndex.value = -1
    highlightedFeature.value = null
  }
  
  function removeSelectedFeature(index: number) {
    if (index >= 0 && index < selectedFeatures.value.length) {
      selectedFeatures.value.splice(index, 1)
      if (selectedFeatureIndex.value >= selectedFeatures.value.length) {
        selectedFeatureIndex.value = selectedFeatures.value.length - 1
      }
    }
  }
  
  function updateSelectedFeature(index: number, feature: any) {
    if (index >= 0 && index < selectedFeatures.value.length) {
      selectedFeatures.value[index] = feature
    }
  }
  
  return {
    // 状态
    selectionMode,
    selectedFeatures,
    selectedFeatureIndex,
    highlightedFeature,
    
    // 计算属性
    hasSelectedFeatures,
    currentSelectedFeature,
    
    // Actions
    setSelectionMode,
    addSelectedFeature,
    setSelectedFeatures,
    setSelectedFeatureIndex,
    setHighlightedFeature,
    clearSelection,
    removeSelectedFeature,
    updateSelectedFeature
  }
})

export { useSelectionStore }
export default useSelectionStore
