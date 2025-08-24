<template>
  <PanelContainer class="traditional-panel">
    <!-- 功能按钮容器 -->
    <div class="function-buttons-container">
      <div class="buttons-grid">
        <div class="button-row">
          <PrimaryButton text="图层管理" :active="isLayerOpen" @click="toggleLayerManager" />
          <PrimaryButton text="按属性选择要素" :active="isQueryOpen" @click="toggleQuery" />
          <PrimaryButton text="按区域选择要素" :active="isbianji" @click="togglebianji" />
        </div>
        <div class="button-row">
          <PrimaryButton text="缓冲区分析" :active="isBufferOpen" @click="toggleBuffer" />
          <PrimaryButton text="最优路径分析" :active="isDistanceOpen" @click="toggleDistance" />
          <PrimaryButton text="可达性分析" :active="isGotowhereOpen" @click="toggleGotowhere" />
        </div>
      </div>
    </div>
    
    <div class="divider"></div>
    
    <!-- 内容区域 -->
    <div class="content-section">
      <FeatureQueryPanel v-if="analysisStore.toolPanel.activeTool === 'query'" />
      <EditTools v-if="analysisStore.toolPanel.activeTool === 'bianji'" />
      <BufferAnalysisPanel v-if="analysisStore.toolPanel.activeTool === 'buffer'" />
      <DistanceAnalysisPanel v-if="analysisStore.toolPanel.activeTool === 'distance'" />
      <AccessibilityAnalysisPanel v-if="analysisStore.toolPanel.activeTool === 'gotowhere'" />
      <LayerManager v-if="analysisStore.toolPanel.activeTool === 'layer'" />
      <div v-if="!analysisStore.toolPanel.visible" class="default-content">
        <div class="welcome-message">
          <p>请从上方工具栏选择功能开始使用</p>
        </div>
      </div>
    </div>
  </PanelContainer>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import FeatureQueryPanel from '@/components/Map/FeatureQueryPanel.vue'
import EditTools from '@/components/Map/EditTools.vue'
import BufferAnalysisPanel from '@/components/Map/BufferAnalysisPanel.vue'
import DistanceAnalysisPanel from '@/components/Map/DistanceAnalysisPanel.vue'
import AccessibilityAnalysisPanel from '@/components/Map/AccessibilityAnalysisPanel.vue'
import LayerManager from '@/components/Map/LayerManager.vue'
import PrimaryButton from '@/components/UI/PrimaryButton.vue'
import PanelContainer from '@/components/UI/PanelContainer.vue'

const analysisStore = useAnalysisStore()

// 工具配置对象
const toolConfigs = {
  bianji: { id: 'bianji', title: '图层编辑' },
  buffer: { id: 'buffer', title: '缓冲区分析' },
  layer: { id: 'layer', title: '图层管理' },
  distance: { id: 'distance', title: '最优路径分析' },
  gotowhere: { id: 'gotowhere', title: '可达性分析' },
  query: { id: 'query', title: '要素查询' }
} as const

// 状态检查变量
const isBufferOpen = computed(() => analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'buffer')
const isLayerOpen = computed(() => analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'layer')
const isbianji = computed(() => analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'bianji')
const isDistanceOpen = computed(() => analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'distance')
const isGotowhereOpen = computed(() => analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'gotowhere')
const isQueryOpen = computed(() => analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'query')

// 通用切换函数
const toggleTool = (toolKey: keyof typeof toolConfigs) => {
  const config = toolConfigs[toolKey]
  const isCurrentlyActive = analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === config.id
  
  if (isCurrentlyActive) {
    analysisStore.closeTool()
  } else {
    analysisStore.openTool(config.id, config.title)
  }
}

// 简化的切换函数
const togglebianji = () => toggleTool('bianji')
const toggleBuffer = () => toggleTool('buffer')
const toggleLayerManager = () => toggleTool('layer')
const toggleDistance = () => toggleTool('distance')
const toggleGotowhere = () => toggleTool('gotowhere')
const toggleQuery = () => toggleTool('query')

// 当进入传统模式时，自动打开图层管理界面
onMounted(() => {
  // 延迟执行，确保组件已完全渲染
  setTimeout(() => {
    if (!analysisStore.toolPanel.visible) {
      analysisStore.openTool('layer', '图层管理')
    }
  }, 100)
})
</script>

<style scoped>
.traditional-panel {
  flex-grow: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.function-buttons-container {
  padding: 15px;
  background: var(--panel);
  border-bottom: 1px solid var(--border);
}

.buttons-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.button-row {
  display: flex;
  gap: 10px;
  justify-content: space-around;
}

.divider {
  height: 1px;
  background: var(--border);
  margin: 0;
}

.content-section {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.default-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
}

.welcome-message {
  text-align: center;
  padding: 20px;
}

.welcome-message p {
  margin: 0;
  font-size: 14px;
  opacity: 0.7;
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

.content-section > * {
  animation: fadeIn 0.3s ease-out;
}
</style>