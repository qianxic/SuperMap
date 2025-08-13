<script setup lang="ts">
import DashboardLayout from '@/components/Layout/DashboardLayout.vue'
import '@/styles/theme.css'
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

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: rgba(66, 165, 245, 0.5);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(66, 165, 245, 0.7);
}

/* 选择文本样式 */
::selection {
  background: rgba(66, 165, 245, 0.3);
  color: var(--text);
}
</style>
