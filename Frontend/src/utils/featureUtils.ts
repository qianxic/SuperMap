/**
 * 统一的要素数据处理工具
 * 确保所有选择方式使用相同的数据结构
 */

/**
 * 标准化要素数据结构
 * @param feature OpenLayers要素对象
 * @returns 标准化的要素数据
 */
export function normalizeFeatureData(feature: any) {
  if (!feature) return null

  // 获取要素的基本信息
  const properties = feature.getProperties ? feature.getProperties() : {}
  const geometry = feature.getGeometry ? feature.getGeometry() : null
  const id = feature.getId ? feature.getId() : feature.id || null

  // 返回标准化的数据结构
  return {
    // 保留原始要素的方法
    getId: () => id,
    getGeometry: () => geometry,
    getProperties: () => properties,
    
    // 展平的属性
    id: id,
    properties: properties,
    geometry: geometry,
    
    // 保留原始要素引用
    _originalFeature: feature
  }
}

/**
 * 从图层中获取所有要素的标准数据结构
 * @param layerInfo 图层信息
 * @returns 标准化的要素数组
 */
export function getNormalizedFeaturesFromLayer(layerInfo: any): any[] {
  if (!layerInfo || !layerInfo.layer) return []
  
  const source = layerInfo.layer.getSource()
  if (!source) return []
  
  const features = source.getFeatures()
  return features.map((feature: any) => normalizeFeatureData(feature))
}

/**
 * 从所有可见图层中获取要素
 * @param vectorLayers 矢量图层数组
 * @returns 所有要素的标准数据结构
 */
export function getAllNormalizedFeatures(vectorLayers: any[]): any[] {
  const allFeatures: any[] = []
  
  vectorLayers.forEach(layerInfo => {
    if (layerInfo.visible && layerInfo.layer) {
      const features = getNormalizedFeaturesFromLayer(layerInfo)
      allFeatures.push(...features)
    }
  })
  
  return allFeatures
}

/**
 * 根据条件过滤要素
 * @param features 要素数组
 * @param condition 过滤条件函数
 * @returns 过滤后的要素数组
 */
export function filterFeatures(features: any[], condition: (feature: any) => boolean): any[] {
  return features.filter(condition)
}

/**
 * 获取要素的显示信息
 * @param feature 要素对象
 * @returns 格式化的显示信息
 */
export function getFeatureDisplayInfo(feature: any) {
  if (!feature) return null
  
  const properties = feature.getProperties ? feature.getProperties() : feature.properties || {}
  const geometry = feature.getGeometry ? feature.getGeometry() : feature.geometry
  const id = feature.getId ? feature.getId() : feature.id
  
  return {
    id: id,
    geometryType: geometry?.getType ? geometry.getType() : '未知',
    properties: properties
  }
}

/**
 * 获取要素的几何类型
 * @param feature 要素对象
 * @returns 几何类型字符串
 */
export function getFeatureGeometryType(feature: any): string {
  const geometry = feature.geometry || feature.getGeometry?.()
  if (!geometry) return '未知'
  
  const geometryType = geometry.getType?.() || geometry.type
  return geometryType || '未知'
}

/**
 * 获取要素的几何信息描述
 * @param feature 要素对象
 * @returns 几何信息描述字符串
 */
export function getFeatureGeometryDescription(feature: any): string {
  const geometry = feature.geometry || feature.getGeometry?.()
  if (!geometry) return '未知坐标'
  
  try {
    const geometryType = geometry.getType?.() || geometry.type
    const coords = geometry.getCoordinates?.() || geometry.coordinates
    
    if (!coords) return '坐标解析失败'
    
    switch (geometryType) {
      case 'Point':
        if (Array.isArray(coords) && coords.length >= 2) {
          return `点坐标: ${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}`
        }
        return '点坐标解析失败'
      
      case 'LineString':
        if (Array.isArray(coords) && coords.length >= 2) {
          const length = calculateLineLength(coords)
          return `线长度: ${length.toFixed(4)}千米`
        }
        return '线长度计算失败'
      
      case 'Polygon':
        if (Array.isArray(coords) && coords.length > 0) {
          const area = calculatePolygonArea(coords[0])
          return `面面积: ${area.toFixed(4)}平方千米`
        }
        return '面积计算失败'
      
      case 'MultiPoint':
        if (Array.isArray(coords) && coords.length > 0) {
          const firstPoint = coords[0]
          if (Array.isArray(firstPoint) && firstPoint.length >= 2) {
            return `${coords.length}个点, 起始: ${firstPoint[0].toFixed(6)}, ${firstPoint[1].toFixed(6)}`
          }
        }
        return '多点坐标解析失败'
      
      case 'MultiLineString':
        if (Array.isArray(coords) && coords.length > 0) {
          let totalLength = 0
          coords.forEach((lineCoords: number[][]) => {
            if (Array.isArray(lineCoords)) {
              totalLength += calculateLineLength(lineCoords)
            }
          })
          return `多线总长度: ${totalLength.toFixed(4)}千米`
        }
        return '多线长度计算失败'
      
      case 'MultiPolygon':
        if (Array.isArray(coords) && coords.length > 0) {
          let totalArea = 0
          coords.forEach((polygonCoords: number[][][]) => {
            if (Array.isArray(polygonCoords) && polygonCoords.length > 0) {
              totalArea += calculatePolygonArea(polygonCoords[0])
            }
          })
          return `多面总面积: ${totalArea.toFixed(4)}平方千米`
        }
        return '多面面积计算失败'
      
      default:
        if (Array.isArray(coords) && coords.length >= 2 && typeof coords[0] === 'number') {
          return `${geometryType}坐标: ${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}`
        }
        return `${geometryType || '未知类型'}`
    }
  } catch (error) {
    console.error('几何信息解析错误:', error)
    return '几何信息解析失败'
  }
}

