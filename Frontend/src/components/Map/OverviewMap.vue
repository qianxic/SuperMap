<template>
  <div class="overview-map-container no-theme-flicker" v-if="isVisible">
    <div class="overview-map-header">
      <span class="overview-title">鹰眼</span>
      <button 
        class="overview-toggle-btn"
        @click="toggleOverview"
        :title="isCollapsed ? '展开' : '收起'"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
          <path v-if="isCollapsed" d="M7 10l5 5 5-5z"/>
          <path v-else d="M7 14l5-5 5 5z"/>
        </svg>
      </button>
    </div>
    <div 
      ref="overviewMapElement" 
      class="overview-map"
      :class="{ collapsed: isCollapsed }"
      :title="!isCollapsed ? '点击导航到指定位置，拖拽移动视图' : ''"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useThemeStore } from '@/stores/themeStore'
import { getCurrentBaseMapUrl } from '@/utils/config'

const mapStore = useMapStore()
const themeStore = useThemeStore()

// 响应式数据
const overviewMapElement = ref<HTMLElement | null>(null)
const isVisible = ref(true)
const isCollapsed = ref(true) // 修改为默认折叠状态
const overviewMap = ref<any>(null)
const extentLayer = ref<any>(null) // 视口框图层

// 更新视口框函数
const updateExtentBox = () => {
  if (!overviewMap.value || !mapStore.map || !extentLayer.value) return
  
  const ol = window.ol
  const mainView = mapStore.map.getView()
  const overviewView = overviewMap.value.getView()
  const extentSource = extentLayer.value.getSource()
  
  // 清除旧的视口框
  extentSource.clear()
  
  // 获取主地图的当前范围
  const mainExtent = mainView.calculateExtent(mapStore.map.getSize())
  
  // 将主地图范围转换到鹰眼坐标系
  const overviewExtent = ol.proj.transformExtent(mainExtent, mainView.getProjection(), overviewView.getProjection())
  
  // 创建视口框要素
  const extentFeature = new ol.Feature({
    geometry: new ol.geom.Polygon.fromExtent(overviewExtent)
  })
  
  extentSource.addFeature(extentFeature)
}

// 同步主地图和鹰眼的视图
const syncViews = () => {
  if (overviewMap.value && mapStore.map) {
    const mainView = mapStore.map.getView()
    const overviewView = overviewMap.value.getView()
    
    // 同步中心点和缩放级别
    overviewView.setCenter(mainView.getCenter())
    overviewView.setZoom(Math.max(4, mainView.getZoom() - 3))
    
    // 更新视口框
    updateExtentBox()
  }
}

// 初始化鹰眼
const initOverviewMap = async () => {
  if (!mapStore.map || !overviewMapElement.value) return

  try {
    const ol = window.ol
    
    // 创建鹰眼的地图实例
    const currentBaseMapUrl = getCurrentBaseMapUrl(themeStore.theme)
    
    const sourceConfig: any = {
      url: currentBaseMapUrl,
      serverType: 'iserver'
    }
    
    if (themeStore.theme === 'light') {
      sourceConfig.crossOrigin = 'anonymous'
    }
    
    const overviewLayer = new ol.layer.Tile({
      source: new ol.source.TileSuperMapRest(sourceConfig),
      visible: true
    })
    
    // 创建鹰眼视图
    const overviewView = new ol.View({
      projection: mapStore.mapConfig.projection,
      center: mapStore.mapConfig.center,
      zoom: 6, // 鹰眼显示更大范围
      maxZoom: 10
    })
    
    // 创建鹰眼
    overviewMap.value = new ol.Map({
      target: overviewMapElement.value,
      layers: [overviewLayer],
      view: overviewView,
      controls: [], // 鹰眼不需要控件
    })
    
    // 添加主地图视口框图层到鹰眼
    extentLayer.value = new ol.layer.Vector({
      source: new ol.source.Vector(),
      style: new ol.style.Style({
        stroke: new ol.style.Stroke({
          color: '#ff0000',
          width: 2
        }),
        fill: new ol.style.Fill({
          color: 'rgba(255, 0, 0, 0.1)'
        })
      })
    })
    overviewMap.value.addLayer(extentLayer.value)
    
    // 监听主地图视图变化
    mapStore.map.getView().on('change:center', syncViews)
    mapStore.map.getView().on('change:resolution', syncViews)
    
    // 添加鹰眼点击导航功能
    overviewMap.value.on('click', (event: any) => {
      if (!mapStore.map) return
      
      const coordinate = event.coordinate
      const mainView = mapStore.map.getView()
      const overviewView = overviewMap.value.getView()
      
      // 将鹰眼坐标转换到主地图坐标系
      const mainCoordinate = ol.proj.transform(coordinate, overviewView.getProjection(), mainView.getProjection())
      
      // 导航到点击位置
      mainView.animate({
        center: mainCoordinate,
        duration: 500
      })
      
      // 显示提示信息
      console.log('鹰眼导航: 已跳转到点击位置')
    })
    
    // 添加鹰眼拖拽导航功能
    const dragPan = new ol.interaction.DragPan({
      condition: ol.events.condition.always
    })
    
    dragPan.on('panend', (event: any) => {
      if (!mapStore.map) return
      
      const overviewView = overviewMap.value.getView()
      const mainView = mapStore.map.getView()
      
      // 获取鹰眼中心点
      const overviewCenter = overviewView.getCenter()
      
      // 转换到主地图坐标系
      const mainCenter = ol.proj.transform(overviewCenter, overviewView.getProjection(), mainView.getProjection())
      
      // 导航到新位置
      mainView.animate({
        center: mainCenter,
        duration: 300
      })
    })
    
    overviewMap.value.addInteraction(dragPan)
    
    // 初始同步
    nextTick(() => {
      syncViews()
    })
    
  } catch (error) {
    console.error('鹰眼初始化失败:', error)
  }
}

