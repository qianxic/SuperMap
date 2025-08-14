import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useLayerManager } from '@/composables/useLayerManager'

const ol = window.ol;

export function useMap() {
  let mapStore = useMapStore()
  const analysisStore = useAnalysisStore()
  const layerManager = useLayerManager()
  const mapContainer = ref<HTMLElement | null>(null)
  const hoverTimer = ref<number | null>(null)
  const selectSourceRef = ref<any>(null) // ol.source.Vector

  const initMap = (): void => {
    mapStore = useMapStore()
    
    try {
      if (!window.ol || !mapContainer.value) return
      
      const resolutions: number[] = [];
      for (let i = 0; i < 19; i++) {
          resolutions[i] = 180 / 256 / Math.pow(2, i);
      }

      const map = new ol.Map({
        target: mapContainer.value,
        controls: new ol.Collection([
          new ol.supermap.control.Logo({ link: "https://iclient.supermap.io" }),
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
      
      const projectionExtent = mapStore.mapConfig.extent;

      const tileGrid = new ol.tilegrid.TileGrid({
          extent: projectionExtent,
          origin: ol.extent.getTopLeft(projectionExtent),
          resolutions: resolutions
      });

      const baseLayer = new ol.layer.Tile({
        source: new ol.source.TileSuperMapRest({
          url: mapStore.mapConfig.baseUrl,
          tileGrid: tileGrid
        }),
      })
      map.addLayer(baseLayer)
      
      mapStore.mapConfig.vectorLayers.forEach(layerConfig => {
        let style;
        if (layerConfig.style) {
          const accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim();
          const strokeOptions = { 
            ...layerConfig.style.stroke, 
            color: accentColor || 'blue' 
          };
          
          style = new ol.style.Style({
            stroke: new ol.style.Stroke(strokeOptions),
            fill: new ol.style.Fill(layerConfig.style.fill)
          });
        }
        
        const vectorLayer = new ol.layer.Vector({
          source: new ol.source.Vector({
            loader: (extent: any, resolution: any, projection: any) => {
              const featureService = new ol.supermap.FeatureService(mapStore.mapConfig.dataUrl);
              
              const parts = layerConfig.name.split('@');
              const dataset = parts[0];
              const datasource = parts[1];

              const getFeaturesBySQLParams = new ol.supermap.GetFeaturesBySQLParameters({
                queryParameter: new ol.supermap.FilterParameter({
                  name: dataset,
                  attributeFilter: "1=1" 
                }),
                datasetNames: [`${datasource}:${dataset}`],
                returnContent: true
              });

              featureService.getFeaturesBySQL(getFeaturesBySQLParams, (serviceResult: any) => {
                if (serviceResult.result && serviceResult.result.features) {
                  const features = (new ol.format.GeoJSON()).readFeatures(serviceResult.result.features);
                  vectorLayer.getSource().addFeatures(features);
                }
              });
            },
            strategy: ol.loadingstrategy.bbox
          }),
          style: style // 如果 style 未定义，则使用默认样式
        });
        map.addLayer(vectorLayer);
        mapStore.vectorLayers.push({
          id: layerConfig.name,
          name: layerConfig.name.split('@')[0],
          layer: vectorLayer,
          visible: true,
          type: 'vector'
        });
      });
      
      const hoverSource = new ol.source.Vector()
      const accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim();
      const hoverLayer = new ol.layer.Vector({
        source: hoverSource,
        style: new ol.style.Style({
          image: new ol.style.Circle({ 
            radius: 8, 
            stroke: new ol.style.Stroke({color: accentColor, width:2}), 
            fill: new ol.style.Fill({color: accentColor.replace(')', ', 0.25)').replace('rgb', 'rgba')}) 
          }),
          stroke: new ol.style.Stroke({color: accentColor, width:2}),
          fill: new ol.style.Fill({color: accentColor.replace(')', ', 0.15)').replace('rgb', 'rgba')})
        })
      })
      map.addLayer(hoverLayer)
        
      const selectSource = new ol.source.Vector()
      const selectLayer = new ol.layer.Vector({
        source: selectSource,
        style: new ol.style.Style({
          image: new ol.style.Circle({ 
            radius: 5, 
            stroke: new ol.style.Stroke({color: accentColor, width:1.5}), 
            fill: new ol.style.Fill({color: accentColor.replace(')', ', 0.15)').replace('rgb', 'rgba')}) 
          }),
          stroke: new ol.style.Stroke({color: accentColor, width:1.5}),
          fill: new ol.style.Fill({color: accentColor.replace(')', ', 0.08)').replace('rgb', 'rgba')})
        })
      })
      map.addLayer(selectLayer)
      selectSourceRef.value = selectSource
        
      mapStore.setMap(map)
      mapStore.setLayers({
        base: baseLayer,
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
        
    } catch (error) {
      console.error('地图初始化失败:', error)
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
      selectSource.addFeature(feature);
      mapStore.setSelectedFeature(feature);

      const properties = feature.getProperties();
      let content = '';
      
      const fieldsToShow: { key: string, label: string }[] = [
        { key: 'PAC_1', label: '邮编' },
        { key: 'NAME_1', label: '区名称' }
      ];

      fieldsToShow.forEach(field => {
        if (properties[field.key]) {
          content += `<div class="kv"><span class="k">${field.label}</span><span class="v">${properties[field.key]}</span></div>`;
        }
      });

      mapStore.showPopup(
        { x: evt.pixel[0], y: evt.pixel[1] },
        content,
        feature,
        evt.coordinate
      );
    } else {
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
    cleanup
  }
}
