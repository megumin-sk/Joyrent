<template>
  <view class="container">
    <view class="header">
      <text class="title">人脸管理</text>
      <text class="subtitle">用于人脸识别登录及安全验证</text>
    </view>

    <view class="status-card" :class="{ 'is-registered': isRegistered }">
      <view class="status-icon">
        <text v-if="isRegistered" class="icon">✅</text>
        <text v-else class="icon">🔍</text>
      </view>
      <view class="status-info">
        <text class="status-text">{{ isRegistered ? '已启用人脸识别' : '未注册人脸数据' }}</text>
        <text class="status-desc">{{ isRegistered ? '您可以使用人脸识别快速登录系统' : '注册人脸后可开启更便捷的登录体验' }}</text>
      </view>
    </view>

    <view class="action-section">
      <block v-if="!isRegistered">
        <view class="camera-preview-box">
          <camera
            v-if="showCamera"
            class="camera"
            device-position="front"
            flash="off"
            @error="onCameraError"
          >
            <cover-view class="face-guide">
              <cover-view class="guide-circle"></cover-view>
            </cover-view>
          </camera>
          <image v-else-if="tempPhoto" :src="tempPhoto" class="camera" mode="aspectFill"></image>
          <view v-else class="camera-placeholder" @tap="startRegister">
            <text class="plus">+</text>
            <text class="placeholder-text">点击开始录入人脸</text>
          </view>
        </view>

        <view class="btns" v-if="showCamera">
          <button class="primary-btn" @tap="takePhoto">拍照采样</button>
        </view>
        <view class="btns" v-if="tempPhoto && !showCamera">
          <button class="secondary-btn" @tap="reset">重新拍摄</button>
          <button class="primary-btn" :loading="loading" @tap="submitRegister">立即注册</button>
        </view>
      </block>

      <block v-else>
        <view class="manage-btns">
          <button class="danger-btn" @tap="handleDelete">删除人脸数据</button>
          <text class="warning-tip">删除后将无法使用人脸登录功能</text>
        </view>
      </block>
    </view>
  </view>
</template>

<script>
import { mapGetters } from 'vuex';
import { registerFace, deleteFace, getFaceStatus } from '@/api/face';

export default {
  data() {
    return {
      showCamera: false,
      tempPhoto: '',
      loading: false,
      isRegistered: false
    };
  },
  computed: {
    ...mapGetters(['userInfo'])
  },
  onLoad() {

    this.checkStatus();
  },
  methods: {
    async checkStatus() {
      if (!this.userInfo || !this.userInfo.id) return;
      
      try {
        const res = await getFaceStatus(this.userInfo.id);
        if (res.code === 200) {
          this.isRegistered = !!res.data;
          // 同时同步到 store 保持一致
          this.$store.dispatch('updateUserInfo', { ...this.userInfo, face_enabled: this.isRegistered });
        }
      } catch (e) {
        console.error('获取人脸状态失败', e);
      }
    },
    startRegister() {
      this.showCamera = true;
    },
    onCameraError(e) {
      uni.showModal({
        title: '提示',
        content: '相机授权失败，请检查设置',
        showCancel: false
      });
    },
    takePhoto() {
      const ctx = uni.createCameraContext();
      ctx.takePhoto({
        quality: 'high',
        success: (res) => {
          this.tempPhoto = res.tempImagePath;
          this.showCamera = false;
        }
      });
    },
    reset() {
      this.tempPhoto = '';
      this.showCamera = true;
    },
    async submitRegister() {
      if (this.loading) return;
      this.loading = true;
      
      try {
        const base64 = await this.pathToBase64(this.tempPhoto);
        const res = await registerFace(base64, this.userInfo.id);
        console.log(res);
        
        if (res.code === 200) {
          uni.showToast({ title: '人脸注册成功', icon: 'success' });
          this.isRegistered = true;
          this.tempPhoto = '';
          // 更新用户信息
          this.$store.dispatch('updateUserInfo', { ...this.userInfo, face_enabled: true });
        } else {
          uni.showToast({ title: res.msg || '注册失败', icon: 'none' });
        }
      } catch (e) {
        uni.showToast({ title: '网络错误', icon: 'none' });
      } finally {
        this.loading = false;
      }
    },
    handleDelete() {
      uni.showModal({
        title: '警告',
        content: '确定要删除您的人脸数据吗？',
        confirmColor: '#ff4d4f',
        success: async (res) => {
          if (res.confirm) {
            try {
              const resDelete = await deleteFace(this.userInfo.id);
              if (resDelete.code === 200) {
                uni.showToast({ title: '已删除' });
                this.isRegistered = false;
                this.$store.dispatch('updateUserInfo', { ...this.userInfo, face_enabled: false });
              }
            } catch (e) {
              uni.showToast({ title: '请求失败', icon: 'none' });
            }
          }
        }
      });
    },
    pathToBase64(path) {
      return new Promise((resolve, reject) => {
        uni.getFileSystemManager().readFile({
          filePath: path,
          encoding: 'base64',
          success: (res) => resolve(res.data),
          fail: (err) => reject(err)
        });
      });
    }
  }
};
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: #f8f9fc;
  padding: 40rpx 32rpx;
}

