import { defineStore } from 'pinia'
import { ref } from 'vue'

const usePopupStore = defineStore('popup', () => {
  // 弹窗可见性
  const visible = ref<boolean>(false)
  
  // 弹窗位置
  const position = ref<{ x: number, y: number }>({ x: 0, y: 0 })
  
  // 弹窗内容
  const content = ref<string>('')
  
  // 弹窗关联的要素
  const feature = ref<any>(null)
  
  // 弹窗坐标
  const coordinate = ref<number[] | null>(null)
  
  // Actions
  function showPopup(
    pos: { x: number, y: number }, 
    cont: string, 
    feat: any = null, 
    coord: number[] | null = null
  ) {
    position.value = pos
    content.value = cont
    feature.value = feat
    coordinate.value = coord
    visible.value = true
  }
  
  function hidePopup() {
    visible.value = false
    content.value = ''
    feature.value = null
    coordinate.value = null
  }
  
  function updatePosition(pos: { x: number, y: number }) {
    position.value = pos
  }
  
  function updateContent(cont: string) {
    content.value = cont
  }
  
  function updateCoordinate(coord: number[]) {
    coordinate.value = coord
  }
  
  return {
    // 状态
    visible,
    position,
    content,
    feature,
    coordinate,
    
    // Actions
    showPopup,
    hidePopup,
    updatePosition,
    updateContent,
    updateCoordinate
  }
})

export { usePopupStore }
export default usePopupStore
