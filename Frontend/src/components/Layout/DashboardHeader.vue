<template>
  <div class="screen-header">
    <div class="header-left">
      <div class="screen-title">基于大语言模型的智能化城市管理平台</div>
    </div>
    
    <div class="header-right">
      <div class="theme-toggle">
        <button 
          @click="toggleTheme" 
          class="theme-btn"
          :title="theme === 'light' ? '切换到暗色主题' : '切换到浅色主题'"
        >
          <!-- 浅色主题图标 (太阳) -->
          <svg v-if="theme === 'light'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="5"/>
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
          <!-- 暗色主题图标 (月亮) -->
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        </button>
      </div>
      
      <ButtonGroup
        :buttons="modeButtons"
        :active-button="activeMode"
        @select="setMode"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, provide, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import ButtonGroup from '@/components/UI/ButtonGroup.vue'
import { useThemeStore } from '@/stores/themeStore'

// 主题管理
const themeStore = useThemeStore()
const { theme } = storeToRefs(themeStore)
const { toggleTheme, applySystemTheme, setupSystemThemeListener } = themeStore

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

// 初始化主题
onMounted(() => {
  applySystemTheme()
  setupSystemThemeListener()
})

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
  gap: 16px;
}

.theme-toggle {
  display: flex;
  align-items: center;
}

.theme-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--panel);
  color: var(--text);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.theme-btn:hover {
  background: var(--surface-hover, var(--btn-secondary-bg));
  transform: translateY(-1px);
  box-shadow: var(--glow);
}

.theme-btn svg {
  width: 18px;
  height: 18px;
  stroke: var(--text);
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
