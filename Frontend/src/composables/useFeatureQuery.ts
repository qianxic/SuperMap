import { computed } from 'vue'
import { useFeatureQueryStore } from '@/stores/featureQueryStore'

export function useFeatureQuery() {
  const store = useFeatureQueryStore()
  
  return {
    // 状态（computed 形式，保持与原 API 兼容）
    selectedLayerId: computed({ get: () => store.selectedLayerId, set: v => (store.selectedLayerId = v) }),
    queryResults: computed(() => store.queryResults),
    layerFields: computed(() => store.layerFields),
    queryConfig: computed(() => store.queryConfig),
    isQuerying: computed(() => store.isQuerying),
    lastExecutedQuery: computed(() => store.lastExecutedQuery),
    selectedFeatureIndex: computed({ get: () => store.selectedFeatureIndex, set: v => (store.selectedFeatureIndex = v) }),
    highlightedFeature: computed(() => store.highlightedFeature),
    
    // 查询执行
    executeQuery: store.executeQuery,
    getLayerFields: store.getLayerFields,
    highlightQueryResults: store.highlightQueryResults,
    
    // 要素选择功能
    handleSelectFeature: store.handleSelectFeature,
    highlightFeatureOnMap: store.highlightFeatureOnMap,
    triggerMapFeatureHighlight: store.triggerMapFeatureHighlight,
    removeHighlightFeature: store.removeHighlightFeature,
    isSameFeature: store.isSameFeature,
    
    // 点击事件管理
    setupClickOnSelectedFeatures: store.setupClickOnSelectedFeatures,
    
    // 自动滚动功能
    initAutoScroll: store.initAutoScroll,
    scrollToSelectedFeature: store.scrollToSelectedFeature,
    
    // 事件管理
    clearSelectionInteractions: store.clearSelectionInteractions,
    
    // 图层管理
    clearSelectedLayer: store.clearSelectedLayer,
    invertSelectedLayer: store.invertSelectedLayer,
    getLayerOptions: store.getLayerOptions,
    getSelectedLayerName: store.getSelectedLayerName,
    getLayerFeatureCount: store.getLayerFeatureCount
  }
}
