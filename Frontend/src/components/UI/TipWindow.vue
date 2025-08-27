<template>
  <div class="tip-window" :class="{ 'tip-visible': visible }">
    <div class="tip-content">
      <div class="tip-icon" v-if="showIcon">
        <slot name="icon">
          <span class="default-icon">💡</span>
        </slot>
      </div>
      <div class="tip-text">
        <slot>{{ text }}</slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  text?: string
  visible?: boolean
  showIcon?: boolean
  variant?: 'info' | 'warning' | 'success' | 'error'
}

const props = withDefaults(defineProps<Props>(), {
  text: '',
  visible: true,
  showIcon: false,
  variant: 'info'
})

const tipClass = computed(() => {
  return {
    'tip-info': props.variant === 'info',
    'tip-warning': props.variant === 'warning',
    'tip-success': props.variant === 'success',
    'tip-error': props.variant === 'error'
  }
})
</script>

<style scoped>
.tip-window {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text);
  padding: 12px;
  background: rgba(66, 165, 245, 0.08);
  border-radius: 12px;
  border-left: 4px solid var(--accent);
  /* 禁用动画，防止主题切换闪烁 */
  animation: none !important;
  opacity: 1;
  transform: translateY(0);
}

.tip-window.tip-visible {
  opacity: 1;
  transform: translateY(0);
}

.tip-content {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.tip-icon {
  flex-shrink: 0;
  font-size: 14px;
  line-height: 1;
}

.tip-text {
  flex: 1;
  line-height: 1.4;
}

/* 变体样式 */
.tip-info {
  background: rgba(66, 165, 245, 0.08);
  border-left-color: var(--accent);
  color: var(--text);
}

.tip-warning {
  background: rgba(255, 193, 7, 0.08);
  border-left-color: #ffc107;
  color: var(--text);
}

.tip-success {
  background: rgba(40, 167, 69, 0.08);
  border-left-color: #28a745;
  color: var(--text);
}

.tip-error {
  background: rgba(220, 53, 69, 0.08);
  border-left-color: #dc3545;
  color: var(--text);
}

/* 保留fadeIn动画定义但不使用 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
