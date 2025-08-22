import { ref, computed } from 'vue'

export function useFeatureInfo() {
  const currentFeature = ref<any>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 生成简单的弹窗内容
  const generatePopupContent = (): string => {
    return '<div class="kv"><span class="k">状态</span><span class="v">要素已选中</span></div>'
  }

  // 清除当前要素信息
  const clearFeatureInfo = (): void => {
    currentFeature.value = null
    error.value = null
  }

  // 计算属性
  const hasFeature = computed(() => !!currentFeature.value)
  const hasError = computed(() => !!error.value)

  return {
    // 状态
    currentFeature,
    isLoading,
    error,
    
    // 计算属性
    hasFeature,
    hasError,
    
    // 方法
    generatePopupContent,
    clearFeatureInfo
  }
}
