/**
 * 统一的要素数据处理工具
 * 确保所有选择方式使用相同的数据结构
 */

/**
 * 标准化要素数据结构
 * @param feature OpenLayers要素对象
 * @param layerName 图层名称
 * @returns 标准化的要素数据
 */
export function normalizeFeatureData(feature: any, layerName: string = '') {
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
    layerName: layerName,
    
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
  return features.map((feature: any) => normalizeFeatureData(feature, layerInfo.name))
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
    properties: properties,
    layerName: feature.layerName || '未知图层'
  }
}
