import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useMapStore } from '@/stores/mapStore'

export function useFeatureQuery() {
  const analysisStore = useAnalysisStore()
  const mapStore = useMapStore()
  
  const selectedLayerId = ref<string>('')
  const queryKeyword = ref<string>('')
  const queryResults = ref<any[]>([])
  
  // 查询要素
  const queryFeatures = (layerId: string, keyword: string) => {
    if (!layerId || !keyword.trim()) {
      return []
    }
    
    const layer = mapStore.vectorLayers.find(l => l.id === layerId)
    if (!layer || !layer.layer) {
      return []
    }
    
    try {
      const source = layer.layer.getSource()
      if (!source) return []
      
      const features = source.getFeatures()
      const results = features.filter(feature => {
        const properties = feature.getProperties()
        // 在所有属性中搜索关键字
        return Object.values(properties).some(value => 
          String(value).toLowerCase().includes(keyword.toLowerCase())
        )
      })
      
      queryResults.value = results
      return results
    } catch (error) {
      console.error('查询要素时出错:', error)
      return []
    }
  }
  
  // 清空选中图层
  const clearSelectedLayer = (layerId: string) => {
    if (!layerId) return
    
    const layer = mapStore.vectorLayers.find(l => l.id === layerId)
    if (!layer || !layer.layer) return
    
    try {
      // 这里可以添加清空选中图层的逻辑
      // 例如清除选择状态、重置样式等
      console.log(`清空图层 ${layer.name} 的选中状态`)
    } catch (error) {
      console.error('清空选中图层时出错:', error)
    }
  }
  
  // 反选当前图层
  const invertSelectedLayer = (layerId: string) => {
    if (!layerId) return
    
    const layer = mapStore.vectorLayers.find(l => l.id === layerId)
    if (!layer || !layer.layer) return
    
    try {
      // 这里可以添加反选图层的逻辑
      // 例如切换选择状态、更新样式等
      console.log(`反选图层 ${layer.name}`)
    } catch (error) {
      console.error('反选图层时出错:', error)
    }
  }
  
  // 获取图层选项
  const getLayerOptions = () => {
    return mapStore.vectorLayers
      .filter(layer => layer.layer && layer.layer.getVisible())
      .map(layer => ({
        value: layer.id,
        label: layer.name,
        disabled: false
      }))
  }
  
  // 获取选中图层名称
  const getSelectedLayerName = (layerId: string) => {
    const layer = mapStore.vectorLayers.find(l => l.id === layerId)
    return layer ? layer.name : ''
  }
  
  return {
    selectedLayerId,
    queryKeyword,
    queryResults,
    queryFeatures,
    clearSelectedLayer,
    invertSelectedLayer,
    getLayerOptions,
    getSelectedLayerName
  }
}
