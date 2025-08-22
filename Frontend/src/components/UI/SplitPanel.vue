<template>
  <div class="split-panel">
    <splitpanes 
      :class="splitThemeClass" 
      :horizontal="direction === 'horizontal'"
    >
      <pane 
        v-for="(pane, index) in panes" 
        :key="index"
        :size="pane.size"
      >
        <slot :name="`pane-${index}`" :pane="pane">
          <div class="default-pane-content">
            {{ pane.content || `面板 ${index + 1}` }}
          </div>
        </slot>
      </pane>
    </splitpanes>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'

interface PaneConfig {
  size: number;
  content?: string;
}

interface Props {
  direction?: 'horizontal' | 'vertical';
  panes: PaneConfig[];
  theme?: 'default' | 'chat' | 'custom';
  splitterSize?: number;
  showHandle?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  direction: 'vertical',
  theme: 'default',
  splitterSize: 5,
  showHandle: true
})

const splitThemeClass = computed(() => {
  return `${props.theme}-split-theme`
})
</script>

<style>
/* 默认分割主题样式 */
.default-split-theme .splitpanes__pane {
  background-color: transparent !important;
}

.default-split-theme .splitpanes__splitter {
  background-color: transparent !important;
  position: relative;
  width: 5px !important;
  height: 5px !important;
  border: none !important;
  transition: background-color 0.2s ease-in-out;
}

.default-split-theme .splitpanes__splitter:before {
  content: '';
  position: absolute;
  left: -2px;
  top: -2px;
  width: 10px;
  height: 10px;
  background: transparent;
  z-index: 1;
  transition: background-color 0.2s ease-in-out;
}



.default-split-theme .splitpanes__splitter:hover {
  background-color: var(--accent) !important;
}

/* 聊天分割主题样式 */
.chat-split-theme .splitpanes__pane {
  background-color: transparent !important;
  min-height: 0 !important;
  min-width: 0 !important;
}

.chat-split-theme .splitpanes__splitter {
  background-color: transparent !important;
  position: relative;
  height: 5px !important;
  border: none !important;
  transition: background-color 0.2s ease-in-out;
  z-index: 10 !important;
}

.chat-split-theme .splitpanes__splitter:before {
  content: '';
  position: absolute;
  top: -1px;
  left: 0;
  width: 100%;
  height: 6px;
  background: transparent;
  z-index: 1;
  transition: background-color 0.2s ease-in-out;
}

.chat-split-theme .splitpanes__splitter:after {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 4px;
  border-radius: 2px;
  background: var(--border);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  z-index: 2;
}

.chat-split-theme .splitpanes__splitter:hover:after {
  background: var(--border);
}

.chat-split-theme .splitpanes__splitter:hover:before {
  background-color: transparent !important;
}

.chat-split-theme .splitpanes__splitter:hover {
  background-color: transparent !important;
}

/* 自定义分割主题样式 */
.custom-split-theme .splitpanes__pane {
  background-color: transparent !important;
}

.custom-split-theme .splitpanes__splitter {
  background-color: transparent !important;
  position: relative;
  width: 5px !important;
  height: 5px !important;
  border: none !important;
  transition: background-color 0.2s ease-in-out;
}

.custom-split-theme .splitpanes__splitter:before {
  content: '';
  position: absolute;
  left: -2px;
  top: -2px;
  width: 10px;
  height: 10px;
  background: transparent;
  z-index: 1;
  transition: background-color 0.2s ease-in-out;
}



.custom-split-theme .splitpanes__splitter:hover {
  background-color: var(--accent) !important;
}
</style>

<style scoped>
.split-panel {
  height: 100%;
  width: 100%;
  overflow: hidden;
}

.default-pane-content {
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--sub);
  font-size: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border);
  border-radius: 8px;
}
</style>
