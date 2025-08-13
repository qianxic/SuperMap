<template>
  <textarea 
    v-if="as === 'textarea'"
    :value="modelValue"
    @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
    :placeholder="placeholder"
    :rows="rows"
    :disabled="disabled"
    @keyup.enter.exact="$emit('enter')"
    class="input-element"
  />
  <input 
    v-else
    :value="modelValue"
    @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    :type="type"
    :placeholder="placeholder"
    :disabled="disabled"
    @keyup.enter="$emit('enter')"
    class="input-element"
  />
</template>

<script setup lang="ts">
interface Props {
  modelValue?: string;
  placeholder?: string;
  as?: 'input' | 'textarea';
  type?: string;
  rows?: number;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '',
  as: 'input',
  type: 'text',
  rows: 1,
  disabled: false
});

defineEmits(['update:modelValue', 'enter']);
</script>

<style scoped>
/* 输入元素样式 */
.input-element {
  flex: 1;
  font-size: 14px;
  padding: 6px 8px;
  background: transparent;
  border: none;
  color: var(--text);
  outline: none;
  font-family: inherit;
  resize: none;
  min-height: auto;
  max-height: none;
  overflow: hidden;
  box-sizing: border-box;
}

.input-element::placeholder {
  color: var(--sub);
  opacity: 0.7;
}

.input-element[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 隐藏textarea滚动条 */
.input-element {
  scrollbar-width: none !important; /* Firefox */
  -ms-overflow-style: none !important; /* IE and Edge */
}

.input-element::-webkit-scrollbar {
  display: none !important; /* Chrome, Safari, Opera */
}
</style>
