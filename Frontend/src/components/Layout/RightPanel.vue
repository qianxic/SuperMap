<template>
  <PanelWindow 
    :visible="true" 
    :embed="true" 
    :width="'100%'" 
    :height="'100%'"
    class="right-panel-content"
  >


    <!-- 传统功能区 -->
    <PanelContainer v-if="activeMode === 'traditional'" class="traditional-panel">
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

    <!-- LLM 助手区 -->
    <PanelContainer v-if="activeMode === 'llm'" class="llm-panel">
      <div class="chat-container">
        <ChatAssistant :initial-layers="layersStatus" :map-ready="mapStore.isMapReady" />
      </div>
    </PanelContainer>
  </PanelWindow>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import FeatureQueryPanel from '@/components/Map/FeatureQueryPanel.vue'
import EditTools from '@/components/Map/EditTools.vue'
import BufferAnalysisPanel from '@/components/Map/BufferAnalysisPanel.vue'
import DistanceAnalysisPanel from '@/components/Map/DistanceAnalysisPanel.vue'
import AccessibilityAnalysisPanel from '@/components/Map/AccessibilityAnalysisPanel.vue'
import LayerManager from '@/components/Map/LayerManager.vue'
import PrimaryButton from '@/components/UI/PrimaryButton.vue'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'
import PanelWindow from '@/components/UI/PanelWindow.vue'
import PanelContainer from '@/components/UI/PanelContainer.vue'

import ChatAssistant from '@/components/Map/ChatAssistant.vue'
import { useMapStore } from '@/stores/mapStore'

// 模式管理 - 从父组件注入或监听全局事件
const activeMode = ref<'traditional' | 'llm'>('llm');
// 跟踪是否首次进入传统模式
const isFirstTimeTraditional = ref<boolean>(true);

// 监听模式变化事件
const handleModeChange = (event: CustomEvent) => {
  const newMode = event.detail;
  activeMode.value = newMode;
  
  // 当首次进入传统模式时，自动打开图层管理界面
  if (newMode === 'traditional' && isFirstTimeTraditional.value) {
    isFirstTimeTraditional.value = false;
    // 延迟执行，确保组件已完全渲染
    setTimeout(() => {
      analysisStore.openTool('layer', '图层管理');
    }, 100);
  }
};

onMounted(() => {
  window.addEventListener('modeChanged', handleModeChange as EventListener);
  
  // 如果初始化时就是传统模式，也自动打开图层管理界面
  if (activeMode.value === 'traditional' && isFirstTimeTraditional.value) {
    isFirstTimeTraditional.value = false;
    setTimeout(() => {
      analysisStore.openTool('layer', '图层管理');
    }, 100);
  }
});

onUnmounted(() => {
  window.removeEventListener('modeChanged', handleModeChange as EventListener);
});

const analysisStore = useAnalysisStore()
const mapStore = useMapStore()

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

const layersStatus = computed(() => {
  return mapStore.vectorLayers.map(l => ({ name: l.name, visible: l.visible }))
})

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
</script>

<style scoped>
.right-panel-content {
  padding: 0;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--glow);
  display: flex;
  flex-direction: column;
  height: calc(100vh - 96px);
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



.traditional-panel {
  flex-grow: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.llm-panel {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* 功能按钮容器样式 */
.function-buttons-container {
  flex-shrink: 0;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px;
  animation: fadeIn 0.3s ease-out;
}



.buttons-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.button-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.button-row:last-child {
  grid-template-columns: repeat(3, 1fr);
}

/* 按钮样式优化 */
.button-row :deep(.btn) {
  width: 100%;
  min-height: 32px;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 8px;
}

/* 确保active状态显示蓝色 */
.button-row :deep(.btn.active) {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  color: white !important;
}

/* 响应式设计 */
@media (max-width: 320px) {
  .button-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .function-buttons-container {
    padding: 16px;
  }
}



.content-section {
  flex-grow: 1;
  min-height: 0;
  overflow: hidden;
}



.divider {
  height: 1px;
  background: var(--border);
  margin: 16px 0;
  opacity: 0.5;
  flex-shrink: 0;
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
  padding: 16px;
  border-radius: 8px;
}



.welcome-message p {
  margin: 0;
  font-size: 14px;
}
</style>
