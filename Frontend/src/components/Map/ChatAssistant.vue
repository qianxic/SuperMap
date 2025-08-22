<template>
  <div class="chat-assistant">
    <!-- 聊天记录显示区域 -->
    <div class="messages-container" ref="messagesContainer">
      <!-- 用户消息 -->
      <div v-for="msg in messages" :key="msg.id" class="message-wrapper" :class="msg.sender">
        <div class="avatar" v-if="msg.sender === 'system'">AI</div>
        <div class="message-bubble">
          <div v-if="msg.sender === 'system'" class="message-content" v-html="renderMarkdown(msg.text)"></div>
          <div v-else class="message-content">{{ msg.text }}</div>
        </div>
        <div class="avatar" v-if="msg.sender === 'user'">我</div>
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
import { ref, watch, onMounted, nextTick } from 'vue';
import { useThemeStore } from '@/stores/themeStore';
import LLMInputGroup from '@/components/UI/LLMInputGroup.vue';

interface LayerStatus {
  name: string;
  visible: boolean;
}

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'system';
}

useThemeStore();
const props = defineProps<{
  initialLayers: LayerStatus[];
  mapReady: boolean;
}>();
const messages = ref<Message[]>([]);
const newMessage = ref('');
const hasAnnounced = ref(false);
const messagesContainer = ref<HTMLElement | null>(null);

const scrollToBottom = () => {
  const el = messagesContainer.value;
  if (el) {
    el.scrollTop = el.scrollHeight;
  }
}

const renderMarkdown = (md: string): string => {
  const lines = md.split('\n');
  const htmlParts: string[] = [];
  let inList = false;
  let isFirstLine = true;
  
  for (const rawLine of lines) {
    const line = rawLine.trimEnd();
    if (line.startsWith('- ')) {
      if (!inList) {
        htmlParts.push('<ul>');
        inList = true;
      }
      const item = line.slice(2)
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1<\/strong>');
      htmlParts.push(`<li>${item}<\/li>`);
    } else if (line.length === 0) {
      if (inList) {
        htmlParts.push('<\/ul>');
        inList = false;
      }
      // 跳过空行以减少间距
    } else {
      if (inList) {
        htmlParts.push('<\/ul>');
        inList = false;
      }
      const paragraph = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1<\/strong>');
      // 第一行不添加额外的段落间距
      if (isFirstLine) {
        htmlParts.push(paragraph);
        isFirstLine = false;
      } else {
        htmlParts.push(`<p>${paragraph}<\/p>`);
      }
    }
  }
  if (inList) {
    htmlParts.push('<\/ul>');
  }
  return htmlParts.join('');
}

const formatLayerStatus = (layers: LayerStatus[]): string => {
  if (!layers || layers.length === 0) {
    return '当前无可用图层。';
  }
  const enabled = layers.filter(l => l.visible);
  const disabled = layers.filter(l => !l.visible);
  const enabledLines = enabled.map(l => `- **${l.name}: 开启**`);
  const disabledLines = disabled.map(l => `- ${l.name}: 关闭`);
  const lines = [...enabledLines, ...disabledLines];
  return ['您好！底图初始化完成。图层状态如下:', ...lines].join('\n');
}

const demoMessage = (): string => {
  return [
    '请输入您的需求，我将为您执行。',
    '您可以这样说：',
    '- 打开 道路 图层',
    '- 查询 距您最近的学校',
    '- 统计 距您最近的医院数量',
    '- 进行 缓冲区分析',
    '- 进行 最优路径分析',
    '- 进行 可达性分析'
  ].join('\n');
}

const maybeAnnounceInitialLayers = () => {
  if (props.mapReady && !hasAnnounced.value) {
    messages.value.push({
      id: Date.now(),
      text: formatLayerStatus(props.initialLayers || []),
      sender: 'system'
    });
    messages.value.push({
      id: Date.now() + 1,
      text: demoMessage(),
      sender: 'system'
    });
    hasAnnounced.value = true;
  }
}

onMounted(async () => {
  maybeAnnounceInitialLayers();
  await nextTick();
  scrollToBottom();
});

watch(() => props.mapReady, (ready) => {
  if (ready) {
    maybeAnnounceInitialLayers();
  }
});

watch(messages, async () => {
  await nextTick();
  scrollToBottom();
});

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
  nextTick(() => scrollToBottom());
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

.message-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 0;
  animation: fadeIn 0.3s ease-out;
  user-select: text;
  -webkit-user-select: text;
  -moz-user-select: text;
  -ms-user-select: text;
}

.message-wrapper.user {
  flex-direction: row-reverse;
}

.message-bubble {
  border-radius: 16px;
  padding: 6px 10px;
  margin: 0;
  word-wrap: break-word;
  max-width: 85%;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  background: rgba(255,255,255,0.12);
  border: 1px solid var(--border);
  flex-shrink: 0;
}

.nickname {
  font-size: 12px;
  opacity: 0.8;
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

.message-wrapper.user .message-bubble {
  background: var(--accent);
  color: white;
  box-shadow: 0 3px 12px rgba(var(--accent-rgb), 0.4);
}

.message-wrapper.system .message-bubble {
  background: var(--panel);
  color: var(--text);
  border: 1px solid var(--border);
}

.message-content {
  font-size: 13px;
  line-height: 1.3;
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

.message-wrapper.system .message-content ul {
  margin: 2px 0;
  padding-left: 16px;
}

.message-wrapper.system .message-content p {
  margin: 1px 0;
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
