import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { QueryConfig } from '@/types/query'

export type SelectionMode = 'single' | 'area'

const useSelectionStore = defineStore('selection', () => {
  // 选择模式
  const selectionMode = ref<SelectionMode>('single')
  
  // 选择的要素
  const selectedFeatures = ref<any[]>([])
  const selectedFeatureIndex = ref<number>(-1)
  
  // 高亮要素
  const highlightedFeature = ref<any>(null)

  // 按属性查询的持久化状态
  const querySelectedLayerId = ref<string>('')
  const queryConfig = ref<QueryConfig>({
    condition: {
      fieldName: '',
      operator: 'eq',
      value: ''
    }
  })
  
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

  // 清除地图上的点击选择高亮
  function clearClickSelection() {
    // 这个方法需要在外部调用时传入 mapStore
    // 这里只清除本地状态，地图高亮清除在外部处理
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

  // 按属性查询：设置/获取图层与条件
  function setQuerySelectedLayerId(layerId: string) {
    querySelectedLayerId.value = layerId
  }

  function setQueryConfig(config: QueryConfig) {
    queryConfig.value = config
  }
  
  return {
    // 状态
    selectionMode,
    selectedFeatures,
    selectedFeatureIndex,
    highlightedFeature,
    querySelectedLayerId,
    queryConfig,
    
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
    updateSelectedFeature,
    setQuerySelectedLayerId,
    setQueryConfig,
    clearClickSelection
  }
})

export { useSelectionStore }
export default useSelectionStore
