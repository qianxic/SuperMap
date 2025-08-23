import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem('authToken'))
  const userInfo = ref<any>(null)
  const isLoggedIn = computed(() => !!token.value)

  // 初始化用户信息
  const initUserInfo = () => {
    const storedUserInfo = localStorage.getItem('userInfo')
    if (storedUserInfo) {
      userInfo.value = JSON.parse(storedUserInfo)
    }
  }

  // 登录
  const login = (userData: any, authToken: string) => {
    token.value = authToken
    userInfo.value = userData
    
    localStorage.setItem('authToken', authToken)
    localStorage.setItem('userInfo', JSON.stringify(userData))
  }

  // 登出
  const logout = () => {
    token.value = null
    userInfo.value = null
    
    localStorage.removeItem('authToken')
    localStorage.removeItem('userInfo')
  }

  // 检查登录状态
  const checkAuth = () => {
    const storedToken = localStorage.getItem('authToken')
    if (storedToken) {
      token.value = storedToken
      initUserInfo()
      return true
    }
    return false
  }

  // 初始化
  initUserInfo()

  return {
    token,
    userInfo,
    isLoggedIn,
    login,
    logout,
    checkAuth,
    initUserInfo
  }
})
