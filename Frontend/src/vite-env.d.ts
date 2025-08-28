/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'splitpanes'
declare module 'ol'
declare module 'ol/supermap'

interface Window {
  ol: any
}

declare module 'ant-design-vue' {
  const content: any
  export default content
}

declare module 'ant-design-vue/es/*' {
  const content: any
  export default content
}
