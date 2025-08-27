<template>
  <div class="chat-assistant">
    <!-- 功能按钮固定在聊天容器外部 -->
    <div class="fixed-buttons">
      <!-- 新对话按钮 -->
      <IconButton 
        class="new-chat-button" 
        size="medium"
        :title="'开启新对话'"
        @click="startNewConversation"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 5v14M5 12h14"/>
        </svg>
        <span class="button-text">新对话</span>
      </IconButton>
      
      <!-- 历史记录按钮 -->
      <IconButton 
        class="history-button" 
        size="medium"
        :title="'查看历史聊天记录'"
        @click="showChatHistory"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <span class="button-text">历史</span>
      </IconButton>
    </div>
    
    <!-- 聊天记录显示区域 -->
    <div class="messages-container" ref="messagesContainer" @scroll="handleScroll">
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
import { ref, watch, onMounted, nextTick, onUnmounted } from 'vue';
import { useThemeStore } from '@/stores/themeStore';
import { useModeStateStore } from '@/stores/modeStateStore';
import LLMInputGroup from '@/components/UI/LLMInputGroup.vue';
import IconButton from '@/components/UI/IconButton.vue';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'system';
}

useThemeStore();
const modeStateStore = useModeStateStore();

const props = defineProps<{
  mapReady: boolean;
}>();
const messages = ref<Message[]>([]);
const newMessage = ref('');
const hasAnnounced = ref(false);
const messagesContainer = ref<HTMLElement | null>(null);

// 新增：智能滚动相关状态
const isNearBottom = ref(true);
const isUserScrolling = ref(false);
const scrollThreshold = 100; // 滚动阈值（像素）
const scrollTimeout = ref<number | null>(null);

// 检测滚动位置
const checkScrollPosition = () => {
  const el = messagesContainer.value;
  if (!el) return;
  
  const { scrollTop, scrollHeight, clientHeight } = el;
  const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
  isNearBottom.value = distanceFromBottom <= scrollThreshold;
};

// 判断是否应该自动滚动
const shouldAutoScroll = (): boolean => {
  return isNearBottom.value && !isUserScrolling.value;
};

// 平滑滚动到底部
const smoothScrollToBottom = () => {
  const el = messagesContainer.value;
  if (!el) return;
  
  // 使用 scrollIntoView 实现平滑滚动
  const lastMessage = el.lastElementChild;
  if (lastMessage) {
    lastMessage.scrollIntoView({
      behavior: 'smooth',
      block: 'end',
      inline: 'nearest'
    });
  }
};

// 处理滚动事件
const handleScroll = () => {
  checkScrollPosition();
  
  // 清除之前的定时器
  if (scrollTimeout.value) {
    clearTimeout(scrollTimeout.value);
  }
  
  // 设置用户正在滚动的状态
  isUserScrolling.value = true;
  
  // 500ms 后重置滚动状态
  scrollTimeout.value = window.setTimeout(() => {
    isUserScrolling.value = false;
  }, 500);
};

// 优化的滚动到底部函数
const scrollToBottom = () => {
  if (shouldAutoScroll()) {
    smoothScrollToBottom();
  }
};

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
};

const demoMessage = (): string => {
  return [
    '请输入您的需求，我将为您执行。',
    '您可以这样说：',
    '- 打开 道路 图层',
    '- 查询 距我最近的学校',
    '- 统计 距我最近的医院数量',
    '- 进行 缓冲区分析',
    '- 进行 最优路径分析',
    '- 进行 可达性分析'
  ].join('\n');
}

const maybeAnnounceInitialLayers = () => {
  if (props.mapReady && !hasAnnounced.value) {
    messages.value.push({
      id: Date.now() + 2,
      text: demoMessage(),
      sender: 'system'
    });
    hasAnnounced.value = true;
    
    // 智能滚动到初始消息
    nextTick(() => {
      smoothScrollToBottom();
      checkScrollPosition();
    });
  }
}

