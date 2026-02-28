<template>
  <view class="login-page">
    <!-- 背景动画 -->
    <view class="login-bg">
      <view class="bg-grid"></view>
      <view class="bg-glow orb-1"></view>
      <view class="bg-glow orb-2"></view>
      <view class="bg-glow orb-3"></view>
    </view>
    
    <view class="login-container">
      <!-- Logo -->
      <view class="brand-section">
        <view class="brand-icon">🎮</view>
        <text class="brand-name">JOYRENT</text>
        <text class="brand-slogan">游戏租赁 · 随租随玩</text>
      </view>

      <!-- 登录表单 -->
      <view class="form-section">
        <view class="input-group">
          <text class="input-icon">📱</text>
          <input 
            class="input" 
            v-model="phone" 
            type="number" 
            placeholder="请输入手机号"
            maxlength="11"
            placeholder-class="placeholder"
          />
        </view>

        <view class="input-group">
          <text class="input-icon">🔒</text>
          <input 
            class="input" 
            v-model="password" 
            :type="showPassword ? 'text' : 'password'" 
            placeholder="请输入密码"
            placeholder-class="placeholder"
          />
          <view class="toggle-password" @tap="showPassword = !showPassword">
            <text>{{ showPassword ? '👁️' : '👁️‍🗨️' }}</text>
          </view>
        </view>

        <view class="options-row">
          <view class="remember-me" @tap="rememberMe = !rememberMe">
            <view class="checkbox" :class="{ checked: rememberMe }">
              <text v-if="rememberMe" class="check-icon">✓</text>
            </view>
            <text class="option-text">记住密码</text>
          </view>
          <text class="forgot-link" @tap="handleForgetPassword">忘记密码？</text>
        </view>

        <button class="login-btn" @tap="handleLogin" :disabled="loading">
          <text v-if="!loading" class="btn-text">登 录</text>
          <view v-else class="btn-loading">
            <view class="loading-dot"></view>
            <view class="loading-dot"></view>
            <view class="loading-dot"></view>
          </view>
        </button>

        <view class="register-link">
          还没有账号？
          <text class="link-text" @tap="handleRegister">立即注册</text>
        </view>
      </view>

      <!-- 其他登录方式 -->
      <view class="divider">
        <view class="divider-line"></view>
        <text class="divider-text">其他方式登录</text>
        <view class="divider-line"></view>
      </view>

      <view class="social-login">
        <view class="social-item" @tap="handleSocialLogin('wechat')">
          <view class="social-icon wechat">
            <text>💬</text>
          </view>
          <text class="social-text">微信</text>
        </view>
        <view class="social-item" @tap="handleSocialLogin('face')">
          <view class="social-icon face">
            <text>👤</text>
          </view>
          <text class="social-text">人脸</text>
        </view>
        <view class="social-item" @tap="handleSocialLogin('phone')">
          <view class="social-icon phone">
            <text>📞</text>
          </view>
          <text class="social-text">验证码</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { userLogin } from '@/api/user';
import { mapActions } from 'vuex';

