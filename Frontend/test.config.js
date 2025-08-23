/**
 * 测试配置文件
 * 用于管理路由化功能的测试设置
 */

module.exports = {
  // 测试环境配置
  testEnvironment: {
    baseUrl: 'http://localhost:5173',
    timeout: 10000,
    headless: false, // 显示浏览器窗口
    slowMo: 100 // 操作间隔
  },

  // 路由测试配置
  routes: {
    // 公开路由
    public: [
      { path: '/', expectedRedirect: '/login' },
      { path: '/login', component: 'Login.vue' },
      { path: '/register', component: 'Register.vue' }
    ],
    
    // 需要认证的路由
    protected: [
      { path: '/dashboard', component: 'Dashboard.vue' },
      { path: '/dashboard/llm', component: 'LLMMode.vue' },
      { path: '/dashboard/traditional', component: 'TraditionalMode.vue' }
    ]
  },

  // 组件测试配置
  components: {
    // 布局组件
    layout: [
      'src/components/Layout/DashboardLayout.vue',
      'src/components/Layout/DashboardHeader.vue',
      'src/components/Layout/RightPanel.vue'
    ],
    
    // 模式组件
    modes: [
      'src/components/Modes/LLMMode.vue',
      'src/components/Modes/TraditionalMode.vue'
    ],
    
    // 页面组件
    views: [
      'src/views/Dashboard.vue',
      'src/views/Login.vue',
      'src/views/Register.vue'
    ]
  },

  // 功能测试配置
  features: {
    // 模式切换测试
    modeSwitching: {
      enabled: true,
      testCases: [
        { from: 'llm', to: 'traditional' },
        { from: 'traditional', to: 'llm' }
      ]
    },
    
    // 路由导航测试
    navigation: {
      enabled: true,
      testCases: [
        { action: 'back', expected: 'previous-mode' },
        { action: 'forward', expected: 'next-mode' },
        { action: 'refresh', expected: 'same-mode' }
      ]
    },
    
    // 状态同步测试
    stateSync: {
      enabled: true,
      testCases: [
        { state: 'map-layers', shouldPersist: true },
        { state: 'user-preferences', shouldPersist: true },
        { state: 'current-mode', shouldPersist: true }
      ]
    }
  },

  // 报告配置
  reporting: {
    outputDir: './test-reports',
    formats: ['json', 'html', 'markdown'],
    includeScreenshots: true,
    includeVideos: false
  }
};