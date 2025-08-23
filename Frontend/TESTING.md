# 🧪 路由化功能测试指南

## 📋 测试概述

本文档描述了如何测试路由化功能的各个方面，包括自动化测试和手动测试。

## 🚀 快速开始

### 1. 运行自动化测试
```bash
# 运行路由测试
npm run test:routing

# 运行构建测试
npm run test:build

# 运行所有测试
npm run test:all
```

### 2. 启动开发服务器
```bash
npm run dev
```

## 🔧 自动化测试

### 测试脚本功能
- ✅ 检查组件文件是否存在
- ✅ 验证路由配置是否正确
- ✅ 检查导入路径是否正确
- ✅ 验证构建是否成功

### 运行测试
```bash
# 基础测试
node scripts/test-routing.js

# 带详细输出的测试
node scripts/test-routing.js --verbose

# 生成测试报告
node scripts/test-routing.js --report
```

## 🎯 手动测试清单

### 第一阶段：基础功能测试

#### 1. 应用启动测试
- [ ] 开发服务器正常启动
- [ ] 浏览器能正常访问应用
- [ ] 无控制台错误

#### 2. 路由访问测试
- [ ] 访问 `/` 自动重定向到 `/login`
- [ ] 访问 `/login` 显示登录页面
- [ ] 访问 `/register` 显示注册页面
- [ ] 未登录时访问 `/dashboard` 重定向到 `/login`

### 第二阶段：用户认证测试

#### 3. 登录功能测试
- [ ] 登录表单正常显示
- [ ] 输入用户名密码
- [ ] 点击登录按钮
- [ ] 登录成功后跳转到 `/dashboard`
- [ ] 登录后访问 `/login` 重定向到 `/dashboard`

#### 4. 注册功能测试
- [ ] 注册表单正常显示
- [ ] 输入注册信息
- [ ] 点击注册按钮
- [ ] 注册成功后跳转到登录页面

### 第三阶段：路由化功能测试

#### 5. 模式切换测试
- [ ] 登录后默认进入 `/dashboard/llm`（LLM模式）
- [ ] 点击"传统模式"按钮，URL变为 `/dashboard/traditional`
- [ ] 点击"LLM模式"按钮，URL变为 `/dashboard/llm`
- [ ] 模式切换时界面正常更新

#### 6. URL直接访问测试
- [ ] 直接访问 `/dashboard/llm` 显示LLM模式
- [ ] 直接访问 `/dashboard/traditional` 显示传统模式
- [ ] 访问不存在的路由显示404或重定向

#### 7. 浏览器导航测试
- [ ] 点击浏览器后退按钮，回到上一个模式
- [ ] 点击浏览器前进按钮，前进到下一个模式
- [ ] 刷新页面后保持当前模式

### 第四阶段：功能完整性测试

#### 8. LLM模式功能测试
- [ ] LLM模式界面正常显示
- [ ] 聊天界面正常加载
- [ ] 输入框可以输入文字
- [ ] 发送消息功能正常

#### 9. 传统模式功能测试
- [ ] 传统模式界面正常显示
- [ ] 功能按钮正常显示
- [ ] 点击"图层管理"按钮
- [ ] 图层管理面板正常显示
- [ ] 其他功能按钮正常工作

#### 10. 地图功能测试
- [ ] 地图正常加载
- [ ] 地图交互正常（缩放、平移）
- [ ] 图层切换功能正常
- [ ] 要素查询功能正常

### 第五阶段：状态同步测试

#### 11. 状态保持测试
- [ ] 模式切换后地图状态保持
- [ ] 图层显示状态保持
- [ ] 用户操作状态保持

#### 12. 主题切换测试
- [ ] 主题切换按钮正常工作
- [ ] 浅色/深色主题正常切换
- [ ] 主题设置持久化

## 🔍 测试工具

### 浏览器开发者工具
```javascript
// 在浏览器控制台执行以下测试：

// 1. 检查当前路由
console.log('当前路由:', window.location.pathname);

// 2. 检查认证状态
console.log('认证状态:', localStorage.getItem('authToken'));

// 3. 模拟登录
localStorage.setItem('authToken', 'test-token');

// 4. 检查Vue组件状态
// 在Vue DevTools中查看组件状态
```

### 网络请求监控
```javascript
// 监控网络请求
// 在Network标签页中查看：
// - 路由切换时的请求
// - API调用
// - 资源加载
```

## 📊 测试报告

### 自动化测试报告
测试完成后，会在项目根目录生成 `test-report.json` 文件，包含：
- 测试时间戳
- 测试结果统计
- 错误详情
- 测试配置

### 手动测试报告模板
```markdown
## 测试报告

### 测试环境
- 浏览器: Chrome 120.0
- 开发服务器: http://localhost:5173
- 测试时间: 2024-01-XX

### 测试结果
| 测试项目 | 状态 | 备注 |
|----------|------|------|
| 应用启动 | ✅ 通过 | 无错误 |
| 路由访问 | ✅ 通过 | 所有路由正常 |
| 用户认证 | ✅ 通过 | 登录注册正常 |
| 模式切换 | ✅ 通过 | URL正确更新 |
| 浏览器导航 | ✅ 通过 | 前进后退正常 |
| 功能完整性 | ✅ 通过 | 所有功能正常 |
| 状态同步 | ✅ 通过 | 状态保持正常 |

### 发现的问题
- 无

### 建议
- 测试通过，可以继续开发
```

## 🐛 常见问题排查

### 问题1：路由不工作
```bash
# 检查路由配置
cat src/router/index.ts

# 检查main.js是否正确引入router
cat src/main.js
```

### 问题2：组件不加载
```bash
# 检查组件导入路径
ls src/components/Modes/
ls src/components/Layout/

# 检查构建错误
npm run build
```

### 问题3：状态不同步
```javascript
// 在浏览器控制台检查状态
console.log('当前路由:', window.location.pathname);
console.log('认证状态:', localStorage.getItem('authToken'));
```

## 🚀 持续集成

### GitHub Actions 配置
```yaml
# .github/workflows/test.yml
name: 路由化功能测试

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: npm install
    
    - name: Run tests
      run: npm run test:all
    
    - name: Upload test results
      uses: actions/upload-artifact@v2
      with:
        name: test-results
        path: test-report.json
```

## 📞 测试支持

如果在测试过程中遇到问题，请：
1. 查看测试报告中的错误详情
2. 检查浏览器控制台的错误信息
3. 查看网络请求的失败情况
4. 提交Issue并附上测试报告

---

**测试是确保代码质量的重要环节，请认真执行每一项测试！** 🎯