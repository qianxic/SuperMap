<script setup lang="ts">
import { onMounted } from 'vue'
import DashboardLayout from '@/components/Layout/DashboardLayout.vue'
import { useThemeStore } from '@/stores/themeStore'
import '@/styles/theme.css'

// 确保主题在应用启动时正确初始化
const themeStore = useThemeStore()

onMounted(() => {
  themeStore.applySystemTheme()
  themeStore.setupSystemThemeListener()
})
</script>

<template>
  <DashboardLayout />
</template>

<style>
/* 全局样式重置 */
* {
  box-sizing: border-box;
}

html, body {
  height: 100%;
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--text);
  font-family: "Segoe UI", PingFang SC, Microsoft YaHei, Arial, sans-serif;
  overflow: hidden;
}

#app {
  height: 100vh;
  width: 100vw;
}

/* 滚动条样式 - 支持主题切换 */
::-webkit-scrollbar {
  width: 3px;
  height: 1.5px;
}

::-webkit-scrollbar-track {
  background: var(--scrollbar-track, rgba(200, 200, 200, 0.1));
  border-radius: 1.5px;
}

::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb, rgba(150, 150, 150, 0.3));
  border-radius: 1.5px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--scrollbar-thumb-hover, rgba(150, 150, 150, 0.5));
}

/* 选择文本样式 - 支持主题切换 */
::selection {
  background: var(--selection-bg, rgba(66, 165, 245, 0.3));
  color: var(--text);
}
</style>
