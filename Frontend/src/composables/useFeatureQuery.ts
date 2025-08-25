import { ref, reactive, computed, nextTick } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useMapStore } from '@/stores/mapStore'
import { useSelectionStore } from '@/stores/selectionStore'
import type { QueryCondition, QueryConfig, FieldInfo } from '@/types/query'
import { createAutoScroll } from '@/utils/autoScroll'

// 定义要素类型
interface Feature {
  getProperties(): Record<string, any>
  getGeometry(): any
  getId(): string | number | null
}

// 查询结果接口
interface QueryResult {
  success: boolean
  data: any[]
  totalCount: number
  queryType: 'frontend' | 'sql'
  error?: string
}

export function useFeatureQuery() {
  const analysisStore = useAnalysisStore()
  const mapStore = useMapStore()
  const selectionStore = useSelectionStore()
  
  // 使用 reactive 管理查询配置
  const queryConfig = reactive<QueryConfig>({
    condition: {
      fieldName: '',
      operator: 'eq',
      value: ''
    }
  })
  
  const selectedLayerId = ref<string>('')
  const queryResults = ref<any[]>([])
  const layerFields = ref<FieldInfo[]>([])
  const isQuerying = ref<boolean>(false)
  const lastExecutedQuery = ref<string>('')
  
  // 集成要素选择功能的状态
  const selectedFeatureIndex = computed({
    get: () => selectionStore.selectedFeatureIndex,
    set: (value) => selectionStore.setSelectedFeatureIndex(value)
  })
  
  const highlightedFeature = ref<any>(null)
  
  // 设置点击已选择要素的处理
  const setupClickOnSelectedFeatures = () => {
    if (!mapStore.map) return

    const clickHandler = (evt: any) => {
      const pixel = evt.pixel
      
      // 检查是否点击到了已选择的要素
      const clickedFeature = mapStore.map.forEachFeatureAtPixel(
        pixel,
        (feature: any, layer: any) => {
          if (layer === mapStore.selectLayer) {
            return feature
          }
          return undefined
        },
        { hitTolerance: 5 }
      )

      if (clickedFeature) {
        // 阻止默认的要素信息窗口弹出
        evt.preventDefault()
        evt.stopPropagation()

        // 在已选择的要素列表中查找对应的要素
        const selectedFeatureIndex = findSelectedFeatureIndex(clickedFeature)

        if (selectedFeatureIndex !== -1) {
          // 高亮对应的列表项
          handleSelectFeature(selectedFeatureIndex)
          
          // 显示橙色常亮效果
          triggerMapFeatureHighlight(queryResults.value[selectedFeatureIndex])
          
          analysisStore.setAnalysisStatus(`已选择要素 ${selectedFeatureIndex + 1}`)
        }

        return false
      }
    }

    // 添加点击事件监听
    mapStore.map.on('click', clickHandler)
    
    // 保存事件处理器引用，以便后续移除
    mapStore.map._queryToolsClickHandler = clickHandler
  }

  // 清除选择交互
  const clearSelectionInteractions = () => {
    if (!mapStore.map) return

    // 移除点击事件监听
    if (mapStore.map._queryToolsClickHandler) {
      mapStore.map.un('click', mapStore.map._queryToolsClickHandler)
      delete mapStore.map._queryToolsClickHandler
    }
  }

  // 在已选择的要素中查找对应的索引
  const findSelectedFeatureIndex = (clickedFeature: any): number => {
    return queryResults.value.findIndex(feature => {
      return isSameFeature(feature, clickedFeature)
    })
  }

  // 自动滚动实例
  let autoScrollInstance: any = null

  // 初始化自动滚动
  const initAutoScroll = () => {
    const resultList = document.querySelector('.query-results') as HTMLElement
    if (resultList && !autoScrollInstance) {
      autoScrollInstance = createAutoScroll(resultList, {
        scrollBehavior: 'smooth',
        centerOnSelect: true,
        scrollOffset: 0
      })
      
      // 添加滚动监听器
      if (autoScrollInstance) {
        autoScrollInstance.addScrollListener((scrollInfo: any) => {
          console.log('查询结果滚动信息:', scrollInfo)
        })
      }
    }
  }

  // 自动滚动到选中的要素位置
  const scrollToSelectedFeature = async (index: number) => {
    try {
      // 确保自动滚动实例已初始化
      if (!autoScrollInstance) {
        initAutoScroll()
      }
      
      if (autoScrollInstance) {
        const success = await autoScrollInstance.scrollToIndex(index)
        if (success) {
          console.log(`成功滚动到查询结果索引 ${index}`)
        } else {
          console.error(`滚动到查询结果索引 ${index} 失败`)
        }
      } else {
        console.error('查询结果自动滚动实例未初始化')
      }
    } catch (error) {
      console.error('查询结果自动滚动失败:', error)
    }
  }
  
  // 获取图层字段结构 - 从已加载的OpenLayers要素中获取
  const getLayerFields = async (layerId: string) => {
    console.log('开始获取图层字段结构:', layerId)
    
    if (!layerId) {
      console.log('图层ID为空，清空字段结构')
      layerFields.value = []
      return []
    }
    
    const layer = mapStore.vectorLayers.find(l => l.id === layerId)
    if (!layer || !layer.layer) {
      console.log('未找到图层或图层对象:', layerId)
      layerFields.value = []
      return []
    }
    
    try {
      // 从已加载的要素中获取字段结构
      const source = layer.layer.getSource()
      if (source) {
        const features = source.getFeatures()
        if (features.length > 0) {
          const firstFeature = features[0]
          const properties = firstFeature.getProperties()
          console.log('从已加载要素获取字段结构:', properties)
          
          const fields: FieldInfo[] = []
          Object.keys(properties).forEach(key => {
            if (key !== 'geometry') {
              const value = properties[key]
              const fieldType = getFieldType(value)
              const sampleValue = getSampleValue(value)
              
              fields.push({
                name: key,
                type: fieldType,
                sampleValue: sampleValue,
                description: getFieldDescription(key, fieldType)
              })
            }
          })
          
          fields.sort((a, b) => a.name.localeCompare(b.name))
          layerFields.value = fields
          return fields
        }
      }
      
      console.log('图层中没有找到要素数据')
      layerFields.value = []
      return []
      
    } catch (error) {
      console.error('获取图层字段结构时出错:', error)
      layerFields.value = []
      return []
    }
  }
  
  // 获取字段类型
  const getFieldType = (value: any): string => {
    if (value === null || value === undefined) return '空值'
    if (typeof value === 'string') return '文本'
    if (typeof value === 'number') {
      return Number.isInteger(value) ? '整数' : '小数'
    }
    if (typeof value === 'boolean') return '布尔值'
    if (value instanceof Date) return '日期'
    if (Array.isArray(value)) return '数组'
    if (typeof value === 'object') return '对象'
    return '未知'
  }
  
  // 获取示例值
  const getSampleValue = (value: any): string => {
    if (value === null || value === undefined) return '(空值)'
    if (typeof value === 'string') {
      return value.length > 20 ? value.substring(0, 20) + '...' : value
    }
    if (typeof value === 'number') {
      return value.toString()
    }
    if (typeof value === 'boolean') {
      return value ? 'true' : 'false'
    }
    if (value instanceof Date) {
      return value.toLocaleDateString()
    }
    if (Array.isArray(value)) {
      return `[${value.length}个元素]`
    }
    if (typeof value === 'object') {
      return '{对象}'
    }
    return String(value)
  }
  
  // 获取字段描述
  const getFieldDescription = (fieldName: string, fieldType: string): string => {
    const commonFields: { [key: string]: string } = {
      'name': '名称字段',
      'id': '标识字段',
      'code': '编码字段',
      'type': '类型字段',
      'area': '面积字段',
      'length': '长度字段',
      'population': '人口字段',
      'address': '地址字段',
      'description': '描述字段',
      'remark': '备注字段',
      'note': '注释字段',
      'comment': '评论字段'
    }
    
    const lowerFieldName = fieldName.toLowerCase()
    for (const [key, desc] of Object.entries(commonFields)) {
      if (lowerFieldName.includes(key)) {
        return desc
      }
    }
    
    return `${fieldType}类型字段`
  }
  
  // 验证查询条件
  const validateQueryCondition = (condition: QueryCondition): boolean => {
    if (!condition.fieldName) {
      analysisStore.setAnalysisStatus('请选择查询字段')
      return false
    }
    
    if (condition.value === '' || condition.value === null || condition.value === undefined) {
      analysisStore.setAnalysisStatus('请输入查询值')
      return false
    }
    
    return true
  }
  
  // 执行前端内存查询 - 核心查询逻辑
  const executeFrontendQuery = (condition: QueryCondition): any[] => {
    const layer = mapStore.vectorLayers.find(l => l.id === selectedLayerId.value)
    if (!layer || !layer.layer) {
      console.log('未找到图层:', selectedLayerId.value)
      return []
    }
    
    const source = layer.layer.getSource()
    if (!source) {
      console.log('图层数据源不存在')
      return []
    }
    
    const features = source.getFeatures()
    console.log(`开始前端查询，图层: ${layer.name}，总要素数: ${features.length}`)
    
    // 过滤匹配的要素
    const matchedFeatures = features.filter((feature: Feature) => {
      return executeSingleCondition(feature, condition)
    })
    
    console.log(`查询完成，匹配要素数: ${matchedFeatures.length}`)
    return matchedFeatures
  }
  
  // 执行单个条件查询
  const executeSingleCondition = (feature: Feature, condition: QueryCondition): boolean => {
    const properties = feature.getProperties()
    const fieldValue = properties[condition.fieldName]
    
    if (fieldValue === undefined || fieldValue === null) {
      return false
    }
    
    const field = layerFields.value.find(f => f.name === condition.fieldName)
    if (!field) return false
    
    // 根据字段类型和操作符执行查询
    switch (condition.operator) {
      case 'eq':
        return String(fieldValue).toLowerCase() === String(condition.value).toLowerCase()
      
      case 'gt':
        if (field.type === '整数' || field.type === '小数') {
          return Number(fieldValue) > Number(condition.value)
        }
        return String(fieldValue) > String(condition.value)
      
      case 'lt':
        if (field.type === '整数' || field.type === '小数') {
          return Number(fieldValue) < Number(condition.value)
        }
        return String(fieldValue) < String(condition.value)
      
      case 'gte':
        if (field.type === '整数' || field.type === '小数') {
          return Number(fieldValue) >= Number(condition.value)
        }
        return String(fieldValue) >= String(condition.value)
      
      case 'lte':
        if (field.type === '整数' || field.type === '小数') {
          return Number(fieldValue) <= Number(condition.value)
        }
        return String(fieldValue) <= String(condition.value)
      
      case 'like':
        const fieldStr = String(fieldValue).toLowerCase()
        const pattern = String(condition.value).toLowerCase().replace(/%/g, '.*')
        const regex = new RegExp(pattern)
        return regex.test(fieldStr)
      
      default:
        return false
    }
  }
  
  // 执行查询（主函数）
  const executeQuery = async (): Promise<QueryResult> => {
    if (!selectedLayerId.value) {
      analysisStore.setAnalysisStatus('请选择查询图层')
      return {
        success: false,
        data: [],
        totalCount: 0,
        queryType: 'frontend',
        error: '请选择查询图层'
      }
    }
    
    const condition = queryConfig.condition
    if (!validateQueryCondition(condition)) {
      return {
        success: false,
        data: [],
        totalCount: 0,
        queryType: 'frontend',
        error: '查询条件不完整'
      }
    }
    
    const layer = mapStore.vectorLayers.find(l => l.id === selectedLayerId.value)
    if (!layer || !layer.layer) {
      analysisStore.setAnalysisStatus('图层不存在或不可用')
      return {
        success: false,
        data: [],
        totalCount: 0,
        queryType: 'frontend',
        error: '图层不存在或不可用'
      }
    }
    
    isQuerying.value = true
    analysisStore.setAnalysisStatus('正在执行前端查询...')
    
    try {
      // 执行前端内存查询
      const results = executeFrontendQuery(condition)
      
      // 转换查询结果为标准格式
      const formattedResults = results.map((feature: Feature) => {
        // 确保原始要素有layerName属性
        const originalFeature = (feature as any)._originalFeature || feature
        if (originalFeature && typeof originalFeature.set === 'function') {
          originalFeature.set('layerName', layer.name)
        }
        
        return {
          id: feature.getId?.() || null,
          properties: feature.getProperties(),
          geometry: feature.getGeometry(),
          layerName: layer.name,
          _originalFeature: feature
        }
      })
      
      queryResults.value = formattedResults
      
      // 同步到选择状态管理
      selectionStore.setSelectedFeatures(formattedResults)
      selectedFeatureIndex.value = -1 // 重置选中索引
      
      // 设置点击事件监听
      setupClickOnSelectedFeatures()
      
      // 生成查询描述
      const queryDesc = `${condition.fieldName} ${condition.operator} ${condition.value}`
      lastExecutedQuery.value = `前端查询: ${queryDesc}`
      
      const result: QueryResult = {
        success: true,
        data: formattedResults,
        totalCount: formattedResults.length,
        queryType: 'frontend'
      }
      
      analysisStore.setAnalysisStatus(`前端查询完成，找到 ${formattedResults.length} 个匹配要素`)
      return result
      
    } catch (error) {
      console.error('执行查询时出错:', error)
      const errorResult: QueryResult = {
        success: false,
        data: [],
        totalCount: 0,
        queryType: 'frontend',
        error: error instanceof Error ? error.message : '查询执行失败'
      }
      analysisStore.setAnalysisStatus('查询执行失败，请重试')
      return errorResult
    } finally {
      isQuerying.value = false
    }
  }
  
  // 高亮显示查询结果
  const highlightQueryResults = () => {
    if (queryResults.value.length === 0) {
      return
    }
    
    try {
      // 清空之前的选择
      if (mapStore.selectLayer && mapStore.selectLayer.getSource()) {
        mapStore.selectLayer.getSource().clear()
      }
      
      // 将查询结果添加到选择图层
      const selectSource = mapStore.selectLayer?.getSource()
      if (selectSource) {
        queryResults.value.forEach((result: any) => {
          if (result._originalFeature) {
            selectSource.addFeature(result._originalFeature)
          }
        })
      }
      
      // 设置点击事件监听
      setupClickOnSelectedFeatures()
      
      analysisStore.setAnalysisStatus(`已高亮显示 ${queryResults.value.length} 个查询结果`)
    } catch (error) {
      console.error('高亮显示查询结果时出错:', error)
      analysisStore.setAnalysisStatus('高亮显示失败')
    }
  }
  
  // 选择要素（在列表中点击）
  const handleSelectFeature = (index: number) => {
    selectedFeatureIndex.value = index
    const feature = queryResults.value[index]
    if (feature) {
      highlightFeatureOnMap(feature)
      triggerMapFeatureHighlight(feature)
      analysisStore.setAnalysisStatus(`已选择要素 ${index + 1}`)
      
      // 自动滚动到选中的要素位置
      scrollToSelectedFeature(index)
    }
  }
  
  // 在地图上高亮显示要素
  const highlightFeatureOnMap = (feature: any) => {
    if (!mapStore.map || !feature) return

    // 使用原始要素对象进行高亮显示
    const originalFeature = feature._originalFeature || feature

    // 确保选择图层中包含当前要素
    if (mapStore.selectLayer && mapStore.selectLayer.getSource) {
      const source = mapStore.selectLayer.getSource()
      if (source) {
        // 检查要素是否已经在高亮图层中，如果不在则添加
        const features = source.getFeatures()
        const exists = features.some((f: any) => {
          const fGeometry = f.getGeometry()
          const originalGeometry = originalFeature.getGeometry()
          if (!fGeometry || !originalGeometry) return false

          const fCoords = JSON.stringify(fGeometry.getCoordinates())
          const originalCoords = JSON.stringify(originalGeometry.getCoordinates())
          return fCoords === originalCoords
        })

        if (!exists) {
          // 确保要素包含图层信息
          if (feature.layerName) {
            originalFeature.set('layerName', feature.layerName)
          }
          source.addFeature(originalFeature)
        }
      }
    }
  }
  
  // 触发地图中要素常亮效果
  const triggerMapFeatureHighlight = (feature: any) => {
    // 清除之前的常亮要素
    if (highlightedFeature.value) {
      removeHighlightFeature()
    }

    // 设置常亮要素
    highlightedFeature.value = feature

    // 开始常亮效果
    startHighlightAnimation()
  }
  
  // 开始常亮效果
  const startHighlightAnimation = () => {
    if (!highlightedFeature.value || !mapStore.selectLayer) return

    const source = mapStore.selectLayer.getSource()
    if (!source) return

    // 创建常亮样式
    const createFlashingStyle = () => {
      const accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#007bff'
      const grayFillColor = getComputedStyle(document.documentElement).getPropertyValue('--map-select-fill').trim() || 'rgba(128, 128, 128, 0.3)'
      const highlightColor = '#ff6b35' // 橙色常亮

      return (feature: any) => {
        // 检查是否是常亮要素
        const isHighlightFeature = isSameFeature(feature, highlightedFeature.value)

        const geometry = feature.getGeometry()
        if (!geometry) return null

        const geometryType = geometry.getType()

        if (isHighlightFeature) {
          // 常亮样式 - 橙色高亮
          switch (geometryType) {
            case 'Point':
            case 'MultiPoint':
              return new window.ol.style.Style({
                image: new window.ol.style.Circle({ 
                  radius: 12, 
                  stroke: new window.ol.style.Stroke({color: highlightColor, width: 4}), 
                  fill: new window.ol.style.Fill({color: 'rgba(255, 107, 53, 0.4)'})
                })
              })
              
            case 'LineString':
            case 'MultiLineString':
              return new window.ol.style.Style({
                stroke: new window.ol.style.Stroke({
                  color: highlightColor, 
                  width: 6,
                  lineCap: 'round',
                  lineJoin: 'round'
                })
              })
              
            case 'Polygon':
            case 'MultiPolygon':
              return new window.ol.style.Style({
                stroke: new window.ol.style.Stroke({color: highlightColor, width: 4}),
                fill: new window.ol.style.Fill({color: 'rgba(255, 107, 53, 0.3)'})
              })
              
            default:
              return new window.ol.style.Style({
                image: new window.ol.style.Circle({ 
                  radius: 12, 
                  stroke: new window.ol.style.Stroke({color: highlightColor, width: 4}), 
                  fill: new window.ol.style.Fill({color: 'rgba(255, 107, 53, 0.4)'})
                }),
                stroke: new window.ol.style.Stroke({color: highlightColor, width: 4}),
                fill: new window.ol.style.Fill({color: 'rgba(255, 107, 53, 0.3)'})
              })
          }
        } else {
          // 正常样式 - 蓝色高亮
          switch (geometryType) {
            case 'Point':
            case 'MultiPoint':
              return new window.ol.style.Style({
                image: new window.ol.style.Circle({ 
                  radius: 8, 
                  stroke: new window.ol.style.Stroke({color: accentColor, width: 3}), 
                  fill: new window.ol.style.Fill({color: grayFillColor})
                })
              })
              
            case 'LineString':
            case 'MultiLineString':
              return new window.ol.style.Style({
                stroke: new window.ol.style.Stroke({
                  color: accentColor, 
                  width: 5,
                  lineCap: 'round',
                  lineJoin: 'round'
                })
              })
              
            case 'Polygon':
            case 'MultiPolygon':
              return new window.ol.style.Style({
                stroke: new window.ol.style.Stroke({color: accentColor, width: 3}),
                fill: new window.ol.style.Fill({color: grayFillColor})
              })
              
            default:
              return new window.ol.style.Style({
                image: new window.ol.style.Circle({ 
                  radius: 8, 
                  stroke: new window.ol.style.Stroke({color: accentColor, width: 3}), 
                  fill: new window.ol.style.Fill({color: grayFillColor})
                }),
                stroke: new window.ol.style.Stroke({color: accentColor, width: 3}),
                fill: new window.ol.style.Fill({color: grayFillColor})
              })
          }
        }
      }
    }

    // 设置常亮样式
    mapStore.selectLayer.setStyle(createFlashingStyle())
    mapStore.selectLayer.changed()
  }
  
  // 移除常亮要素
  const removeHighlightFeature = () => {
    if (!mapStore.selectLayer) return

    // 恢复原始样式
    const accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#007bff'
    const grayFillColor = getComputedStyle(document.documentElement).getPropertyValue('--map-select-fill').trim() || 'rgba(128, 128, 128, 0.3)'

    const restoreOriginalStyle = (feature: any) => {
      const geometry = feature.getGeometry()
      if (!geometry) return null

      const geometryType = geometry.getType()

      switch (geometryType) {
        case 'Point':
        case 'MultiPoint':
          return new window.ol.style.Style({
            image: new window.ol.style.Circle({ 
              radius: 8, 
              stroke: new window.ol.style.Stroke({color: accentColor, width: 3}), 
              fill: new window.ol.style.Fill({color: grayFillColor})
            })
          })
          
        case 'LineString':
        case 'MultiLineString':
          return new window.ol.style.Style({
            stroke: new window.ol.style.Stroke({
              color: accentColor, 
              width: 5,
              lineCap: 'round',
              lineJoin: 'round'
            })
          })
          
        case 'Polygon':
        case 'MultiPolygon':
          return new window.ol.style.Style({
            stroke: new window.ol.style.Stroke({color: accentColor, width: 3}),
            fill: new window.ol.style.Fill({color: grayFillColor})
          })
          
        default:
          return new window.ol.style.Style({
            image: new window.ol.style.Circle({ 
              radius: 8, 
              stroke: new window.ol.style.Stroke({color: accentColor, width: 3}), 
              fill: new window.ol.style.Fill({color: grayFillColor})
            }),
            stroke: new window.ol.style.Stroke({color: accentColor, width: 3}),
            fill: new window.ol.style.Fill({color: grayFillColor})
          })
      }
    }

    mapStore.selectLayer.setStyle(restoreOriginalStyle)
    mapStore.selectLayer.changed()
  }
  
  // 检查两个要素是否相同
  const isSameFeature = (feature1: any, feature2: any): boolean => {
    if (!feature1 || !feature2) return false

    // 比较ID
    const id1 = feature1.getId?.() || feature1.id
    const id2 = feature2.getId?.() || feature2.id
    if (id1 && id2 && id1 === id2) return true

    // 比较几何坐标
    const geom1 = feature1.getGeometry?.() || feature1.geometry
    const geom2 = feature2.getGeometry?.() || feature2.geometry

    if (geom1 && geom2) {
      const coords1 = geom1.getCoordinates?.() || geom1.coordinates
      const coords2 = geom2.getCoordinates?.() || geom2.coordinates

      if (coords1 && coords2) {
        const coordStr1 = JSON.stringify(coords1)
        const coordStr2 = JSON.stringify(coords2)
        return coordStr1 === coordStr2
      }
    }

    // 比较原始要素引用
    if (feature1._originalFeature && feature2._originalFeature) {
      return feature1._originalFeature === feature2._originalFeature
    }

    return false
  }
  

  
  // 清空选中图层
  const clearSelectedLayer = (layerId: string) => {
    if (!layerId) return
    
    const layer = mapStore.vectorLayers.find(l => l.id === layerId)
    if (!layer || !layer.layer) return
    
    try {
      // 清空选择图层
      if (mapStore.selectLayer && mapStore.selectLayer.getSource()) {
        mapStore.selectLayer.getSource().clear()
      }
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
      const source = layer.layer.getSource()
      if (!source) return
      
      const allFeatures = source.getFeatures()
      const selectSource = mapStore.selectLayer?.getSource()
      
      if (selectSource) {
        // 清空当前选择
        selectSource.clear()
        
        // 获取当前已选择的要素
        const currentSelectedFeatures = queryResults.value.map((result: any) => result._originalFeature || result)
        
        // 找出所有未选中的要素
        const unselectedFeatures: any[] = []
        allFeatures.forEach((feature: Feature) => {
          const isSelected = currentSelectedFeatures.some((selectedFeature: any) => {
            const selectedGeometry = selectedFeature.getGeometry()
            const featureGeometry = feature.getGeometry()
            
            if (selectedGeometry && featureGeometry) {
              const selectedCoords = JSON.stringify(selectedGeometry.getCoordinates())
              const featureCoords = JSON.stringify(featureGeometry.getCoordinates())
              return selectedCoords === featureCoords
            }
            return false
          })
          
          if (!isSelected) {
            unselectedFeatures.push(feature)
          }
        })
        
        // 将未选中的要素添加到选择图层
        unselectedFeatures.forEach(feature => {
          selectSource.addFeature(feature)
        })
        
        // 更新查询结果列表为反选后的要素
        const invertedResults = unselectedFeatures.map((feature: Feature) => {
          const properties = feature.getProperties ? feature.getProperties() : {}
          const geometry = feature.getGeometry ? feature.getGeometry() : null
          
          return {
            id: feature.getId?.() || null,
            properties: properties,
            geometry: geometry,
            layerName: layer.name,
            _originalFeature: feature
          }
        })
        
        // 更新查询结果
        queryResults.value = invertedResults
        
        // 同步到选择状态管理
        selectionStore.setSelectedFeatures(invertedResults)
        selectedFeatureIndex.value = -1 // 重置选中索引
        
        // 设置点击事件监听
        setupClickOnSelectedFeatures()
      }
      
      console.log(`反选图层 ${layer.name}，更新查询结果列表`)
    } catch (error) {
      console.error('反选图层时出错:', error)
    }
  }
  
  // 获取图层选项
  const getLayerOptions = () => {
    const visibleLayers = mapStore.vectorLayers
      .filter(layer => layer.layer && layer.layer.getVisible())
    
    // 如果没有可见图层，返回空数组
    if (visibleLayers.length === 0) {
      return []
    }
    
    return visibleLayers.map(layer => ({
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
  
  // 获取图层要素数量
  const getLayerFeatureCount = (layerId: string) => {
    const layer = mapStore.vectorLayers.find(l => l.id === layerId)
    if (!layer || !layer.layer) {
      return 0
    }
    
    try {
      const source = layer.layer.getSource()
      if (!source) return 0
      
      const features = source.getFeatures()
      return features.length
    } catch (error) {
      console.error('获取图层要素数量时出错:', error)
      return 0
    }
  }
  
  return {
    // 状态
    selectedLayerId,
    queryResults,
    layerFields,
    queryConfig,
    isQuerying,
    lastExecutedQuery,
    selectedFeatureIndex,
    highlightedFeature,
    
    // 查询执行
    executeQuery,
    getLayerFields,
    highlightQueryResults,
    
    // 要素选择功能
    handleSelectFeature,
    highlightFeatureOnMap,
    triggerMapFeatureHighlight,
    removeHighlightFeature,
    isSameFeature,
    
    // 点击事件管理
    setupClickOnSelectedFeatures,
    
    // 自动滚动功能
    initAutoScroll,
    scrollToSelectedFeature,
    
    // 事件管理
    clearSelectionInteractions,
    
    // 图层管理
    clearSelectedLayer,
    invertSelectedLayer,
    getLayerOptions,
    getSelectedLayerName,
    getLayerFeatureCount
  }
}
