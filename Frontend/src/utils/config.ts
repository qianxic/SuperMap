import type { APIConfig, WuhanLayer } from '@/types/map'

/**
 * 创建SuperMap API配置 - 定义所有服务器连接地址和图层配置
 * 调用者: mapStore.ts -> createMapConfig() -> createAPIConfig()
 * 作用: 集中管理SuperMap iServer的服务器地址、服务路径和图层定义
 */
export const createAPIConfig = (): APIConfig => {
  // ===== 服务器连接配置 =====
  // 调用者: createAPIConfig()
  // 服务器地址: 从环境变量获取，默认localhost:8090
  // 作用: 定义SuperMap iServer的基础服务器地址
  const baseUrl = import.meta.env.VITE_SUPERMAP_BASE_URL || 'http://localhost:8090'
  
  // ===== 地图服务路径配置 =====
  // 调用者: createAPIConfig()
  // 服务路径: iserver/services/map-WuHan/rest
  // 作用: 定义地图服务的REST API路径，用于底图和地图服务
  const mapService = import.meta.env.VITE_SUPERMAP_MAP_SERVICE || 'iserver/services/map-WuHan/rest'
  
  // ===== 数据服务路径配置 =====
  // 调用者: createAPIConfig()
  // 服务路径: iserver/services/data-WuHan/rest/data
  // 作用: 定义数据服务的REST API路径，用于矢量要素数据获取
  const dataService = import.meta.env.VITE_SUPERMAP_DATA_SERVICE || 'iserver/services/data-WuHan/rest/data'
  
      return {
      baseUrl: baseUrl.replace(/\/$/, ''), // 移除末尾斜杠
      mapService,
      dataService,
      datasetName: import.meta.env.VITE_SUPERMAP_DATASET_NAME || '',
      
      // ===== 底图服务配置 =====
      // 调用者: useMap.ts -> updateBaseMap() -> getCurrentBaseMapUrl()
      // 服务器地址: https://www.supermapol.com/proxy/... (SuperMap在线底图服务)
      // 作用: 提供浅色和深色主题的底图瓦片服务，根据主题自动切换
      baseMaps: {
        light: 'https://www.supermapol.com/proxy/gqzvimgx/iserver/services/map_china-1-_331nhzuk/rest/maps/China_Light?prjCoordSys=%7B%22epsgCode%22:4326%7D',
        dark: 'https://www.supermapol.com/proxy/dd2z0vuq/iserver/services/map_china-1-_hl5n2ma6/rest/maps/China_Dark'
      },
      
      // ===== 备用底图服务配置 =====
      // 调用者: useMap.ts -> updateBaseMap() (备用方案)
      // 服务器地址: https://www.supermapol.com/proxy/... (SuperMap在线底图服务)
      // 作用: 当主底图服务不可用时的备用底图服务
      fallbackBaseMaps: {
        light: 'https://www.supermapol.com/proxy/gqzvimgx/iserver/services/map_china-1-_331nhzuk/rest/maps/China_Light?prjCoordSys=%7B%22epsgCode%22:4326%7D',
        dark: 'https://www.supermapol.com/proxy/dd2z0vuq/iserver/services/map_china-1-_hl5n2ma6/rest/maps/China_Dark'
      },
          // ===== 武汉矢量图层配置 =====
      // 调用者: useMap.ts -> loadVectorLayers() -> loadVectorLayer()
      // 服务器地址: ${baseUrl}/${dataService}/datasources/wuhan/datasets/{数据集名}
      // 作用: 定义所有武汉地区的矢量图层，包括县级边界、交通、水系、建筑物、基础设施等
      wuhanLayers: [
        // ===== 武汉市县级行政区图层 =====
        // 调用者: useMap.ts -> loadVectorLayer()
        // 服务器地址: ${baseUrl}/iserver/services/data-WuHan/rest/data/datasources/wuhan/datasets/武汉_县级
        // 作用: 提供武汉市的县级行政区边界数据，用于区域划分和空间分析
        { 
          name: '武汉_县级@wuhan@@武汉', 
          type: 'polygon', 
          visible: true, 
          group: '县级行政区',
          datasetName: '武汉_县级',
          dataService: 'iserver/services/map-WuHan/rest/maps/武汉'
        },
      
        // ===== 交通设施图层组 =====
        // 调用者: useMap.ts -> loadVectorLayer()
        // 服务器地址: ${baseUrl}/iserver/services/data-WuHan/rest/data/datasources/wuhan/datasets/公路
        // 作用: 提供武汉市公路网络数据，用于交通分析和路径规划
        { 
          name: '公路@wuhan@@武汉', 
          type: 'line', 
          visible: true, 
          group: '城市基本信息',
          datasetName: '公路',
          dataService: 'iserver/services/map-WuHan/rest/maps/武汉'
        },
        // 调用者: useMap.ts -> loadVectorLayer()
        // 服务器地址: ${baseUrl}/iserver/services/data-WuHan/rest/data/datasources/wuhan/datasets/铁路
        // 作用: 提供武汉市铁路网络数据，用于交通分析和运输规划
        { 
          name: '铁路@wuhan@@武汉', 
          type: 'line', 
          visible: true, 
          group: '城市基本信息',
          datasetName: '铁路',
          dataService: 'iserver/services/map-WuHan/rest/maps/武汉'
        },
      
      // 城市基本信息图层组 - 水系信息
      { 
        name: '水系线@wuhan@@武汉', 
        type: 'line', 
        visible: true, 
        group: '城市基本信息',
        datasetName: '水系线',
        dataService: 'iserver/services/map-WuHan/rest/maps/武汉'
      },
      { 
        name: '水系面@wuhan@@武汉', 
        type: 'polygon', 
        visible: true, 
        group: '城市基本信息',
        datasetName: '水系面',
        dataService: 'iserver/services/map-WuHan/rest/maps/武汉'
      },
      
      // 城市基本信息图层组 - 建筑信息
      { 
        name: '建筑物面@wuhan@@武汉', 
        type: 'polygon', 
        visible: true, 
        group: '城市基本信息',
        datasetName: '建筑物面',
        dataService: 'iserver/services/map-WuHan/rest/maps/武汉'
      },
      
      // 基础设施图层组 - 居民地信息
      { 
        name: '居民地地名点@wuhan@@武汉', 
        type: 'point', 
        visible: true, 
        group: '基础设施',
        datasetName: '居民地地名点',
        dataService: 'iserver/services/map-WuHan/rest/maps/武汉'
      },
      
      // 基础设施图层组 - 公共服务设施
      { 
        name: '学校@wuhan@@武汉', 
        type: 'point', 
        visible: true, 
        group: '基础设施',
        datasetName: '学校',
        dataService: 'iserver/services/map-WuHan/rest/maps/武汉'
      },
      { 
        name: '医院@wuhan@@武汉', 
        type: 'point', 
        visible: true, 
        group: '基础设施',
        datasetName: '医院',
        dataService: 'iserver/services/map-WuHan/rest/maps/武汉'
      },
      
      // DEM图层 - 已禁用加载，避免使用瓦片服务
      // { 
      //   name: 'DEM_wuhan@wuhan@@武汉', 
      //   type: 'raster', 
      //   visible: true, 
      //   group: '地形数据',
      //   datasetName: 'DEM_wuhan',
      //   dataService: 'iserver/services/map-WuHan/rest/maps/武汉'
      // }
    ],
    timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 10000,
    retryCount: Number(import.meta.env.VITE_API_RETRY_COUNT) || 3,
    devMode: import.meta.env.VITE_DEV_MODE === 'true' || import.meta.env.DEV
  }
}

