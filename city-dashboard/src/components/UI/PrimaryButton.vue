<template>
  <button 
    class="primary-btn"
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
<!-- 主按钮 -->
<script setup lang="ts">
const props = defineProps({
  text: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary'].includes(value)
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

const isActive = props.active

const handleClick = (event) => {
  if (!props.disabled) {
    emit('click', event)
  }
}
</script>

<style scoped>
.primary-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.primary-btn.primary { 
  background: var(--btn-primary-bg); 
  color: var(--btn-primary-color); 
  box-shadow: inset 0 0 12px rgba(59,130,246,.5); 
}

.primary-btn.primary:hover:not(:disabled) {
  background: #1976d2;
  box-shadow: inset 0 0 16px rgba(59,130,246,.7);
}

.primary-btn.secondary { 
  background: var(--btn-secondary-bg); 
  color: var(--btn-secondary-color); 
  border: 1px solid var(--border); 
}

.primary-btn.secondary:hover:not(:disabled) {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}

.primary-btn:disabled { 
  opacity: 0.6; 
  cursor: not-allowed; 
}

.primary-btn.active {
  transform: scale(0.98);
}
</style>
