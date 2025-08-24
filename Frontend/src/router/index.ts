import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'
import Dashboard from '@/views/Dashboard.vue'
import UserProfile from '@/views/profile/UserProfile.vue'
import AIManagement from '@/views/management/AIManagement.vue'

/**
 * Vue Router 配置
 * 使用 History API 模式，支持更友好的URL结构
 */
const router = createRouter({
  history: createWebHistory(),
  routes: [
    // 根路径重定向到登录页
    {
      path: '/',
      redirect: '/login'
    },
    // 登录页面 - 不需要认证
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { 
        requiresAuth: false,  // 不需要登录即可访问
        title: '系统登录'
      }
    },
    // 注册页面 - 不需要认证
    {
      path: '/register',
      name: 'register',
      component: Register,
      meta: { 
        requiresAuth: false,  // 不需要登录即可访问
        title: '用户注册'
      }
    },
    // 个人中心页面 - 需要认证
    {
      path: '/profile',
      name: 'profile',
      component: UserProfile,
      meta: { 
        requiresAuth: true,   // 需要登录才能访问
        title: '个人中心'
      }
    },
    // Agent管理页面 - 需要认证
    {
      path: '/Agent-management',
      name: 'Agent-management',
      component: AIManagement,
      meta: { 
        requiresAuth: true,   // 需要登录才能访问
        title: 'Agent管理'
      }
    },
    // 仪表板页面 - 需要认证，包含模式子路由
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard,
      meta: { 
        requiresAuth: true,   // 需要登录才能访问
        title: '地图系统'
      },
      children: [
        // 默认子路由 - 根据状态管理决定重定向
        {
          path: '',
          redirect: (to) => {
            // 从localStorage获取上次的模式状态
            const savedMode = localStorage.getItem('currentMode')
            if (savedMode === 'traditional') {
              return '/dashboard/traditional'
            }
            return '/dashboard/llm'
          }
        },
        // LLM模式
        {
          path: 'llm',
          name: 'llm-mode',
          component: () => import('@/views/dashboard/LLM/LLMMode.vue'),
          meta: {
            title: 'AI助手',
            mode: 'llm',
            requiresAuth: true
          }
        },
        // 传统模式
        {
          path: 'traditional',
          name: 'traditional-mode',
          component: () => import('@/views/dashboard/traditional/TraditionalMode.vue'),
          meta: {
            title: '传统模式',
            mode: 'traditional',
            requiresAuth: true
          },
                      children: [
              // 传统模式默认子路由 - 根据状态管理决定重定向
              {
                path: '',
                redirect: (to) => {
                  // 从localStorage获取上次的工具状态
                  const savedState = localStorage.getItem('traditionalModeState')
                  if (savedState) {
                    try {
                      const state = JSON.parse(savedState)
                      if (state.activeTool) {
                        // 根据activeTool找到对应的路径
                        const toolPathMap: { [key: string]: string } = {
                          'layer': 'layer',
                          'query': 'query',
                          'bianji': 'edit',
                          'buffer': 'buffer',
                          'distance': 'distance',
                          'gotowhere': 'accessibility'
                        }
                        const path = toolPathMap[state.activeTool]
                        if (path) {
                          return `/dashboard/traditional/${path}`
                        }
                      }
                    } catch (error) {
                      console.warn('解析传统模式状态失败:', error)
                    }
                  }
                  return '/dashboard/traditional/layer'
                }
              },
            // 图层管理
            {
              path: 'layer',
              name: 'layer-management',
              component: () => import('@/views/dashboard/traditional/tools/LayerManager.vue'),
              meta: {
                title: '图层管理',
                tool: 'layer',
                requiresAuth: true
              }
            },
            // 要素查询
            {
              path: 'query',
              name: 'feature-query',
              component: () => import('@/views/dashboard/traditional/tools/FeatureQueryPanel.vue'),
              meta: {
                title: '要素查询',
                tool: 'query',
                requiresAuth: true
              }
            },
            // 图层编辑
            {
              path: 'edit',
              name: 'edit-tools',
              component: () => import('@/views/dashboard/traditional/tools/EditTools.vue'),
              meta: {
                title: '图层编辑',
                tool: 'bianji',
                requiresAuth: true
              }
            },
            // 缓冲区分析
            {
              path: 'buffer',
              name: 'buffer-analysis',
              component: () => import('@/views/dashboard/traditional/tools/BufferAnalysisPanel.vue'),
              meta: {
                title: '缓冲区分析',
                tool: 'buffer',
                requiresAuth: true
              }
            },
            // 距离分析
            {
              path: 'distance',
              name: 'distance-analysis',
              component: () => import('@/views/dashboard/traditional/tools/DistanceAnalysisPanel.vue'),
              meta: {
                title: '距离分析',
                tool: 'distance',
                requiresAuth: true
              }
            },
            // 可达性分析
            {
              path: 'accessibility',
              name: 'accessibility-analysis',
              component: () => import('@/views/dashboard/traditional/tools/AccessibilityAnalysisPanel.vue'),
              meta: {
                title: '可达性分析',
                tool: 'gotowhere',
                requiresAuth: true
              }
            }
          ]
        }
      ]
    }
  ]
})

/**
 * 全局路由守卫
 * 在每次路由跳转前执行，用于权限控制和页面重定向
 */
router.beforeEach((to, from, next) => {
  // 检查用户是否已登录（通过localStorage中的authToken判断）
  const isLoggedIn = localStorage.getItem('authToken')
  
  // 如果需要认证但用户未登录，重定向到登录页
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
  } 
  // 如果已登录用户访问登录页或注册页，重定向到仪表板
  else if ((to.path === '/login' || to.path === '/register') && isLoggedIn) {
    next('/dashboard')
  } 
  // 其他情况正常跳转
  else {
    next()
  }
})

export default router
