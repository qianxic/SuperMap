import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useModeStateStore } from '../modeStateStore'

describe('ModeStateStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    // 清除localStorage
    localStorage.clear()
  })

  it('should initialize with default state', () => {
    const store = useModeStateStore()
    
    expect(store.currentMode).toBe('llm')
    expect(store.llmState.messages).toEqual([])
    expect(store.llmState.inputText).toBe('')
    expect(store.traditionalState.activeTool).toBe('layer')
    expect(store.traditionalState.toolStates).toEqual({})
  })

  it('should save and restore LLM state', () => {
    const store = useModeStateStore()
    
    const testState = {
      messages: [{ id: 1, text: 'test', sender: 'user' as const }],
      inputText: 'test input',
      scrollPosition: 100
    }
    
    store.saveLLMState(testState)
    
    const restoredState = store.getLLMState()
    expect(restoredState.messages).toEqual(testState.messages)
    expect(restoredState.inputText).toBe(testState.inputText)
    expect(restoredState.scrollPosition).toBe(testState.scrollPosition)
  })

  it('should save and restore traditional state', () => {
    const store = useModeStateStore()
    
    const testState = {
      activeTool: 'query',
      toolStates: {
        query: { selectedLayerId: 'layer1', queryKeyword: 'test' }
      }
    }
    
    store.saveTraditionalState(testState)
    
    const restoredState = store.getTraditionalState()
    expect(restoredState.activeTool).toBe(testState.activeTool)
    expect(restoredState.toolStates).toEqual(testState.toolStates)
  })

  it('should save and restore tool state', () => {
    const store = useModeStateStore()
    
    const toolState = {
      selectedLayerId: 'layer1',
      queryKeyword: 'test keyword',
      queryResults: [{ id: 1, name: 'test' }]
    }
    
    store.saveToolState('query', toolState)
    
    const restoredState = store.getToolState('query')
    expect(restoredState).toEqual(toolState)
  })

  it('should switch modes correctly', () => {
    const store = useModeStateStore()
    
    // 设置初始状态
    store.saveLLMState({ messages: [{ id: 1, text: 'test', sender: 'user' }] })
    store.saveTraditionalState({ activeTool: 'query' })
    
    // 切换到传统模式
    store.switchMode('traditional')
    
    expect(store.currentMode).toBe('traditional')
    
    // 验证LLM状态被保存
    const llmState = store.getLLMState()
    expect(llmState.messages).toHaveLength(1)
    
    // 切换到LLM模式
    store.switchMode('llm')
    
    expect(store.currentMode).toBe('llm')
    
    // 验证传统模式状态被保存
    const traditionalState = store.getTraditionalState()
    expect(traditionalState.activeTool).toBe('query')
  })

  it('should persist state to localStorage', () => {
    const store = useModeStateStore()
    
    const testLLMState = {
      messages: [{ id: 1, text: 'test', sender: 'user' as const }],
      inputText: 'test input'
    }
    
    store.saveLLMState(testLLMState)
    
    const savedLLMState = localStorage.getItem('llmModeState')
    expect(savedLLMState).toBeTruthy()
    
    const parsedState = JSON.parse(savedLLMState!)
    expect(parsedState.messages).toEqual(testLLMState.messages)
    expect(parsedState.inputText).toBe(testLLMState.inputText)
  })

  it('should restore state from localStorage on initialization', () => {
    // 预先设置localStorage
    const testState = {
      messages: [{ id: 1, text: 'test', sender: 'user' }],
      inputText: 'test input',
      scrollPosition: 100,
      lastActiveTime: Date.now()
    }
    
    localStorage.setItem('llmModeState', JSON.stringify(testState))
    localStorage.setItem('currentMode', 'traditional')
    
    // 创建新的store实例
    const store = useModeStateStore()
    
    expect(store.currentMode).toBe('traditional')
    
    const llmState = store.getLLMState()
    expect(llmState.messages).toEqual(testState.messages)
    expect(llmState.inputText).toBe(testState.inputText)
  })

  it('should clear all states', () => {
    const store = useModeStateStore()
    
    // 设置一些状态
    store.saveLLMState({ messages: [{ id: 1, text: 'test', sender: 'user' }] })
    store.saveTraditionalState({ activeTool: 'query' })
    store.saveToolState('query', { selectedLayerId: 'layer1' })
    
    // 清除所有状态
    store.clearAllStates()
    
    expect(store.currentMode).toBe('llm')
    expect(store.llmState.messages).toEqual([])
    expect(store.traditionalState.activeTool).toBe('layer')
    expect(store.traditionalState.toolStates).toEqual({})
    
    // 验证localStorage也被清除
    expect(localStorage.getItem('llmModeState')).toBeNull()
    expect(localStorage.getItem('traditionalModeState')).toBeNull()
    expect(localStorage.getItem('currentMode')).toBeNull()
  })
})
