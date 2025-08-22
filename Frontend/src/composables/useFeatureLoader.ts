import { ref, computed } from 'vue'
import { superMapClient } from '@/api/supermap'
import type { Feature, FeatureListInfo, GeometryType } from '@/types/map'
import { handleError } from '@/utils/notification'

export function useFeatureLoader() {
  const isLoading = ref<boolean>(false)
  const loadingProgress = ref<{ loaded: number, total: number }>({ loaded: 0, total: 0 })
  const features = ref<Feature[]>([])
  const currentDataset = ref<string>('')
  const featureListInfo = ref<FeatureListInfo | null>(null)

  // 计算属性
  const loadingPercentage = computed(() => {
    if (loadingProgress.value.total === 0) return 0
    return Math.round((loadingProgress.value.loaded / loadingProgress.value.total) * 100)
  })

  const hasFeatures = computed(() => features.value.length > 0)

  const featuresByType = computed(() => {
    const grouped: Record<GeometryType, Feature[]> = {
      'POINT': [],
      'LINE': [],
      'POLYGON': []
    }
    
    features.value.forEach(feature => {
      if (feature.geometry && feature.geometry.type) {
        const type = feature.geometry.type.toUpperCase() as GeometryType
        if (grouped[type]) {
          grouped[type].push(feature)
        }
      }
    })
    
    return grouped
  })

  // 重置状态
  const resetState = () => {
    isLoading.value = false
    loadingProgress.value = { loaded: 0, total: 0 }
    features.value = []
    currentDataset.value = ''
    featureListInfo.value = null
  }

  /**
   * 获取数据集的要素列表信息
   * @param datasetName 数据集名称
   */
  const getFeaturesList = async (datasetName: string): Promise<FeatureListInfo | null> => {
    try {
      isLoading.value = true
      const result = await superMapClient.getFeaturesList(datasetName)
      
      if (result.success && result.data) {
        featureListInfo.value = result.data
        return result.data
      } else {
        handleError(new Error(result.error || '获取要素列表失败'), '要素列表查询')
        return null
      }
    } catch (error) {
      handleError(error as Error, '要素列表查询')
      return null
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 加载数据集的所有要素
   * @param datasetName 数据集名称
   * @param batchSize 批次大小
   */
  const loadAllFeatures = async (datasetName: string, batchSize: number = 999999) => {
    try {
      resetState()
      isLoading.value = true
      currentDataset.value = datasetName

      console.log(`开始加载数据集: ${datasetName}`)

      const result = await superMapClient.getAllFeatures(
        datasetName,
        batchSize,
        (loaded, total) => {
          loadingProgress.value = { loaded, total }
          console.log(`加载进度: ${loaded}/${total} (${Math.round(loaded/total*100)}%)`)
        }
      )

      if (result.success && result.data) {
        features.value = result.data
        console.log(`数据集 ${datasetName} 加载完成，共 ${result.data.length} 个要素`)
        
        // 统计不同几何类型的要素数量
        const stats = featuresByType.value
        console.log('要素统计:', {
          points: stats.POINT.length,
          lines: stats.LINE.length, 
          polygons: stats.POLYGON.length
        })
        
        return result.data
      } else {
        handleError(new Error(result.error || '加载要素失败'), '要素加载')
        return []
      }
    } catch (error) {
      handleError(error as Error, '要素加载')
      return []
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 加载指定范围的要素
   * @param datasetName 数据集名称
   * @param startIndex 起始索引
   * @param endIndex 结束索引
   */
  const loadFeatureRange = async (
    datasetName: string, 
    startIndex: number, 
    endIndex: number
  ): Promise<Feature[]> => {
    try {
      isLoading.value = true
      currentDataset.value = datasetName

      console.log(`加载要素范围: ${datasetName}[${startIndex}-${endIndex}]`)

      const result = await superMapClient.getFeaturesBatch(datasetName, startIndex, endIndex)

      if (result.success && result.data) {
        // 如果是同一个数据集，追加到现有要素中
        if (currentDataset.value === datasetName) {
          features.value.push(...result.data)
        } else {
          features.value = result.data
        }
        
        console.log(`要素范围加载完成，获取 ${result.data.length} 个要素`)
        return result.data
      } else {
        handleError(new Error(result.error || '加载要素范围失败'), '要素范围加载')
        return []
      }
    } catch (error) {
      handleError(error as Error, '要素范围加载')
      return []
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 根据几何类型过滤要素
   * @param geometryType 几何类型
   */
  const getFeaturesByType = (geometryType: GeometryType): Feature[] => {
    return featuresByType.value[geometryType] || []
  }

  /**
   * 根据属性过滤要素
   * @param property 属性名
   * @param value 属性值
   */
  const getFeaturesByProperty = (property: string, value: any): Feature[] => {
    return features.value.filter(feature => 
      feature.properties && feature.properties[property] === value
    )
  }

  /**
   * 搜索要素（根据属性值模糊匹配）
   * @param searchText 搜索文本
   * @param properties 搜索的属性字段列表
   */
  const searchFeatures = (searchText: string, properties: string[] = []): Feature[] => {
    if (!searchText.trim()) return features.value

    const searchLower = searchText.toLowerCase()
    
    return features.value.filter(feature => {
      if (!feature.properties) return false
      
      // 如果没有指定属性，搜索所有属性
      const searchProps = properties.length > 0 ? properties : Object.keys(feature.properties)
      
      return searchProps.some(prop => {
        const value = feature.properties[prop]
        return value && String(value).toLowerCase().includes(searchLower)
      })
    })
  }

  /**
   * 清除加载的要素
   */
  const clearFeatures = () => {
    resetState()
  }

  return {
    // 状态
    isLoading,
    loadingProgress,
    loadingPercentage,
    features,
    currentDataset,
    featureListInfo,
    hasFeatures,
    featuresByType,

    // 方法
    getFeaturesList,
    loadAllFeatures,
    loadFeatureRange,
    getFeaturesByType,
    getFeaturesByProperty,
    searchFeatures,
    clearFeatures,
    resetState
  }
}