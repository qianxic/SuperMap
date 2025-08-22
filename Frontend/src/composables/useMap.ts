import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useLoadingStore } from '@/stores/loadingStore'
import { useLayerManager } from '@/composables/useLayerManager'
import { superMapClient } from '@/api/supermap'
import { handleError, notificationManager } from '@/utils/notification'
import { createAPIConfig, testLayerConfig } from '@/utils/config'
import { useFeatureInfo } from '@/composables/useFeatureInfo'

const ol = window.ol;

export function useMap() {
  let mapStore = useMapStore()
  const analysisStore = useAnalysisStore()
  const loadingStore = useLoadingStore()
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

      // 不使用任何底图，只显示通过FeatureService加载的矢量图层
      // 这样可以确保所有显示的内容都来自SuperMap的FeatureService
      
      loadingStore.updateLoading('map-init', '正在加载图层...')
      
      // 使用新的API客户端加载矢量图层
      await loadVectorLayers(map)
      
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
            fill: new ol.style.Fill({color: getComputedStyle(document.documentElement).getPropertyValue('--map-select-point-fill').trim()}) 
          }),
          stroke: new ol.style.Stroke({color: accentColor, width: 3}),
          fill: new ol.style.Fill({color: getComputedStyle(document.documentElement).getPropertyValue('--map-select-fill').trim()})
        })
      })
      map.addLayer(selectLayer)
      selectSourceRef.value = selectSource
        
      mapStore.setMap(map)
      mapStore.setLayers({
        base: null, // 不使用底图
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
    
    for (const layerConfig of apiConfig.wuhanLayers) {
      try {
        const layerName = layerConfig.name.split('@')[0] || layerConfig.name
        loadingStore.updateLoading('map-init', `正在加载图层: ${layerName}`)
        
        if (layerConfig.type === 'raster') {
          // 暂时跳过栅格图层，避免使用TileSuperMapRest服务
          // 栅格图层通常不支持FeatureService+SQL方式加载
          console.log(`跳过栅格图层: ${layerName} (避免使用瓦片服务)`)
          continue;
        } else {
          // 加载矢量图层（使用FeatureService+SQL方式）
          await loadVectorLayer(map, layerConfig)
        }
      } catch (error) {
        console.error(`配置图层 ${layerConfig.name} 失败:`, error)
        // 继续处理其他图层
      }
    }
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

  // 监听主题变化，更新图层样式
  const observeThemeChanges = () => {
    const observer = new MutationObserver(() => {
      updateLayerStyles();
    });
    
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class', 'style'],
      subtree: false
    });
    
    onUnmounted(() => {
      observer.disconnect();
    });
  }

  const createLayerStyle = (layerConfig: any, layerName: string): any => {
    // 获取CSS变量中的颜色值，支持主题切换
    const accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#007bff';
    const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text').trim() || '#333333';
    
    // 从mapStore配置中查找对应的样式配置
    const styleConfig = mapStore.mapConfig.vectorLayers.find(vl => vl.name === layerConfig.name)?.style;
    
    // 特殊处理县级图层，设置为透明显示
    if (layerName === '武汉_县级') {
      return new ol.style.Style({
        stroke: new ol.style.Stroke({ 
          color: styleConfig?.stroke?.color || accentColor, 
          width: styleConfig?.stroke?.width || 1.5 
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
              color: styleConfig?.stroke?.color || '#ff0000', 
              width: styleConfig?.stroke?.width || 2 
            }),
            fill: new ol.style.Fill({ 
              color: styleConfig?.fill?.color || 'rgba(255, 0, 0, 0.6)' 
            })
          })
        });
      case 'line':
        return new ol.style.Style({
          stroke: new ol.style.Stroke({ 
            color: styleConfig?.stroke?.color || '#28a745', 
            width: styleConfig?.stroke?.width || 2 
          }),
          fill: new ol.style.Fill({ color: 'rgba(0, 0, 0, 0)' })
        });
      case 'polygon':
        return new ol.style.Style({
          stroke: new ol.style.Stroke({ 
            color: styleConfig?.stroke?.color || accentColor, 
            width: styleConfig?.stroke?.width || 1.5 
          }),
          fill: new ol.style.Fill({ 
            color: styleConfig?.fill?.color || 'rgba(0, 123, 255, 0.1)' 
          })
        });
      default:
        return new ol.style.Style({
          stroke: new ol.style.Stroke({ 
            color: styleConfig?.stroke?.color || accentColor, 
            width: styleConfig?.stroke?.width || 1.5 
          }),
          fill: new ol.style.Fill({ 
            color: styleConfig?.fill?.color || 'rgba(0, 123, 255, 0.1)' 
          })
        });
    }
  }

  const loadVectorLayer = async (map: any, layerConfig: any): Promise<void> => {
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

    // 创建武汉市的完整边界范围
    const wuhanBounds = new ol.geom.Polygon([[
      [113.7, 29.97],
      [115.08, 29.97],
      [115.08, 31.36],
      [113.7, 31.36],
      [113.7, 29.97]
    ]]);

    const getFeaturesByBoundsParams = new ol.supermap.GetFeaturesByBoundsParameters({
      datasetNames: [`${datasource}:${dataset}`],
      bounds: ol.extent.boundingExtent(wuhanBounds.getCoordinates()[0]),
      maxFeatures: 10000, // 设置较大的值以获取所有要素
      returnContent: true
    });

    featureService.getFeaturesByBounds(getFeaturesByBoundsParams, (serviceResult: any) => {
      if (serviceResult.result && serviceResult.result.features) {
        const features = (new ol.format.GeoJSON()).readFeatures(serviceResult.result.features);
        vectorLayer.getSource().addFeatures(features);
        console.log(`图层 ${layerName} 加载完成，共 ${features.length} 个要素`);
      } else {
        console.warn(`图层 ${layerName} 未获取到数据`);
      }
    });
    
    // 设置图层可见性
    vectorLayer.setVisible(layerConfig.visible);
    
    map.addLayer(vectorLayer);
    mapStore.vectorLayers.push({
      id: layerConfig.name,
      name: layerName,
      layer: vectorLayer,
      visible: layerConfig.visible,
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
      
      // 创建几何查询参数 - 点击位置的缓冲区查询
      const tolerance = 0.001; // 容差值，可根据需要调整
      const buffer = new ol.geom.Point(coordinate).buffer(tolerance);
      
      const getFeaturesByGeometryParams = new ol.supermap.GetFeaturesByGeometryParameters({
        datasetNames: [`${datasource}:${dataset}`],
        geometry: buffer,
        spatialQueryMode: ol.supermap.SpatialQueryMode.INTERSECT,
        returnContent: true,
        // 确保返回所有字段
        attributeFilter: '',
        fields: ['*'] // 返回所有字段
      });

      return new Promise((resolve, reject) => {
        featureService.getFeaturesByGeometry(getFeaturesByGeometryParams, (serviceResult: any) => {
          if (serviceResult.result && serviceResult.result.features) {
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
      
      const response = await fetch(datasetsUrl);
      const data = await response.json();
      
      if (data && data.datasetNames) {
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
      
      // 显示所有属性字段，不区分重要字段
      Object.keys(properties).forEach(key => {
        if (key !== 'geometry') {
          const value = properties[key];
          if (value !== undefined && value !== null && value !== '') {
            content += `<div class="field-row"><span class="field-label">${key}:</span><span class="field-value">${value}</span></div>`;
          }
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
        // 显示查询到的要素信息 - 显示所有从数据服务中读取的数据
        let content = '<div class="multi-feature-info">';
        content += `<div class="feature-count">找到 ${allFeatures.length} 个要素:</div>`;
        
        allFeatures.forEach((feature, index) => {
          content += `<div class="feature-item">`;
          content += `<div class="feature-header">要素 ${index + 1} (${feature.layerName})</div>`;
          
          // 显示所有属性字段，包括从数据服务中读取的所有数据
          const properties = feature.properties || {};
          Object.keys(properties).forEach(key => {
            const value = properties[key];
            if (value !== undefined && value !== null && value !== '') {
              content += `<div class="field-row"><span class="field-label">${key}:</span><span class="field-value">${value}</span></div>`;
            }
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
