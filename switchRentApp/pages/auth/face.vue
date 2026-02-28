<template>
  <view class="face-login-container">
    <view class="title-section">
      <text class="main-title">人脸识别登录</text>
      <text class="sub-title">系统将自动识别您的身份</text>
    </view>

    <view class="camera-wrapper">
      <camera
          v-if="!capturedImage"
          class="camera"
          device-position="front"
          flash="off"
          @error="onCameraError"
      >
        <cover-view class="face-frame">
          <cover-view class="corner corner-tl"></cover-view>
          <cover-view class="corner corner-tr"></cover-view>
          <cover-view class="corner corner-bl"></cover-view>
          <cover-view class="corner corner-br"></cover-view>
          <cover-view class="scan-line" v-if="loading"></cover-view>
        </cover-view>
      </camera>

      <image
          v-else
          class="captured-preview"
          :src="capturedImage"
          mode="aspectFill"
      ></image>
    </view>

    <view class="tips-section">
      <text class="tips-text" :class="{ 'loading-text': loading }">{{ tipsText }}</text>
    </view>

    <view class="button-section">
      <button
          v-if="!capturedImage"
          class="capture-btn"
          hover-class="btn-hover"
          :disabled="loading"
          @click="capturePhoto"
      >
        <view class="btn-content">
          <text class="icon">📸</text>
          <text>{{ loading ? '识别中...' : '开始识别' }}</text>
        </view>
      </button>

      <view v-else class="action-buttons">
        <button class="retry-btn" hover-class="btn-hover" @click="retryCapture" :disabled="loading">
          <text>重拍</text>
        </button>
        <button class="confirm-btn" hover-class="btn-hover" @click="confirmLogin" :disabled="loading">
          <text>{{ loading ? '验证中...' : '确认登录' }}</text>
        </button>
      </view>
    </view>

    <view v-if="errorMessage" class="error-toast">
      <text class="error-icon">⚠️</text>
      <text>{{ errorMessage }}</text>
    </view>

    <view class="back-login" @click="backToLogin">
      <text class="back-text">账号密码登录</text>
    </view>
  </view>
</template>

<script>
import { loginByFace } from '@/api/face';
import { mapActions } from 'vuex';

export default {
  data() {
    return {
      loading: false,
      capturedImage: '',
      errorMessage: '',
      tipsText: '请保持正脸出现在取景框中'
    };
  },

  methods: {
    ...mapActions(['login']),

    capturePhoto() {
      this.errorMessage = '';
      const ctx = uni.createCameraContext();

      ctx.takePhoto({
        quality: 'normal',
        success: (res) => {
          this.capturedImage = res.tempImagePath;
          this.tipsText = '照片已就绪，请点击“确认登录”';
        },
        fail: (err) => {
          console.error('拍照失败:', err);
          this.errorMessage = '无法调用摄像头，请检查权限';
        }
      });
    },

    retryCapture() {
      this.capturedImage = '';
      this.errorMessage = '';
      this.tipsText = '请保持正脸出现在取景框中';
    },

    async confirmLogin() {
      if (!this.capturedImage || this.loading) return;

      this.loading = true;
      this.errorMessage = '';
      // 修改处：去掉了“生物特征比对”的字样，改为简洁的提示
      this.tipsText = '正在识别中...';

      try {
        const base64Data = await this.imageToBase64(this.capturedImage);

        // 发起请求（注意：后端为了测试 Sentinel 这里会睡 3 秒）
        const res = await loginByFace(base64Data);

        console.log('API响应:', res);

        if (res.code === 200 && res.data) {
          const { user, token, fallback, score } = res.data;

          // 核心：阈值判断 (百度建议阈值 80)
          if (score !== undefined && score < 90) {
            this.errorMessage = `匹配度不足(${score.toFixed(2)}), 请正对摄像头重试`;
            this.tipsText = '识别失败';
            this.loading = false;
            return;
          }

          // 核心：Sentinel 降级提示
          if (fallback === true) {
            uni.showToast({
              title: '云端繁忙，已切换至本地引擎',
              icon: 'none',
              duration: 3000
            });
          }

          this.login({
            token: token,
            userInfo: user
          });

          if (res.data.face_id) {
            uni.setStorageSync('faceId', res.data.face_id);
          }

          uni.showToast({
            title: `欢迎回来，${user.nickname || user.username}`,
            icon: 'success',
            duration: 2000
          });

          setTimeout(() => {
            uni.switchTab({ url: '/pages/index/index' });
          }, 1500);

        } else {
          this.errorMessage = res.msg || '无法识别您的身份，请重试';
          this.tipsText = '识别失败';
        }

      } catch (err) {
        console.error('登录异常:', err);
        // 如果后端 sleep 时间过长导致前端超时
        this.errorMessage = '网络连接超时或服务繁忙';
        this.tipsText = '请点击重试或使用密码登录';
      } finally {
        this.loading = false;
      }
    },

    imageToBase64(path) {
      return new Promise((resolve, reject) => {
        if (!path) reject(new Error('图片路径为空'));

        uni.getFileSystemManager().readFile({
          filePath: path,
          encoding: 'base64',
          success: (res) => {
            resolve(res.data);
          },
          fail: (err) => {
            reject(err);
          }
        });
      });
    },

    onCameraError(e) {
      this.errorMessage = '摄像头权限被拒绝';
      uni.showModal({
        title: '提示',
        content: '请在设置中开启摄像头权限以使用人脸登录',
        showCancel: false
      });
    },

    backToLogin() {
      uni.navigateBack();
    }
  }
};
</script>

