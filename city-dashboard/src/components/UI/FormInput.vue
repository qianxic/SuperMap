<template>
  <div class="form-item">
    <label v-if="label" class="form-label">{{ label }}</label>
    <input 
      :value="modelValue"
      @input="$emit('update:modelValue', getInputValue($event))"
      :type="type"
      :min="min"
      :max="max"
      :step="step"
      :placeholder="placeholder"
      :disabled="disabled"
      class="form-input"
      v-bind="$attrs"
    />
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, defineOptions } from 'vue'

defineOptions({
  inheritAttrs: false
})

type InputType = 'text' | 'number' | 'email' | 'password' | 'tel';

interface Props {
  modelValue?: string | number;
  label?: string;
  type?: InputType;
  min?: string | number;
  max?: string | number;
  step?: string | number;
  placeholder?: string;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  label: '',
  type: 'text',
  placeholder: '',
  disabled: false
})

defineEmits(['update:modelValue'])

const getInputValue = (event: Event): string | number | null => {
  const target = event.target as HTMLInputElement;
  const value = target.value;
  if (props.type === 'number') {
    return value === '' ? null : Number(value);
  }
  return value;
}
</script>

<style scoped>
.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.form-label {
  font-size: 12px;
  color: var(--sub);
  font-weight: 500;
}

.form-input {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text);
  font-size: 13px;
  outline: none;
  transition: all 0.2s ease;
}

.form-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 2px rgba(66, 165, 245, 0.2);
}

.form-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: rgba(255, 255, 255, 0.04);
}

.form-input::placeholder {
  color: var(--sub);
  opacity: 0.7;
}

/* 隐藏数字输入框的上下箭头 */
.form-input[type="number"]::-webkit-outer-spin-button,
.form-input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.form-input[type="number"] {
  -moz-appearance: textfield;
  appearance: textfield;
}
</style>