.header {
  margin-bottom: 60rpx;
  .title {
    font-size: 44rpx;
    font-weight: bold;
    color: #1a1a1a;
    display: block;
    margin-bottom: 12rpx;
  }
  .subtitle {
    font-size: 26rpx;
    color: #999;
  }
}

.status-card {
  background: #fff;
  border-radius: 32rpx;
  padding: 48rpx;
  display: flex;
  align-items: center;
  margin-bottom: 60rpx;
  box-shadow: 0 8rpx 30rpx rgba(0,0,0,0.03);
  border: 1rpx solid #efefef;
  
  &.is-registered {
    background: linear-gradient(135deg, #7c4dff, #b388ff);
    .status-text, .status-desc { color: #fff; }
    .icon { background: rgba(255,255,255,0.2); }
  }

  .status-icon {
    width: 100rpx;
    height: 100rpx;
    border-radius: 50%;
    background: #f0f2f5;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 32rpx;
    
    .icon { font-size: 48rpx; }
  }

  .status-info {
    flex: 1;
    .status-text {
      font-size: 34rpx;
      font-weight: bold;
      color: #333;
      display: block;
      margin-bottom: 8rpx;
    }
    .status-desc {
      font-size: 24rpx;
      color: #999;
    }
  }
}

.camera-preview-box {
  width: 500rpx;
  height: 500rpx;
  margin: 0 auto 60rpx;
  border-radius: 50%;
  overflow: hidden;
  background: #eee;
  position: relative;
  box-shadow: 0 0 0 10rpx #fff, 0 20rpx 40rpx rgba(0,0,0,0.08);

  .camera { width: 100%; height: 100%; }
  
  .camera-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #fff;
    
    .plus { font-size: 80rpx; color: #7c4dff; margin-bottom: 20rpx; }
    .placeholder-text { font-size: 26rpx; color: #999; }
  }
}

.face-guide {
  width: 100%;
  height: 100%;
}
.guide-circle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 350rpx;
  height: 350rpx;
  border-radius: 50%;
  border: 4rpx dashed #7c4dff;
}

.btns {
  display: flex;
  gap: 30rpx;
  padding: 0 40rpx;
}

.primary-btn {
  flex: 1;
  background: #7c4dff;
  color: #fff;
  border-radius: 50rpx;
  font-weight: bold;
  height: 100rpx;
  line-height: 100rpx;
}

.secondary-btn {
  flex: 1;
  background: #f0f2f5;
  color: #333;
  border-radius: 50rpx;
  height: 100rpx;
  line-height: 100rpx;
}

.manage-btns {
  padding: 40rpx;
  text-align: center;
  
  .danger-btn {
    background: #fff;
    color: #ff4d4f;
    border: 2rpx solid #ff4d4f;
    border-radius: 50rpx;
    margin-bottom: 24rpx;
  }
  .warning-tip {
    font-size: 24rpx;
    color: #999;
  }
}
</style>
