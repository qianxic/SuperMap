/**
 * 自动滚动工具类
 * 提供容器列表的自动滚动功能，支持居中显示、边界处理、平滑滚动等
 */

interface AutoScrollOptions {
  scrollBehavior?: 'auto' | 'smooth'
  scrollOffset?: number
  centerOnSelect?: boolean
  itemSelector?: string
}

interface ScrollInfo {
  scrollTop: number
  scrollHeight: number
  clientHeight: number
  maxScrollTop: number
  scrollPercentage: number
  isAtTop: boolean
  isAtBottom: boolean
}

class AutoScroll {
  private container: HTMLElement
  private options: Required<AutoScrollOptions>
  private isInitialized: boolean = false
  private scrollListeners: Array<(scrollInfo: ScrollInfo) => void> = []
  private boundHandleScroll: any

  constructor(container: HTMLElement, options: AutoScrollOptions = {}) {
    this.container = container
    this.options = {
      scrollBehavior: 'smooth',
      scrollOffset: 0,
      centerOnSelect: true,
      itemSelector: '',
      ...options
    }
    
    this.init()
  }
  
  /**
   * 初始化滚动容器
   */
  init(): boolean {
    if (!this.container || this.isInitialized) {
      return false
    }
    
    // 确保容器有正确的样式
    this.container.style.overflowY = 'auto'
    this.container.style.overflowX = 'hidden'
    this.container.style.position = 'relative'
    
    // 添加滚动事件监听
    this.boundHandleScroll = this.handleScroll.bind(this)
    this.container.addEventListener('scroll', this.boundHandleScroll)
    
    this.isInitialized = true
    return true
  }
  
  /**
   * 滚动到指定索引的项
   * @param index - 目标索引
   * @returns 是否成功
   */
  async scrollToIndex(index: number): Promise<boolean> {
    if (!this.isInitialized || index < 0) {
      return false
    }
    
    try {
      // 等待DOM更新
      await this.waitForNextTick()
      
      // 获取目标元素
      let targetElement: HTMLElement | null = null
      
      if (this.options.itemSelector) {
        // 使用自定义选择器
        const elements = this.container.querySelectorAll(this.options.itemSelector)
        targetElement = elements[index] as HTMLElement
      } else {
        // 使用直接子元素
        const children = this.container.children
        targetElement = children[index] as HTMLElement
      }
      
      if (!targetElement) {
        console.error(`未找到索引为 ${index} 的元素`)
        return false
      }
      
      return this.scrollToElement(targetElement)
      
    } catch (error) {
      console.error('滚动到索引失败:', error)
      return false
    }
  }
  
  /**
   * 滚动到指定元素
   * @param element - 目标元素
   * @returns 是否成功
   */
  scrollToElement(element: HTMLElement): boolean {
    if (!this.isInitialized || !element) {
      return false
    }
    
    try {
      // 计算滚动位置
      const containerHeight = this.container.clientHeight
      const elementTop = element.offsetTop
      const elementHeight = element.offsetHeight
      
      let targetScrollTop: number
      
      if (this.options.centerOnSelect) {
        // 居中显示算法
        targetScrollTop = elementTop - (containerHeight / 2) + (elementHeight / 2)
      } else {
        // 顶部对齐算法
        targetScrollTop = elementTop
      }
      
      // 添加额外偏移量
      targetScrollTop += this.options.scrollOffset
      
      // 确保滚动位置在有效范围内
      const maxScrollTop = this.container.scrollHeight - containerHeight
      const finalScrollTop = Math.max(0, Math.min(targetScrollTop, maxScrollTop))
      
      // 执行滚动
      this.container.scrollTo({
        top: finalScrollTop,
        behavior: this.options.scrollBehavior
      })
      
      // 触发滚动事件
      this.triggerScrollEvent({
        scrollTop: finalScrollTop,
        scrollHeight: this.container.scrollHeight,
        clientHeight: containerHeight,
        maxScrollTop,
        scrollPercentage: maxScrollTop > 0 ? (finalScrollTop / maxScrollTop) * 100 : 0,
        isAtTop: finalScrollTop === 0,
        isAtBottom: finalScrollTop >= maxScrollTop
      })
      
      return true
      
    } catch (error) {
      console.error('滚动到元素失败:', error)
      return false
    }
  }
  
  /**
   * 滚动到底部
   * @returns 是否成功
   */
  scrollToBottom(): boolean {
    if (!this.isInitialized) {
      return false
    }
    
    try {
      const scrollHeight = this.container.scrollHeight
      const clientHeight = this.container.clientHeight
      const targetScrollTop = scrollHeight - clientHeight
      
      this.container.scrollTo({
        top: targetScrollTop,
        behavior: this.options.scrollBehavior
      })
      
      this.triggerScrollEvent({
        scrollTop: targetScrollTop,
        scrollHeight,
        clientHeight,
        maxScrollTop: targetScrollTop,
        scrollPercentage: 100,
        isAtTop: false,
        isAtBottom: true
      })
      
      return true
    } catch (error) {
      console.error('滚动到底部失败:', error)
      return false
    }
  }
  
  /**
   * 滚动到顶部
   * @returns 是否成功
   */
  scrollToTop(): boolean {
    if (!this.isInitialized) {
      return false
    }
    
    try {
      this.container.scrollTo({
        top: 0,
        behavior: this.options.scrollBehavior
      })
      
      this.triggerScrollEvent({
        scrollTop: 0,
        scrollHeight: this.container.scrollHeight,
        clientHeight: this.container.clientHeight,
        maxScrollTop: this.container.scrollHeight - this.container.clientHeight,
        scrollPercentage: 0,
        isAtTop: true,
        isAtBottom: false
      })
      
      return true
    } catch (error) {
      console.error('滚动到顶部失败:', error)
      return false
    }
  }
  
