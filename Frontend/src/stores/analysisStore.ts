import { defineStore } from 'pinia'
import { ref } from 'vue'

type ToolId = 'draw' | 'buffer' | 'distance' | 'servicearea' | 'layer' | 'bianji' | 'llm' | 'query' | 'thiessen' | '';

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
  
  // 距离量测模式状态
  const isDistanceMeasureMode = ref<boolean>(false)
  
  // 面积量测模式状态
  const isAreaMeasureMode = ref<boolean>(false)
  
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

  // 设置当前工具（用于状态同步）
  function setActiveTool(toolId: ToolId) {
    toolPanel.activeTool.value = toolId
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
  
  // 距离量测模式控制
  function setDistanceMeasureMode(mode: boolean) {
    isDistanceMeasureMode.value = mode
  }
  
  // 面积量测模式控制
  function setAreaMeasureMode(mode: boolean) {
    isAreaMeasureMode.value = mode
  }
  
  return {
    // State
    analysisStatus,
    toolPanel,
    drawMode,
    selectionMode,
    currentLayer,
    isDistanceMeasureMode,
    isAreaMeasureMode,
    
    // Actions
    setAnalysisStatus,
    openTool,
    closeTool,
    setActiveTool,
    setDrawMode,
    setSelectionMode,
    setCurrentLayer,
    setDistanceMeasureMode,
    setAreaMeasureMode
  }
})
