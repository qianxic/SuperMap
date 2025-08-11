<template>
  <div 
    v-show="visible"
    class="panel-window"
    :style="panelStyle"
  >
    <div class="panel-title" v-if="!embed && title">{{ title }}</div>
    <slot></slot>
  </div>
</template>
<!-- 面板窗口 -->
<script setup lang="ts">
import { computed, defineProps, withDefaults } from 'vue'
import type { CSSProperties } from 'vue'

interface Props {
  visible?: boolean;
  title?: string;
  embed?: boolean;
  width?: string | number;
  height?: string | number;
  position?: 'left' | 'right';
  top?: string | number;
  resizable?: boolean;
  zIndex?: number;
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  title: '',
  embed: false,
  width: 320,
  height: 'auto',
  position: 'right',
  top: 64,
  resizable: false,
  zIndex: 1300
})

const panelStyle = computed((): CSSProperties => {
  const styles: CSSProperties = {
    width: typeof props.width === 'number' ? `${props.width}px` : props.width,
    top: typeof props.top === 'number' ? `${props.top}px` : props.top,
    zIndex: props.zIndex,
    position: 'absolute', // Default position
  }
  
  if (props.height !== 'auto') {
    styles.height = typeof props.height === 'number' ? `${props.height}px` : props.height
  }
  
  if (!props.embed) {
    if (props.position === 'right') {
      styles.right = '24px'
    } else {
      styles.left = '24px'
    }
  } else {
    styles.position = 'relative'
    styles.right = 'auto'
    styles.left = 'auto'
    styles.top = 'auto'
    styles.width = '100%'
    if (props.height === 'auto') styles.height = '100%'
  }
  
  if (props.resizable) {
    styles.resize = 'both'
    styles.overflow = 'auto'
  }
  
  return styles
})
</script>

<style scoped>
.panel-window {
  position: absolute;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--glow);
  padding: 12px;
}

.panel-title { 
  font-size: 14px; 
  font-weight: 600; 
  color: var(--text); 
  margin-bottom: 12px; 
}
</style>