/**
 * 获取要素的完整信息（包括几何信息）
 * @param feature 要素对象
 * @returns 完整的要素信息数组
 */
export function getFeatureCompleteInfo(feature: any): Array<{label: string, value: string}> {
  if (!feature) return []
  
  const properties = feature.getProperties ? feature.getProperties() : feature.properties || {}
  const info: Array<{label: string, value: string}> = []
  
  // 所有属性字段
  Object.keys(properties).forEach(key => {
    if (key !== 'geometry') {
      const value = properties[key]
      const displayValue = value !== undefined && value !== null ? String(value) : '(空值)'
      info.push({ label: key, value: displayValue })
    }
  })
  
  return info
}

/**
 * 获取增强的字段信息（包括几何字段）
 * @param feature 要素对象
 * @returns 包含几何信息的字段数组
 */
export function getEnhancedLayerFields(feature: any): Array<{name: string, type: string, sampleValue: string, description: string}> {
  if (!feature) return []
  
  const properties = feature.getProperties ? feature.getProperties() : feature.properties || {}
  const geometry = feature.getGeometry ? feature.getGeometry() : feature.geometry
  const fields: Array<{name: string, type: string, sampleValue: string, description: string}> = []
  
  // 移除几何字段显示
  
  // 添加属性字段
  Object.keys(properties).forEach(key => {
    if (key !== 'geometry') {
      const value = properties[key]
      const type = getFieldType(value)
      const sample = getSampleValue(value)
      fields.push({
        name: key,
        type: type,
        sampleValue: sample,
        description: getFieldDescription(key, type)
      })
    }
  })
  
  return fields.sort((a, b) => a.name.localeCompare(b.name))
}

// 辅助函数
function getFieldType(value: any): string {
  if (value === null || value === undefined) return '空值'
  if (typeof value === 'string') return '文本'
  if (typeof value === 'number') return Number.isInteger(value) ? '整数' : '小数'
  if (typeof value === 'boolean') return '布尔值'
  if (value instanceof Date) return '日期'
  if (Array.isArray(value)) return '数组'
  if (typeof value === 'object') return '对象'
  return '未知'
}

function getSampleValue(value: any): string {
  if (value === null || value === undefined) return '(空值)'
  if (typeof value === 'string') return value.length > 20 ? value.substring(0, 20) + '...' : value
  if (typeof value === 'number') return String(value)
  if (typeof value === 'boolean') return value ? 'true' : 'false'
  if (value instanceof Date) return value.toLocaleDateString()
  if (Array.isArray(value)) return `[${value.length}个元素]`
  if (typeof value === 'object') return '{对象}'
  return String(value)
}

function getFieldDescription(fieldName: string, fieldType: string): string {
  const commonFields: Record<string, string> = {
    name: '名称字段', id: '标识字段', code: '编码字段', type: '类型字段',
    area: '面积字段', length: '长度字段', population: '人口字段', address: '地址字段',
    description: '描述字段', remark: '备注字段', note: '注释字段', comment: '评论字段'
  }
  const lower = fieldName.toLowerCase()
  for (const [k, v] of Object.entries(commonFields)) {
    if (lower.includes(k)) return v
  }
  return `${fieldType}类型字段`
}

// 几何计算函数
function calculateLineLength(coordinates: number[][]): number {
  if (!coordinates || coordinates.length < 2) return 0
  
  let totalLength = 0
  for (let i = 1; i < coordinates.length; i++) {
    const [lon1, lat1] = coordinates[i - 1]
    const [lon2, lat2] = coordinates[i]
    totalLength += haversineDistance(lat1, lon1, lat2, lon2)
  }
  return totalLength
}

function calculatePolygonArea(coordinates: number[][]): number {
  if (!coordinates || coordinates.length < 3) return 0
  
  let area = 0
  const n = coordinates.length
  
  for (let i = 0; i < n - 1; i++) {
    const [x1, y1] = coordinates[i]
    const [x2, y2] = coordinates[i + 1]
    area += x1 * y2 - x2 * y1
  }
  
  const earthRadius = 6371
  const latRad = coordinates[0][1] * Math.PI / 180
  const kmPerDegLat = earthRadius * Math.PI / 180
  const kmPerDegLon = kmPerDegLat * Math.cos(latRad)
  
  return Math.abs(area * kmPerDegLat * kmPerDegLon / 2)
}

function haversineDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}