/**
 * 获取完整的SuperMap服务URL
 * 调用者: mapStore.ts -> createMapConfig() -> getFullUrl()
 * 作用: 根据服务类型构建完整的SuperMap iServer服务访问地址
 */
export const getFullUrl = (endpoint: 'map' | 'data'): string => {
  // ===== 获取API配置 =====
  // 调用者: getFullUrl() -> createAPIConfig()
  // 作用: 获取SuperMap服务器的基础配置信息
  const config = createAPIConfig()
  
  // ===== 选择服务类型 =====
  // 调用者: getFullUrl()
  // 作用: 根据endpoint参数选择对应的服务路径
  const service = endpoint === 'map' ? config.mapService : config.dataService
  
  // ===== 构建完整URL =====
  // 调用者: mapStore.ts -> createMapConfig()
  // 服务器地址: ${baseUrl}/${service}
  // 作用: 返回完整的SuperMap服务访问地址
  return `${config.baseUrl}/${service}`
}

export const isDevelopment = (): boolean => {
  return createAPIConfig().devMode
}

// 获取按组分类的图层
export const getLayersByGroup = () => {
  const config = createAPIConfig()
  const groupedLayers: Record<string, WuhanLayer[]> = {}
  
  config.wuhanLayers.forEach(layer => {
    const group = layer.group || '其他'
    if (!groupedLayers[group]) {
      groupedLayers[group] = []
    }
    groupedLayers[group].push(layer)
  })
  
  return groupedLayers
}

