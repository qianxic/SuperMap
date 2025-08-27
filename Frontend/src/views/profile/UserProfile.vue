<template>
  <teleport to="body">
  <div class="page-modal-overlay" @click="closeModal">
    <div class="page-modal-content" @click.stop>
      <div class="page-modal-header">
        <h2>个人中心</h2>
        <button class="page-modal-close" @click="closeModal" aria-label="close">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <PanelContainer class="user-profile">
    <div class="profile-header">
      <h1 class="profile-title">个人中心</h1>
      <p class="profile-subtitle">管理您的账户信息和设置</p>
    </div>

    <div class="profile-content">
      <!-- 基本信息卡片 -->
      <div class="profile-card">
        <div class="card-header">
          <h2 class="card-title">基本信息</h2>
          <button class="edit-btn" @click="toggleEditMode">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            {{ isEditing ? '保存' : '编辑' }}
          </button>
        </div>

        <div class="info-grid">
          <div class="info-item">
            <label class="info-label">用户名</label>
            <div v-if="!isEditing" class="info-value">{{ userInfo.username }}</div>
            <input v-else v-model="editForm.username" type="text" class="info-input" />
          </div>

          <div class="info-item">
            <label class="info-label">邮箱</label>
            <div v-if="!isEditing" class="info-value">{{ userInfo.email }}</div>
            <input v-else v-model="editForm.email" type="email" class="info-input" />
          </div>

          <div class="info-item">
            <label class="info-label">手机号</label>
            <div v-if="!isEditing" class="info-value">{{ userInfo.phone || '未设置' }}</div>
            <input v-else v-model="editForm.phone" type="tel" class="info-input" placeholder="请输入手机号" />
          </div>

          <div class="info-item">
            <label class="info-label">注册时间</label>
            <div class="info-value">{{ formatDate(userInfo.createdAt) }}</div>
          </div>
        </div>
      </div>

      <!-- 账户安全卡片 -->
      <div class="profile-card">
        <div class="card-header">
          <h2 class="card-title">账户安全</h2>
        </div>

        <div class="security-items">
          <div class="security-item">
            <div class="security-info">
              <div class="security-title">修改密码</div>
              <div class="security-desc">定期更新密码以确保账户安全</div>
            </div>
            <button class="security-btn" @click="showChangePassword = true">
              修改
            </button>
          </div>

          <div class="security-item">
            <div class="security-info">
              <div class="security-title">登录历史</div>
              <div class="security-desc">查看最近的登录记录</div>
            </div>
            <button class="security-btn" @click="showLoginHistory = true">
              查看
            </button>
          </div>
        </div>
      </div>

      <!-- 系统设置卡片 -->
      <div class="profile-card">
        <div class="card-header">
          <h2 class="card-title">系统设置</h2>
        </div>

        <div class="setting-items">
          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-title">主题设置</div>
              <div class="setting-desc">选择您喜欢的界面主题</div>
            </div>
            <div class="setting-control">
              <button 
                class="theme-btn" 
                :class="{ active: theme === 'light' }"
                @click="setTheme('light')"
              >
                浅色
              </button>
              <button 
                class="theme-btn" 
                :class="{ active: theme === 'dark' }"
                @click="setTheme('dark')"
              >
                深色
              </button>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <div class="setting-title">通知设置</div>
              <div class="setting-desc">管理系统通知偏好</div>
            </div>
            <button class="setting-btn">
              配置
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <div v-if="showChangePassword" class="modal-overlay" @click="showChangePassword = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>修改密码</h3>
          <button class="modal-close" @click="showChangePassword = false">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label>当前密码</label>
            <input type="password" v-model="passwordForm.currentPassword" placeholder="请输入当前密码" />
          </div>
          <div class="form-item">
            <label>新密码</label>
            <input type="password" v-model="passwordForm.newPassword" placeholder="请输入新密码" />
          </div>
          <div class="form-item">
            <label>确认新密码</label>
            <input type="password" v-model="passwordForm.confirmPassword" placeholder="请再次输入新密码" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showChangePassword = false">取消</button>
          <button class="btn-primary" @click="changePassword">确认修改</button>
        </div>
      </div>
    </div>
      </PanelContainer>
    </div>
  </div>
  </teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { useThemeStore } from '@/stores/themeStore'
import PanelContainer from '@/components/UI/PanelContainer.vue'

const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()

// 响应式数据
const isEditing = ref(false)
const showChangePassword = ref(false)
const showLoginHistory = ref(false)

// 编辑表单
const editForm = ref({
  username: '',
  email: '',
  phone: ''
})

// 密码表单
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 计算属性
const userInfo = computed(() => {
  const info = userStore.userInfo
  return {
    username: info?.username || '用户',
    email: info?.email || 'user@example.com',
    phone: info?.phone || '',
    createdAt: info?.createdAt || new Date().toISOString()
  }
})

