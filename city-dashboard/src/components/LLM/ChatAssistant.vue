<template>
  <div class="chat-assistant">
    <SplitPanel 
      direction="horizontal"
      theme="chat"
      :panes="[
        { size: 80 },
        { size: 20 }
      ]"
    >
      <!-- 聊天记录显示区域 -->
      <template #pane-0>
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
      </template>
      
      <!-- 输入区域 -->
      <template #pane-1>
        <div class="input-container">
          <InputGroup
            v-model="newMessage"
            placeholder="请输入您的需求..."
            as="textarea"
            :rows="1"
            @enter="sendMessage"
          />
          <button class="action-button" @click="sendMessage" :disabled="!newMessage.trim()">
            <!-- 这里可以使用图标 -->
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
          </button>
        </div>
      </template>
    </SplitPanel>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import InputGroup from '@/components/UI/InputGroup.vue';
import SplitPanel from '@/components/UI/SplitPanel.vue';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'system';
}

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
  overflow: hidden;
  padding: 4px;
  display: flex;
  flex-direction: column;
}

.messages-container {
  height: 100%;
  overflow-y: auto;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: all 0.3s ease;
  animation: fadeIn 0.3s ease-out;
}

.messages-container:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(66, 165, 245, 0.3);
  box-shadow: 0 4px 16px rgba(66, 165, 245, 0.1);
}

.input-container {
  height: 100%;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border);
  border-radius: 16px;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
  animation: fadeIn 0.3s ease-out;
}

.input-container :deep(.input-element) {
  height: 100%;
  min-height: 100%;
  max-height: 100%;
  resize: none;
  overflow: hidden;
  padding-right: 44px;
}

.input-container:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(66, 165, 245, 0.3);
  box-shadow: 0 4px 16px rgba(66, 165, 245, 0.1);
}

/* 自定义滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: rgba(66, 165, 245, 0.4);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: rgba(66, 165, 245, 0.6);
}

.message {
  border-radius: 16px;
  padding: 10px 14px;
  margin: 0;
  word-wrap: break-word;
  animation: fadeIn 0.3s ease-out;
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
  background: linear-gradient(135deg, var(--accent) 0%, rgba(66, 165, 245, 0.9) 100%);
  color: white;
  align-self: flex-end;
  margin-left: auto;
  box-shadow: 0 3px 12px rgba(66, 165, 245, 0.4);
}

.message.system {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text);
  align-self: flex-start;
  border: 1px solid var(--border);
}

.message-content {
  font-size: 13px;
  line-height: 1.5;
  margin: 0;
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
  transition: all 0.2s ease;
  flex-shrink: 0;
  position: absolute;
  bottom: 8px;
  right: 8px;
  z-index: 10;
}

.action-button:hover:not(:disabled) {
  background: rgba(66, 165, 245, 0.9);
  transform: scale(1.05);
}

.action-button:active:not(:disabled) {
  transform: translateY(0);
}

.action-button:disabled {
  background: rgba(66, 165, 245, 0.3);
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