// 切换鹰眼显示/隐藏
const toggleOverview = () => {
  isCollapsed.value = !isCollapsed.value
}

// 首次展开时再初始化，避免 0 尺寸容器报错
watch(isCollapsed, (collapsed) => {
  if (!collapsed) {
    if (!overviewMap.value) {
      nextTick(() => {
        initOverviewMap()
      })
    } else {
      nextTick(() => {
        try { overviewMap.value.updateSize() } catch (e) {}
        // 展开后立即同步一次视口
        syncViews()
      })
    }
  }
})

// 重建鹰眼图层的函数
const rebuildOverviewLayer = () => {
  if (!overviewMap.value) return
  
  try {
    const ol = window.ol
    const currentBaseMapUrl = getCurrentBaseMapUrl(themeStore.theme)
    
    // 创建新的底图源
    const sourceConfig: any = {
      url: currentBaseMapUrl,
      serverType: 'iserver'
    }
    
    if (themeStore.theme === 'light') {
      sourceConfig.crossOrigin = 'anonymous'
    }
    
    const newSource = new ol.source.TileSuperMapRest(sourceConfig)
    
    // 创建新图层
    const newLayer = new ol.layer.Tile({
      source: newSource,
      visible: true
    })
    
    // 获取当前图层集合
    const layers = overviewMap.value.getLayers()
    
    // 移除旧图层（保留视口框图层）
    if (layers.getLength() > 1) {
      layers.removeAt(0)
    }
    
    // 添加新图层
    layers.insertAt(0, newLayer)
    
    // 强制刷新地图
    overviewMap.value.updateSize()
    
    // 重新同步视图和视口框
    const syncViews = () => {
      if (overviewMap.value && mapStore.map) {
        const mainView = mapStore.map.getView()
        const overviewView = overviewMap.value.getView()
        
        // 同步中心点和缩放级别
        overviewView.setCenter(mainView.getCenter())
        overviewView.setZoom(Math.max(4, mainView.getZoom() - 3))
        
        // 更新视口框
        setTimeout(() => updateExtentBox(), 50)
      }
    }
    
    // 延迟执行同步，确保新图层已加载
    setTimeout(syncViews, 100)
    
  } catch (error) {
    console.error('重建鹰眼图层失败:', error)
  }
}

// 监听主题变化
watch(() => themeStore.theme, () => {
  if (overviewMap.value) {
    // 直接重建鹰眼图层，这是最可靠的方式
    rebuildOverviewLayer()
  }
}, { immediate: false })

// 监听地图就绪状态
watch(() => mapStore.isMapReady, (ready) => {
  if (ready && !overviewMap.value && !isCollapsed.value) {
    nextTick(() => {
      initOverviewMap()
    })
  }
})

// 生命周期
onMounted(() => {
  if (mapStore.isMapReady && !isCollapsed.value) {
    nextTick(() => {
      initOverviewMap()
    })
  }
})

onUnmounted(() => {
  if (overviewMap.value) {
    overviewMap.value.setTarget(undefined)
    overviewMap.value = null
  }
})
</script>

<style scoped>
.overview-map-container {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 1000;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--glow);
  overflow: hidden;
  /* 禁用过渡动画，防止主题切换闪烁 */
  transition: none !important;
}

/* 防闪烁类 - 禁用所有过渡和动画 */
.no-theme-flicker,
.no-theme-flicker *,
.no-theme-flicker *::before,
.no-theme-flicker *::after {
  transition: none !important;
  animation: none !important;
}

.overview-map-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  min-width: 240px;
  /* 禁用过渡动画 */
  transition: none !important;
}

.overview-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
  user-select: none;
}

.overview-toggle-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--text);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  /* 禁用过渡动画 */
  transition: none !important;
}

.overview-toggle-btn:hover {
  background: var(--surface-hover);
  color: var(--accent);
}

.overview-map {
  width: 240px;
  height: 160px;
  /* 禁用过渡动画 */
  transition: none !important;
  overflow: hidden;
  border-radius: 4px;
  box-shadow: inset 0 0 0 1px var(--border);
  cursor: pointer;
}

.overview-map:hover {
  box-shadow: inset 0 0 0 2px var(--accent);
}

/* OpenLayers 鹰眼样式覆盖 */
.overview-map :deep(.ol-viewport) {
  border-radius: 4px;
}

.overview-map :deep(.ol-canvas) {
  border-radius: 4px;
}

.overview-map.collapsed {
  height: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .overview-map-container {
    top: 8px;
    right: 8px;
  }
  
  .overview-map {
    width: 180px;
    height: 120px;
  }
  
  .overview-map-header {
    min-width: 180px;
    padding: 6px 10px;
  }
  
  .overview-title {
    font-size: 12px;
  }
  
  .overview-toggle-btn {
    width: 24px;
    height: 24px;
  }
}
</style>