onMounted(async () => {
  // 恢复LLM模式状态
  const llmState = modeStateStore.getLLMState()
  if (llmState.messages.length > 0) {
    messages.value = [...llmState.messages]
    hasAnnounced.value = true
  }
  if (llmState.inputText) {
    newMessage.value = llmState.inputText
  }
  
  // 如果没有恢复的状态，则显示初始消息
  if (messages.value.length === 0) {
    maybeAnnounceInitialLayers();
  }
  
  await nextTick();
  
  // 初始化滚动位置检测
  checkScrollPosition();
  
  // 恢复滚动位置
  if (llmState.scrollPosition > 0) {
    setTimeout(() => {
      const el = messagesContainer.value;
      if (el) {
        el.scrollTop = llmState.scrollPosition;
        checkScrollPosition(); // 重新检测滚动位置
      }
    }, 100);
  } else {
    // 如果没有保存的滚动位置，滚动到底部
    smoothScrollToBottom();
  }
});

// 保存LLM模式状态
const saveLLMState = () => {
  const scrollPosition = messagesContainer.value?.scrollTop || 0;
  modeStateStore.saveLLMState({
    messages: messages.value,
    inputText: newMessage.value,
    scrollPosition
  });
};

// 组件卸载时保存状态和清理定时器
onUnmounted(() => {
  saveLLMState();
  // 清理定时器
  if (scrollTimeout.value) {
    clearTimeout(scrollTimeout.value);
  }
});

// 监听状态变化，自动保存
watch([messages, newMessage], () => {
  saveLLMState();
}, { deep: true });

watch(() => props.mapReady, (ready) => {
  if (ready) {
    maybeAnnounceInitialLayers();
  }
});

watch(messages, async () => {
  await nextTick();
  // 使用智能滚动逻辑
  if (shouldAutoScroll()) {
    smoothScrollToBottom();
  }
  checkScrollPosition();
}, { deep: true });

// 发送消息
const sendMessage = () => {
  const message = newMessage.value.trim();
  if (!message) return;

  // 添加用户消息
  messages.value.push({
    id: Date.now(),
    text: message,
    sender: 'user'
  });

  // 处理用户输入并生成AI响应
  const userInput = message.toLowerCase();
  
  let aiResponse = `我理解您的需求："${message}"，正在处理中...`;
  
  // 添加AI响应
  messages.value.push({
    id: Date.now() + 1,
    text: aiResponse,
    sender: 'system'
  });

  newMessage.value = '';
  
  // 使用智能滚动逻辑
  nextTick(() => {
    if (shouldAutoScroll()) {
      smoothScrollToBottom();
    }
    checkScrollPosition();
  });
};

// 显示历史聊天记录
const showChatHistory = () => {
  // 获取保存的聊天历史记录
  const savedChatHistory = localStorage.getItem('chatHistory') || '[]';
  const chatHistory = JSON.parse(savedChatHistory);
  
  if (chatHistory.length === 0) {
    window.dispatchEvent(new CustomEvent('showNotification', {
      detail: {
        title: '聊天历史',
        message: '暂无历史聊天记录',
        type: 'info',
        duration: 3000
      }
    }));
    return;
  }
  
  // 格式化历史记录显示 - 每次对话一行，按时间倒序排列
  const historyText = chatHistory
    .sort((a: any, b: any) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()) // 按时间倒序
    .map((record: any, index: number) => {
      const date = new Date(record.timestamp).toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
      const messageCount = record.messages ? record.messages.length : 0;
      const firstMessage = record.messages && record.messages.length > 0 
        ? record.messages[0].text.substring(0, 20) + (record.messages[0].text.length > 20 ? '...' : '')
        : '空对话';
      return `${index + 1}. ${date} | ${messageCount}条消息 | ${firstMessage}`;
    })
    .join('\n');
  
  // 显示历史记录
  window.dispatchEvent(new CustomEvent('showNotification', {
    detail: {
      title: `历史聊天记录 (共${chatHistory.length}次对话)`,
      message: historyText,
      type: 'info',
      duration: 10000
    }
  }));
};

