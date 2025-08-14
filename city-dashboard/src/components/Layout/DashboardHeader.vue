<template>
  <div class="screen-header">
    <div class="header-left">
      <div class="screen-title">基于大语言模型的智能化城市管理平台</div>
    </div>
    
    <div class="header-right">
      <ButtonGroup
        :buttons="modeButtons"
        :active-button="activeMode"
        @select="setMode"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, provide } from 'vue'
import ButtonGroup from '@/components/UI/ButtonGroup.vue'

// 模式管理 - 使用 provide/inject 或全局状态
const activeMode = ref<'traditional' | 'llm'>('llm');
const modeButtons = [
  { id: 'llm', text: 'LLM 模式' },
  { id: 'traditional', text: '传统模式' },
];

const setMode = (modeId: 'traditional' | 'llm') => {
  activeMode.value = modeId;
  // 触发全局事件，通知其他组件模式变化
  window.dispatchEvent(new CustomEvent('modeChanged', { detail: modeId }));
};

// 提供模式状态给其他组件使用
provide('activeMode', activeMode);


</script>

<style scoped>
.screen-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  letter-spacing: 0.5px;
  background: var(--panel);
  border-bottom: 1px solid var(--border);
  box-shadow: var(--glow);
}

.header-left {
  flex: 1;
}

.screen-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--accent);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.header-left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}


.header-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

@media (max-width: 1200px) {
  .screen-header {
    padding: 0 16px;
  }
  
  .screen-title {
    font-size: 18px;
  }
}
</style>
