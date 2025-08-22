<template>
  <div class="chat-assistant">
    <!-- 聊天记录显示区域 -->
    <div class="messages-container">
      <!-- 系统欢迎消息 -->
      <div class="message system">
        <div class="message-content">您好！请输入您的需求，我将为您执行。</div>
      </div>
      <!-- 用户消息 -->
      <div v-for="msg in messages" :key="msg.id" class="message" :class="msg.sender">
        <div class="message-content">{{ msg.text }}</div>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div class="input-container">
      <LLMInputGroup
        v-model="newMessage"
        placeholder="请输入您的需求..."
        as="textarea"
        :rows="3"
        @enter="sendMessage"
      />
      <button class="action-button" @click="sendMessage" :disabled="!newMessage.trim()">
        <!-- 这里可以使用图标 -->
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useThemeStore } from '@/stores/themeStore';
import LLMInputGroup from '@/components/UI/LLMInputGroup.vue';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'system';
}

const themeStore = useThemeStore();
const messages = ref<Message[]>([]);
const newMessage = ref('');

const sendMessage = () => {
  if (!newMessage.value.trim()) return;

  messages.value.push({
    id: Date.now(),
    text: newMessage.value,
    sender: 'user'
  });

  // 在这里可以添加调用大模型API的逻辑
  // 例如: const response = await callLLMApi(newMessage.value);
  // ...然后将模型的回复添加到 messages 数组中

  newMessage.value = '';
};
</script>



<style scoped>
.chat-assistant {
  height: 100%;
  width: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
  flex: 1;
}

.messages-container {
  flex: 1;
  width: 100%;
  overflow-y: auto;
  padding: 12px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  gap: 10px;
  animation: fadeIn 0.3s ease-out;
  min-height: 120px;
  margin-bottom: 8px;
  user-select: text;
  -webkit-user-select: text;
  -moz-user-select: text;
  -ms-user-select: text;
}



.input-container {
  width: 100%;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  position: relative;
  z-index: 1;
  animation: fadeIn 0.3s ease-out;
  margin-top: 8px;
}





/* 自定义滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 3px;
  height: 1.5px;
}

.messages-container::-webkit-scrollbar-track {
  background: var(--scrollbar-track, rgba(200, 200, 200, 0.1));
  border-radius: 1.5px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb, rgba(150, 150, 150, 0.3));
  border-radius: 1.5px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: var(--scrollbar-thumb-hover, rgba(150, 150, 150, 0.5));
}

.message {
  border-radius: 16px;
  padding: 10px 14px;
  margin: 0;
  word-wrap: break-word;
  animation: fadeIn 0.3s ease-out;
  user-select: text;
  -webkit-user-select: text;
  -moz-user-select: text;
  -ms-user-select: text;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  max-width: 85%;
  background: var(--accent);
  color: white;
  align-self: flex-end;
  margin-left: auto;
  box-shadow: 0 3px 12px rgba(var(--accent-rgb), 0.4);
}

.message.system {
  background: var(--panel);
  color: var(--text);
  align-self: flex-start;
  border: 1px solid var(--border);
}

.message-content {
  font-size: 13px;
  line-height: 1.5;
  margin: 0;
  color: inherit;
  font-family: "Segoe UI", PingFang SC, Microsoft YaHei, Arial, sans-serif;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  user-select: text;
  -webkit-user-select: text;
  -moz-user-select: text;
  -ms-user-select: text;
  cursor: text;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent);
  border: none;
  color: white;
  cursor: pointer;
  flex-shrink: 0;
  position: absolute;
  bottom: 8px;
  right: 8px;
  z-index: 10;
}

.action-button:hover {
  background: var(--surface-hover);
  transform: scale(1.05);
}



.action-button:active:not(:disabled) {
  transform: translateY(0);
}

.action-button:disabled {
  background: rgba(0, 123, 255, 0.3);
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
