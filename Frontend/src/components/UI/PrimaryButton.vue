<template>
  <button 
    class="btn"
    :class="[
      variant,
      { active: isActive }
    ]"
    :disabled="disabled"
    @click="handleClick"
  >
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
  disabled: {
    type: Boolean,
    default: false
  },
  active: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

import { computed } from 'vue'

const isActive = computed(() => props.active)

const handleClick = (event: MouseEvent) => {
  if (!props.disabled) {
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
  min-width: 100px;
  flex: 1;
  text-align: center;
  white-space: nowrap;
  font-family: "Segoe UI", PingFang SC, Microsoft YaHei, Arial, sans-serif;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn:hover:not(:disabled) {
  background: var(--surface-hover);
}

.btn:disabled { 
  opacity: 0.4; 
  cursor: not-allowed; 
}

.btn.primary { 
  background: var(--btn-primary-bg); 
  color: var(--btn-primary-color); 
  border-color: var(--btn-primary-bg);
}

.btn.primary:hover:not(:disabled) {
  background: var(--btn-primary-bg);
  opacity: 0.9;
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
  border-color: var(--border);
}

.btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--btn-primary-color);
  box-shadow: 0 2px 8px rgba(var(--accent-rgb), 0.3);
}

.btn.active:hover:not(:disabled) {
  background: var(--accent);
  opacity: 0.9;
}
</style>
