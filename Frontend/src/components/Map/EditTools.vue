<template>
  <PanelWindow 
    :visible="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'bianji'"
    :embed="true"
    :width="'100%'"
    :height="'100%'"
    class="edit-tools-panel"
  >
    <!-- 已选中要素列表 -->
    <div class="analysis-section">
      <div class="section-title">已选中要素列表 ({{ selectedFeatures.length }})</div>
      <div class="layer-list" v-if="selectedFeatures.length > 0">
        <div 
          v-for="(feature, index) in selectedFeatures" 
          :key="feature.id || index"
          class="layer-item"
          :class="{ 'active': selectedFeatureIndex === index }"
          @click="selectFeature(index)"
        >
          <div class="layer-info">
            <div class="layer-name">要素 {{ index + 1 }} - {{ getFeatureType(feature) }}</div>
            <div class="layer-desc">{{ feature.layerName || '未知图层' }} | {{ getFeatureGeometryInfo(feature) }}</div>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <div class="empty-text">未选中要素</div>
        <div class="empty-desc">请在地图上框选要素</div>
      </div>
    </div>

    <!-- 要素详细信息 -->
    <div class="analysis-section" v-if="selectedFeatureIndex !== -1 && selectedFeatures[selectedFeatureIndex]">
      <div class="section-title">要素详细信息</div>
      <div class="feature-details">
        <div 
          v-for="(item, index) in selectedFeatureInfo" 
          :key="index"
          class="info-item"
        >
          <span class="info-label">{{ item.label }}</span>
          <span class="info-value">{{ item.value }}</span>
        </div>
      </div>
    </div>

    <!-- 选择操作 -->
    <div class="analysis-section">
      <div class="section-title">选择操作</div>
      <div class="button-column">
        <SecondaryButton 
          text="清除选择"
          variant="danger"
          @click="clearSelection"
        />
      </div>
    </div>

    <!-- 提示信息移至底部 -->
    <div class="analysis-section">
      <TipWindow text="在地图上按住左键拖拽鼠标进行框选要素，框选完成后松开左键" />
    </div>
    
  </PanelWindow>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore.ts'
import { useMapStore } from '@/stores/mapStore.ts'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import PanelWindow from '@/components/UI/PanelWindow.vue'
import TipWindow from '@/components/UI/TipWindow.vue'

const ol = window.ol

const analysisStore = useAnalysisStore()
const mapStore = useMapStore()

// 状态管理 - 使用mapStore的持久化状态
const selectedFeatures = computed({
  get: () => mapStore.persistentSelectedFeatures,
  set: (value) => mapStore.setPersistentSelectedFeatures(value)
})

const selectedFeatureIndex = computed({
  get: () => mapStore.selectedFeatureIndex,
  set: (value) => mapStore.setSelectedFeatureIndex(value)
})
const boxSelectInteraction = ref<any>(null) // 框选交互

// 选中要素的详细信息
const selectedFeatureInfo = computed(() => {
  if (selectedFeatureIndex.value === -1 || !selectedFeatures.value[selectedFeatureIndex.value]) {
    return []
  }
  
  const feature = selectedFeatures.value[selectedFeatureIndex.value]
  const properties = feature.properties || feature.getProperties?.() || {}
  
  const info = [
    { label: '要素ID', value: feature.getId?.() || feature.id || '无' },
    { label: '图层名称', value: feature.layerName || '未知图层' },
    { label: '几何类型', value: getFeatureType(feature) },
    { label: '几何信息', value: getFeatureCoords(feature) }
  ]
  
  // 添加属性字段计数
  const attributeCount = Object.keys(properties).filter(key => key !== 'geometry').length
  info.push({ label: '属性字段数', value: `${attributeCount}个` })
  
  // 添加所有属性字段，包括空值 - 与useMap中的显示逻辑一致
  Object.keys(properties).forEach(key => {
    if (key !== 'geometry') {
      const value = properties[key]
      const displayValue = value !== undefined && value !== null ? value : '(空值)'
      info.push({ label: key, value: displayValue })
    }
  })
  
  return info
})

// 获取要素类型 - 直接返回几何类型
const getFeatureType = (feature: any): string => {
  const geometry = feature.geometry || feature.getGeometry?.()
  if (!geometry) return '未知'
  
  // 直接返回几何类型，不进行映射
  const geometryType = geometry.getType?.() || geometry.type
  return geometryType || '未知'
}