// 获取指定组的图层
export const getLayersByGroupName = (groupName: string): WuhanLayer[] => {
  const config = createAPIConfig()
  return config.wuhanLayers.filter(layer => layer.group === groupName)
}

// 获取所有图层组名称
export const getLayerGroupNames = (): string[] => {
  const config = createAPIConfig()
  const groups = new Set(config.wuhanLayers.map(layer => layer.group).filter((group): group is string => Boolean(group)))
  return Array.from(groups)
}

// 获取指定图层的完整地图服务URL
export const getLayerMapServiceUrl = (layerName: string): string | null => {
  const config = createAPIConfig()
  const layer = config.wuhanLayers.find(l => l.name === layerName)
  
  if (layer && layer.dataService) {
    return `${config.baseUrl}/${layer.dataService}/${layer.name}`
  }
  
  return null
}

// 获取指定图层的完整数据服务URL（包含数据集）
export const getLayerDatasetUrl = (layerName: string): string | null => {
  const config = createAPIConfig()
  const layer = config.wuhanLayers.find(l => l.name === layerName)
  
  if (layer && layer.dataService && layer.datasetName) {
    return `${config.baseUrl}/${layer.dataService}/${layer.datasetName}`
  }
  
  return null
}

// 获取所有地图服务URL
export const getAllMapServiceUrls = (): Record<string, string> => {
  const config = createAPIConfig()
  const urls: Record<string, string> = {}
  
  config.wuhanLayers.forEach(layer => {
    if (layer.dataService) {
      urls[layer.name] = `${config.baseUrl}/${layer.dataService}/${layer.name}`
    }
  })
  
  return urls
}

// 测试函数：验证图层配置
export const testLayerConfig = () => {
  const config = createAPIConfig()
  console.log('\n=== 图层列表 ===')
  config.wuhanLayers.forEach((layer, index) => {
    console.log(`${index + 1}. ${layer.name}`)
    console.log(`   类型: ${layer.type}`)
    console.log(`   组: ${layer.group}`)
    console.log(`   服务URL: ${config.baseUrl}/${layer.dataService}`)
    console.log(`   图层名称: ${layer.name}`)
    console.log('')
  })
  
  return config
}

// 获取当前主题对应的底图URL
export const getCurrentBaseMapUrl = (theme: 'light' | 'dark'): string => {
  const config = createAPIConfig()
  return config.baseMaps[theme]
}

// 获取所有底图配置
export const getBaseMapConfig = () => {
  const config = createAPIConfig()
  return config.baseMaps
}

export default createAPIConfig