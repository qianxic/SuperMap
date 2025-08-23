<template>
  <button 
    :class="['icon-button', size, { 'disabled': disabled }]"
    :title="title"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <slot></slot>
  </button>
</template>

<script setup lang="ts">
interface Props {
  size?: 'small' | 'medium' | 'large'
  title?: string
  disabled?: boolean
}

withDefaults(defineProps<Props>(), {
  size: 'medium',
  title: '',
  disabled: false
})

defineEmits<{
  click: [event: MouseEvent]
}>()
</script>

<style scoped>
.icon-button {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--panel);
  color: var(--text);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: none;
  outline: none;
}

.icon-button:hover:not(.disabled) {
  background: var(--surface-hover, var(--btn-secondary-bg));
  transform: translateY(-1px);
  box-shadow: var(--glow);
}

.icon-button:active:not(.disabled) {
  transform: translateY(0);
}

.icon-button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 尺寸变体 */
.icon-button.small {
  width: 28px;
  height: 28px;
}

.icon-button.small :deep(svg) {
  width: 14px;
  height: 14px;
}

.icon-button.medium {
  width: 36px;
  height: 36px;
}

.icon-button.medium :deep(svg) {
  width: 18px;
  height: 18px;
}

.icon-button.large {
  width: 44px;
  height: 44px;
}

.icon-button.large :deep(svg) {
  width: 22px;
  height: 22px;
}

/* 图标样式 */
.icon-button :deep(svg) {
  stroke: var(--text);
  fill: none;
  stroke-width: 2;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .icon-button.small {
    width: 24px;
    height: 24px;
  }
  
  .icon-button.small :deep(svg) {
    width: 12px;
    height: 12px;
  }
  
  .icon-button.medium {
    width: 32px;
    height: 32px;
  }
  
  .icon-button.medium :deep(svg) {
    width: 16px;
    height: 16px;
  }
  
  .icon-button.large {
    width: 40px;
    height: 40px;
  }
  
  .icon-button.large :deep(svg) {
    width: 20px;
    height: 20px;
  }
}
</style>