export default {
  data() {
    return {
      phone: '',
      password: '',
      showPassword: false,
      rememberMe: false,
      loading: false
    };
  },
  onLoad() {
    const savedPhone = uni.getStorageSync('savedPhone');
    const savedPassword = uni.getStorageSync('savedPassword');
    
    if (savedPhone && savedPassword) {
      this.phone = savedPhone;
      this.password = savedPassword;
      this.rememberMe = true;
    }
  },
  methods: {
    ...mapActions(['login']),
    
    async handleLogin() {
      if (!this.phone) {
        uni.showToast({ title: '请输入手机号', icon: 'none' });
        return;
      }
      
      if (!/^1[3-9]\d{9}$/.test(this.phone)) {
        uni.showToast({ title: '手机号格式不正确', icon: 'none' });
        return;
      }

      if (!this.password) {
        uni.showToast({ title: '请输入密码', icon: 'none' });
        return;
      }

      if (this.password.length < 6) {
        uni.showToast({ title: '密码至少6位', icon: 'none' });
        return;
      }

      this.loading = true;
      
      try {
        const res = await userLogin({
          phone: this.phone,
          password: this.password
        });
        
        if (res.code === 200) {
          this.login({
            token: res.data.token,
            userInfo: res.data.user
          });
          
          if (this.rememberMe) {
            uni.setStorageSync('savedPhone', this.phone);
            uni.setStorageSync('savedPassword', this.password);
          } else {
            uni.removeStorageSync('savedPhone');
            uni.removeStorageSync('savedPassword');
          }
          
          uni.showToast({ title: '登录成功', icon: 'success' });
          
          setTimeout(() => {
            uni.switchTab({ url: '/pages/index/index' });
          }, 1000);
        } else {
          uni.showToast({ title: res.msg || '登录失败', icon: 'none' });
        }
      } catch (error) {
        uni.showToast({ title: error.msg || '网络错误', icon: 'none' });
      } finally {
        this.loading = false;
      }
    },

    handleForgetPassword() {
      uni.showToast({ title: '请联系客服重置密码', icon: 'none' });
    },

    handleRegister() {
      uni.navigateTo({ url: '/pages/auth/register' });
    },

    handleSocialLogin(type) {
      if (type === 'face') {
        uni.navigateTo({ url: '/pages/auth/face' });
      } else {
        const name = type === 'wechat' ? '微信' : '验证码';
        uni.showToast({ title: `${name}登录暂未开放`, icon: 'none' });
      }
    }
  }
};
</script>

<style lang="scss">
$neon-purple: #b026ff;
$neon-cyan: #00f5ff;
$neon-pink: #ff0080;
$bg-primary: #0a0a0f;
$bg-secondary: #12121a;
$text-primary: #ffffff;
$text-secondary: rgba(255, 255, 255, 0.85);
$text-muted: rgba(255, 255, 255, 0.5);
$border-color: rgba(255, 255, 255, 0.08);
$gradient-primary: linear-gradient(135deg, $neon-purple 0%, $neon-cyan 100%);

.login-page {
  min-height: 100vh;
  background: $bg-primary;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40rpx;
  box-sizing: border-box;
  position: relative;
  overflow: hidden;
}

// 背景动画
.login-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  
  .bg-grid {
    position: absolute;
    inset: 0;
    background: 
      linear-gradient(rgba(0, 245, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 245, 255, 0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: grid-move 20s linear infinite;
  }
  
  .bg-glow {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.4;
    animation: float 10s ease-in-out infinite;
  }
  
  .orb-1 {
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, $neon-purple 0%, transparent 70%);
    top: -100px;
    right: -100px;
    animation-delay: 0s;
  }
  
  .orb-2 {
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, $neon-cyan 0%, transparent 70%);
    bottom: 100px;
    left: -100px;
    animation-delay: -3s;
  }
  
  .orb-3 {
    width: 250px;
    height: 250px;
    background: radial-gradient(circle, $neon-pink 0%, transparent 70%);
    bottom: -50px;
    right: 20%;
    animation-delay: -6s;
  }
}

@keyframes grid-move {
  0% { transform: translateY(0); }
  100% { transform: translateY(60px); }
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-30px) scale(1.1); }
}

// 登录容器
.login-container {
  width: 100%;
  max-width: 600rpx;
  position: relative;
  z-index: 1;
}

// 品牌区域
.brand-section {
  text-align: center;
  margin-bottom: 80rpx;
  
  .brand-icon {
    font-size: 80rpx;
    margin-bottom: 24rpx;
    display: block;
    animation: bounce 2s ease-in-out infinite;
  }
  
  .brand-name {
    display: block;
    font-size: 56rpx;
    font-weight: 900;
    background: $gradient-primary;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    letter-spacing: 4rpx;
    margin-bottom: 16rpx;
  }
  
  .brand-slogan {
    display: block;
    font-size: 28rpx;
    color: $text-muted;
    letter-spacing: 4rpx;
  }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10rpx); }
}

