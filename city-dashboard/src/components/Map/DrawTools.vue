<template>
  <div 
    v-show="analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'draw'"
    class="draw-tools-panel"
  >
    <!-- 绘制模式选择 -->
    <div class="analysis-section">
      <div class="section-title">选择创建类型</div>
      <div class="button-row">
        <SecondaryButton 
          text="创建点图层"
          :active="analysisStore.drawMode === 'point'"
          @click="setDrawMode('point')"
        />
        <SecondaryButton 
          text="创建线图层"
          :active="analysisStore.drawMode === 'line'"
          @click="setDrawMode('line')"
        />
        <SecondaryButton 
          text="创建面图层"
          :active="analysisStore.drawMode === 'polygon'"
          @click="setDrawMode('polygon')"
        />
      </div>
    </div>
    
    <!-- 图层配置 -->
    <div class="analysis-section">
      <div class="section-title">图层配置</div>
      <FormInput 
        v-model="layerName" 
        label="图层名称" 
        placeholder="请输入图层名称"
      />
    </div>

    <!-- 绘制操作 -->
    <div class="analysis-section">
      <div class="section-title">绘制操作</div>
      <div class="button-column">
        <SecondaryButton 
          text="清空绘制"
          @click="clearDrawing"
        />
        <SecondaryButton 
          text="完成绘制"
          @click="finishDrawing"
        />
      </div>
    </div>
    
    <div class="tip" v-if="analysisStore.drawMode">在地图上点击开始绘制{{ analysisStore.drawMode === 'point' ? '点' : analysisStore.drawMode === 'line' ? '线' : '面' }}</div>
    <div class="tip" v-else>选择绘制工具开始创建要素</div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore.ts'
import { useDraw } from '@/composables/useDraw.ts'
import { useLayerManager } from '@/composables/useLayerManager.ts'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
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


// 设置绘制模式
const setDrawMode = (mode: string) => {
  analysisStore.setDrawMode(mode)
  
  if (mode === 'point') {
    analysisStore.setAnalysisStatus('绘制点功能暂未实现')
  } else if (mode === 'line') {
    analysisStore.setAnalysisStatus('绘制线功能暂未实现')
  } else if (mode === 'polygon') {
    analysisStore.setAnalysisStatus('绘制面功能暂未实现')
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
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.analysis-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px;
  transition: all 0.3s ease;
  animation: fadeIn 0.3s ease-out;
}

.analysis-section:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(66, 165, 245, 0.3);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-title {
  font-size: 13px;
  color: var(--text);
  margin-bottom: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
}



.button-row {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}





.button-column {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.tip { 
  margin-top: 8px; 
  font-size: 12px; 
  color: var(--sub);
  padding: 12px;
  background: rgba(66,165,245,0.08);
  border-radius: 12px;
  border-left: 4px solid var(--accent);
  animation: fadeIn 0.3s ease-out;
}
</style>


