<template>
  <div 
    v-show="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'draw'"
    class="draw-tools-panel"
  >
    <!-- 绘制工具区域 -->
    <div class="draw-section">
      
      <!-- 图层名称设置 -->
      <FormInput 
        v-model="layerName" 
        label="图层名称" 
        placeholder="请输入图层名称"
      />
      
      <ButtonGroup :columns="3">
        <SecondaryButton 
          text="绘制点"
          :active="analysisStore.drawMode === 'point'"
          @click="setDrawMode('point')"
        />
        <SecondaryButton 
          text="绘制线"
          :active="analysisStore.drawMode === 'line'"
          @click="setDrawMode('line')"
        />
        <SecondaryButton 
          text="绘制面"
          :active="analysisStore.drawMode === 'polygon'"
          @click="setDrawMode('polygon')"
        />
      </ButtonGroup>
      
      <ButtonGroup :columns="3">
        <SecondaryButton 
          text="修改点"
          :active="analysisStore.drawMode === 'edit-point'"
          @click="setDrawMode('edit-point')"
        />
        <SecondaryButton 
          text="修改线"
          :active="analysisStore.drawMode === 'edit-line'"
          @click="setDrawMode('edit-line')"
        />
        <SecondaryButton 
          text="修改面"
          :active="analysisStore.drawMode === 'edit-polygon'"
          @click="setDrawMode('edit-polygon')"
        />
      </ButtonGroup>
      
      <ButtonGroup :columns="1" gap="8px">
        <SecondaryButton 
          text="清空绘制"
          @click="clearDrawing"
        />
        <SecondaryButton 
          text="完成绘制"
          @click="finishDrawing"
        />
      </ButtonGroup>
    </div>
    
    <div class="tip">{{ currentTip }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore.ts'
import { useDraw } from '@/composables/useDraw.ts'
import { useLayerManager } from '@/composables/useLayerManager.ts'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import ButtonGroup from '@/components/UI/ButtonGroup.vue'
import FormInput from '@/components/UI/FormInput.vue'

const analysisStore = useAnalysisStore()
const layerManager = useLayerManager()

// 使用绘制composable
const {
  drawSource,
  clearDrawing
} = useDraw()

// 状态管理
const layerName = ref('')

// 计算属性
const currentTip = computed(() => {
  if (analysisStore.drawMode === 'point') {
    return '点击地图绘制点要素'
  }
  if (analysisStore.drawMode === 'line') {
    return '点击地图开始绘制线要素，双击结束绘制'
  }
  if (analysisStore.drawMode === 'polygon') {
    return '点击地图开始绘制面要素，双击结束绘制'
  }
  
  if (analysisStore.drawMode === 'edit-point') {
    return '点击地图上的点要素进行修改'
  }
  if (analysisStore.drawMode === 'edit-line') {
    return '点击地图上的线要素进行修改'
  }
  if (analysisStore.drawMode === 'edit-polygon') {
    return '点击地图上的面要素进行修改'
  }
  return '选择绘制工具开始创建要素'
})

// 设置绘制模式
const setDrawMode = (mode: string) => {
  analysisStore.setDrawMode(mode)
  
  if (mode === 'point') {
    analysisStore.setAnalysisStatus('绘制点功能暂未实现')
  } else if (mode === 'line') {
    analysisStore.setAnalysisStatus('绘制线功能暂未实现')
  } else if (mode === 'polygon') {
    analysisStore.setAnalysisStatus('绘制面功能暂未实现')
  } else if (mode === 'edit-point') {
    analysisStore.setAnalysisStatus('点击地图上的点要素进行修改')
  } else if (mode === 'edit-line') {
    analysisStore.setAnalysisStatus('点击地图上的线要素进行修改')
  } else if (mode === 'edit-polygon') {
    analysisStore.setAnalysisStatus('点击地图上的面要素进行修改')
  }
}

// 完成绘制
const finishDrawing = () => {
  if (!layerName.value.trim()) {
    analysisStore.setAnalysisStatus('请先输入图层名称')
    return
  }
  
  if (!drawSource.value || !drawSource.value.getFeatures().length) {
    analysisStore.setAnalysisStatus('没有可完成的绘制内容')
    return
  }
  
  try {
    const features: any[] = drawSource.value.getFeatures()
    
    const newLayer: any = {
      id: Date.now().toString(),
      name: layerName.value.trim(),
      features: features.map(feature => ({
        id: feature.getId() || Date.now() + Math.random(),
        geometry: feature.getGeometry(),
        properties: feature.getProperties()
      })),
      visible: true,
      type: 'draw',
      createdAt: new Date().toISOString()
    }
    
    layerManager.acceptDrawLayer(newLayer)
    clearDrawing()
    layerName.value = ''
    analysisStore.setAnalysisStatus(`图层 "${newLayer.name}" 已添加到图层管理`)
    
  } catch (error) {
    console.error('完成绘制时出错:', error)
    analysisStore.setAnalysisStatus('完成绘制时出错，请重试')
  }
}

// 监听绘制工具关闭
watch(() => analysisStore.toolPanel?.activeTool, (tool) => {
  if (tool !== 'draw') {
    analysisStore.setDrawMode('')
  }
})

defineExpose({
})
</script>

<style scoped>
.draw-tools-panel {
  height: 100%;
  overflow-y: auto;
}

.layer-section, .draw-section {
  margin-bottom: 12px;
}

.section-title {
  font-size: 12px;
  color: var(--sub);
  margin-bottom: 8px;
  font-weight: 500;
}

.existing-layers {
  margin-bottom: 12px;
}

.layer-select-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 8px;
}

.layer-select-item {
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.layer-select-item:hover {
  background: rgba(66,165,245,0.1);
  border-color: var(--accent);
}

.layer-info {
  display: flex;
  flex-direction: column;
}

.layer-name {
  font-size: 12px;
  color: var(--text);
  font-weight: 500;
}

.layer-count {
  font-size: 10px;
  color: var(--sub);
  margin-top: 2px;
}

.divider {
  text-align: center;
  color: var(--sub);
  font-size: 11px;
  margin: 8px 0;
  position: relative;
}

.divider::before,
.divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 30%;
  height: 1px;
  background: var(--border);
}

.divider::before {
  left: 10%;
}

.divider::after {
  right: 10%;
}

.input-group {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.layer-input {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: rgba(255,255,255,0.05);
  color: var(--text);
  font-size: 12px;
}

.layer-input::placeholder {
  color: var(--sub);
}

.layer-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 1px rgba(66,165,245,0.3);
}

.tip { 
  margin-top: 8px; 
  font-size: 12px; 
  color: var(--sub);
  padding: 8px;
  background: rgba(66,165,245,0.08);
  border-radius: 6px;
  border-left: 3px solid var(--accent);
}
</style>