// 获取要素几何信息（坐标/面积/长度）
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

// 计算线长度（球面距离）
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

// 计算多边形面积（球面面积）
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

// Haversine距离公式计算两点间的球面距离
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

// 获取要素几何信息（用于列表显示）
const getFeatureGeometryInfo = (feature: any): string => {
  return getFeatureCoords(feature)
}

// 设置选择模式 - 移除，默认框选
// const setSelectionMode = (mode: 'box' | 'click') => {
//   selectionMode.value = mode
//   setupSelectionInteractions()
//   analysisStore.setAnalysisStatus(`已切换到${mode === 'box' ? '框选' : '点击选择'}模式`)
//   
//   // 清除当前选择
//   clearMapSelection()
// }

// 清除选择
const clearSelection = () => {
  mapStore.clearPersistentSelection() // 使用mapStore的方法清除持久化状态
  clearMapSelection() // 清除地图上的高亮显示
  analysisStore.setAnalysisStatus('已清除所有选择')
}

// 闪烁状态管理
const flashingFeatureIndex = ref<number>(-1)
const flashingTimer = ref<number | null>(null)
const flashingFeature = ref<any>(null)

// 选择要素（在列表中点击）
const selectFeature = (index: number) => {
  selectedFeatureIndex.value = index
  const feature = selectedFeatures.value[index]
  if (feature) {
    highlightFeatureOnMap(feature)
    analysisStore.setAnalysisStatus(`已选择要素 ${index + 1}`)
    
    // 触发地图中的要素闪烁效果
    triggerMapFeatureFlash(feature)
  }
}

// 触发地图中要素闪烁效果
const triggerMapFeatureFlash = (feature: any) => {
  // 清除之前的闪烁
  if (flashingTimer.value) {
    clearTimeout(flashingTimer.value)
    flashingTimer.value = null
  }
  
  // 清除之前的闪烁要素
  if (flashingFeature.value) {
    removeFlashingFeature()
  }
  
  // 设置闪烁要素
  flashingFeature.value = feature
  
  // 开始闪烁动画
  startFlashingAnimation()
  
  // 3秒后自动清除闪烁效果
  flashingTimer.value = window.setTimeout(() => {
    removeFlashingFeature()
    flashingFeature.value = null
    flashingTimer.value = null
  }, 3000)
}

