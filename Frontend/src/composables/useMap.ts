import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useLoadingStore } from '@/stores/loadingStore'
import { useThemeStore } from '@/stores/themeStore'
import { useLayerManager } from '@/composables/useLayerManager'
import { superMapClient } from '@/api/supermap'
import { handleError, notificationManager } from '@/utils/notification'
import { createAPIConfig, testLayerConfig, getCurrentBaseMapUrl } from '@/utils/config'
import { useFeatureInfo } from '@/composables/useFeatureInfo'

const ol = window.ol;

export function useMap() {
  let mapStore = useMapStore()
  const analysisStore = useAnalysisStore()
  const loadingStore = useLoadingStore()
  const themeStore = useThemeStore()
  const layerManager = useLayerManager()
  const featureInfo = useFeatureInfo()
  const mapContainer = ref<HTMLElement | null>(null)
  const hoverTimer = ref<number | null>(null)
  const selectSourceRef = ref<any>(null) // ol.source.Vector
  const apiConfig = createAPIConfig()

  const initMap = async (): Promise<void> => {
    mapStore = useMapStore()
    
    // 测试图层配置
    testLayerConfig()
    
    try {
      if (!window.ol || !mapContainer.value) {
        throw new Error('地图容器或SuperMap SDK未准备就绪')
      }
      
      loadingStore.startLoading('map-init', '正在初始化地图...')
      
      // 检查服务健康状态
      const healthCheck = await superMapClient.checkServiceHealth()
      if (!healthCheck.success) {
        throw new Error(`SuperMap服务不可用: ${healthCheck.error}`)
      }
      
      const resolutions: number[] = [];
      for (let i = 0; i < 19; i++) {
          resolutions[i] = 180 / 256 / Math.pow(2, i);
      }

      const map = new ol.Map({
        target: mapContainer.value,
        controls: new ol.Collection([
          // 移除SuperMap Logo控件以避免水印显示
          new ol.control.Zoom({
            className: 'custom-zoom-control',
            target: undefined
          })
        ]),
        view: new ol.View({
          projection: mapStore.mapConfig.projection,
          resolutions: resolutions,
          center: mapStore.mapConfig.center,
          zoom: mapStore.mapConfig.zoom
        })
      })
      
      // 禁用双击放大功能
      const doubleClickInteraction = map.getInteractions().getArray().find(
        (interaction: any) => interaction instanceof ol.interaction.DoubleClickZoom
      )
      if (doubleClickInteraction) {
        map.removeInteraction(doubleClickInteraction)
      }
      
      const projectionExtent = mapStore.mapConfig.extent;

      const tileGrid = new ol.tilegrid.TileGrid({
          extent: projectionExtent,
          origin: ol.extent.getTopLeft(projectionExtent),
          resolutions: resolutions
      });

      // 创建底图图层 - 根据当前主题选择对应的底图
      const currentBaseMapUrl = getCurrentBaseMapUrl(themeStore.theme)
      console.log('当前主题:', themeStore.theme)
      console.log('底图URL:', currentBaseMapUrl)
      
      // 为不同主题使用不同的配置
      const sourceConfig: any = {
        url: currentBaseMapUrl,
        serverType: 'iserver'
      }
      
      // 为浅色主题添加额外配置
      if (themeStore.theme === 'light') {
        sourceConfig.crossOrigin = 'anonymous'
        sourceConfig.tileLoadFunction = undefined // 使用默认加载函数
      }
      
      const baseMapLayer = new ol.layer.Tile({
        source: new ol.source.TileSuperMapRest(sourceConfig),
        visible: true,
        zIndex: -1000 // 确保底图在最底层
      })
      
      // 添加底图加载事件监听
      baseMapLayer.getSource().on('tileloadstart', () => {
        console.log('底图瓦片开始加载')
      })
      baseMapLayer.getSource().on('tileloadend', () => {
        console.log('底图瓦片加载完成')
      })
      baseMapLayer.getSource().on('tileloaderror', (event: any) => {
        console.error('底图瓦片加载失败:', event)
      })
      
      // 确保底图图层被正确添加到地图
      map.addLayer(baseMapLayer)
      
      // 强制刷新地图以确保底图显示
      setTimeout(() => {
        map.updateSize()
        baseMapLayer.changed()
      }, 100)
      
      loadingStore.updateLoading('map-init', '正在加载图层...')
      
      // 使用新的API客户端加载矢量图层
      await loadVectorLayers(map)
      // 初始加载完成后立即应用一次样式（确保CSS变量生效）
      updateLayerStyles()
      
      const hoverSource = new ol.source.Vector()
      const accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim();
      const hoverLayer = new ol.layer.Vector({
        source: hoverSource,
        style: new ol.style.Style({
          image: new ol.style.Circle({ 
            radius: 6, 
            stroke: new ol.style.Stroke({color: accentColor, width: 2}), 
            fill: new ol.style.Fill({color: getComputedStyle(document.documentElement).getPropertyValue('--map-hover-fill').trim()}) 
          }),
          stroke: new ol.style.Stroke({color: accentColor, width: 2}),
          fill: new ol.style.Fill({color: getComputedStyle(document.documentElement).getPropertyValue('--map-hover-fill').trim()})
        })
      })
      map.addLayer(hoverLayer)
        
      const selectSource = new ol.source.Vector()
      const selectLayer = new ol.layer.Vector({
        source: selectSource,
        style: new ol.style.Style({
          image: new ol.style.Circle({ 
            radius: 8, 
            stroke: new ol.style.Stroke({color: accentColor, width: 3}), 
            fill: new ol.style.Fill({color: 'rgba(0,0,0,0)'}) 
          }),
          stroke: new ol.style.Stroke({color: accentColor, width: 3}),
          fill: new ol.style.Fill({color: 'rgba(0,0,0,0)'})
        })
      })
      map.addLayer(selectLayer)
      selectSourceRef.value = selectSource
        
      mapStore.setMap(map)
      mapStore.setLayers({
        base: baseMapLayer, // 设置底图图层
        hover: hoverLayer,
        select: selectLayer
      })
        
      setupMapEvents(map, hoverSource, selectSource)
        
      setTimeout(() => {
        map.updateSize()
      }, 100)

      const handleDrawLayerCompleted = (event: Event) => {
        layerManager.acceptDrawLayer((event as CustomEvent).detail)
      }
      window.addEventListener('drawLayerCompleted', handleDrawLayerCompleted)
      
      // 启动主题变化监听
      observeThemeChanges()
      
      loadingStore.stopLoading('map-init')
      notificationManager.success('地图初始化成功', '地图已准备就绪')
        
    } catch (error) {
      loadingStore.stopLoading('map-init')
      handleError(error, '地图初始化')
    }
  }
  
  const loadVectorLayers = async (map: any): Promise<void> => {
    const apiConfig = createAPIConfig()
    
    const loadTasks: Promise<void>[] = []
    for (const layerConfig of apiConfig.wuhanLayers) {
      const layerName = layerConfig.name.split('@')[0] || layerConfig.name
      loadingStore.updateLoading('map-init', `正在加载图层: ${layerName}`)
      if (layerConfig.type === 'raster') {
        console.log(`跳过栅格图层: ${layerName} (避免使用瓦片服务)`)
        continue;
      }
      const isDefaultVisible = layerName === '武汉_县级'
      loadTasks.push(loadVectorLayer(map, layerConfig, isDefaultVisible))
    }
    await Promise.allSettled(loadTasks)
  }
  

  
  // 动态更新图层样式，支持主题切换
  const updateLayerStyles = () => {
    mapStore.vectorLayers.forEach(layerInfo => {
      if (layerInfo.layer && layerInfo.source === 'supermap') {
        // 查找对应的配置
        const layerConfig = createAPIConfig().wuhanLayers.find(config => config.name === layerInfo.id);
        if (layerConfig) {
          const newStyle = createLayerStyle(layerConfig, layerInfo.name);
          layerInfo.layer.setStyle(newStyle);
        }
      }
    });
  }

  // 监听主题变化，更新图层样式和底图
  const observeThemeChanges = () => {
    const observer = new MutationObserver(() => {
      updateLayerStyles();
      updateBaseMap();
    });
    
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class', 'style'],
      subtree: false
    });
    
    // 监听主题存储的变化
    watch(() => themeStore.theme, (newTheme) => {
      console.log('主题变化检测到:', newTheme)
      updateBaseMap();
    });
    
    onUnmounted(() => {
      observer.disconnect();
    });
  }

  // 更新底图
  const updateBaseMap = () => {
    if (mapStore.map && mapStore.baseLayer) {
      const currentBaseMapUrl = getCurrentBaseMapUrl(themeStore.theme)
      console.log('更新底图 - 主题:', themeStore.theme, 'URL:', currentBaseMapUrl)
      
      // 为浅色主题使用不同的配置
      const sourceConfig: any = {
        url: currentBaseMapUrl,
        serverType: 'iserver'
      }
      
      // 为浅色主题添加额外配置
      if (themeStore.theme === 'light') {
        sourceConfig.crossOrigin = 'anonymous'
        sourceConfig.tileLoadFunction = undefined // 使用默认加载函数
      }
      
      const newBaseMapSource = new ol.source.TileSuperMapRest(sourceConfig)
      
      // 添加新底图源的事件监听
      newBaseMapSource.on('tileloadstart', () => {
        console.log(`新底图瓦片开始加载 (${themeStore.theme} 主题)`)
      })
      newBaseMapSource.on('tileloadend', () => {
        console.log(`新底图瓦片加载完成 (${themeStore.theme} 主题)`)
      })
      newBaseMapSource.on('tileloaderror', (event: any) => {
        console.error(`新底图瓦片加载失败 (${themeStore.theme} 主题):`, event)
        console.error('失败的瓦片URL:', event.tile?.src_)
        console.error('错误详情:', event.target?.getState?.())
      })
      
      // 清除旧的底图源
      const oldSource = mapStore.baseLayer.getSource()
      if (oldSource) {
        oldSource.clear?.()
      }
      
      // 设置新的底图源
      mapStore.baseLayer.setSource(newBaseMapSource)
      
      // 强制刷新底图图层
      mapStore.baseLayer.changed()
      
      // 强制刷新地图视图
      mapStore.map.renderSync()
      
      // 确保地图正确显示
      setTimeout(() => {
        mapStore.map.updateSize()
        mapStore.map.renderSync()
      }, 100)
    }
  }

  const createLayerStyle = (layerConfig: any, layerName: string): any => {
    // 固定图层颜色（不随主题变化）：优先读取 --layer-stroke-<name> / --layer-fill-<name>
    const css = getComputedStyle(document.documentElement);
    const strokeVar = css.getPropertyValue(`--layer-stroke-${layerName}`).trim();
    const fillVar = css.getPropertyValue(`--layer-fill-${layerName}`).trim();
    const accentFallback = css.getPropertyValue('--accent').trim() || '#007bff';

    // 明确的图层颜色映射（按图层名），优先级低于 CSS 变量
    const fallbackColorMap: Record<string, { stroke: string; fill: string } > = {
      '武汉_县级': { stroke: accentFallback, fill: 'rgba(0,0,0,0)' },
      '公路': { stroke: '#f39c12', fill: 'rgba(243,156,18,0.08)' },
      '铁路': { stroke: '#8e44ad', fill: 'rgba(142,68,173,0.08)' },
      '水系面': { stroke: '#2980b9', fill: 'rgba(41,128,185,0.18)' },
      '水系线': { stroke: '#3498db', fill: 'rgba(52,152,219,0.10)' },
      '建筑物面': { stroke: '#7f8c8d', fill: 'rgba(127,140,141,0.20)' },
      '居民地地名点': { stroke: '#e74c3c', fill: 'rgba(231,76,60,0.35)' },
      '学校': { stroke: '#27ae60', fill: 'rgba(39,174,96,0.35)' },
      '医院': { stroke: '#c0392b', fill: 'rgba(192,57,43,0.35)' }
    };
    const mapped = fallbackColorMap[layerName] || { stroke: accentFallback, fill: 'rgba(0,123,255,0.1)' };
    const resolvedStroke = strokeVar || mapped.stroke;
    const resolvedFill = fillVar || mapped.fill;
    
    // 特殊处理县级图层，设置为透明显示
    if (layerName === '武汉_县级') {
      return new ol.style.Style({
        stroke: new ol.style.Stroke({ 
          color: resolvedStroke, 
          width: 1.5 
        }),
        fill: new ol.style.Fill({ color: 'rgba(0, 0, 0, 0)' }) // 完全透明
      });
    }
    
    // 根据图层类型设置不同的样式
    switch (layerConfig.type) {
      case 'point':
        return new ol.style.Style({
          image: new ol.style.Circle({
            radius: 6,
            stroke: new ol.style.Stroke({ 
              color: resolvedStroke, 
              width: 2 
            }),
            fill: new ol.style.Fill({ 
              color: resolvedFill 
            })
          })
        });
      case 'line':
        return new ol.style.Style({
          stroke: new ol.style.Stroke({ 
            color: resolvedStroke, 
            width: 2 
          }),
          fill: new ol.style.Fill({ color: 'rgba(0, 0, 0, 0)' })
        });
      case 'polygon':
        return new ol.style.Style({
          stroke: new ol.style.Stroke({ 
            color: resolvedStroke, 
            width: 1.5 
          }),
          fill: new ol.style.Fill({ 
            color: resolvedFill 
          })
        });
      default:
        return new ol.style.Style({
          stroke: new ol.style.Stroke({ 
            color: resolvedStroke, 
            width: 1.5 
          }),
          fill: new ol.style.Fill({ 
            color: resolvedFill 
          })
        });
    }
  }

  const loadVectorLayer = async (map: any, layerConfig: any, visibleOverride?: boolean): Promise<void> => {
    const layerName = layerConfig.name.split('@')[0] || layerConfig.name
    
    console.log(`开始加载图层: ${layerName}`)
    
    // 使用增强的样式系统
    const style = createLayerStyle(layerConfig, layerName);
    
    // 创建矢量图层，使用 FeatureService 加载数据
    const vectorLayer = new ol.layer.Vector({
      source: new ol.source.Vector({}),
      style: style // 应用自定义样式
    });
    
    // 异步加载所有数据 - 使用 getFeaturesByBounds
    const featureService = new ol.supermap.FeatureService(mapStore.mapConfig.dataUrl);
    
    const parts = layerConfig.name.split('@');
    const dataset = parts[0];
    const datasource = parts[1];
    


    // 预读服务器features.json，提取 startIndex 与分页长度，作为 fromIndex/toIndex 的默认值
    const metaUrlBounds = `${mapStore.mapConfig.dataUrl}/datasources/${datasource}/datasets/${dataset}/features.json`;
    const metaJsonBounds = await (await fetch(metaUrlBounds)).json();
    const startIndexDefaultBounds: number = (metaJsonBounds && typeof metaJsonBounds.startIndex === 'number') ? metaJsonBounds.startIndex : 0;
    const featureCountBounds: number = (metaJsonBounds && typeof metaJsonBounds.featureCount === 'number') ? metaJsonBounds.featureCount : 20;
    const computedFromIndexBounds: number = startIndexDefaultBounds;
    const computedToIndexBounds: number = startIndexDefaultBounds + featureCountBounds - 1;
    console.log('Bounds预读(严格按JSON): startIndex=', startIndexDefaultBounds, ' featureCount=', featureCountBounds, ' => fromIndex=', computedFromIndexBounds, ' toIndex=', computedToIndexBounds);

    // 创建武汉市的完整边界范围
    const wuhanBounds = new ol.geom.Polygon([[
      [113.7, 29.97],
      [115.08, 29.97],
      [115.08, 31.36],
      [113.7, 31.36],
      [113.7, 29.97]
    ]]);

    // 分页大小（首批 + 后续批次）
    const pageSize = 10000;
    const initialToIndex = Math.min(computedFromIndexBounds + pageSize - 1, computedToIndexBounds);

    const getFeaturesByBoundsParams = new ol.supermap.GetFeaturesByBoundsParameters({
      datasetNames: [`${datasource}:${dataset}`],
      bounds: ol.extent.boundingExtent(wuhanBounds.getCoordinates()[0]),
      // 移除所有限制，获取所有要素
      returnContent: true,
      returnFeaturesOnly: true,
      maxFeatures: -1, // 设置为-1表示无限制，获取所有要素
      fromIndex: computedFromIndexBounds,
      toIndex: initialToIndex
    });

    // 打印查询参数信息
    console.log(`=== 图层 ${layerName} 查询参数信息 ===`);
    console.log('查询边界范围:', ol.extent.boundingExtent(wuhanBounds.getCoordinates()[0]));
    console.log('数据集路径:', `${datasource}:${dataset}`);
    console.log('完整查询参数:', getFeaturesByBoundsParams);
    console.log('分页参数(范围查询): fromIndex=', getFeaturesByBoundsParams.fromIndex, ' toIndex=', getFeaturesByBoundsParams.toIndex, ' totalToIndex=', computedToIndexBounds, ' pageSize=', pageSize);
    
    // 检查数据集总要素数量
    try {
      const countParams = new ol.supermap.GetFeaturesByBoundsParameters({
        datasetNames: [`${datasource}:${dataset}`],
        bounds: ol.extent.boundingExtent(wuhanBounds.getCoordinates()[0]),
        returnContent: false, // 不返回要素内容，只获取数量
        returnFeaturesOnly: true
      });
      
      featureService.getFeaturesByBounds(countParams, (countResult: any) => {
        console.log(`=== 图层 ${layerName} 数据集统计信息 ===`);
        console.log('数据集总要素数量:', countResult.result?.totalCount || '未知');
        console.log('当前查询返回数量:', countResult.result?.features?.length || 0);
      });
    } catch (error) {
      console.log('无法获取数据集统计信息:', error);
    }

    featureService.getFeaturesByBounds(getFeaturesByBoundsParams, (serviceResult: any) => {
      if (serviceResult.result && serviceResult.result.features) {
        // 输出原始要素数据
        console.log('==============serviceResult=======================', serviceResult);
        console.log(`=== 图层 ${layerName} 原始要素数据 ===`);
        console.log('原始要素数组:', serviceResult.result.features);
        console.log('要素数量:', serviceResult.result.features.length);
        console.log('原始数据来源:', 'SuperMap iServer FeatureService API');
        console.log('API响应完整结构:', serviceResult);
        console.log('API响应状态:', serviceResult.succeed ? '成功' : '失败');
        console.log('API响应错误信息:', serviceResult.error || '无');
        console.log('原始数据格式:', 'GeoJSON (由SuperMap iServer自动生成)');
        console.log('数据获取方式:', 'HTTP POST请求到FeatureService');
        const fullApiUrlBounds = `${mapStore.mapConfig.dataUrl}/datasources/${datasource}/datasets/${dataset}/features.json`;
        console.log('完整请求URL:', fullApiUrlBounds);
        // 直接GET请求该JSON资源，打印其完整返回内容（仅用于调试）
        fetch(fullApiUrlBounds)
          .then(r => r.json())
          .then(json => {
            console.log('完整API响应JSON(范围查询):', json);
            const printPairs = (node: any, path: string) => {
              if (node !== null && typeof node === 'object') {
                if (Array.isArray(node)) {
                  for (let i = 0; i < node.length; i += 1) {
                    printPairs(node[i], `${path}[${i}]`);
                  }
                } else {
                  for (const key in node) {
                    if (Object.prototype.hasOwnProperty.call(node, key)) {
                      const nextPath = path ? `${path}.${key}` : key;
                      printPairs(node[key], nextPath);
                    }
                  }
                }
              } else {
                console.log('KV(范围查询):', path, '=', node);
              }
            };
            printPairs(json, '');
          });
        console.log('请求参数:', getFeaturesByBoundsParams);
        // 显式打印 startIndex 与 featureCount（范围查询）
        console.log('startIndex:', serviceResult.result.startIndex);
        console.log('featureCount:', serviceResult.result.featureCount);
        // 重点显示 featureCount（范围查询）
        console.log('==============featureCount=======================', serviceResult.result.featureCount ?? serviceResult.result.totalCount ?? serviceResult.result.currentCount ?? serviceResult.result.features?.length ?? 0);
        
        // 关联 childUriList 与当前加载要素的关系
        const startIndexBounds = serviceResult.result.startIndex;
        const childUriListBounds: string[] | undefined = serviceResult.result.childUriList;
        const serverReportedFeatureCountBounds = serviceResult.result.featureCount ?? serviceResult.result.totalCount;
        // 当 startIndex/featureCount 未定义时，尝试从 childUriList/返回要素推导
        let derivedStartIndexBounds: number | null = null;
        if ((startIndexBounds === undefined || startIndexBounds === null) && Array.isArray(childUriListBounds) && childUriListBounds.length > 0) {
          const lastPath = childUriListBounds[0].split('/').pop() || '';
          const parts = lastPath.split('-');
          if (parts.length >= 1) {
            const parsed = parseInt(parts[0], 10);
            if (!isNaN(parsed)) derivedStartIndexBounds = parsed;
          }
        }
        let derivedFeatureCountBounds: number | null = null;
        if (serverReportedFeatureCountBounds === undefined || serverReportedFeatureCountBounds === null) {
          if (Array.isArray(childUriListBounds)) derivedFeatureCountBounds = childUriListBounds.length;
          if (derivedFeatureCountBounds === null && Array.isArray(serviceResult.result.features)) derivedFeatureCountBounds = serviceResult.result.features.length;
        }
        console.log('StartIndex(范围查询):', startIndexBounds, '=> 推导:', derivedStartIndexBounds);
        console.log('Server端统计的featureCount(范围查询):', serverReportedFeatureCountBounds, '=> 推导:', derivedFeatureCountBounds);
        console.log('childUriList是否存在(范围查询):', Array.isArray(childUriListBounds));
        console.log('childUriList长度(范围查询):', Array.isArray(childUriListBounds) ? childUriListBounds.length : 0);
        if (Array.isArray(childUriListBounds) && childUriListBounds.length > 0) {
          console.log('childUriList示例(前3条，范围查询):', childUriListBounds.slice(0, 3));
          console.log('childUriList示例(后3条，范围查询):', childUriListBounds.slice(-3));
        }
        
        // 输出第一个要素的详细信息
        if (serviceResult.result.features.length > 0) {
          console.log('第一个要素详情:', JSON.stringify(serviceResult.result.features[0], null, 2));
          console.log('第一个要素数据来源:', 'SuperMap iServer数据库');
          console.log('第一个要素原始格式:', 'SuperMap内部格式 -> GeoJSON转换');
        }
        
        // 打印转换方式信息
        console.log(`=== 图层 ${layerName} 转换方式信息 ===`);
        console.log('转换要素使用的方式是:', 'new ol.format.GeoJSON().readFeatures()');
        console.log('转换的原始数据:', serviceResult.result.features);
        
        const features = (new ol.format.GeoJSON()).readFeatures(serviceResult.result.features);
        
        // 输出转换后的OpenLayers要素信息
        console.log(`=== 图层 ${layerName} OpenLayers要素信息 ===`);
        console.log('转换后要素数量:', features.length);
        if (features.length > 0) {
          const firstFeature = features[0];
          console.log('第一个OpenLayers要素:', {
            geometry: firstFeature.getGeometry() ? {
              type: firstFeature.getGeometry().getType(),
              coordinates: firstFeature.getGeometry().getCoordinates()
            } : null,
            properties: firstFeature.getProperties(),
            id: firstFeature.getId()
          });
        }
        
        // 打印显示方法信息
        console.log(`=== 图层 ${layerName} 显示方法信息 ===`);
        console.log('把OpenLayers要素显示到地图的方法是:', 'vectorLayer.getSource().addFeatures()');
        console.log('使用的图层类型:', 'ol.layer.Vector');
        console.log('使用的数据源类型:', 'ol.source.Vector');
        
        // 进一步打印本次加载与服务器返回之间的对齐关系
        console.log('本次添加到地图的要素数量(范围查询):', features.length);
        console.log('服务器返回要素数组长度(范围查询):', serviceResult.result.features.length);
        console.log('childUriList与features数量是否一致(范围查询):', Array.isArray(childUriListBounds) ? childUriListBounds.length === serviceResult.result.features.length : 'childUriList缺失');
        if (Array.isArray(childUriListBounds)) {
          for (let i = 0; i < Math.min(3, features.length, childUriListBounds.length); i += 1) {
            const f = features[i];
            console.log(`示例映射[范围查询] i=${i}: childUri=${childUriListBounds[i]}`, {
              featureId: f.getId?.() || null,
              geometryType: f.getGeometry?.()?.getType?.() || null
            });
          }
        }
        
        vectorLayer.getSource().addFeatures(features);

        // 后续分页：从 initialToIndex+1 到 computedToIndexBounds，按 pageSize 继续加载
        const addPage = (from: number, to: number): Promise<void> => new Promise(resolve => {
          const pageParams = new ol.supermap.GetFeaturesByBoundsParameters({
            datasetNames: [`${datasource}:${dataset}`],
            bounds: ol.extent.boundingExtent(wuhanBounds.getCoordinates()[0]),
            returnContent: true,
            returnFeaturesOnly: true,
            maxFeatures: -1,
            fromIndex: from,
            toIndex: to
          });
          featureService.getFeaturesByBounds(pageParams, (res: any) => {
            if (res.result && res.result.features) {
              const feats = (new ol.format.GeoJSON()).readFeatures(res.result.features);
              vectorLayer.getSource().addFeatures(feats);
              console.log('分页加载完成: fromIndex=', from, ' toIndex=', to, ' 本批要素数=', feats.length);
            }
            resolve();
          });
        });

        (async () => {
          for (let start = initialToIndex + 1; start <= computedToIndexBounds; start += pageSize) {
            const end = Math.min(start + pageSize - 1, computedToIndexBounds);
            await addPage(start, end);
          }
          console.log('全部分页预加载完成: ', layerName, ' 范围: ', computedFromIndexBounds, '-', computedToIndexBounds);
        })();
        
        // 显示图层加载完成的详细信息
        const layerInfo = {
          layerName: layerName,
          featureCount: features.length,
          serviceResult: serviceResult.result,
          features: serviceResult.result.features,
          totalCount: serviceResult.result.totalCount,
          currentCount: serviceResult.result.currentCount,
          maxFeatures: serviceResult.result.maxFeatures
        };
        
        // 在界面上显示图层加载信息
        notificationManager.info(
          `图层 ${layerName} 加载完成`,
          `共 ${features.length} 个要素\n总要素数: ${serviceResult.result.totalCount || '未知'}\n当前返回: ${serviceResult.result.currentCount || features.length}\n最大要素数: ${serviceResult.result.maxFeatures || '无限制'}\n==============featureCount======================= ${(serviceResult.result.featureCount ?? serviceResult.result.totalCount ?? serviceResult.result.currentCount ?? features.length) || 0}\n数据来源: SuperMap iServer\n服务器地址: ${mapStore.mapConfig.dataUrl}`
        );
        
        // 输出详细信息到控制台
        console.log(`=== 图层 ${layerName} 加载完成详细信息 ===`);
        console.log('图层名称:', layerName);
        console.log('要素数量:', features.length);
        console.log('服务返回完整信息:', serviceResult.result);
        console.log('总要素数:', serviceResult.result.totalCount);
        console.log('当前返回数:', serviceResult.result.currentCount);
        console.log('最大要素数:', serviceResult.result.maxFeatures);
        console.log('原始要素数据:', serviceResult.result.features);
        console.log('数据来源服务器:', mapStore.mapConfig.dataUrl);
        console.log('数据获取API:', 'SuperMap FeatureService GetFeaturesByBounds');
        console.log('数据原始格式:', 'SuperMap内部格式');
        console.log('数据转换格式:', 'GeoJSON');
        console.log('数据转换工具:', 'SuperMap iServer自动转换');
        console.log('完整API请求地址:', `${mapStore.mapConfig.dataUrl}/datasources/${datasource}/datasets/${dataset}/features.json`);
        console.log('数据存储位置:', 'SuperMap iServer数据库');
        console.log('数据服务类型:', 'RESTful FeatureService');
        
        // 显示第一个要素的详细信息
        if (serviceResult.result.features && serviceResult.result.features.length > 0) {
          console.log('第一个要素完整信息:', JSON.stringify(serviceResult.result.features[0], null, 2));
        }
      } else {
        console.warn(`图层 ${layerName} 未获取到数据`);
        notificationManager.warning(
          `图层 ${layerName} 加载失败`,
          '未获取到任何要素数据'
        );
      }
    });
    
    // 设置图层可见性：优先使用覆盖值，否则沿用配置
    const resolvedVisible = typeof visibleOverride === 'boolean' ? visibleOverride : !!layerConfig.visible
    vectorLayer.setVisible(resolvedVisible);
    // 设置图层zIndex：将“武汉_县级”置于最底层
    const zIndex = layerName === '武汉_县级' ? 0 : 10 + mapStore.vectorLayers.length;
    vectorLayer.setZIndex(zIndex);
    
    map.addLayer(vectorLayer);
    mapStore.vectorLayers.push({
      id: layerConfig.name,
      name: layerName,
      layer: vectorLayer,
      visible: resolvedVisible,
      type: 'vector',
      source: 'supermap'
    });
    
    console.log(`图层 ${layerName} 已添加到地图`)
  }
  

  // 完全移除栅格图层加载函数，只保留矢量图层
  // const loadRasterLayer = ... 已删除

  // 要素信息显示功能
  const getFeatureInfo = async (coordinate: number[], layerName: string): Promise<any> => {
    try {
      const featureService = new ol.supermap.FeatureService(mapStore.mapConfig.dataUrl);
      
      // 解析图层信息
      const parts = layerName.split('@');
      const dataset = parts[0]; // 如 "武汉_县级"
      const datasource = parts[1] || 'wuhan'; // 默认为 "wuhan"
      
      // 增加详细的服务器地址和API端点信息
      console.log(`=== 要素查询 ${layerName} 服务器地址信息 ===`);
      console.log('基础数据服务URL:', mapStore.mapConfig.dataUrl);
      console.log('FeatureService实例:', featureService);
      console.log('数据集名称:', dataset);
      console.log('数据源名称:', datasource);
      console.log('完整数据集路径:', `${datasource}:${dataset}`);
      console.log('实际请求的API端点:', `${mapStore.mapConfig.dataUrl}/datasources/${datasource}/datasets/${dataset}/features.json`);
      console.log('GetFeaturesByGeometry API完整URL:', `${mapStore.mapConfig.dataUrl}/datasources/${datasource}/datasets/${dataset}/features.json`);
      console.log('数据来源说明:', '原始数据来自SuperMap iServer的FeatureService，通过GetFeaturesByGeometry接口获取');
      console.log('查询坐标:', coordinate);
      console.log('查询容差:', 0.001);
      
      // 预读服务器features.json，提取 startIndex 与分页长度，作为 fromIndex/toIndex 的默认值（几何查询）
      const metaUrlGeometry = `${mapStore.mapConfig.dataUrl}/datasources/${datasource}/datasets/${dataset}/features.json`;
      const metaJsonGeometry = await (await fetch(metaUrlGeometry)).json();
      const startIndexDefaultGeometry: number = (metaJsonGeometry && typeof metaJsonGeometry.startIndex === 'number') ? metaJsonGeometry.startIndex : 0;
      const featureCountGeometry: number = (metaJsonGeometry && typeof metaJsonGeometry.featureCount === 'number') ? metaJsonGeometry.featureCount : 20;
      const computedFromIndexGeometry: number = startIndexDefaultGeometry;
      const computedToIndexGeometry: number = startIndexDefaultGeometry + featureCountGeometry - 1;
      console.log('Geometry预读(严格按JSON): startIndex=', startIndexDefaultGeometry, ' featureCount=', featureCountGeometry, ' => fromIndex=', computedFromIndexGeometry, ' toIndex=', computedToIndexGeometry);

      // 创建几何查询参数 - 点击位置的缓冲区查询
      const tolerance = 0.001; // 容差值，可根据需要调整
      const buffer = new ol.geom.Point(coordinate).buffer(tolerance);
      
      const getFeaturesByGeometryParams = new ol.supermap.GetFeaturesByGeometryParameters({
        datasetNames: [`${datasource}:${dataset}`],
        geometry: buffer,
        spatialQueryMode: ol.supermap.SpatialQueryMode.INTERSECT,
        returnContent: true,
        returnFeaturesOnly: true, // 性能优化：只返回要素数据，不返回元数据
        // 确保返回所有字段
        attributeFilter: '',
        fields: ['*'], // 返回所有字段
        fromIndex: computedFromIndexGeometry,
        toIndex: computedToIndexGeometry
      });
      
      console.log('查询参数:', getFeaturesByGeometryParams);
      console.log('分页参数(几何查询): fromIndex=', getFeaturesByGeometryParams.fromIndex, ' toIndex=', getFeaturesByGeometryParams.toIndex);
      console.log('查询几何体:', buffer);
      console.log('空间查询模式:', ol.supermap.SpatialQueryMode.INTERSECT);

      return new Promise((resolve, reject) => {
        featureService.getFeaturesByGeometry(getFeaturesByGeometryParams, (serviceResult: any) => {
                // 详细分析服务返回的完整结构
      console.log(`=== 图层 ${layerName} 服务返回完整结构分析 ===`);
      console.log('完整serviceResult:', serviceResult);
      console.log('serviceResult.result:', serviceResult.result);
      console.log('serviceResult.result.features:', serviceResult.result?.features);
      console.log('serviceResult.result.features.length:', serviceResult.result?.features?.length);
      console.log('serviceResult.result.totalCount:', serviceResult.result?.totalCount);
      console.log('serviceResult.result.currentCount:', serviceResult.result?.currentCount);
      console.log('serviceResult.result.maxFeatures:', serviceResult.result?.maxFeatures);
      console.log('原始数据来源:', 'SuperMap iServer FeatureService API');
      console.log('API响应状态:', serviceResult.succeed ? '成功' : '失败');
      console.log('API响应错误信息:', serviceResult.error || '无');
      console.log('数据获取方式:', 'HTTP POST请求到FeatureService');
      const fullApiUrlGeometry = `${mapStore.mapConfig.dataUrl}/datasources/${datasource}/datasets/${dataset}/features.json`;
      console.log('完整请求URL:', fullApiUrlGeometry);
      // 直接GET请求该JSON资源，打印其完整返回内容（仅用于调试）
      fetch(fullApiUrlGeometry)
        .then(r => r.json())
        .then(json => {
          console.log('完整API响应JSON(几何查询):', json);
          const printPairs = (node: any, path: string) => {
            if (node !== null && typeof node === 'object') {
              if (Array.isArray(node)) {
                for (let i = 0; i < node.length; i += 1) {
                  printPairs(node[i], `${path}[${i}]`);
                }
              } else {
                for (const key in node) {
                  if (Object.prototype.hasOwnProperty.call(node, key)) {
                    const nextPath = path ? `${path}.${key}` : key;
                    printPairs(node[key], nextPath);
                  }
                }
              }
            } else {
              console.log('KV(几何查询):', path, '=', node);
            }
          };
          printPairs(json, '');
        });
      console.log('数据原始格式:', 'SuperMap内部格式');
      console.log('数据转换格式:', 'GeoJSON (由SuperMap iServer自动转换)');
      
      // 如果是按几何查询，补充 childUriList 等与地图要素关系日志
      const startIndexGeometry = serviceResult.result?.startIndex;
      const childUriListGeometry: string[] | undefined = serviceResult.result?.childUriList;
      const serverReportedFeatureCountGeometry = serviceResult.result?.featureCount ?? serviceResult.result?.totalCount;
      // 推导缺失字段
      let derivedStartIndexGeometry: number | null = null;
      if ((startIndexGeometry === undefined || startIndexGeometry === null) && Array.isArray(childUriListGeometry) && childUriListGeometry.length > 0) {
        const lastPath = childUriListGeometry[0].split('/').pop() || '';
        const parts = lastPath.split('-');
        if (parts.length >= 1) {
          const parsed = parseInt(parts[0], 10);
          if (!isNaN(parsed)) derivedStartIndexGeometry = parsed;
        }
      }
      let derivedFeatureCountGeometry: number | null = null;
      if (serverReportedFeatureCountGeometry === undefined || serverReportedFeatureCountGeometry === null) {
        if (Array.isArray(childUriListGeometry)) derivedFeatureCountGeometry = childUriListGeometry.length;
        if (derivedFeatureCountGeometry === null && Array.isArray(serviceResult.result?.features)) derivedFeatureCountGeometry = serviceResult.result.features.length;
      }
      console.log('StartIndex(几何查询):', startIndexGeometry, '=> 推导:', derivedStartIndexGeometry);
      console.log('Server端统计的featureCount(几何查询):', serverReportedFeatureCountGeometry, '=> 推导:', derivedFeatureCountGeometry);
      console.log('childUriList是否存在(几何查询):', Array.isArray(childUriListGeometry));
      console.log('childUriList长度(几何查询):', Array.isArray(childUriListGeometry) ? childUriListGeometry.length : 0);
      if (Array.isArray(childUriListGeometry) && childUriListGeometry.length > 0) {
        console.log('childUriList示例(前3条，几何查询):', childUriListGeometry.slice(0, 3));
        console.log('childUriList示例(后3条，几何查询):', childUriListGeometry.slice(-3));
      }
      
      // 显示服务返回的完整信息
      if (serviceResult.result) {
        notificationManager.info(
          `要素查询结果 - ${layerName}`,
          `找到要素数: ${serviceResult.result.features?.length || 0}\n总要素数: ${serviceResult.result.totalCount || '未知'}\n当前返回: ${serviceResult.result.currentCount || serviceResult.result.features?.length || 0}\n最大要素数: ${serviceResult.result.maxFeatures || '无限制'}\n==============featureCount======================= ${(serviceResult.result.featureCount ?? serviceResult.result.totalCount ?? serviceResult.result.currentCount ?? (serviceResult.result.features?.length || 0)) || 0}\n数据来源: SuperMap iServer\n服务器地址: ${mapStore.mapConfig.dataUrl}`
        );
      }
          if (serviceResult.result && serviceResult.result.features) {
            // 将服务返回与features进行简单对齐校验
            const tmpFeatures = (new ol.format.GeoJSON()).readFeatures(serviceResult.result.features);
            console.log('本次解析到的要素数量(几何查询):', tmpFeatures.length);
            console.log('服务器返回要素数组长度(几何查询):', serviceResult.result.features.length);
            console.log('childUriList与features数量是否一致(几何查询):', Array.isArray(childUriListGeometry) ? childUriListGeometry.length === serviceResult.result.features.length : 'childUriList缺失');
            if (Array.isArray(childUriListGeometry)) {
              for (let i = 0; i < Math.min(3, tmpFeatures.length, childUriListGeometry.length); i += 1) {
                const f = tmpFeatures[i];
                console.log(`示例映射[几何查询] i=${i}: childUri=${childUriListGeometry[i]}`, {
                  featureId: f.getId?.() || null,
                  geometryType: f.getGeometry?.()?.getType?.() || null
                });
              }
            }
            resolve({
              success: true,
              features: serviceResult.result.features,
              layerName: dataset
            });
          } else {
            resolve({
              success: false,
              features: [],
              layerName: dataset
            });
          }
        });
      });
    } catch (error) {
      return {
        success: false,
        error: error,
        features: [],
        layerName: layerName
      };
    }
  }

  // 获取数据集列表
  const getDatasetList = async (): Promise<string[]> => {
    try {
      // 数据服务完整路径: http://localhost:8090/iserver/services/data-WuHan/rest/data/datasources/wuhan/datasets
      const datasetsUrl = `${mapStore.mapConfig.dataUrl}/datasources/wuhan/datasets`;
      
      console.log(`=== 获取数据集列表服务器地址信息 ===`);
      console.log('基础数据服务URL:', mapStore.mapConfig.dataUrl);
      console.log('数据集列表API完整URL:', datasetsUrl);
      console.log('数据来源说明:', '原始数据来自SuperMap iServer的数据源管理API');
      console.log('API类型:', 'REST API');
      console.log('HTTP方法:', 'GET');
      console.log('数据格式:', 'JSON');
      console.log('数据存储位置:', 'SuperMap iServer数据库');
      
      const response = await fetch(datasetsUrl);
      const data = await response.json();
      
      if (data && data.datasetNames) {
        console.log('成功获取数据集列表:', data.datasetNames);
        console.log('数据集数量:', data.datasetNames.length);
        console.log('数据来源服务器:', mapStore.mapConfig.dataUrl);
        return data.datasetNames;
      }
      
      // 如果API返回格式不同，使用预定义列表
      return [
        '武汉_县级',
        '公路',
        '铁路',
        '居民地地名点',
        '水系线',
        '水系面',
        '建筑物面',
        '学校',
        '医院'
        // 移除了 '武汉_市级' 和 'DEM_wuhan'
      ];
    } catch (error) {
      console.warn('获取数据集列表失败，使用预定义列表:', error);
      // 返回预定义的数据集列表
      return [
        '武汉_县级',
        '公路',
        '铁路',
        '居民地地名点',
        '水系线',
        '水系面',
        '建筑物面',
        '学校',
        '医院'
        // 移除了 '武汉_市级' 和 'DEM_wuhan'
      ];
    }
  }

  // 获取特定数据集的详细信息
  const getDatasetInfo = async (datasetName: string): Promise<any> => {
    try {
      // 构建数据集信息查询URL
      const datasetUrl = `${mapStore.mapConfig.dataUrl}/datasources/wuhan/datasets/${datasetName}`;
      
      const response = await fetch(datasetUrl);
      const data = await response.json();
      
      return {
        success: true,
        info: data,
        fields: data.fieldInfos || [], // 字段信息
        geometryType: data.type || 'UNKNOWN', // 几何类型
        recordCount: data.recordCount || 0 // 记录数
      };
    } catch (error) {
      return {
        success: false,
        error: error
      };
    }
  }
  
  const setupMapEvents = (map: any, hoverSource: any, selectSource: any): void => {
    const view = map.getView()
    view.on('change:center', () => {
      mapStore.updatePopupPosition()
    })
    view.on('change:resolution', () => {
      mapStore.updatePopupPosition()
    })
    
    map.on('pointermove', (evt: any) => {
      mapStore.updateCoordinate(evt.coordinate)
      if (hoverTimer.value) clearTimeout(hoverTimer.value)
      hoverTimer.value = window.setTimeout(() => {
        handleFeatureHover(hoverSource)
      }, 120)
      
    })
    
    map.on('click', (evt: any) => {
      handleMapClick(evt, selectSource)
    })
    
    const resizeHandler = () => map.updateSize()
    window.addEventListener('resize', resizeHandler)
    
    onUnmounted(() => {
      window.removeEventListener('resize', resizeHandler)
    })
  }
  
  const handleFeatureHover = async (hoverSource: any): Promise<void> => {
    hoverSource.clear()
    if (mapStore.map) {
      mapStore.map.getTargetElement().style.cursor = 'default'
    }
  }
  
  const handleMapClick = async (evt: any, selectSource: any): Promise<void> => {
    if (analysisStore.toolPanel?.activeTool === 'draw' && analysisStore.drawMode === 'point') {
      const coord = mapStore.map.getCoordinateFromPixel(evt.pixel)
      if (coord) {
        window.dispatchEvent(new CustomEvent('drawPointClick', { 
          detail: { coordinate: coord, pixel: evt.pixel } 
        }))
      }
      return
    }
    
    await handleNormalClick(evt, selectSource)
  }

  const handleNormalClick = async (evt: any, selectSource: any): Promise<void> => {
    const map = evt.map;
    const coordinate = evt.coordinate;
    
    // 首先检查是否点击到了已加载的要素
    const feature = map.forEachFeatureAtPixel(
      evt.pixel,
      (f: any, l: any) => {
        const isInteractiveLayer = l && l !== mapStore.baseLayer && l !== mapStore.hoverLayer && l !== mapStore.selectLayer;
        if (isInteractiveLayer) {
          return f;
        }
        return undefined;
      },
      {
        hitTolerance: 5
      }
    );

    selectSource.clear();
    mapStore.setSelectedFeature(null);

         if (feature) {
       // 如果点击到要素，显示其属性信息
       selectSource.addFeature(feature);
       mapStore.setSelectedFeature(feature);

       // 生成详细的要素属性信息 - 显示所有从数据服务中读取的数据
       const properties = feature.getProperties();
       let content = '<div class="feature-info">';
       
       // 显示要素基本信息
       content += `<div class="feature-header">要素详细信息</div>`;
       content += `<div class="field-row"><span class="field-label">要素ID:</span><span class="field-value">${feature.getId() || '无'}</span></div>`;
       content += `<div class="field-row"><span class="field-label">几何类型:</span><span class="field-value">${feature.getGeometry()?.getType() || '未知'}</span></div>`;
       
       // 显示所有属性字段，包括空值
       content += `<div class="feature-header">属性字段 (共${Object.keys(properties).filter(k => k !== 'geometry').length}个)</div>`;
       Object.keys(properties).forEach(key => {
         if (key !== 'geometry') {
           const value = properties[key];
           const displayValue = value !== undefined && value !== null ? value : '(空值)';
           content += `<div class="field-row"><span class="field-label">${key}:</span><span class="field-value">${displayValue}</span></div>`;
         }
       });
       
       content += '</div>';

      mapStore.showPopup(
        { x: evt.pixel[0], y: evt.pixel[1] },
        content,
        feature,
        evt.coordinate
      );
    } else {
      // 如果没有点击到要素，查询所有图层的要素信息
      await queryFeaturesAtPoint(coordinate, evt.pixel);
    }
  }

  // 在指定点查询所有图层的要素
  const queryFeaturesAtPoint = async (coordinate: number[], pixel: number[]): Promise<void> => {
    try {
      const allFeatures: any[] = [];
      
      // 查询所有已加载的矢量图层
      for (const layerInfo of mapStore.vectorLayers) {
        if (layerInfo.visible && layerInfo.source === 'supermap') {
          const result = await getFeatureInfo(coordinate, layerInfo.id);
          if (result.success && result.features.length > 0) {
            result.features.forEach((feature: any) => {
              allFeatures.push({
                ...feature,
                layerName: result.layerName
              });
            });
          }
        }
      }
      
      if (allFeatures.length > 0) {
        // 按图层的zIndex从高到低排序（顶层优先），县级图层在最底
        const layerNameToZ: Record<string, number> = {};
        mapStore.vectorLayers.forEach(vl => {
          if (vl.layer && typeof vl.layer.getZIndex === 'function') {
            layerNameToZ[vl.name] = vl.layer.getZIndex() ?? 0;
          }
        });
        allFeatures.sort((a, b) => {
          const za = layerNameToZ[a.layerName] ?? 0;
          const zb = layerNameToZ[b.layerName] ?? 0;
          return zb - za;
        });
        // 显示查询到的要素信息 - 显示所有从数据服务中读取的数据
        let content = '<div class="multi-feature-info">';
        content += `<div class="feature-count">==============featureCount======================= ${allFeatures.length}</div>`;
        
        allFeatures.forEach((feature, index) => {
          content += `<div class="feature-item">`;
          content += `<div class="feature-header">要素 ${index + 1} (${feature.layerName})</div>`;
          content += `<div class="field-row"><span class="field-label">==============featureCount=======================</span><span class="field-value">1</span></div>`;
          
          // 显示要素基本信息
          content += `<div class="field-row"><span class="field-label">要素ID:</span><span class="field-value">${feature.id || '无'}</span></div>`;
          content += `<div class="field-row"><span class="field-label">几何类型:</span><span class="field-value">${feature.geometry?.type || '未知'}</span></div>`;
          
          // 显示所有属性字段，包括空值
          const properties = feature.properties || {};
          content += `<div class="field-row"><span class="field-label">属性字段数:</span><span class="field-value">${Object.keys(properties).length}个</span></div>`;
          Object.keys(properties).forEach(key => {
            const value = properties[key];
            const displayValue = value !== undefined && value !== null ? value : '(空值)';
            content += `<div class="field-row"><span class="field-label">${key}:</span><span class="field-value">${displayValue}</span></div>`;
          });
          
          content += '</div>';
        });
        
        content += '</div>';
        
        mapStore.showPopup(
          { x: pixel[0], y: pixel[1] },
          content,
          null,
          coordinate
        );
      } else {
        // 没有找到要素，隐藏弹窗
        mapStore.hidePopup();
      }
    } catch (error) {
      console.error('查询要素信息失败:', error);
      mapStore.hidePopup();
    }
  }



  const cleanup = (): void => {
    if (hoverTimer.value) {
      clearTimeout(hoverTimer.value)
    }
  }
  
  onUnmounted(cleanup)

  watch(() => analysisStore.drawMode, (newMode) => {
    if (!mapStore.map) return;
    const targetElement = mapStore.map.getTargetElement();
    if (['point', 'line', 'polygon'].includes(newMode)) {
      targetElement.style.cursor = 'crosshair';
    } else {
      targetElement.style.cursor = 'default';
    }
  });

  onMounted(() => {
    const drawCompleteHandler = (e: Event) => {
      layerManager.acceptDrawLayer((e as CustomEvent).detail)
    }
    
    const removeLayerHandler = (e: Event) => {
      const { layer } = (e as CustomEvent).detail
      if (layer && mapStore.map) {
        try {
          mapStore.map.removeLayer(layer)
        } catch (error) {
          console.error('移除图层时出错:', error)
        }
      }
    }
    
    window.addEventListener('drawLayerCompleted', drawCompleteHandler)
    window.addEventListener('removeLayerRequested', removeLayerHandler)
    
    onUnmounted(() => {
      window.removeEventListener('drawLayerCompleted', drawCompleteHandler)
      window.removeEventListener('removeLayerRequested', removeLayerHandler)
    })
  })
  
  return {
    mapContainer,
    initMap,
    cleanup,
    updateLayerStyles, // 导出样式更新函数
    createLayerStyle,  // 导出样式创建函数
    getFeatureInfo,    // 导出要素信息查询函数
    getDatasetList,    // 导出数据集列表查询函数
    getDatasetInfo,    // 导出数据集信息查询函数
    queryFeaturesAtPoint // 导出点查询函数
  }
}
