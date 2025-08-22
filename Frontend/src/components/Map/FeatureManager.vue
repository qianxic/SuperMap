<template>
  <PanelWindow title="要素管理器" :loading="isLoading">
    <div class="feature-manager">
      <!-- 数据集选择 -->
      <div class="dataset-selector">
        <label class="form-label">选择数据集：</label>
        <DropdownSelect 
          v-model="selectedDataset"
          :options="datasetOptions"
          placeholder="请选择数据集"
          @change="onDatasetChange"
        />
      </div>

      <!-- 加载进度 -->
      <div v-if="isLoading" class="loading-progress">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: loadingPercentage + '%' }"
          ></div>
        </div>
        <div class="progress-text">
          {{ loadingProgress.loaded }} / {{ loadingProgress.total }} 
          ({{ loadingPercentage }}%)
        </div>
      </div>

      <!-- 要素统计信息 -->
      <div v-if="featureListInfo" class="feature-stats">
        <h4>数据集信息</h4>
        <div class="stat-item">
          <span>要素总数：</span>
          <strong>{{ featureListInfo.featureCount }}</strong>
        </div>
        <div class="stat-item">
          <span>几何类型：</span>
          <strong>{{ geometryTypeText }}</strong>
        </div>
        <div class="stat-item">
          <span>已加载：</span>
          <strong>{{ features.length }}</strong>
        </div>
      </div>

      <!-- 要素类型分布 -->
      <div v-if="hasFeatures" class="geometry-stats">
        <h4>几何类型分布</h4>
        <div class="type-item" v-if="featuresByType.POINT.length > 0">
          <span class="type-label point">点要素：</span>
          <span>{{ featuresByType.POINT.length }}</span>
        </div>
        <div class="type-item" v-if="featuresByType.LINE.length > 0">
          <span class="type-label line">线要素：</span>
          <span>{{ featuresByType.LINE.length }}</span>
        </div>
        <div class="type-item" v-if="featuresByType.POLYGON.length > 0">
          <span class="type-label polygon">面要素：</span>
          <span>{{ featuresByType.POLYGON.length }}</span>
        </div>
      </div>

      <!-- 搜索功能 -->
      <div v-if="hasFeatures" class="feature-search">
        <TraditionalInputGroup
          label="搜索要素"
          v-model="searchText"
          placeholder="输入要素名称或属性值..."
          @input="onSearch"
        />
        <div v-if="searchResults.length > 0" class="search-results">
          搜索结果：{{ searchResults.length }} 个要素
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <PrimaryButton 
          v-if="selectedDataset && !isLoading"
          @click="loadFeatures"
          :disabled="isLoading"
        >
          {{ hasFeatures ? '重新加载' : '加载要素' }}
        </PrimaryButton>
        
        <SecondaryButton 
          v-if="hasFeatures"
          @click="clearAllFeatures"
        >
          清除要素
        </SecondaryButton>

        <SecondaryButton 
          v-if="hasFeatures"
          @click="exportFeatures"
        >
          导出数据
        </SecondaryButton>
      </div>

      <!-- 要素列表 -->
      <div v-if="displayFeatures.length > 0" class="feature-list">
        <h4>要素列表 (显示前50个)</h4>
        <div class="list-container">
          <div 
            v-for="(feature, index) in displayFeatures.slice(0, 50)"
            :key="feature.id"
            class="feature-item"
            @click="showFeatureDetails(feature)"
          >
            <div class="feature-info">
              <span class="feature-id">ID: {{ feature.id }}</span>
              <span :class="['geometry-badge', getGeometryTypeClass(feature.geometry?.type)]">
                {{ getGeometryTypeText(feature.geometry?.type) }}
              </span>
            </div>
            <div class="feature-properties">
              <span v-if="getFeatureName(feature)" class="feature-name">
                {{ getFeatureName(feature) }}
              </span>
              <span class="properties-count">
                {{ Object.keys(feature.properties || {}).length }} 个属性
              </span>
            </div>
          </div>
        </div>
        <div v-if="displayFeatures.length > 50" class="more-indicator">
          还有 {{ displayFeatures.length - 50 }} 个要素未显示...
        </div>
      </div>
    </div>
  </PanelWindow>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useFeatureLoader } from '@/composables/useFeatureLoader'
import { getLayersByGroupName } from '@/utils/config'
import type { Feature, GeometryType } from '@/types/map'
import PanelWindow from '@/components/UI/PanelWindow.vue'
import DropdownSelect from '@/components/UI/DropdownSelect.vue'
import TraditionalInputGroup from '@/components/UI/TraditionalInputGroup.vue'
import PrimaryButton from '@/components/UI/PrimaryButton.vue'
import SecondaryButton from '@/components/UI/SecondaryButton.vue'

const {
  isLoading,
  loadingProgress,
  loadingPercentage,
  features,
  currentDataset,
  featureListInfo,
  hasFeatures,
  featuresByType,
  loadAllFeatures,
  searchFeatures,
  clearFeatures
} = useFeatureLoader()

// 本地状态
const selectedDataset = ref<string>('')
const searchText = ref<string>('')
const searchResults = ref<Feature[]>([])

