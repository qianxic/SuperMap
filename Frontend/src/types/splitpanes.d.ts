declare module 'splitpanes' {
  import { DefineComponent } from 'vue'
  
  export const Splitpanes: DefineComponent<{
    class?: string
    horizontal?: boolean
    dblClickSplitter?: boolean
    firstSplitter?: boolean
    pushOtherPanes?: boolean
    minSplitterSize?: number
    maxSplitterSize?: number
  }>
  
  export const Pane: DefineComponent<{
    size?: number | string
    minSize?: number | string
    maxSize?: number | string
  }>
}
