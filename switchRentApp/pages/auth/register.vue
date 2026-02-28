<template>
  <view class="register-page">
    <view class="register-container">
      <!-- Logo 和标题 -->
      <view class="header">
        <text class="brand">Joy Rent</text>
        <text class="slogan">欢迎注册 · 开启租赁之旅</text>
      </view>

      <!-- 注册表单 -->
      <view class="form">
        <view class="input-group">
          <view class="input-icon">📱</view>
          <input 
            class="input" 
            v-model="phone" 
            type="text" 
            placeholder="请输入手机号"
            maxlength="11"
          />
        </view>

        <view class="input-group code-group">
          <view class="input-icon">🔐</view>
          <input 
            class="input" 
            v-model="code" 
            type="text" 
            placeholder="请输入验证码"
            maxlength="6"
          />
          <button 
            class="code-btn" 
            @tap="sendCode" 
            :disabled="codeCountdown > 0"
          >
            {{ codeCountdown > 0 ? `${codeCountdown}秒后重试` : '获取验证码' }}
          </button>
        </view>

        <view class="input-group">
          <view class="input-icon">🔒</view>
          <input 
            class="input" 
            v-model="password" 
            :type="showPassword ? 'text' : 'password'" 
            placeholder="请设置密码（至少6位）"
          />
          <view class="toggle-password" @tap="showPassword = !showPassword">
            {{ showPassword ? '👁️' : '👁️‍🗨️' }}
          </view>
        </view>

        <view class="input-group">
          <view class="input-icon">🔒</view>
          <input 
            class="input" 
            v-model="confirmPassword" 
            :type="showConfirmPassword ? 'text' : 'password'" 
            placeholder="请再次输入密码"
          />
          <view class="toggle-password" @tap="showConfirmPassword = !showConfirmPassword">
            {{ showConfirmPassword ? '👁️' : '👁️‍🗨️' }}
          </view>
        </view>

        <view class="agreement">
          <view class="checkbox-wrapper" @tap="agreed = !agreed">
            <view :class="['checkbox', agreed ? 'checked' : '']">
              <text v-if="agreed">✓</text>
            </view>
            <text class="agreement-text">
              我已阅读并同意
              <text class="link" @tap.stop="showAgreement('user')">《用户协议》</text>
              和
              <text class="link" @tap.stop="showAgreement('privacy')">《隐私政策》</text>
            </text>
          </view>
        </view>

        <button class="register-btn" @tap="handleRegister" :disabled="loading">
          {{ loading ? '注册中...' : '立即注册' }}
        </button>

        <view class="login-tip">
          已有账号？
          <text class="link" @tap="goToLogin">立即登录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      phone: '',
      code: '',
      password: '',
      confirmPassword: '',
      showPassword: false,
      showConfirmPassword: false,
      agreed: false,
      loading: false,
      codeCountdown: 0,
      countdownTimer: null
    };
  },
  methods: {
    sendCode() {
      // 验证手机号
      if (!this.phone) {
        uni.showToast({
          title: '请输入手机号',
          icon: 'none'
        });
        return;
      }
      
      if (!/^1[3-9]\d{9}$/.test(this.phone)) {
        uni.showToast({
          title: '手机号格式不正确',
          icon: 'none'
        });
        return;
      }

      // TODO: 调用发送验证码 API
      // import { sendCode } from '@/api/auth';
      // sendCode(this.phone).then(res => {
      //   if (res.code === 200) {
      //     uni.showToast({ title: '验证码已发送', icon: 'success' });
      //     this.startCountdown();
      //   }
      // });

      // 模拟发送验证码
      uni.showToast({
        title: '验证码已发送',
        icon: 'success'
      });
      this.startCountdown();
    },

    startCountdown() {
      this.codeCountdown = 60;
      this.countdownTimer = setInterval(() => {
        this.codeCountdown--;
        if (this.codeCountdown <= 0) {
          clearInterval(this.countdownTimer);
        }
      }, 1000);
    },

    handleRegister() {
      // 表单验证
      if (!this.phone) {
        uni.showToast({
          title: '请输入手机号',
          icon: 'none'
        });
        return;
      }

      if (!/^1[3-9]\d{9}$/.test(this.phone)) {
        uni.showToast({
          title: '手机号格式不正确',
          icon: 'none'
        });
        return;
      }

      if (!this.code) {
        uni.showToast({
          title: '请输入验证码',
          icon: 'none'
        });
        return;
      }

      if (!this.password) {
        uni.showToast({
          title: '请设置密码',
          icon: 'none'
        });
        return;
      }

      if (this.password.length < 6) {
        uni.showToast({
          title: '密码至少6位',
          icon: 'none'
        });
        return;
      }

      if (this.password !== this.confirmPassword) {
        uni.showToast({
          title: '两次密码不一致',
          icon: 'none'
        });
        return;
      }

      if (!this.agreed) {
        uni.showToast({
          title: '请先阅读并同意用户协议',
          icon: 'none'
        });
        return;
      }

      // 发送注册请求
      this.loading = true;

      // TODO: 调用注册 API
      // import { register } from '@/api/auth';
      // register({ phone: this.phone, code: this.code, password: this.password })
      //   .then(res => {
      //     if (res.code === 200) {
      //       uni.showToast({ title: '注册成功', icon: 'success' });
      //       setTimeout(() => {
      //         uni.navigateBack();
      //       }, 1500);
      //     }
      //   })
      //   .finally(() => {
      //     this.loading = false;
      //   });

      // 模拟注册
      setTimeout(() => {
        this.loading = false;
        uni.showToast({
          title: '注册成功',
          icon: 'success'
        });
        
        setTimeout(() => {
          uni.navigateBack();
        }, 1500);
      }, 1500);
    },

    showAgreement(type) {
      uni.showToast({
        title: type === 'user' ? '查看用户协议' : '查看隐私政策',
        icon: 'none'
      });
    },

    goToLogin() {
      uni.navigateBack();
    }
  },

  beforeDestroy() {
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer);
    }
  }
};
</script>

