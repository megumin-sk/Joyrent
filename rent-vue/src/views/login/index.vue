<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { adminLogin } from '@/api/auth.js';
import { ElMessage } from 'element-plus';

import { useStore } from 'vuex';

const store = useStore();
const router = useRouter();
const loading = ref(false);
const error = ref('');
const rememberMe = ref(true);
const form = ref({
  username: '',
  password: ''
});

onMounted(() => {
  const cached = localStorage.getItem('joyrent-login');
  if (cached) {
    try {
      const parsed = JSON.parse(cached);
      form.value.username = parsed?.username ?? '';
    } catch (err) {
      localStorage.removeItem('joyrent-login');
    }
  }
});

const handleLogin = async () => {
  error.value = '';
  const trimmedUsername = form.value.username.trim();
  if (!trimmedUsername || !form.value.password) {
    error.value = '请输入账号和密码';
    return;
  }
  form.value.username = trimmedUsername;

  loading.value = true;
  try {
    const response = await adminLogin({
      username: form.value.username,
      password: form.value.password
    });
    
    const res = response.data || response;
    
    if (res.code === 200) {
      const { token, user } = res.data;
      
      // 使用 Vuex action 保存状态
      store.dispatch('loginSuccess', { user, token });

      if (rememberMe.value) {
        localStorage.setItem('joyrent-login', JSON.stringify({ username: form.value.username }));
      } else {
        localStorage.removeItem('joyrent-login');
      }

      ElMessage.success('登录成功');
      
      // 获取重定向地址
      const redirect = router.currentRoute.value.query.redirect || '/dashboard';
      router.push(redirect);
    } else {
      error.value = res.msg || '登录失败，请稍后再试';
    }
  } catch (e) {
    console.error('Login error:', e);
    error.value = e?.response?.data?.msg || e.message || '登录失败，请稍后再试';
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="login-page">
    <div class="glow"></div>
    <div class="login-card">
      <div class="brand">
        <span class="logo-joy">Joy</span><span class="logo-rent">Rent</span>
        <p>欢迎回来，请登录后台</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <label>
          <span>账号</span>
          <input
            v-model="form.username"
            type="text"
            placeholder="请输入管理员账号"
            autocomplete="username"
          >
        </label>

        <label>
          <span>密码</span>
          <input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            autocomplete="current-password"
          >
        </label>

        <div class="form-extra">
          <label class="remember">
            <input type="checkbox" v-model="rememberMe">
            <span>记住我</span>
          </label>
          <button type="button" class="link">忘记密码？</button>
        </div>

        <button class="btn btn-primary submit-btn" type="submit" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>

        <p v-if="error" class="error-text">{{ error }}</p>
      </form>

      <p class="tips">测试账号：admin / 密码：123456</p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  background: radial-gradient(circle at top, rgba(139, 92, 246, 0.3), transparent 60%) #0f172a;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

.glow {
  position: absolute;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.35), transparent 60%);
  top: -100px;
  right: -100px;
  filter: blur(40px);
  opacity: 0.8;
}

.login-card {
  width: 420px;
  background-color: rgba(30, 41, 59, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 2.5rem;
  box-shadow: 0 30px 80px rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
}

.brand {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-joy {
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-text-primary);
}

.logo-rent {
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-accent);
  margin-left: 0.25rem;
}

.brand p {
  margin-top: 0.5rem;
  color: var(--color-text-secondary);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.login-form label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.login-form input[type="text"],
.login-form input[type="password"] {
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 12px;
  padding: 0.85rem 1rem;
  background-color: rgba(15, 23, 42, 0.6);
  color: var(--color-text-primary);
  font-size: 0.95rem;
  transition: border 0.2s, box-shadow 0.2s;
}

.login-form input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
}

.form-extra {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.remember {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.remember input {
  accent-color: var(--color-accent);
}

.link {
  background: none;
  color: var(--color-accent);
  font-size: 0.85rem;
  text-decoration: underline;
  padding: 0;
}

.submit-btn {
  width: 100%;
  margin-top: 0.5rem;
  border-radius: 12px;
  font-size: 1rem;
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-text {
  margin-top: 0.5rem;
  color: var(--color-danger);
  text-align: center;
}

.tips {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

@media (max-width: 520px) {
  .login-card {
    width: 100%;
    padding: 2rem;
  }
}
</style>

