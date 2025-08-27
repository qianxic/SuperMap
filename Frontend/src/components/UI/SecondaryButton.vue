<template>
  <button 
    class="btn"
    :class="[
      variant,
      { active: isActive, loading: loading }
    ]"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="loading-spinner"></span>
    <slot>{{ text }}</slot>
  </button>
</template>
<!-- 次按钮 -->
<script setup lang="ts">
const props = defineProps({
  text: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'secondary',
    validator: (value: string) => ['primary', 'secondary', 'danger'].includes(value)
  },
  active: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const isActive = props.active

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
.btn { 
  padding: 6px 8px; 
  border: 1px solid var(--border); 
  border-radius: 6px; 
  background: var(--btn-secondary-bg); 
  color: var(--btn-secondary-color); 
  font-size: 12px; 
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 32px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn:hover:not(:disabled) {
  background: var(--btn-secondary-bg);
  border-color: var(--border);
  color: var(--btn-secondary-color);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn.primary { 
  background: var(--btn-primary-bg); 
  color: var(--btn-primary-color); 
  border-color: var(--btn-primary-bg);
}

.btn.primary:hover:not(:disabled) {
  background: var(--btn-primary-bg);
  color: var(--btn-primary-color);
  border-color: var(--btn-primary-bg);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn.secondary {
  background: var(--btn-secondary-bg);
  color: var(--btn-secondary-color);
}

.btn.danger {
  background: var(--surface);
  color: var(--text);
  border-color: var(--border);
}

.btn.danger:hover:not(:disabled) {
  background: var(--surface-hover);
  color: var(--text);
  border-color: var(--border);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn.active {
  background: var(--btn-secondary-bg);
  color: var(--btn-secondary-color);
  border-color: var(--border);
  box-shadow: none;
}

.btn.danger.active {
  background: var(--surface);
  color: var(--text);
  border-color: var(--border);
  box-shadow: none;
}

/* 加载动画 */
.loading-spinner {
  width: 12px;
  height: 12px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.btn.loading {
  cursor: wait;
}
</style>