// 开始闪烁动画
const startFlashingAnimation = () => {
  if (!flashingFeature.value || !mapStore.selectLayer) return
  
  const source = mapStore.selectLayer.getSource()
  if (!source) return
  
  // 保存原始样式
  const originalStyle = mapStore.selectLayer.getStyle()
  
  // 创建闪烁样式 - 只对特定要素应用闪烁效果
  const createFlashingStyle = () => {
    const accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#007bff'
    const grayFillColor = getComputedStyle(document.documentElement).getPropertyValue('--map-select-fill').trim() || 'rgba(128, 128, 128, 0.3)'
    const flashColor = '#ff6b35' // 橙色闪烁
    
    return (feature: any) => {
      // 检查是否是闪烁要素
      const isFlashingFeature = isSameFeature(feature, flashingFeature.value)
      
      const geometry = feature.getGeometry()
      if (!geometry) return null
      
      const geometryType = geometry.getType()
      
      if (isFlashingFeature) {
        // 闪烁样式
        switch (geometryType) {
          case 'Point':
          case 'MultiPoint':
            return new ol.style.Style({
              image: new ol.style.Circle({ 
                radius: 12, 
                stroke: new ol.style.Stroke({color: flashColor, width: 4}), 
                fill: new ol.style.Fill({color: 'rgba(255, 107, 53, 0.4)'})
              })
            })
            
          case 'LineString':
          case 'MultiLineString':
            return new ol.style.Style({
              stroke: new ol.style.Stroke({
                color: flashColor, 
                width: 6,
                lineCap: 'round',
                lineJoin: 'round'
              })
            })
            
          case 'Polygon':
          case 'MultiPolygon':
            return new ol.style.Style({
              stroke: new ol.style.Stroke({color: flashColor, width: 4}),
              fill: new ol.style.Fill({color: 'rgba(255, 107, 53, 0.3)'})
            })
            
          default:
            return new ol.style.Style({
              image: new ol.style.Circle({ 
                radius: 12, 
                stroke: new ol.style.Stroke({color: flashColor, width: 4}), 
                fill: new ol.style.Fill({color: 'rgba(255, 107, 53, 0.4)'})
              }),
              stroke: new ol.style.Stroke({color: flashColor, width: 4}),
              fill: new ol.style.Fill({color: 'rgba(255, 107, 53, 0.3)'})
            })
        }
      } else {
        // 正常样式
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
  
  // 设置闪烁样式
  mapStore.selectLayer.setStyle(createFlashingStyle())
  
  // 闪烁动画：5次闪烁，每次0.6秒
  let flashCount = 0
  const maxFlashes = 5
  
  const flashInterval = setInterval(() => {
    flashCount++
    
    if (flashCount >= maxFlashes) {
      clearInterval(flashInterval)
      // 恢复原始样式
      mapStore.selectLayer.setStyle(originalStyle)
      mapStore.selectLayer.changed()
    } else {
      // 切换闪烁效果
      mapStore.selectLayer.changed()
    }
  }, 600)
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
      return JSON.stringify(coords1) === JSON.stringify(coords2)
    }
  }
  
  return false
}

// 移除闪烁要素
const removeFlashingFeature = () => {
  if (!mapStore.selectLayer) return
  
  // 恢复原始样式
  const originalStyle = mapStore.selectLayer.getStyle()
  if (originalStyle) {
    mapStore.selectLayer.setStyle(originalStyle)
    mapStore.selectLayer.changed()
  }
}

// 设置选择交互 - 只保留框选
const setupSelectionInteractions = () => {
  if (!mapStore.map) return
  
  // 清除现有交互
  clearSelectionInteractions()
  
  // 创建框选交互
  boxSelectInteraction.value = new ol.interaction.DragBox({
    condition: ol.events.condition.always
  })
  
  // 设置框选样式
  boxSelectInteraction.value.on('boxstart', (event: any) => {
    analysisStore.setAnalysisStatus('开始框选，请拖拽鼠标选择要素')
  })
  
  boxSelectInteraction.value.on('boxend', async (event: any) => {
    const extent = event.target.getGeometry().getExtent()
    await selectFeaturesInExtent(extent)
  })
  
  mapStore.map.addInteraction(boxSelectInteraction.value)
}

// 清除选择交互
const clearSelectionInteractions = () => {
  if (!mapStore.map) return
  
  if (boxSelectInteraction.value) {
    mapStore.map.removeInteraction(boxSelectInteraction.value)
    boxSelectInteraction.value = null
  }
}

// 在范围内选择要素 - 异步处理
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
    await addFeaturesToSelectionAsync(features)
  } else {
    analysisStore.setAnalysisStatus('框选范围内没有找到要素')
  }
}

