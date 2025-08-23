<template>
  <div class="dashboard">
    <!-- 主要内容区域 -->
    <main class="dashboard-main">
      <DashboardLayout />
    </main>
  </div>
</template>

<script setup lang="ts">
import DashboardLayout from '@/components/Layout/DashboardLayout.vue'
</script>

<style scoped>
.dashboard {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}

.dashboard-main {
  flex: 1;
  overflow: hidden;
  position: relative;
}
</style>
