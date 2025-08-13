<template>
  <PanelWindow 
    :visible="true" 
    :embed="true" 
    :width="'100%'" 
    :height="'100%'"
    class="right-panel-content"
  >
    <!-- 模式切换器 -->
    <div class="mode-switcher">
      <ButtonGroup
        :buttons="modeButtons"
        :active-button="activeMode"
        @select="setMode"
      />
    </div>

    <!-- 传统功能区 -->
    <div v-if="activeMode === 'traditional'" class="traditional-panel">
      <!-- 功能按钮容器 -->
      <div class="function-buttons-container">
        <div class="buttons-grid">
          <div class="button-row">
            <PrimaryButton text="图层管理" @click="toggleLayerManager" />
            <PrimaryButton text="图层创建" @click="toggleDraw" />
            <PrimaryButton text="要素编辑" @click="togglebianji" />
          </div>
          <div class="button-row">
            <PrimaryButton text="缓冲区分析" @click="toggleBuffer" />
          </div>
        </div>
      </div>
      
      <div class="divider"></div>
      
      <!-- 内容区域 -->
      <div class="content-section">
        <DrawTools v-if="analysisStore.toolPanel.activeTool === 'draw'" />
        <EditTools v-if="analysisStore.toolPanel.activeTool === 'bianji'" />
        <BufferAnalysisPanel v-if="analysisStore.toolPanel.activeTool === 'buffer'" />
        <LayerManager v-if="analysisStore.toolPanel.activeTool === 'layer'" />
        <div v-if="!analysisStore.toolPanel.visible" class="default-content">
          <div class="welcome-message">
            <p>请从上方工具栏选择功能开始使用</p>
          </div>
        </div>
      </div>
    </div>

    <!-- LLM 助手区 -->
    <div v-if="activeMode === 'llm'" class="llm-panel">
      <ChatAssistant />
    </div>
  </PanelWindow>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysisStore'
import DrawTools from '@/components/Map/DrawTools.vue'
import EditTools from '@/components/Map/EditTools.vue'
import BufferAnalysisPanel from '@/components/Map/BufferAnalysisPanel.vue'
import LayerManager from '@/components/Map/LayerManager.vue'
import PrimaryButton from '@/components/UI/PrimaryButton.vue'
import PanelWindow from '@/components/UI/PanelWindow.vue'
import ButtonGroup from '@/components/UI/ButtonGroup.vue'
import ChatAssistant from '@/components/LLM/ChatAssistant.vue'

// 模式管理
const activeMode = ref<'traditional' | 'llm'>('llm');
const modeButtons = [
  { id: 'llm', text: 'LLM 模式' },
  { id: 'traditional', text: '传统模式' },
];
const setMode = (modeId: 'traditional' | 'llm') => {
  activeMode.value = modeId;
};

const analysisStore = useAnalysisStore()

const isDrawOpen = computed(() => analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'draw')
const isBufferOpen = computed(() => analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'buffer')
const isLayerOpen = computed(() => analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'layer')
const isbianji = computed(() => analysisStore.toolPanel.visible && analysisStore.toolPanel.activeTool === 'bianji')

const toggleDraw = () => {
  if (isDrawOpen.value) {
    analysisStore.closeTool()
  } else {
    analysisStore.openTool('draw', '图层创建')
  }
}

const togglebianji = () => {
  if (isbianji.value) {
    analysisStore.closeTool()
  } else {
    analysisStore.openTool('bianji', '图层编辑')
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
.right-panel-content {
  padding: 16px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--glow);
  display: flex;
  flex-direction: column;
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

.mode-switcher {
  margin-bottom: 16px;
  flex-shrink: 0;
}

.traditional-panel, .llm-panel {
  flex-grow: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

/* 功能按钮容器样式 */
.function-buttons-container {
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
  animation: fadeIn 0.3s ease-out;
}

.function-buttons-container:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(66, 165, 245, 0.3);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(66, 165, 245, 0.1);
}

.buttons-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.button-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.button-row:last-child {
  grid-template-columns: repeat(3, 1fr);
}

.button-row:last-child :deep(.primary-button) {
  grid-column: 1;
}

/* 按钮样式优化 */
.button-row :deep(.primary-button) {
  width: 100%;
  min-height: 40px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.button-row :deep(.primary-button):hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(66, 165, 245, 0.3);
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
}

.welcome-message p {
  margin: 0;
  font-size: 14px;
}
</style>
