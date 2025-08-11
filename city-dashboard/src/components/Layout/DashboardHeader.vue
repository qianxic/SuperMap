<template>
  <div class="screen-header">
    <div class="header-left"></div>
    
    <div class="header-center">
      <div class="screen-title">城市智慧管理平台</div>
    </div>
    
    <div class="header-right">
      <div class="time-display">{{ currentTime }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

// 当前时间
const currentTime = ref<string>('')
const timeTimer = ref<number | null>(null)

// 更新时间显示
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 生命周期
onMounted(() => {
  updateTime()
  timeTimer.value = window.setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeTimer.value) {
    clearInterval(timeTimer.value)
  }
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
  color: var(--text);
}

.header-center {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

.time-display {
  font-size: 14px;
  color: var(--text);
  font-family: 'Consolas', 'Monaco', monospace;
  letter-spacing: 1px;
  padding: 4px 12px;
  background: rgba(255,255,255,0.06);
  border: 1px solid var(--border);
  border-radius: 6px;
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
  
  .time-display {
    font-size: 12px;
  }
  

}
</style>