// 异步添加要素到选择列表 - 避免UI卡顿
const addFeaturesToSelectionAsync = async (features: any[]) => {
  let addedCount = 0
  const batchSize = 50 // 每批处理50个要素
  const newFeatures: any[] = [] // 存储新添加的要素
  
  // 分批处理要素，避免一次性处理太多导致卡顿
  for (let i = 0; i < features.length; i += batchSize) {
    const batch = features.slice(i, i + batchSize)
    
    // 更新进度状态
    const progress = Math.min(i + batchSize, features.length)
    analysisStore.setAnalysisStatus(`正在处理要素 ${progress}/${features.length}...`)
    
    // 处理当前批次
    batch.forEach(feature => {
      // 使用更可靠的唯一标识：几何坐标 + 图层名称
      const geometry = feature.getGeometry ? feature.getGeometry() : feature.geometry
      const geometryKey = geometry ? JSON.stringify(geometry.getCoordinates?.() || geometry.coordinates) : 'no-geometry'
      const uniqueKey = `${feature.layerName}_${geometryKey}`
      
      // 检查是否已经存在 - 使用几何坐标和图层名称作为唯一标识
      const exists = selectedFeatures.value.some(f => {
        const fGeometry = f.getGeometry ? f.getGeometry() : f.geometry
        const fGeometryKey = fGeometry ? JSON.stringify(fGeometry.getCoordinates?.() || fGeometry.coordinates) : 'no-geometry'
        const fUniqueKey = `${f.layerName}_${fGeometryKey}`
        return fUniqueKey === uniqueKey
      })
      
      if (!exists) {
        // 为要素生成一个稳定的ID（如果没有的话）
        const originalId = feature.getId?.() || feature.id
        if (!originalId) {
          // 使用几何坐标的哈希作为稳定ID
          const stableId = `${feature.layerName}_${Math.abs(geometryKey.split('').reduce((a, b) => { a = ((a << 5) - a) + b.charCodeAt(0); return a & a }, 0))}`
          feature.id = stableId
        }
        
        selectedFeatures.value.push(feature)
        newFeatures.push(feature)
        addedCount++
      }
    })
    
    // 让UI有机会更新，避免长时间阻塞
    if (i + batchSize < features.length) {
      await new Promise(resolve => setTimeout(resolve, 5))
    }
  }
  
  // 异步高亮显示所有新添加的要素
  if (newFeatures.length > 0) {
    await highlightFeaturesAsync(newFeatures)
  }
  
  // 完成处理后更新状态
  if (addedCount > 0) {
    analysisStore.setAnalysisStatus(`新增 ${addedCount} 个要素，总计 ${selectedFeatures.value.length} 个`)
  } else {
    analysisStore.setAnalysisStatus(`框选区域内 ${features.length} 个要素已存在，总计 ${selectedFeatures.value.length} 个`)
  }
}

// 添加要素到选择列表 - 保留原函数用于兼容性
const addFeaturesToSelection = (features: any[]) => {
  let addedCount = 0
  
  features.forEach(feature => {
    // 使用更可靠的唯一标识：几何坐标 + 图层名称
    const geometry = feature.getGeometry ? feature.getGeometry() : feature.geometry
    const geometryKey = geometry ? JSON.stringify(geometry.getCoordinates?.() || geometry.coordinates) : 'no-geometry'
    const uniqueKey = `${feature.layerName}_${geometryKey}`
    
    // 检查是否已经存在 - 使用几何坐标和图层名称作为唯一标识
    const exists = selectedFeatures.value.some(f => {
      const fGeometry = f.getGeometry ? f.getGeometry() : f.geometry
      const fGeometryKey = fGeometry ? JSON.stringify(fGeometry.getCoordinates?.() || fGeometry.coordinates) : 'no-geometry'
      const fUniqueKey = `${f.layerName}_${fGeometryKey}`
      return fUniqueKey === uniqueKey
    })
    
    if (!exists) {
      // 为要素生成一个稳定的ID（如果没有的话）
      const originalId = feature.getId?.() || feature.id
      if (!originalId) {
        // 使用几何坐标的哈希作为稳定ID
        const stableId = `${feature.layerName}_${Math.abs(geometryKey.split('').reduce((a, b) => { a = ((a << 5) - a) + b.charCodeAt(0); return a & a }, 0))}`
        feature.id = stableId
      }
      
      selectedFeatures.value.push(feature)
      addedCount++
    }
  })
  
  if (addedCount > 0) {
    analysisStore.setAnalysisStatus(`新增 ${addedCount} 个要素，总计 ${selectedFeatures.value.length} 个`)
  } else {
    analysisStore.setAnalysisStatus(`框选区域内 ${features.length} 个要素已存在，总计 ${selectedFeatures.value.length} 个`)
  }
}

// 异步高亮显示多个要素 - 避免UI卡顿
const highlightFeaturesAsync = async (features: any[]) => {
  if (!mapStore.map || !mapStore.selectLayer || features.length === 0) return
  
  const source = mapStore.selectLayer.getSource()
  if (!source) return
  
  const batchSize = 100 // 每批高亮100个要素
  
  // 分批添加要素到高亮图层
  for (let i = 0; i < features.length; i += batchSize) {
    const batch = features.slice(i, i + batchSize)
    
    batch.forEach(feature => {
      const originalFeature = feature._originalFeature || feature
      if (originalFeature) {
        source.addFeature(originalFeature)
      }
    })
    
    // 让UI有机会更新
    if (i + batchSize < features.length) {
      await new Promise(resolve => setTimeout(resolve, 5))
    }
  }
}