// 新增：开启新对话功能
const startNewConversation = () => {
  // 保存当前对话到历史记录
  if (messages.value.length > 0) {
    const savedChatHistory = localStorage.getItem('chatHistory') || '[]';
    const chatHistory = JSON.parse(savedChatHistory);
    
    const currentChat = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      messages: [...messages.value],
      messageCount: messages.value.length
    };
    
    chatHistory.push(currentChat);
    
    // 限制历史记录数量，最多保存20条
    if (chatHistory.length > 20) {
      chatHistory.splice(0, chatHistory.length - 20);
    }
    
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
  }
  
  // 清空消息历史
  messages.value = [];
  // 清空输入框
  newMessage.value = '';
  // 重置状态
  hasAnnounced.value = false;
  
  // 重新显示初始消息
  maybeAnnounceInitialLayers();
  
  // 清空保存的状态
  modeStateStore.saveLLMState({
    messages: [],
    inputText: '',
    scrollPosition: 0
  });
  
  // 滚动到顶部
  nextTick(() => {
    smoothScrollToBottom();
    checkScrollPosition();
  });
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
  /* 设置相对定位，为固定按钮提供定位上下文 */
  position: relative;
}

.fixed-buttons {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 20;
  /* 确保按钮完全脱离文档流，不占用空间 */
  pointer-events: auto;
  display: flex;
  gap: 8px;
  flex-direction: column;
}

.messages-container {
  flex: 1;
  width: 100%;
  overflow-y: auto;
  padding: 8px 6px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  display: flex;
  flex-direction: column;
  gap: 10px;
  animation: none; /* 禁用动画，防止主题切换闪烁 */
  min-height: 120px;
  margin-bottom: 8px;
  user-select: text;
  -webkit-user-select: text;
  -moz-user-select: text;
  -ms-user-select: text;
  /* 添加平滑滚动 */
  scroll-behavior: smooth;
  /* 优化滚动性能 */
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  /* 移除顶部内边距，因为按钮使用绝对定位不会占用空间 */
}


.history-button,
.new-chat-button {
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  padding: 6px 12px !important;
  width: auto !important;
  height: auto !important;
  /* 浮动按钮效果 - 确保完全浮动 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
  backdrop-filter: blur(8px) !important;
  background: rgba(var(--panel-rgb), 0.9) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  transition: all 0.2s ease !important;
}

.history-button:hover,
.new-chat-button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
  background: rgba(var(--panel-rgb), 0.95) !important;
  border-color: var(--accent) !important;
}

.history-button:active,
.new-chat-button:active {
  transform: translateY(0) !important;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15) !important;
}

.history-button .button-text,
.new-chat-button .button-text {
  font-size: 12px !important;
  font-weight: 500 !important;
  color: var(--text) !important;
  margin-left: 2px !important;
  white-space: nowrap !important;
}

.history-button svg,
.new-chat-button svg {
  flex-shrink: 0 !important;
  width: 14px !important;
  height: 14px !important;
  color: var(--text) !important;
  stroke-width: 2 !important;
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
  animation: none; /* 禁用动画，防止主题切换闪烁 */
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
  gap: 6px;
  margin: 0;
  animation: none; /* 禁用动画，防止主题切换闪烁 */
  user-select: text;
  -webkit-user-select: text;
  -moz-user-select: text;
  -ms-user-select: text;
}

.message-wrapper.user {
  flex-direction: row;
  gap: 4px;
  justify-content: flex-end;
  align-items: flex-end;
}

.message-bubble {
  border-radius: 16px;
  padding: 6px 10px;
  margin: 0;
  word-wrap: break-word;
  max-width: 95%;
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

/* 保留fadeIn动画定义但不使用 */
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

.chat-message {
  margin-bottom: 16px;
  padding: 12px;
  border-radius: 8px;
  /* 禁用动画，防止主题切换闪烁 */
  animation: none !important;
}

.user-message {
  background: var(--accent);
  color: white;
  margin-left: 20%;
  /* 禁用动画，防止主题切换闪烁 */
  animation: none !important;
}

.assistant-message {
  background: var(--surface);
  border: 1px solid var(--border);
  margin-right: 20%;
  /* 禁用动画，防止主题切换闪烁 */
  animation: none !important;
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
  font-family: "Times New Roman", "SimSun", serif;
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
