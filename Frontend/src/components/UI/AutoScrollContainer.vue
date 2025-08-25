<template>
  <div 
    ref="containerRef"
    class="auto-scroll-container"
    :class="containerClass"
    :style="containerStyle"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted, watch } from 'vue'

interface Props {
  // 容器配置
  maxHeight?: string | number
  containerClass?: string
  containerStyle?: Record<string, any>
  
  // 滚动配置
  scrollBehavior?: 'auto' | 'smooth'
  scrollOffset?: number // 额外的偏移量
  centerOnSelect?: boolean // 是否居中显示选中项
  
  // 自动滚动配置
  autoScrollEnabled?: boolean
  scrollThreshold?: number // 滚动阈值（像素）
  
  // 选中项配置
  selectedIndex?: number
  itemSelector?: string // 子元素选择器，默认为直接子元素
}

interface Emits {
  (e: 'scroll', event: { scrollTop: number, scrollHeight: number, clientHeight: number }): void
  (e: 'scrollToItem', event: { index: number, success: boolean, error?: string }): void
}

const props = withDefaults(defineProps<Props>(), {
  maxHeight: '300px',
  scrollBehavior: 'smooth',
  scrollOffset: 0,
  centerOnSelect: true,
  autoScrollEnabled: true,
  scrollThreshold: 100,
  selectedIndex: -1,
  itemSelector: ''
})

const emit = defineEmits<Emits>()

const containerRef = ref<HTMLElement | null>(null)

// 滚动到指定索引的项
const scrollToIndex = async (index: number): Promise<boolean> => {
  if (!containerRef.value || index < 0) {
    emit('scrollToItem', { index, success: false, error: '容器未初始化或索引无效' })
    return false
  }

  try {
    await nextTick()
    
    // 获取目标元素
    let targetElement: HTMLElement | null = null
    
    if (props.itemSelector) {
      // 使用自定义选择器
      const elements = containerRef.value.querySelectorAll(props.itemSelector)
      targetElement = elements[index] as HTMLElement
    } else {
      // 使用直接子元素
      const children = containerRef.value.children
      targetElement = children[index] as HTMLElement
    }
    
    if (!targetElement) {
      emit('scrollToItem', { index, success: false, error: `未找到索引为 ${index} 的元素` })
      return false
    }

    // 计算滚动位置
    const containerHeight = containerRef.value.clientHeight
    const elementTop = targetElement.offsetTop
    const elementHeight = targetElement.offsetHeight

    let targetScrollTop: number

    if (props.centerOnSelect) {
      // 居中显示算法
      targetScrollTop = elementTop - (containerHeight / 2) + (elementHeight / 2)
    } else {
      // 顶部对齐算法
      targetScrollTop = elementTop
    }

    // 添加额外偏移量
    targetScrollTop += props.scrollOffset

    // 确保滚动位置在有效范围内
    const maxScrollTop = containerRef.value.scrollHeight - containerHeight
    const finalScrollTop = Math.max(0, Math.min(targetScrollTop, maxScrollTop))

    // 执行滚动
    containerRef.value.scrollTo({
      top: finalScrollTop,
      behavior: props.scrollBehavior
    })

    // 触发滚动事件
    emit('scroll', {
      scrollTop: finalScrollTop,
      scrollHeight: containerRef.value.scrollHeight,
      clientHeight: containerHeight
    })

    emit('scrollToItem', { index, success: true })
    return true

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '未知错误'
    emit('scrollToItem', { index, success: false, error: errorMessage })
    return false
  }
}

