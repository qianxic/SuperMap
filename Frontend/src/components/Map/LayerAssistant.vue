<template>
  <div class="layer-assistant">
    <button 
      class="assistant-btn zoom-in" 
      @click="zoomIn"
      title="放大"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
        <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
      </svg>
    </button>
    <button 
      class="assistant-btn zoom-out" 
      @click="zoomOut"
      title="缩小"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
        <path d="M19 13H5v-2h14v2z"/>
      </svg>
    </button>
    <button 
      @click="toggleDistanceMeasure" 
      :class="['assistant-btn measure-btn', { active: mapStore.distanceMeasureMode }]"
      :title="mapStore.distanceMeasureMode ? '停止距离量算' : '开始距离量算'"
    >
      <svg class="measure-icon" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
      </svg>
    </button>
    
    <!-- 绘制工具分隔线 -->
    <div class="tool-separator"></div>
    
    <!-- 绘制工具按钮 -->
    <button 
      @click="startDraw('Point')" 
      :class="['assistant-btn draw-btn', { active: currentDrawType === 'Point' }]"
      title="绘制点"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
        <circle cx="12" cy="12" r="3"/>
      </svg>
    </button>
    <button 
      @click="startDraw('LineString')" 
      :class="['assistant-btn draw-btn', { active: currentDrawType === 'LineString' }]"
      title="绘制线"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M3 12l6-6 6 6 6-6"/>
      </svg>
    </button>
    <button 
      @click="startDraw('Polygon')" 
      :class="['assistant-btn draw-btn', { active: currentDrawType === 'Polygon' }]"
      title="绘制面"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
        <path d="M3 3h18v18H3z"/>
      </svg>
    </button>

    <button 
      @click="clearDrawFeatures" 
      class="assistant-btn clear-btn"
      title="清除绘制内容"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
      </svg>
    </button>
  </div>
  
  <!-- 确认对话框 -->
  <ConfirmDialog
    :visible="layerManager.confirmDialogVisible.value"
    :title="layerManager.confirmDialogConfig.value.title"
    :message="layerManager.confirmDialogConfig.value.message"
    confirm-text="保存"
    cancel-text="放弃"
    @confirm="layerManager.handleConfirmDialogConfirm"
    @cancel="layerManager.handleConfirmDialogCancel"
    @close="layerManager.handleConfirmDialogClose"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { useAnalysisStore } from '@/stores/analysisStore'
import { useLayerManager } from '@/composables/useLayerManager'
import ConfirmDialog from '@/components/UI/ConfirmDialog.vue'

const mapStore = useMapStore()
const analysisStore = useAnalysisStore()
const layerManager = useLayerManager()

// 绘制相关状态
const draw = ref<any>(null)
const drawSource = ref<any>(null)
const drawLayer = ref<any>(null)
const currentDrawType = ref<string>('None')

const ol = window.ol

const zoomIn = () => {
  if (mapStore.map) {
    const view = mapStore.map.getView()
    const zoom = view.getZoom()
    view.animate({
      zoom: zoom + 1,
      duration: 250
    })
  }
}

const zoomOut = () => {
  if (mapStore.map) {
    const view = mapStore.map.getView()
    const zoom = view.getZoom()
    view.animate({
      zoom: zoom - 1,
      duration: 250
    })
  }
}

const toggleDistanceMeasure = () => {
  if (mapStore.distanceMeasureMode) {
    mapStore.stopDistanceMeasure()
    analysisStore.setDistanceMeasureMode(false)
  } else {
    mapStore.startDistanceMeasure()
    analysisStore.setDistanceMeasureMode(true)
  }
}

// 初始化绘制图层
const initDrawLayer = () => {
  console.log('开始初始化绘制图层...')
  console.log('地图实例:', mapStore.map)
  
  if (!mapStore.map) {
    console.warn('地图实例未准备好，延迟重试...')
    setTimeout(initDrawLayer, 1000)
    return
  }
  
  if (!window.ol) {
    console.error('OpenLayers库未加载')
    return
  }
  
  try {
    // 创建绘制数据源
    drawSource.value = new ol.source.Vector({ wrapX: false })
    console.log('绘制数据源创建成功:', drawSource.value)
    
    // 创建绘制图层
    drawLayer.value = new ol.layer.Vector({
      source: drawSource.value,
      style: new ol.style.Style({
        stroke: new ol.style.Stroke({
          color: '#ff0000',
          width: 2
        }),
        fill: new ol.style.Fill({
          color: 'rgba(255, 0, 0, 0.1)'
        }),
        image: new ol.style.Circle({
          radius: 6,
          fill: new ol.style.Fill({
            color: '#ff0000'
          }),
          stroke: new ol.style.Stroke({
            color: '#ffffff',
            width: 2
          })
        })
      })
    })
    
    // 设置绘制图层标识
    drawLayer.value.set('isDrawLayer', true)
    console.log('绘制图层创建成功:', drawLayer.value)
    
    // 添加到地图
    mapStore.map.addLayer(drawLayer.value)
    console.log('绘制图层已添加到地图')
    
  } catch (error) {
    console.error('初始化绘制图层失败:', error)
  }
}

