<template>
  <div class="button-group" :class="{ inline: layout === 'inline' }">
    <slot></slot>
  </div>
</template>
<!-- 按钮组 -->
<script setup lang="ts">
const props = defineProps({
  layout: {
    type: String,
    default: 'block',
    validator: (value) => ['block', 'inline'].includes(value)
  },
  columns: {
    type: Number,
    default: 3
  },
  gap: {
    type: String,
    default: '8px'
  }
})
</script>

<style scoped>
.button-group {
  display: grid;
  gap: v-bind(gap);
  margin-bottom: 8px;
}

.button-group:not(.inline) {
  grid-template-columns: repeat(v-bind(columns), 1fr);
}

.button-group.inline {
  grid-template-columns: auto;
  grid-auto-flow: column;
}

.button-group :deep(.btn) {
  margin-right: 0;
}

.button-group.inline :deep(.btn) {
  margin-right: 8px;
}

.button-group.inline :deep(.btn:last-child) {
  margin-right: 0;
}
</style>
