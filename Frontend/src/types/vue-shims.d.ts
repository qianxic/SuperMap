declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'vue' {
  export * from '@vue/runtime-dom'
}

declare module 'pinia' {
  export * from 'pinia'
}

declare module 'vue-router' {
  export * from 'vue-router'
}