  /**
   * 滚动到指定位置
   * @param scrollTop - 目标滚动位置
   * @returns 是否成功
   */
  scrollToPosition(scrollTop: number): boolean {
    if (!this.isInitialized) {
      return false
    }
    
    try {
      // 确保滚动位置在有效范围内
      const maxScrollTop = this.container.scrollHeight - this.container.clientHeight
      const finalScrollTop = Math.max(0, Math.min(scrollTop, maxScrollTop))
      
      this.container.scrollTo({
        top: finalScrollTop,
        behavior: this.options.scrollBehavior
      })
      
      this.triggerScrollEvent({
        scrollTop: finalScrollTop,
        scrollHeight: this.container.scrollHeight,
        clientHeight: this.container.clientHeight,
        maxScrollTop,
        scrollPercentage: maxScrollTop > 0 ? (finalScrollTop / maxScrollTop) * 100 : 0,
        isAtTop: finalScrollTop === 0,
        isAtBottom: finalScrollTop >= maxScrollTop
      })
      
      return true
    } catch (error) {
      console.error('滚动到位置失败:', error)
      return false
    }
  }
  
  /**
   * 获取当前滚动信息
   * @returns 滚动信息
   */
  getScrollInfo(): ScrollInfo | null {
    if (!this.isInitialized) {
      return null
    }
    
    const scrollTop = this.container.scrollTop
    const scrollHeight = this.container.scrollHeight
    const clientHeight = this.container.clientHeight
    const maxScrollTop = scrollHeight - clientHeight
    
    return {
      scrollTop,
      scrollHeight,
      clientHeight,
      maxScrollTop,
      scrollPercentage: maxScrollTop > 0 ? (scrollTop / maxScrollTop) * 100 : 0,
      isAtTop: scrollTop === 0,
      isAtBottom: scrollTop >= maxScrollTop
    }
  }
  
  /**
   * 检查元素是否在可视区域内
   * @param element - 目标元素
   * @returns 是否在可视区域内
   */
  isElementVisible(element: HTMLElement): boolean {
    if (!this.isInitialized || !element) {
      return false
    }
    
    const containerRect = this.container.getBoundingClientRect()
    const elementRect = element.getBoundingClientRect()
    
    return (
      elementRect.top >= containerRect.top &&
      elementRect.bottom <= containerRect.bottom
    )
  }
  
  /**
   * 添加滚动事件监听器
   * @param listener - 监听器函数
   */
  addScrollListener(listener: (scrollInfo: ScrollInfo) => void): void {
    if (typeof listener === 'function') {
      this.scrollListeners.push(listener)
    }
  }
  
  /**
   * 移除滚动事件监听器
   * @param listener - 监听器函数
   */
  removeScrollListener(listener: (scrollInfo: ScrollInfo) => void): void {
    const index = this.scrollListeners.indexOf(listener)
    if (index > -1) {
      this.scrollListeners.splice(index, 1)
    }
  }
  
  /**
   * 处理滚动事件
   */
  private handleScroll(): void {
    const scrollInfo = this.getScrollInfo()
    if (scrollInfo) {
      this.triggerScrollEvent(scrollInfo)
    }
  }
  
  /**
   * 触发滚动事件
   * @param scrollInfo - 滚动信息
   */
  private triggerScrollEvent(scrollInfo: ScrollInfo): void {
    this.scrollListeners.forEach(listener => {
      try {
        listener(scrollInfo)
      } catch (error) {
        console.error('滚动监听器执行失败:', error)
      }
    })
  }
  
  /**
   * 等待下一个tick
   * @returns Promise对象
   */
  private waitForNextTick(): Promise<void> {
    return new Promise(resolve => {
      if (typeof requestAnimationFrame !== 'undefined') {
        requestAnimationFrame(() => resolve())
      } else {
        setTimeout(resolve, 0)
      }
    })
  }
  
  /**
   * 更新配置
   * @param newOptions - 新配置
   */
  updateOptions(newOptions: Partial<AutoScrollOptions>): void {
    this.options = {
      ...this.options,
      ...newOptions
    }
  }
  
  /**
   * 销毁实例
   */
  destroy(): void {
    if (this.container) {
      if (this.boundHandleScroll) {
        this.container.removeEventListener('scroll', this.boundHandleScroll)
      }
    }
    
    this.scrollListeners = []
    this.isInitialized = false
  }

  /**
   * 获取当前容器
   */
  getContainer(): HTMLElement {
    return this.container
  }

  /**
   * 替换容器并重新初始化
   */
  replaceContainer(newContainer: HTMLElement): void {
    if (!newContainer || newContainer === this.container) {
      return
    }
    this.destroy()
    this.container = newContainer
    this.init()
  }
}

/**
 * 创建自动滚动实例的工厂函数
 * @param container - 容器元素或选择器
 * @param options - 配置选项
 * @returns 自动滚动实例
 */
function createAutoScroll(container: HTMLElement | string, options: AutoScrollOptions = {}): AutoScroll | null {
  let containerElement: HTMLElement | null = container as HTMLElement
  
  // 如果传入的是选择器字符串，则查找元素
  if (typeof container === 'string') {
    containerElement = document.querySelector(container)
  }
  
  if (!containerElement) {
    console.error('未找到容器元素:', container)
    return null
  }
  
  return new AutoScroll(containerElement, options)
}

// 导出
export { AutoScroll, createAutoScroll }
export type { AutoScrollOptions, ScrollInfo }
export default AutoScroll