// 表单区域
.form-section {
  margin-bottom: 48rpx;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20rpx;
  padding: 0 28rpx;
  margin-bottom: 28rpx;
  height: 100rpx;
  transition: all 0.3s ease;
  
  &:focus-within {
    border-color: rgba(0, 245, 255, 0.4);
    box-shadow: 0 0 30rpx rgba(0, 245, 255, 0.1);
    background: rgba(255, 255, 255, 0.05);
  }
}

.input-icon {
  font-size: 36rpx;
  margin-right: 20rpx;
  opacity: 0.7;
}

.input {
  flex: 1;
  font-size: 30rpx;
  color: $text-primary;
  height: 100%;
  background: transparent;
}

.placeholder {
  color: $text-muted;
}

.toggle-password {
  font-size: 32rpx;
  padding: 20rpx;
  opacity: 0.7;
}

// 选项行
.options-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 48rpx;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.checkbox {
  width: 36rpx;
  height: 36rpx;
  border: 2rpx solid rgba(255, 255, 255, 0.2);
  border-radius: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  
  &.checked {
    background: $gradient-primary;
    border-color: transparent;
  }
  
  .check-icon {
    font-size: 22rpx;
    color: white;
    font-weight: 700;
  }
}

.option-text {
  font-size: 26rpx;
  color: $text-secondary;
}

.forgot-link {
  font-size: 26rpx;
  color: $neon-cyan;
  font-weight: 600;
}

// 登录按钮
.login-btn {
  width: 100%;
  height: 100rpx;
  background: $gradient-primary;
  border-radius: 20rpx;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 40rpx rgba(176, 38, 255, 0.4);
  margin-bottom: 32rpx;
  position: relative;
  overflow: hidden;
  
  &::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transform: translateX(-100%);
    transition: transform 0.5s ease;
  }
  
  &:active::after {
    transform: translateX(100%);
  }
  
  &:active {
    transform: scale(0.98);
    box-shadow: 0 4rpx 20rpx rgba(176, 38, 255, 0.3);
  }
  
  &[disabled] {
    opacity: 0.7;
  }
  
  .btn-text {
    font-size: 32rpx;
    font-weight: 800;
    color: white;
    letter-spacing: 8rpx;
  }
}

.btn-loading {
  display: flex;
  gap: 12rpx;
  
  .loading-dot {
    width: 12rpx;
    height: 12rpx;
    background: white;
    border-radius: 50%;
    animation: loading-bounce 1.4s ease-in-out infinite both;
    
    &:nth-child(1) { animation-delay: -0.32s; }
    &:nth-child(2) { animation-delay: -0.16s; }
  }
}

@keyframes loading-bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

// 注册链接
.register-link {
  text-align: center;
  font-size: 26rpx;
  color: $text-muted;
  
  .link-text {
    color: $neon-cyan;
    font-weight: 700;
    margin-left: 8rpx;
  }
}

// 分隔线
.divider {
  display: flex;
  align-items: center;
  margin-bottom: 40rpx;
  
  .divider-line {
    flex: 1;
    height: 1rpx;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  }
  
  .divider-text {
    font-size: 24rpx;
    color: $text-muted;
    padding: 0 24rpx;
  }
}

// 社交登录
.social-login {
  display: flex;
  justify-content: center;
  gap: 64rpx;
}

.social-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}

.social-icon {
  width: 100rpx;
  height: 100rpx;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44rpx;
  transition: all 0.3s ease;
  
  &:active {
    transform: scale(0.95);
    background: rgba(255, 255, 255, 0.1);
  }
  
  &.wechat:active {
    border-color: rgba(0, 255, 0, 0.3);
    box-shadow: 0 0 30rpx rgba(0, 255, 0, 0.1);
  }
  
  &.face:active {
    border-color: rgba(0, 245, 255, 0.3);
    box-shadow: 0 0 30rpx rgba(0, 245, 255, 0.1);
  }
  
  &.phone:active {
    border-color: rgba(255, 138, 0, 0.3);
    box-shadow: 0 0 30rpx rgba(255, 138, 0, 0.1);
  }
}

.social-text {
  font-size: 24rpx;
  color: $text-muted;
}
</style>