<style lang="scss" scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40rpx;
  box-sizing: border-box;
}

.register-container {
  width: 100%;
  max-width: 600rpx;
  background: #fff;
  border-radius: 32rpx;
  padding: 60rpx 48rpx;
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.2);
}

.header {
  text-align: center;
  margin-bottom: 60rpx;
}

.brand {
  display: block;
  font-size: 56rpx;
  font-weight: 900;
  color: #667eea;
  margin-bottom: 16rpx;
  letter-spacing: -1px;
  font-style: italic;
}

.slogan {
  display: block;
  font-size: 28rpx;
  color: #666;
}

.form {
  margin-bottom: 24rpx;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
  background: #f5f7fa;
  border-radius: 16rpx;
  padding: 0 24rpx;
  margin-bottom: 24rpx;
  height: 96rpx;
}

.code-group {
  padding-right: 0;
}

.input-icon {
  font-size: 36rpx;
  margin-right: 16rpx;
}

.input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
  height: 100%;
}

.toggle-password {
  font-size: 28rpx;
  padding: 0 8rpx;
}

.code-btn {
  margin: 0;
  padding: 0 24rpx;
  height: 96rpx;
  line-height: 96rpx;
  background: transparent;
  color: #667eea;
  font-size: 24rpx;
  border: none;
  white-space: nowrap;
}

.code-btn[disabled] {
  color: #999;
}

.agreement {
  margin-bottom: 32rpx;
}

.checkbox-wrapper {
  display: flex;
  align-items: flex-start;
}

.checkbox {
  width: 36rpx;
  height: 36rpx;
  border: 2rpx solid #ddd;
  border-radius: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  color: #fff;
  flex-shrink: 0;
  margin-right: 12rpx;
  margin-top: 4rpx;
}

.checkbox.checked {
  background: #667eea;
  border-color: #667eea;
}

.agreement-text {
  font-size: 24rpx;
  color: #666;
  line-height: 1.6;
}

.link {
  color: #667eea;
  font-weight: 600;
}

.register-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 32rpx;
  font-weight: 700;
  border-radius: 16rpx;
  border: none;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 24rpx rgba(102, 126, 234, 0.4);
}

.register-btn:active {
  opacity: 0.9;
  transform: scale(0.98);
}

.register-btn[disabled] {
  opacity: 0.6;
}

.login-tip {
  text-align: center;
  font-size: 26rpx;
  color: #666;
}
</style>