const theme = computed(() => themeStore.theme)

// 方法
import { useGlobalModalStore } from '@/stores/modalStore'
const modal = useGlobalModalStore()
const closeModal = () => {
  modal.close()
}

const toggleEditMode = () => {
  if (isEditing.value) {
    // 保存编辑
    saveUserInfo()
  } else {
    // 进入编辑模式
    editForm.value = {
      username: userInfo.value.username,
      email: userInfo.value.email,
      phone: userInfo.value.phone
    }
  }
  isEditing.value = !isEditing.value
}

const saveUserInfo = () => {
  // 这里应该调用API保存用户信息
  console.log('保存用户信息:', editForm.value)
  
  // 触发通知
  window.dispatchEvent(new CustomEvent('showNotification', {
    detail: {
      title: '保存成功',
      message: '用户信息已更新',
      type: 'success',
      duration: 3000
    }
  }))
}

const setTheme = (newTheme: 'light' | 'dark') => {
  themeStore.setTheme(newTheme)
}

const changePassword = () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    window.dispatchEvent(new CustomEvent('showNotification', {
      detail: {
        title: '密码不匹配',
        message: '新密码与确认密码不一致',
        type: 'error',
        duration: 3000
      }
    }))
    return
  }

  // 这里应该调用API修改密码
  console.log('修改密码:', passwordForm.value)
  
  window.dispatchEvent(new CustomEvent('showNotification', {
    detail: {
      title: '修改成功',
      message: '密码已成功修改',
      type: 'success',
      duration: 3000
    }
  }))
  
  showChangePassword.value = false
  passwordForm.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {
  // 初始化编辑表单
  editForm.value = {
    username: userInfo.value.username,
    email: userInfo.value.email,
    phone: userInfo.value.phone
  }
})
</script>

<style scoped>
.page-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
}

.page-modal-content {
  width: 90%;
  max-width: 880px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.16);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.page-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
}

.page-modal-header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
}

.page-modal-close {
  border: none;
  background: transparent;
  color: var(--sub);
  cursor: pointer;
  border-radius: 6px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-modal-close:hover {
  background: var(--surface-hover);
  color: var(--text);
}

.user-profile {
  width: 100%;
  padding: 12px;
  overflow-y: auto;
  max-height: 60vh;
}

.profile-header {
  text-align: center;
  margin-bottom: 32px;
}

.profile-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 8px;
}

.profile-subtitle {
  font-size: 16px;
  color: var(--sub);
  margin: 0;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--glow);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
  margin: 0;
}

.edit-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--btn-primary-bg);
  color: var(--btn-primary-color);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.edit-btn:hover {
  background: var(--btn-primary-bg);
  opacity: 0.9;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  font-size: 14px;
  color: var(--sub);
  font-weight: 500;
}

.info-value {
  font-size: 16px;
  color: var(--text);
  font-weight: 500;
}

.info-input {
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  transition: all 0.2s ease;
}

.info-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(var(--accent-rgb), 0.1);
}

.security-items,
.setting-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.security-item,
.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--surface);
  border-radius: 12px;
  border: 1px solid var(--border);
}

.security-info,
.setting-info {
  flex: 1;
}

.security-title,
.setting-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 4px;
}

.security-desc,
.setting-desc {
  font-size: 14px;
  color: var(--sub);
}

.security-btn,
.setting-btn {
  padding: 8px 16px;
  background: var(--btn-primary-bg);
  color: var(--btn-primary-color);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.security-btn:hover,
.setting-btn:hover {
  opacity: 0.9;
}

.setting-control {
  display: flex;
  gap: 8px;
}

.theme-btn {
  padding: 8px 16px;
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.theme-btn.active {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}

.theme-btn:hover:not(.active) {
  background: var(--surface-hover);
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--panel);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 400px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
}

.modal-close {
  background: none;
  border: none;
  color: var(--sub);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: var(--surface-hover);
  color: var(--text);
}

.modal-body {
  padding: 24px;
}

.form-item {
  margin-bottom: 16px;
}

.form-item:last-child {
  margin-bottom: 0;
}

.form-item label {
  display: block;
  font-size: 14px;
  color: var(--text);
  margin-bottom: 8px;
  font-weight: 500;
}

.form-item input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  transition: all 0.2s ease;
}

.form-item input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(var(--accent-rgb), 0.1);
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border);
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary {
  background: var(--btn-primary-bg);
  color: var(--btn-primary-color);
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-secondary {
  background: var(--btn-secondary-bg);
  color: var(--btn-secondary-color);
  border: 1px solid var(--border);
}

.btn-secondary:hover {
  background: var(--surface-hover);
}

@media (max-width: 768px) {
  .user-profile {
    padding: 16px;
  }
  
  .profile-title {
    font-size: 24px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .security-item,
  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .setting-control {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
