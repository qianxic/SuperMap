<script setup lang="ts">
import DashboardLayout from '@/components/Layout/DashboardLayout.vue'
</script>

<template>
  <DashboardLayout />
</template>

<style>
/* 全局CSS变量 */
:root {
  --bg: #0b1221;
  --panel: #111b33;
  --border: rgba(66, 133, 244, 0.35);
  --glow: 0 0 0 1px rgba(66, 133, 244, 0.25), 0 0 20px rgba(66, 133, 244, 0.15) inset;
  --text: #e6f1ff;
  --sub: #8aa2c2;
  --accent: #42a5f5;
  --header-h: 64px;
  --gap: 16px;
  --radius: 10px;
}

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
