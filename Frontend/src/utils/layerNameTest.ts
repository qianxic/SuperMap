// 图层名称解析测试脚本
import { createAPIConfig } from './config'

export function testLayerNameParsing() {
  console.log('=== 图层名称解析测试 ===')
  
  const config = createAPIConfig()
  
  config.wuhanLayers.forEach((layer, index) => {
    console.log(`\n测试图层 ${index + 1}:`)
    console.log(`原始名称: ${layer.name}`)
    
    // 模拟 loadVectorLayer 中的解析逻辑
    let layerName = layer.name
    if (layer.name.includes('@')) {
      const parts = layer.name.split('@')
      if (parts.length >= 1) {
        layerName = parts[0]
      }
    }
    
    if (!layerName || layerName === '未知' || layerName === 'unknown') {
      layerName = layer.datasetName || layer.name || '未知图层'
    }
    
    console.log(`解析后名称: ${layerName}`)
    console.log(`数据集名称: ${layer.datasetName}`)
    console.log(`图层类型: ${layer.type}`)
    console.log(`图层组: ${layer.group}`)
    
    // 验证解析结果
    if (layerName === '未知' || layerName === 'unknown' || layerName === '未知图层') {
      console.warn('⚠️  警告: 图层名称解析失败，显示为未知')
    } else {
      console.log('✅ 图层名称解析成功')
    }
  })
  
  return config.wuhanLayers
}

// 测试图层名称匹配逻辑
export function testLayerNameMatching() {
  console.log('\n=== 图层名称匹配测试 ===')
  
  const config = createAPIConfig()
  const testLayerIds = config.wuhanLayers.map(layer => layer.name)
  
  // 模拟 mapStore.vectorLayers 结构
  const mockVectorLayers = config.wuhanLayers.map(layer => {
    let layerName = layer.name
    if (layer.name.includes('@')) {
      const parts = layer.name.split('@')
      if (parts.length >= 1) {
        layerName = parts[0]
      }
    }
    
    if (!layerName || layerName === '未知' || layerName === 'unknown') {
      layerName = layer.datasetName || layer.name || '未知图层'
    }
    
    return {
      id: layer.name,
      name: layerName,
      layer: null,
      visible: layer.visible,
      type: 'vector',
      source: 'supermap'
    }
  })
  
  // 测试 getSelectedLayerName 逻辑
  testLayerIds.forEach(layerId => {
    console.log(`\n测试图层ID: ${layerId}`)
    
    // 模拟 getSelectedLayerName 逻辑
    const layer = mockVectorLayers.find(l => l.id === layerId)
    let layerName = ''
    
    if (layer && layer.name) {
      layerName = layer.name
    } else {
      const layerByName = mockVectorLayers.find(l => l.name === layerId)
      if (layerByName && layerByName.name) {
        layerName = layerByName.name
      } else {
        layerName = '未知图层'
      }
    }
    
    console.log(`匹配结果: ${layerName}`)
    
    if (layerName === '未知图层') {
      console.warn('⚠️  警告: 图层名称匹配失败')
    } else {
      console.log('✅ 图层名称匹配成功')
    }
  })
}

// 导出测试函数
export default {
  testLayerNameParsing,
  testLayerNameMatching
}
