<template>
  <div class="right-panel">
    <!-- 使用一个大的PanelWindow包装整个右侧面板 -->
    <PanelWindow 
      :visible="true" 
      :embed="true" 
      :width="'100%'" 
      :height="'100%'"
    >
      <!-- 工具栏区域 -->
      <div class="toolbar-section">
        <div class="panel-header">
          <h3 class="panel-title">{{ headerTitle }}</h3>
          <div class="toolbar">
            <PrimaryButton text="图层管理" @click="toggleLayerManager" />
            <PrimaryButton text="编辑工具" @click="toggleDraw" />
            <PrimaryButton text="缓冲区分析" @click="toggleBuffer" />
          </div>
        </div>
      </div>
      
      <!-- 内容分隔线 -->
      <div class="divider"></div>
      
      <!-- 功能区域 -->
      <div class="content-section">
        <DrawTools v-if="analysisStore.toolPanel.activeTool === 'draw'" />
        <BufferAnalysisPanel v-if="analysisStore.toolPanel.activeTool === 'buffer'" />
        <LayerManager v-if="analysisStore.toolPanel.activeTool === 'layer'" />
        
        <!-- 默认状态显示 -->
        <div v-if="!analysisStore.toolPanel.visible" class="default-content">
          <div class="welcome-message">
            <p>请从上方工具栏选择功能开始使用</p>
          </div>
        </div>
      </div>
    </PanelWindow>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import DrawTools from '@/components/Map/DrawTools.vue'
import BufferAnalysisPanel from '@/components/Map/BufferAnalysisPanel.vue'
import LayerManager from '@/components/Map/LayerManager.vue'
import PrimaryButton from '@/components/UI/PrimaryButton.vue'
import PanelWindow from '@/components/UI/PanelWindow.vue'

const analysisStore = useAnalysisStore()
const headerTitle = computed(() => analysisStore.toolPanel.title?.value || '功能区')

const isDrawOpen = computed(() => analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'draw')
const isBufferOpen = computed(() => analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'buffer')
const isLayerOpen = computed(() => analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'layer')

const toggleDraw = () => {
  if (isDrawOpen.value) {
    analysisStore.closeTool()
  } else {
    analysisStore.openTool('draw', '绘制工具')
  }
}

const toggleBuffer = () => {
  if (isBufferOpen.value) {
    analysisStore.closeTool()
  } else {
    analysisStore.openTool('buffer', '缓冲区分析')
  }
}

const toggleLayerManager = () => {
  if (isLayerOpen.value) {
    analysisStore.closeTool()
  } else {
    analysisStore.openTool('layer', '图层管理')
  }
}
</script>

<style scoped>
.right-panel {
  height: 100%;
  padding: 0;
  background: transparent;
}

.toolbar-section {
  flex-shrink: 0;
  margin-bottom: 12px;
}

.content-section {
  height: calc(100% - 140px); /* 减去工具栏和分隔线的高度 */
  min-height: 0;
  overflow: hidden;
}

.panel-header {
  padding: 0;
  background: transparent;
}

.panel-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 500;
  color: var(--text);
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.divider {
  height: 1px;
  background: var(--border);
  margin: 16px 0;
  opacity: 0.5;
}

.default-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-message {
  text-align: center;
  color: var(--sub);
}

.welcome-message h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: var(--text);
}

.welcome-message p {
  margin: 0;
  font-size: 14px;
}
</style>
