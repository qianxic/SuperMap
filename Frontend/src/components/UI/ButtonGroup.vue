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
}

button.active {
  background-color: var(--accent);
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 120, 212, 0.3);
}

button:not(.active):hover {
  color: var(--text);
}
</style>
