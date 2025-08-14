import { defineStore } from 'pinia'
import { ref } from 'vue'

type ToolId = 'draw' | 'buffer' | 'distance' | 'gotowhere' | 'layer' | 'bianji' | 'llm' | '';

export const useAnalysisStore = defineStore('analysis', () => {
  // 分析状态
  const analysisStatus = ref<string>('')
  
  // 通用功能面板（工具面板）状态
  const toolPanel = {
    visible: ref<boolean>(false),
    title: ref<string>(''),
    activeTool: ref<ToolId>('')
  }
  
  // 绘制工具状态
  const drawMode = ref<string>('') // 'point', 'line', 'polygon'
  const selectionMode = ref<string>('') // 
  const currentLayer = ref<any>(null)
  
  // Actions
  function setAnalysisStatus(status: string) {
    analysisStatus.value = status
  }

  // 工具面板控制
  function openTool(toolId: ToolId, title: string = '') {
    toolPanel.activeTool.value = toolId
    toolPanel.title.value = title
    toolPanel.visible.value = true
  }

  function closeTool() {
    toolPanel.visible.value = false
    toolPanel.title.value = ''
    toolPanel.activeTool.value = ''
    drawMode.value = ''
  }
  
  // 绘制工具控制
  function setDrawMode(mode: string) {
    drawMode.value = mode
  }
  
  function setSelectionMode(mode: string) {
    selectionMode.value = mode
  }

  function setCurrentLayer(layer: any) {
    currentLayer.value = layer
  }
  
  return {
    // State
    analysisStatus,
    toolPanel,
    drawMode,
    selectionMode,
    currentLayer,
    
    // Actions
    setAnalysisStatus,
    openTool,
    closeTool,
    setDrawMode,
    setSelectionMode,
    setCurrentLayer
  }
})
