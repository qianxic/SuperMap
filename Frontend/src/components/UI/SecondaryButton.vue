<template>
  <button 
    class="btn"
    :class="[
      variant,
      { active: isActive }
    ]"
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
  active: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const isActive = props.active

const handleClick = (event: MouseEvent) => {
  emit('click', event)
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
}

.btn:hover {
  background: var(--btn-secondary-bg);
  border-color: var(--border);
  color: var(--btn-secondary-color);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn.primary { 
  background: var(--accent); 
  color: white; 
  border-color: var(--accent);
}

.btn.primary:hover {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn.secondary {
  background: var(--btn-secondary-bg);
  color: var(--btn-secondary-color);
}

.btn.danger {
  background: #ff4757;
  color: white;
  border-color: #ff4757;
}

.btn.danger:hover {
  background: #ff3742;
  color: white;
  border-color: #ff3742;
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
  background: #ff4757;
  color: white;
  border-color: #ff4757;
  box-shadow: none;
}
</style>