// 清除地图上的选择高亮
const clearMapSelection = () => {
  // 同时清除选择图层
  if (mapStore.selectLayer && mapStore.selectLayer.getSource) {
    const source = mapStore.selectLayer.getSource()
    if (source) {
      source.clear()
    }
  }
}

// 在地图上高亮显示要素 - 不清除其他已选择要素的高亮
const highlightFeatureOnMap = (feature: any) => {
  if (!mapStore.map || !feature) return
  
  // 不清除之前的高亮，只是添加当前要素的额外高亮效果
  // clearMapSelection() // 移除这行，保持所有已选择要素的高亮
  
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
        source.addFeature(originalFeature)
      }
    }
  }
}

// 监听编辑工具关闭 - 不清除已选择的要素，只清除交互
watch(() => analysisStore.toolPanel?.activeTool, (tool) => {
  if (tool !== 'bianji') {
    // 只清除交互，不清除已选择的要素
    clearSelectionInteractions()
    // 保持已选择的要素和高亮显示
    // selectedFeatures.value = [] // 移除这行，保持要素选择
    // selectedFeatureIndex.value = -1 // 移除这行，保持要素选择
  }
})

// 组件挂载时设置交互
onMounted(() => {
  setupSelectionInteractions()
  
  // 如果已有选中的要素，重新高亮显示它们
  if (selectedFeatures.value.length > 0) {
    // 延迟一下确保地图已经准备好
    setTimeout(async () => {
      await highlightFeaturesAsync(selectedFeatures.value)
    }, 100)
  }
})

// 组件卸载时清理 - 只清除交互，保持要素选择
onUnmounted(() => {
  clearSelectionInteractions()
  // 清理闪烁定时器
  if (flashingTimer.value) {
    clearTimeout(flashingTimer.value)
    flashingTimer.value = null
  }
  // 不清除已选择的要素，保持用户的选择状态
})

defineExpose({
  selectedFeatures,
  selectedFeatureIndex,
  clearSelection
})
</script>

<style scoped>
.edit-tools-panel {
  height: 100%;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  /* 使用全局滚动条样式 */
}

.analysis-section {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px;
  animation: fadeIn 0.3s ease-out;
  margin-bottom: 16px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-title {
  font-size: 13px;
  color: var(--text);
  margin-bottom: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.selection-info {
  margin-bottom: 12px;
  padding: 12px;
  background: var(--btn-secondary-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  animation: fadeIn 0.3s ease-out;
}

.info-text {
  font-size: 12px;
  color: var(--text);
  margin-bottom: 4px;
}

.info-text:last-child {
  margin-bottom: 0;
}

.button-column {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 使用图层管理的列表样式 */
.layer-list { 
  display: flex; 
  flex-direction: column; 
  gap: 8px;
  max-height: 180px; /* 约3个项目的高度 */
  overflow-y: auto;
  padding-right: 4px; /* 为滚动条预留空间 */
}

.layer-item {
  display: flex; 
  align-items: center; 
  justify-content: space-between;
  background: var(--btn-secondary-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px 14px;
  animation: fadeIn 0.3s ease-out;
  cursor: pointer;
  transition: all 0.2s ease;
}

.layer-item:hover {
  background: var(--surface-hover);
  border-color: var(--accent);
}

.layer-item.active {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}



.layer-info { 
  display: flex; 
  flex-direction: column; 
}

.layer-name { 
  font-size: 13px; 
  color: var(--text); 
  font-weight: 500; 
}

.layer-item.active .layer-name {
  color: white;
}

.layer-desc { 
  font-size: 11px; 
  color: var(--sub); 
  margin-top: 2px; 
}

.layer-item.active .layer-desc {
  color: rgba(255, 255, 255, 0.9);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  color: var(--sub);
}

.empty-text {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text);
}

.empty-desc {
  font-size: 14px;
  opacity: 0.8;
}

.feature-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 4px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  padding: 6px 0;
  border-bottom: 1px solid var(--border);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  color: var(--sub);
  min-width: 80px;
  font-weight: 500;
}

.info-value {
  color: var(--text);
  text-align: right;
  word-break: break-word;
  max-width: 200px;
  font-size: 11px;
}
</style>