// 数据集选项
const datasetOptions = computed(() => {
  // 从配置中获取所有数据集
  const allLayers = [
    ...getLayersByGroupName('基础设施'),
    ...getLayersByGroupName('城市基本信息')
  ]
  
  return allLayers
    .filter(layer => layer.datasetName)
    .map(layer => ({
      label: layer.datasetName!,
      value: layer.datasetName!
    }))
})

// 几何类型显示文本
const geometryTypeText = computed(() => {
  if (!featureListInfo.value) return ''
  const typeMap = {
    'POINT': '点要素',
    'LINE': '线要素', 
    'POLYGON': '面要素'
  }
  return typeMap[featureListInfo.value.geometryType] || featureListInfo.value.geometryType
})

// 搜索结果或全部要素
const displayFeatures = computed(() => {
  return searchResults.value.length > 0 ? searchResults.value : features.value
})

// 事件处理
const onDatasetChange = (value: string) => {
  selectedDataset.value = value
  clearFeatures()
  searchText.value = ''
  searchResults.value = []
}

const onSearch = () => {
  if (!searchText.value.trim()) {
    searchResults.value = []
    return
  }
  
  // 搜索常见的属性字段
  const searchFields = ['NAME', 'name', '名称', 'FEATURE_NAME', 'LABEL']
  searchResults.value = searchFeatures(searchText.value, searchFields)
}

const loadFeatures = async () => {
  if (!selectedDataset.value) return
  
  try {
    await loadAllFeatures(selectedDataset.value, 20) // 批次大小为20
  } catch (error) {
    console.error('加载要素失败:', error)
  }
}

const clearAllFeatures = () => {
  clearFeatures()
  searchText.value = ''
  searchResults.value = []
}

const showFeatureDetails = (feature: Feature) => {
  console.log('要素详情:', feature)
  // TODO: 显示要素详情弹窗
}

const exportFeatures = () => {
  if (!hasFeatures.value) return
  
  const data = {
    dataset: currentDataset.value,
    featureCount: features.value.length,
    features: features.value
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { 
    type: 'application/json' 
  })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${currentDataset.value}_features.json`
  link.click()
  URL.revokeObjectURL(url)
}

// 工具函数
const getGeometryTypeClass = (type: string): string => {
  if (!type) return ''
  const lowerType = type.toLowerCase()
  if (lowerType.includes('point')) return 'point'
  if (lowerType.includes('line')) return 'line'
  if (lowerType.includes('polygon')) return 'polygon'
  return ''
}

const getGeometryTypeText = (type: string): string => {
  if (!type) return '未知'
  const lowerType = type.toLowerCase()
  if (lowerType.includes('point')) return '点'
  if (lowerType.includes('line')) return '线'
  if (lowerType.includes('polygon')) return '面'
  return type
}

const getFeatureName = (feature: Feature): string => {
  const props = feature.properties || {}
  return props.NAME || props.name || props['名称'] || props.FEATURE_NAME || props.LABEL || `要素 ${feature.id}`
}

// 监听搜索文本变化
watch(searchText, () => {
  onSearch()
})
</script>

<style scoped>
.feature-manager {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dataset-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-weight: 500;
  font-size: 14px;
  color: var(--text);
}

.loading-progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-bar {
  height: 8px;
  background: var(--border);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: var(--text);
  text-align: center;
}

.feature-stats, .geometry-stats {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px;
}

.feature-stats h4, .geometry-stats h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--text);
}

.stat-item, .type-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  font-size: 13px;
}

.type-label {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.type-label::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.type-label.point::before {
  background: #ff6b6b;
}

.type-label.line::before {
  background: #4ecdc4;
}

.type-label.polygon::before {
  background: #45b7d1;
}

.feature-search {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.search-results {
  font-size: 12px;
  color: var(--primary);
  font-weight: 500;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feature-list {
  max-height: 300px;
  overflow-y: auto;
}

.feature-list h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--text);
}

.list-container {
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}

.feature-item {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.feature-item:hover {
  background: rgba(var(--primary-rgb), 0.1);
}

.feature-item:last-child {
  border-bottom: none;
}

.feature-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.feature-id {
  font-size: 12px;
  color: var(--text);
  font-family: monospace;
}

.geometry-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 3px;
  color: white;
  font-weight: 500;
}

.geometry-badge.point {
  background: #ff6b6b;
}

.geometry-badge.line {
  background: #4ecdc4;
}

.geometry-badge.polygon {
  background: #45b7d1;
}

.feature-properties {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.feature-name {
  font-size: 13px;
  color: var(--text);
  font-weight: 500;
}

.properties-count {
  font-size: 11px;
  color: var(--text-secondary);
}

.more-indicator {
  padding: 8px 12px;
  text-align: center;
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
}

/* 滚动条样式 */
.list-container::-webkit-scrollbar {
  width: 4px;
}

.list-container::-webkit-scrollbar-track {
  background: var(--border);
}

.list-container::-webkit-scrollbar-thumb {
  background: var(--primary);
  border-radius: 2px;
}
</style>