// 开始绘制
const startDraw = (type: 'Point' | 'LineString' | 'Polygon') => {
  console.log('开始绘制，类型:', type)
  console.log('地图实例:', mapStore.map)
  console.log('绘制数据源:', drawSource.value)
  
  if (!mapStore.map) {
    console.error('地图实例未准备好')
    return
  }
  
  if (!drawSource.value) {
    console.error('绘制数据源未初始化，重新初始化...')
    initDrawLayer()
    setTimeout(() => startDraw(type), 100)
    return
  }
  
  // 如果点击的是当前激活的绘制类型，则停止绘制
  if (currentDrawType.value === type) {
    console.log('停止当前绘制模式')
    stopDraw()
    return
  }
  
  // 清除现有绘制交互
  clearDrawInteraction()
  
  try {
    // 创建新的绘制交互
    draw.value = new ol.interaction.Draw({
      source: drawSource.value,
      type: type,
      snapTolerance: 20
    })
    console.log('绘制交互创建成功:', draw.value)
    
    // 添加到地图
    mapStore.map.addInteraction(draw.value)
    console.log('绘制交互已添加到地图')
    
    // 更新当前绘制类型
    currentDrawType.value = type
    
    // 同步绘制模式状态到 analysisStore
    analysisStore.setDrawMode(type)
    
    // 更新鼠标样式
    const targetElement = mapStore.map.getTargetElement()
    targetElement.style.cursor = 'crosshair'
    
    console.log('绘制模式已激活:', type)
    
  } catch (error) {
    console.error('创建绘制交互失败:', error)
  }
}

// 停止绘制
const stopDraw = () => {
  clearDrawInteraction()
  currentDrawType.value = 'None'
  
  // 同步绘制模式状态到 analysisStore
  analysisStore.setDrawMode('')
  
  // 恢复鼠标样式
  if (mapStore.map) {
    const targetElement = mapStore.map.getTargetElement()
    targetElement.style.cursor = 'default'
  }
}

// 清除绘制交互
const clearDrawInteraction = () => {
  if (draw.value && mapStore.map) {
    mapStore.map.removeInteraction(draw.value)
    draw.value = null
  }
}

// 清除绘制内容
const clearDrawFeatures = () => {
  if (drawSource.value) {
    // 检查是否处于绘制模式且有绘制内容
    if (layerManager.isDrawingMode() && drawSource.value.getFeatures().length > 0) {
      // 使用图层管理器的处理逻辑
      layerManager.handleDrawClear()
    } else {
      // 直接清除
      drawSource.value.clear()
    }
  }
  stopDraw()
}

// 组件挂载时初始化
onMounted(() => {
  console.log('LayerAssistant组件已挂载')
  
  // 检查地图是否已准备好
  if (mapStore.map && mapStore.isMapReady) {
    console.log('地图已准备好，立即初始化绘制图层')
    initDrawLayer()
  } else {
    console.log('地图未准备好，等待地图初始化完成...')
    // 监听地图状态变化
    const checkMapReady = () => {
      if (mapStore.map && mapStore.isMapReady) {
        console.log('地图初始化完成，开始初始化绘制图层')
        initDrawLayer()
      } else {
        setTimeout(checkMapReady, 500)
      }
    }
    checkMapReady()
  }
})

// 组件卸载时清理
onUnmounted(() => {
  clearDrawInteraction()
})
</script>

<style scoped>
.layer-assistant {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--glow);
  padding: 4px;
  min-height: fit-content;
}

.assistant-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: var(--panel);
  color: var(--text);
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.assistant-btn:hover {
  background: var(--accent);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.assistant-btn:active {
  transform: translateY(0);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
}

.assistant-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.assistant-btn:disabled:hover {
  background: var(--panel);
  color: var(--text);
  box-shadow: none;
}

.measure-btn.active {
  background: var(--accent);
  color: white;
}

.draw-btn.active {
  background: var(--accent);
  color: white;
}

.clear-btn:hover {
  background: #dc3545;
  color: white;
}

.tool-separator {
  height: 1px;
  background: var(--border);
  margin: 2px 0;
  flex-shrink: 0;
}

.measure-icon {
  width: 16px;
  height: 16px;
}
</style>