<style scoped>
.face-login-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 40rpx;
  box-sizing: border-box;
}

.title-section {
  text-align: center;
  margin-bottom: 60rpx;
}

.main-title {
  display: block;
  font-size: 44rpx;
  color: #fff;
  font-weight: 600;
  margin-bottom: 16rpx;
}

.sub-title {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.6);
}

.camera-wrapper {
  width: 500rpx;
  height: 500rpx;
  border-radius: 50%;
  overflow: hidden;
  position: relative;
  border: 4rpx solid rgba(74, 222, 128, 0.3);
  box-shadow: 0 0 40rpx rgba(74, 222, 128, 0.1);
  background: #000;
}

.camera, .captured-preview {
  width: 100%;
  height: 100%;
}

.face-frame {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  box-sizing: border-box;
}

.scan-line {
  position: absolute;
  width: 100%;
  height: 4rpx;
  background: #4ade80;
  top: 0;
  animation: scan 2s linear infinite;
  box-shadow: 0 0 10rpx #4ade80;
}

@keyframes scan {
  0% { top: 0; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { top: 100%; opacity: 0; }
}

.tips-section {
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 40rpx 0;
}

.tips-text {
  color: #fff;
  font-size: 28rpx;
  transition: all 0.3s;
}

.loading-text {
  color: #4ade80;
}

.button-section {
  width: 100%;
  margin-bottom: 40rpx;
}

.capture-btn {
  width: 80%;
  height: 100rpx;
  background: linear-gradient(90deg, #4ade80, #22c55e);
  border-radius: 50rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 32rpx;
  font-weight: bold;
  box-shadow: 0 10rpx 20rpx rgba(34, 197, 94, 0.3);
  border: none;
}

.action-buttons {
  display: flex;
  justify-content: space-between;
  width: 90%;
  margin: 0 auto;
}

.retry-btn, .confirm-btn {
  width: 45%;
  height: 90rpx;
  border-radius: 45rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
}

.retry-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 2rpx solid rgba(255, 255, 255, 0.2);
}

.confirm-btn {
  background: #4ade80;
  color: #fff;
}

.btn-hover {
  opacity: 0.9;
  transform: scale(0.98);
}

.error-toast {
  background: rgba(239, 68, 68, 0.2);
  padding: 20rpx 40rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.error-icon {
  margin-right: 12rpx;
}

.error-toast text {
  color: #fca5a5;
  font-size: 26rpx;
}

.back-login {
  margin-top: auto;
  padding: 20rpx;
}

.back-text {
  color: rgba(255, 255, 255, 0.5);
  font-size: 26rpx;
  text-decoration: underline;
}
</style>