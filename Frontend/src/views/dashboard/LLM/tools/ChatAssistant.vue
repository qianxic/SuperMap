<template>
  <div class="chat-assistant">
    <!-- 新对话按钮固定在聊天容器外部 -->
    <div class="fixed-new-chat">
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

interface LayerStatus {
  name: string;
  visible: boolean;
}

interface SelectedFeature {
  id: string | number;
  properties: object;
  geometry: any;
  layerName: string;
}

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'system';
}

useThemeStore();
const modeStateStore = useModeStateStore();

const props = defineProps<{
  initialLayers: LayerStatus[];
  mapReady: boolean;
  selectedFeatures?: SelectedFeature[]; // 新增：选中要素列表
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
}



// 新增：格式化选中要素状态 
// 移除选中要素状态格式化函数

const demoMessage = (): string => {
  return [
    '请输入您的需求，我将为您执行。',
    '您可以这样说：',
    '- 打开 道路 图层',
    '- 查询 距我最近的学校',
    '- 统计 距我最近的医院数量',
    '- 进行 缓冲区分析',
    '- 进行 最优路径分析',
    '- 进行 可达性分析',
    '- 分析 已选中要素的属性',
    '- 对 已选中要素 进行空间分析'
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

// 移除图层数量和要素数量监听器

watch(messages, async () => {
  await nextTick();
  // 使用智能滚动逻辑
  if (shouldAutoScroll()) {
    smoothScrollToBottom();
  }
  // 更新滚动位置状态
  checkScrollPosition();
});

const sendMessage = () => {
  if (!newMessage.value.trim()) {
    return;
  }

  const userMessage = newMessage.value;
  
  messages.value.push({
    id: Date.now(),
    text: userMessage,
    sender: 'user'
  });

  // 处理与选中要素相关的请求
  const userInput = userMessage.toLowerCase();
  const hasSelectedFeatures = props.selectedFeatures && props.selectedFeatures.length > 0;
  
  let aiResponse = '';
  
  if (hasSelectedFeatures) {
    // 处理选中要素相关的请求
    if (userInput.includes('分析') && userInput.includes('选中要素')) {
      aiResponse = generateSelectedFeaturesAnalysis();
    } else if (userInput.includes('选中要素') && userInput.includes('属性')) {
      aiResponse = generateSelectedFeaturesProperties();
    } else if (userInput.includes('选中要素') && userInput.includes('空间分析')) {
      aiResponse = generateSelectedFeaturesSpatialAnalysis();
    } else if (userInput.includes('选中要素') && userInput.includes('统计')) {
      aiResponse = generateSelectedFeaturesStatistics();
    }
  }
  
  // 如果没有特定的选中要素处理，使用默认响应
  if (!aiResponse) {
    aiResponse = `我理解您的需求："${userMessage}"，正在处理中...`;
  }
  
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

// 新增：生成选中要素分析报告
const generateSelectedFeaturesAnalysis = (): string => {
  const features = props.selectedFeatures || [];
  const layerGroups = features.reduce((groups, feature) => {
    if (!groups[feature.layerName]) {
      groups[feature.layerName] = [];
    }
    groups[feature.layerName].push(feature);
    return groups;
  }, {} as Record<string, typeof features>);
  
  let analysis = `**选中要素分析报告**\n\n`;
  analysis += `总计选中了 **${features.length}** 个要素，分布在 **${Object.keys(layerGroups).length}** 个图层中：\n\n`;
  
  Object.entries(layerGroups).forEach(([layerName, layerFeatures]) => {
    analysis += `**${layerName}** (${layerFeatures.length}个要素)：\n`;
    
    // 统计几何类型
    const geometryTypes = layerFeatures.reduce((types, feature) => {
      const type = feature.geometry?.type || '未知';
      types[type] = (types[type] || 0) + 1;
      return types;
    }, {} as Record<string, number>);
    
    Object.entries(geometryTypes).forEach(([type, count]) => {
      analysis += `- ${type}: ${count}个\n`;
    });
    
    analysis += '\n';
  });
  
  return analysis;
};

// 新增：生成选中要素属性信息
const generateSelectedFeaturesProperties = (): string => {
  const features = props.selectedFeatures || [];
  if (features.length === 0) return '当前没有选中的要素。';
  
  let properties = `**选中要素属性信息**\n\n`;
  
  features.forEach((feature, index) => {
    properties += `**要素 ${index + 1}** (${feature.layerName}):\n`;
    properties += `- ID: ${feature.id || '无'}\n`;
    properties += `- 几何类型: ${feature.geometry?.type || '未知'}\n`;
    
    const props = feature.properties || {};
    if (Object.keys(props).length > 0) {
      properties += `- 属性字段:\n`;
      Object.entries(props).forEach(([key, value]) => {
        if (key !== 'geometry') {
          properties += `  - ${key}: ${value || '(空值)'}\n`;
        }
      });
    } else {
      properties += `- 属性字段: 无\n`;
    }
    properties += '\n';
  });
  
  return properties;
};

// 新增：生成选中要素空间分析建议
const generateSelectedFeaturesSpatialAnalysis = (): string => {
  const features = props.selectedFeatures || [];
  if (features.length === 0) return '当前没有选中的要素。';
  
  let analysis = `**选中要素空间分析建议**\n\n`;
  analysis += `基于您选中的 **${features.length}** 个要素，我建议可以进行以下空间分析：\n\n`;
  
  // 根据要素类型推荐分析
  const hasPoints = features.some(f => f.geometry?.type === 'Point');
  const hasLines = features.some(f => f.geometry?.type === 'LineString');
  const hasPolygons = features.some(f => f.geometry?.type === 'Polygon');
  
  if (hasPoints) {
    analysis += `- **点要素分析**:\n`;
    analysis += `  - 最近邻分析\n`;
    analysis += `  - 点密度分析\n`;
    analysis += `  - 空间聚类分析\n\n`;
  }
  
  if (hasLines) {
    analysis += `- **线要素分析**:\n`;
    analysis += `  - 网络分析\n`;
    analysis += `  - 路径分析\n`;
    analysis += `  - 可达性分析\n\n`;
  }
  
  if (hasPolygons) {
    analysis += `- **面要素分析**:\n`;
    analysis += `  - 缓冲区分析\n`;
    analysis += `  - 叠加分析\n`;
    analysis += `  - 面积统计\n\n`;
  }
  
  analysis += `您可以选择相应的分析工具进行操作。`;
  
  return analysis;
};

// 新增：生成选中要素统计信息
const generateSelectedFeaturesStatistics = (): string => {
  const features = props.selectedFeatures || [];
  if (features.length === 0) return '当前没有选中的要素。';
  
  let stats = `**选中要素统计信息**\n\n`;
  
  // 按图层统计
  const layerStats = features.reduce((stats, feature) => {
    if (!stats[feature.layerName]) {
      stats[feature.layerName] = { count: 0, types: {} };
    }
    stats[feature.layerName].count++;
    
    const type = feature.geometry?.type || '未知';
    stats[feature.layerName].types[type] = (stats[feature.layerName].types[type] || 0) + 1;
    
    return stats;
  }, {} as Record<string, { count: number; types: Record<string, number> }>);
  
  stats += `**总计**: ${features.length} 个要素\n\n`;
  
  Object.entries(layerStats).forEach(([layerName, layerStat]) => {
    stats += `**${layerName}**: ${layerStat.count} 个要素\n`;
    Object.entries(layerStat.types).forEach(([type, count]) => {
      stats += `- ${type}: ${count}个\n`;
    });
    stats += '\n';
  });
  
  return stats;
};

// 新增：开启新对话功能
const startNewConversation = () => {
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

.fixed-new-chat {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 20;
  /* 确保按钮完全脱离文档流，不占用空间 */
  pointer-events: auto;
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
  animation: fadeIn 0.3s ease-out;
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
}

.new-chat-button:hover {
  transform: none !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
}

.new-chat-button .button-text {
  font-size: 12px;
  margin-left: 2px;
}

.new-chat-button svg {
  flex-shrink: 0;
  width: 14px !important;
  height: 14px !important;
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
  gap: 6px;
  margin: 0;
  animation: fadeIn 0.3s ease-out;
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
