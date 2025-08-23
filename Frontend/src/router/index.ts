import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Dashboard from '@/views/Dashboard.vue'

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
    // 仪表板页面 - 需要认证，包含子路由
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard,
      meta: { 
        requiresAuth: true,   // 需要登录才能访问
        title: '地图系统'
      },
      children: [
        // 默认子路由 - 重定向到图层管理
        {
          path: '',
          redirect: '/dashboard/layer'
        },
        // 图层管理
        {
          path: 'layer',
          name: 'layer-management',
          component: () => import('@/components/Map/LayerManager.vue'),
          meta: {
            title: '图层管理',
            icon: 'layers',
            requiresAuth: true
          }
        },
        // 要素查询
        {
          path: 'query',
          name: 'feature-query',
          component: () => import('@/components/Map/FeatureQueryPanel.vue'),
          meta: {
            title: '按属性选择要素',
            icon: 'search',
            requiresAuth: true
          }
        },
        // 图层编辑
        {
          path: 'edit',
          name: 'layer-edit',
          component: () => import('@/components/Map/EditTools.vue'),
          meta: {
            title: '按区域选择要素',
            icon: 'edit',
            requiresAuth: true
          }
        },
        // 缓冲区分析
        {
          path: 'buffer',
          name: 'buffer-analysis',
          component: () => import('@/components/Map/BufferAnalysisPanel.vue'),
          meta: {
            title: '缓冲区分析',
            icon: 'buffer',
            requiresAuth: true
          }
        },
        // 最优路径分析
        {
          path: 'distance',
          name: 'distance-analysis',
          component: () => import('@/components/Map/DistanceAnalysisPanel.vue'),
          meta: {
            title: '最优路径分析',
            icon: 'route',
            requiresAuth: true
          }
        },
        // 可达性分析
        {
          path: 'accessibility',
          name: 'accessibility-analysis',
          component: () => import('@/components/Map/AccessibilityAnalysisPanel.vue'),
          meta: {
            title: '可达性分析',
            icon: 'accessibility',
            requiresAuth: true
          }
        },
        // LLM助手
        {
          path: 'assistant',
          name: 'llm-assistant',
          component: () => import('@/components/Map/ChatAssistant.vue'),
          meta: {
            title: 'AI助手',
            icon: 'chat',
            requiresAuth: true
          }
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
