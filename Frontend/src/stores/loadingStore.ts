import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface LoadingState {
  id: string
  message: string
  progress?: number
}

export const useLoadingStore = defineStore('loading', () => {
  const loadingStates = ref<Map<string, LoadingState>>(new Map())
  
  const isLoading = computed(() => loadingStates.value.size > 0)
  
  const globalMessage = computed(() => {
    const states = Array.from(loadingStates.value.values())
    return states.length > 0 ? states[states.length - 1].message : ''
  })

  const startLoading = (id: string, message: string, progress?: number): void => {
    loadingStates.value.set(id, { id, message, progress })
  }

  const updateLoading = (id: string, message?: string, progress?: number): void => {
    const state = loadingStates.value.get(id)
    if (state) {
      if (message !== undefined) state.message = message
      if (progress !== undefined) state.progress = progress
    }
  }

  const stopLoading = (id: string): void => {
    loadingStates.value.delete(id)
  }

  const clearAll = (): void => {
    loadingStates.value.clear()
  }

  const getLoadingState = (id: string): LoadingState | undefined => {
    return loadingStates.value.get(id)
  }

  return {
    loadingStates,
    isLoading,
    globalMessage,
    startLoading,
    updateLoading,
    stopLoading,
    clearAll,
    getLoadingState
  }
})