// 滚动到指定元素
const scrollToElement = async (element: HTMLElement): Promise<boolean> => {
  if (!containerRef.value || !element) {
    return false
  }

  try {
    await nextTick()
    
    // 计算滚动位置
    const containerHeight = containerRef.value.clientHeight
    const elementTop = element.offsetTop
    const elementHeight = element.offsetHeight

    let targetScrollTop: number

    if (props.centerOnSelect) {
      // 居中显示算法
      targetScrollTop = elementTop - (containerHeight / 2) + (elementHeight / 2)
    } else {
      // 顶部对齐算法
      targetScrollTop = elementTop
    }

    // 添加额外偏移量
    targetScrollTop += props.scrollOffset

    // 确保滚动位置在有效范围内
    const maxScrollTop = containerRef.value.scrollHeight - containerHeight
    const finalScrollTop = Math.max(0, Math.min(targetScrollTop, maxScrollTop))

    // 执行滚动
    containerRef.value.scrollTo({
      top: finalScrollTop,
      behavior: props.scrollBehavior
    })

    // 触发滚动事件
    emit('scroll', {
      scrollTop: finalScrollTop,
      scrollHeight: containerRef.value.scrollHeight,
      clientHeight: containerHeight
    })

    return true

  } catch (error) {
    console.error('滚动到元素失败:', error)
    return false
  }
}

// 滚动到底部
const scrollToBottom = (): boolean => {
  if (!containerRef.value) return false

  try {
    const scrollHeight = containerRef.value.scrollHeight
    const clientHeight = containerRef.value.clientHeight
    const targetScrollTop = scrollHeight - clientHeight

    containerRef.value.scrollTo({
      top: targetScrollTop,
      behavior: props.scrollBehavior
    })

    emit('scroll', {
      scrollTop: targetScrollTop,
      scrollHeight,
      clientHeight
    })

    return true
  } catch (error) {
    console.error('滚动到底部失败:', error)
    return false
  }
}

// 滚动到顶部
const scrollToTop = (): boolean => {
  if (!containerRef.value) return false

  try {
    containerRef.value.scrollTo({
      top: 0,
      behavior: props.scrollBehavior
    })

    emit('scroll', {
      scrollTop: 0,
      scrollHeight: containerRef.value.scrollHeight,
      clientHeight: containerRef.value.clientHeight
    })

    return true
  } catch (error) {
    console.error('滚动到顶部失败:', error)
    return false
  }
}

// 获取当前滚动信息
const getScrollInfo = () => {
  if (!containerRef.value) return null

  return {
    scrollTop: containerRef.value.scrollTop,
    scrollHeight: containerRef.value.scrollHeight,
    clientHeight: containerRef.value.clientHeight,
    scrollPercentage: (containerRef.value.scrollTop / (containerRef.value.scrollHeight - containerRef.value.clientHeight)) * 100
  }
}

// 监听选中索引变化，自动滚动
watch(() => props.selectedIndex, (newIndex) => {
  if (props.autoScrollEnabled && newIndex >= 0) {
    scrollToIndex(newIndex)
  }
}, { immediate: false })

// 监听滚动事件
const handleScroll = () => {
  if (containerRef.value) {
    emit('scroll', {
      scrollTop: containerRef.value.scrollTop,
      scrollHeight: containerRef.value.scrollHeight,
      clientHeight: containerRef.value.clientHeight
    })
  }
}

// 组件挂载时添加滚动监听
onMounted(() => {
  if (containerRef.value) {
    containerRef.value.addEventListener('scroll', handleScroll)
  }
})

// 组件卸载时移除滚动监听
onUnmounted(() => {
  if (containerRef.value) {
    containerRef.value.removeEventListener('scroll', handleScroll)
  }
})

// 暴露方法供外部调用
defineExpose({
  scrollToIndex,
  scrollToElement,
  scrollToBottom,
  scrollToTop,
  getScrollInfo,
  containerRef
})
</script>

<style scoped>
.auto-scroll-container {
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
}

/* 自定义滚动条样式 */
.auto-scroll-container::-webkit-scrollbar {
  width: 3px;
  height: 3px;
}

.auto-scroll-container::-webkit-scrollbar-track {
  background: var(--scrollbar-track, rgba(200, 200, 200, 0.1));
  border-radius: 1.5px;
}

.auto-scroll-container::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb, rgba(150, 150, 150, 0.3));
  border-radius: 1.5px;
}

.auto-scroll-container::-webkit-scrollbar-thumb:hover {
  background: var(--scrollbar-thumb-hover, rgba(150, 150, 150, 0.5));
}

/* 平滑滚动 */
.auto-scroll-container {
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
}
</style>
