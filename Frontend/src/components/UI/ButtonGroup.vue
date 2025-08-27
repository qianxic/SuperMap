<template>
  <div class="button-group">
    <button
      v-for="btn in buttons"
      :key="btn.id"
      :class="{ 'active': activeButton === btn.id }"
      @click="$emit('select', btn.id)"
    >
      {{ btn.text }}
    </button>
  </div>
</template>

<script setup lang="ts">
interface Button {
  id: string;
  text: string;
}

defineProps<{
  buttons: Button[];
  activeButton: string;
}>();

defineEmits(['select']);
</script>

<style scoped>
.button-group {
  display: flex;
  background-color: var(--btn-secondary-bg);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  padding: 4px;
  width: fit-content;
}

button {
  padding: 6px 16px;
  border: none;
  background-color: transparent;
  color: var(--sub);
  cursor: pointer;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  font-family: "Segoe UI", PingFang SC, Microsoft YaHei, Arial, sans-serif;
  transition: all 0.2s ease;
}

button.active {
  background-color: var(--accent);
  color: var(--btn-primary-color);
  box-shadow: 0 2px 8px rgba(var(--accent-rgb), 0.3);
}

button:not(.active):hover {
  color: var(--text);
  background-color: var(--surface-hover);
}
</style>
