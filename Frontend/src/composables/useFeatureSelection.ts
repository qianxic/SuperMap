import { ref, computed } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useSelectionStore } from '@/stores/selectionStore'
import { useFeatureQueryStore } from '@/stores/featureQueryStore'
import { createAutoScroll } from '@/utils/autoScroll'

const ol = window.ol

export function useFeatureSelection() {
  const mapStore = useMapStore()
  const analysisStore = useAnalysisStore()
  const selectionStore = useSelectionStore()
  const featureQueryStore = useFeatureQueryStore()

  // 状态管理
  const boxSelectInteraction = ref<any>(null)
  const highlightedFeature = ref<any>(null)

  // 选中要素列表（使用 selectionStore 的状态）
  const selectedFeatures = computed({
    get: () => selectionStore.selectedFeatures,
    set: (value) => selectionStore.setSelectedFeatures(value)
  })

  const selectedFeatureIndex = computed({
    get: () => selectionStore.selectedFeatureIndex,
    set: (value) => selectionStore.setSelectedFeatureIndex(value)
  })

  // 几何计算函数
  const calculateLineLength = (coordinates: number[][]): number => {
    if (!coordinates || coordinates.length < 2) return 0
    
    let totalLength = 0
    for (let i = 1; i < coordinates.length; i++) {
      const [lon1, lat1] = coordinates[i - 1]
      const [lon2, lat2] = coordinates[i]
      totalLength += haversineDistance(lat1, lon1, lat2, lon2)
    }
    return totalLength
  }

  const calculatePolygonArea = (coordinates: number[][]): number => {
    if (!coordinates || coordinates.length < 3) return 0
    
    // 简化的球面面积计算（适用于小区域）
    let area = 0
    const n = coordinates.length
    
    for (let i = 0; i < n - 1; i++) {
      const [x1, y1] = coordinates[i]
      const [x2, y2] = coordinates[i + 1]
      area += x1 * y2 - x2 * y1
    }
    
    // 将度转换为米（近似）
    const earthRadius = 6371000 // 地球半径（米）
    const latRad = coordinates[0][1] * Math.PI / 180
    const meterPerDegLat = earthRadius * Math.PI / 180
    const meterPerDegLon = meterPerDegLat * Math.cos(latRad)
    
    return Math.abs(area * meterPerDegLat * meterPerDegLon / 2)
  }

  const haversineDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
    const R = 6371000 // 地球半径（米）
    const dLat = (lat2 - lat1) * Math.PI / 180
    const dLon = (lon2 - lon1) * Math.PI / 180
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    return R * c
  }

  // 要素信息处理函数
  const getFeatureType = (feature: any): string => {
    const geometry = feature.geometry || feature.getGeometry?.()
    if (!geometry) return '未知'
    
    // 直接返回几何类型，不进行映射
    const geometryType = geometry.getType?.() || geometry.type
    return geometryType || '未知'
  }

  const getFeatureCoords = (feature: any): string => {
    const geometry = feature.geometry || feature.getGeometry?.()
    if (!geometry) return '未知坐标'
    
    try {
      const geometryType = geometry.getType?.() || geometry.type
      const coords = geometry.getCoordinates?.() || geometry.coordinates
      
      if (!coords) return '坐标解析失败'
      
      switch (geometryType) {
        case 'Point':
          // 点要素显示坐标
          if (Array.isArray(coords) && coords.length >= 2) {
            return `${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}`
          }
          return '点坐标解析失败'
        
        case 'LineString':
          // 线要素显示长度
          if (Array.isArray(coords) && coords.length >= 2) {
            const length = calculateLineLength(coords)
            if (length >= 1000) {
              return `长度: ${(length / 1000).toFixed(2)}千米`
            } else {
              return `长度: ${length.toFixed(2)}米`
            }
          }
          return '线长度计算失败'
        
        case 'Polygon':
          // 面要素显示面积
          if (Array.isArray(coords) && coords.length > 0) {
            const area = calculatePolygonArea(coords[0]) // 使用外环计算面积
            if (area >= 1000000) {
              return `面积: ${(area / 1000000).toFixed(2)}平方千米`
            } else {
              return `面积: ${area.toFixed(2)}平方米`
            }
          }
          return '面积计算失败'
        
        case 'MultiPoint':
          // 多点显示点数和第一个点的坐标
          if (Array.isArray(coords) && coords.length > 0) {
            const firstPoint = coords[0]
            if (Array.isArray(firstPoint) && firstPoint.length >= 2) {
              return `${coords.length}个点, 起始: ${firstPoint[0].toFixed(6)}, ${firstPoint[1].toFixed(6)}`
            }
          }
          return '多点坐标解析失败'
        
        case 'MultiLineString':
          // 多线显示总长度
          if (Array.isArray(coords) && coords.length > 0) {
            let totalLength = 0
            coords.forEach((lineCoords: number[][]) => {
              if (Array.isArray(lineCoords)) {
                totalLength += calculateLineLength(lineCoords)
              }
            })
            if (totalLength >= 1000) {
              return `总长度: ${(totalLength / 1000).toFixed(2)}千米`
            } else {
              return `总长度: ${totalLength.toFixed(2)}米`
            }
          }
          return '多线长度计算失败'
        
        case 'MultiPolygon':
          // 多面显示总面积
          if (Array.isArray(coords) && coords.length > 0) {
            let totalArea = 0
            coords.forEach((polygonCoords: number[][][]) => {
              if (Array.isArray(polygonCoords) && polygonCoords.length > 0) {
                totalArea += calculatePolygonArea(polygonCoords[0]) // 使用外环
              }
            })
            if (totalArea >= 1000000) {
              return `总面积: ${(totalArea / 1000000).toFixed(2)}平方千米`
            } else {
              return `总面积: ${totalArea.toFixed(2)}平方米`
            }
          }
          return '多面面积计算失败'
        
        default:
          // 未知类型，尝试显示第一个坐标
          if (Array.isArray(coords) && coords.length >= 2 && typeof coords[0] === 'number') {
            return `${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}`
          }
          return `${geometryType || '未知类型'}`
      }
    } catch (error) {
      console.error('几何信息解析错误:', error)
      return '几何信息解析失败'
    }
  }

  const getFeatureGeometryInfo = (feature: any): string => {
    return getFeatureCoords(feature)
  }

  // 创建框选交互
  const createBoxSelectInteraction = () => {
    const interaction = new ol.interaction.DragBox({
      condition: ol.events.condition.always
    })

    interaction.on('boxstart', () => {
      analysisStore.setAnalysisStatus('开始框选，请拖拽鼠标选择要素')
    })

    interaction.on('boxend', async (event: any) => {
      const extent = event.target.getGeometry().getExtent()
      await selectFeaturesInExtent(extent)
    })

    return interaction
  }

  // 设置选择交互
  const setupSelectionInteractions = () => {
    if (!mapStore.map) return

    // 清除现有交互
    clearSelectionInteractions()

    // 创建框选交互
    boxSelectInteraction.value = createBoxSelectInteraction()
    mapStore.map.addInteraction(boxSelectInteraction.value)

    // 添加点击已选择要素的处理
    setupClickOnSelectedFeatures()
  }

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
          triggerMapFeatureHighlight(selectedFeatures.value[selectedFeatureIndex])
          
          analysisStore.setAnalysisStatus(`已选择要素 ${selectedFeatureIndex + 1}`)
        }

        return false
      }
    }

    // 添加点击事件监听
    mapStore.map.on('click', clickHandler)
    
    // 保存事件处理器引用，以便后续移除
    mapStore.map._editToolsClickHandler = clickHandler
  }

  // 清除选择交互
  const clearSelectionInteractions = () => {
    if (!mapStore.map) return

    if (boxSelectInteraction.value) {
      mapStore.map.removeInteraction(boxSelectInteraction.value)
      boxSelectInteraction.value = null
    }

    // 移除点击事件监听
    if (mapStore.map._editToolsClickHandler) {
      mapStore.map.un('click', mapStore.map._editToolsClickHandler)
      delete mapStore.map._editToolsClickHandler
    }
  }

  // 在范围内选择要素
  const selectFeaturesInExtent = async (extent: number[]) => {
    const features: any[] = []

    // 显示加载状态
    analysisStore.setAnalysisStatus('正在收集框选区域内的要素...')

    // 使用 setTimeout 让UI有机会更新
    await new Promise(resolve => setTimeout(resolve, 10))

    mapStore.vectorLayers.forEach(layerInfo => {
      if (layerInfo.visible && layerInfo.layer) {
        const source = layerInfo.layer.getSource()
        if (source && source.forEachFeatureInExtent) {
          source.forEachFeatureInExtent(extent, (feature: any) => {
            // 正确提取要素的所有属性数据
            const properties = feature.getProperties ? feature.getProperties() : {}
            const geometry = feature.getGeometry ? feature.getGeometry() : null

            // 创建包含完整数据的要素对象
            const featureData = {
              // 保留原始要素的方法
              getId: () => feature.getId ? feature.getId() : feature.id || null,
              getGeometry: () => geometry,
              getProperties: () => properties,
              // 添加展平的属性以便访问
              id: feature.getId ? feature.getId() : feature.id || null,
              properties: properties,
              geometry: geometry,
              layerName: layerInfo.name,
              // 保留原始要素引用
              _originalFeature: feature
            }

            features.push(featureData)
          })
        }
      }
    })

    if (features.length > 0) {
      analysisStore.setAnalysisStatus(`找到 ${features.length} 个要素，正在处理...`)
      await featureQueryStore.applyUnifiedSelection(features)
    } else {
      analysisStore.setAnalysisStatus('框选范围内没有找到要素')
    }
  }

  // 统一后不再使用本地批处理添加逻辑，由 featureQueryStore 统一处理

  // 异步高亮显示多个要素
  const highlightFeaturesAsync = async (features: any[]) => {
    if (!mapStore.map || !mapStore.selectLayer || features.length === 0) return

    const source = mapStore.selectLayer.getSource()
    if (!source) return

    const batchSize = 100

    // 分批添加要素到高亮图层
    for (let i = 0; i < features.length; i += batchSize) {
      const batch = features.slice(i, i + batchSize)

      batch.forEach(feature => {
        const originalFeature = feature._originalFeature || feature
        if (originalFeature) {
          // 确保要素包含图层信息
          if (feature.layerName) {
            originalFeature.set('layerName', feature.layerName)
          }
          source.addFeature(originalFeature)
        }
      })

      // 让UI有机会更新
      if (i + batchSize < features.length) {
        await new Promise(resolve => setTimeout(resolve, 5))
      }
    }
  }

  // 选择要素（在列表中点击）
  const handleSelectFeature = (index: number) => {
    selectedFeatureIndex.value = index
    const feature = selectedFeatures.value[index]
    if (feature) {
      highlightFeatureOnMap(feature)
      analysisStore.setAnalysisStatus(`已选择要素 ${index + 1}`)
      
      // 触发地图中的要素常亮效果
      triggerMapFeatureHighlight(feature)
      
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
              return new ol.style.Style({
                image: new ol.style.Circle({ 
                  radius: 12, 
                  stroke: new ol.style.Stroke({color: highlightColor, width: 4}), 
                  fill: new ol.style.Fill({color: 'rgba(255, 107, 53, 0.4)'})
                })
              })
              
            case 'LineString':
            case 'MultiLineString':
              return new ol.style.Style({
                stroke: new ol.style.Stroke({
                  color: highlightColor, 
                  width: 6,
                  lineCap: 'round',
                  lineJoin: 'round'
                })
              })
              
            case 'Polygon':
            case 'MultiPolygon':
              return new ol.style.Style({
                stroke: new ol.style.Stroke({color: highlightColor, width: 4}),
                fill: new ol.style.Fill({color: 'rgba(255, 107, 53, 0.3)'})
              })
              
            default:
              return new ol.style.Style({
                image: new ol.style.Circle({ 
                  radius: 12, 
                  stroke: new ol.style.Stroke({color: highlightColor, width: 4}), 
                  fill: new ol.style.Fill({color: 'rgba(255, 107, 53, 0.4)'})
                }),
                stroke: new ol.style.Stroke({color: highlightColor, width: 4}),
                fill: new ol.style.Fill({color: 'rgba(255, 107, 53, 0.3)'})
              })
          }
        } else {
          // 正常样式 - 蓝色高亮
          switch (geometryType) {
            case 'Point':
            case 'MultiPoint':
              return new ol.style.Style({
                image: new ol.style.Circle({ 
                  radius: 8, 
                  stroke: new ol.style.Stroke({color: accentColor, width: 3}), 
                  fill: new ol.style.Fill({color: grayFillColor})
                })
              })
              
            case 'LineString':
            case 'MultiLineString':
              return new ol.style.Style({
                stroke: new ol.style.Stroke({
                  color: accentColor, 
                  width: 5,
                  lineCap: 'round',
                  lineJoin: 'round'
                })
              })
              
            case 'Polygon':
            case 'MultiPolygon':
              return new ol.style.Style({
                stroke: new ol.style.Stroke({color: accentColor, width: 3}),
                fill: new ol.style.Fill({color: grayFillColor})
              })
              
            default:
              return new ol.style.Style({
                image: new ol.style.Circle({ 
                  radius: 8, 
                  stroke: new ol.style.Stroke({color: accentColor, width: 3}), 
                  fill: new ol.style.Fill({color: grayFillColor})
                }),
                stroke: new ol.style.Stroke({color: accentColor, width: 3}),
                fill: new ol.style.Fill({color: grayFillColor})
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
          return new ol.style.Style({
            image: new ol.style.Circle({ 
              radius: 8, 
              stroke: new ol.style.Stroke({color: accentColor, width: 3}), 
              fill: new ol.style.Fill({color: grayFillColor})
            })
          })
          
        case 'LineString':
        case 'MultiLineString':
          return new ol.style.Style({
            stroke: new ol.style.Stroke({
              color: accentColor, 
              width: 5,
              lineCap: 'round',
              lineJoin: 'round'
            })
          })
          
        case 'Polygon':
        case 'MultiPolygon':
          return new ol.style.Style({
            stroke: new ol.style.Stroke({color: accentColor, width: 3}),
            fill: new ol.style.Fill({color: grayFillColor})
          })
          
        default:
          return new ol.style.Style({
            image: new ol.style.Circle({ 
              radius: 8, 
              stroke: new ol.style.Stroke({color: accentColor, width: 3}), 
              fill: new ol.style.Fill({color: grayFillColor})
            }),
            stroke: new ol.style.Stroke({color: accentColor, width: 3}),
            fill: new ol.style.Fill({color: grayFillColor})
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

  // 在已选择的要素中查找对应的索引
  const findSelectedFeatureIndex = (clickedFeature: any): number => {
    return selectedFeatures.value.findIndex(feature => {
      return isSameFeature(feature, clickedFeature)
    })
  }

  // 清除地图上的选择高亮
  const clearMapSelection = () => {
    if (mapStore.selectLayer && mapStore.selectLayer.getSource) {
      const source = mapStore.selectLayer.getSource()
      if (source) {
        source.clear()
      }
    }
  }

  // 清除选择
  const clearSelection = () => {
    // 清除常亮效果
    if (highlightedFeature.value) {
      removeHighlightFeature()
      highlightedFeature.value = null
    }

    selectionStore.clearSelection()
    clearMapSelection()
    analysisStore.setAnalysisStatus('已清除所有选择')
  }

  // 初始化高亮已有要素
  const initializeHighlightFeatures = async () => {
    if (selectedFeatures.value.length > 0) {
      // 延迟一下确保地图已经准备好
      setTimeout(async () => {
        await highlightFeaturesAsync(selectedFeatures.value)
      }, 100)
    }
  }

  // 自动滚动实例
  let autoScrollInstance: any = null

  // 初始化自动滚动
  const initAutoScroll = () => {
    const layerList = document.querySelector('.layer-list') as HTMLElement | null
    if (layerList && !autoScrollInstance) {
      autoScrollInstance = createAutoScroll(layerList, {
        scrollBehavior: 'smooth',
        centerOnSelect: true,
        scrollOffset: 0
      })
      
      // 添加滚动监听器
      if (autoScrollInstance) {
        autoScrollInstance.addScrollListener(() => {})
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
          console.log(`成功滚动到索引 ${index}`)
        } else {
          console.error(`滚动到索引 ${index} 失败`)
        }
      } else {
        console.error('自动滚动实例未初始化')
      }
    } catch (error) {
      console.error('自动滚动失败:', error)
    }
  }

  return {
    // 状态
    selectedFeatures,
    selectedFeatureIndex,
    highlightedFeature,

    // 方法
    setupSelectionInteractions,
    clearSelectionInteractions,
    handleSelectFeature,
    clearSelection,
    triggerMapFeatureHighlight,
    removeHighlightFeature,
    initializeHighlightFeatures,
    scrollToSelectedFeature,
    initAutoScroll,
    
    // 内部方法（可选择性暴露）
    selectFeaturesInExtent,
    highlightFeatureOnMap,
    findSelectedFeatureIndex,
    isSameFeature,
    getFeatureType,
    getFeatureCoords,
    getFeatureGeometryInfo
  }
}