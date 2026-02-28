<template>
  <view class="page-container">
    <view class="page-bg"></view>
    
    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
      <view class="nav-content">
        <text class="nav-title">个人中心</text>
      </view>
    </view>

    <view class="nav-placeholder" :style="{ height: (statusBarHeight + 44) + 'px' }"></view>

    <!-- 用户信息卡片 -->
    <view class="profile-card" @tap="handleUserInfo">
      <view class="card-glow"></view>
      <view class="avatar-wrap">
        <image class="avatar" :src="avatarUrl" mode="aspectFill" />
        <view class="avatar-ring"></view>
      </view>
      <view class="profile-info">
        <view class="name-row">
          <text class="nickname">{{ displayName }}</text>
          <view class="verify-badge" v-if="isLoggedIn">
            <text class="badge-icon">✓</text>
            <text>已认证</text>
          </view>
        </view>
        <text class="uid">UID: {{ userInfo.id || '---' }}</text>
      </view>
      <text class="arrow">›</text>
    </view>

    <!-- 资产卡片 -->
    <view class="asset-card">
      <view class="asset-glow"></view>
      <view class="asset-content">
        <view class="asset-label">
          <text class="label-icon">💎</text>
          <text>账户余额</text>
        </view>
        <view class="balance-row">
          <text class="balance-symbol">¥</text>
          <text class="balance-value">{{ displayBalance }}</text>
        </view>
      </view>
      <button class="recharge-btn" @tap="handleRecharge">
        <text>充值</text>
        <text class="btn-arrow">➤</text>
      </button>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-section">
      <view class="menu-title">
        <text class="title-icon">◆</text>
        <text>功能服务</text>
      </view>
      
      <view class="menu-grid">
        <view class="menu-item" @tap="navigateTo('order')">
          <view class="menu-icon-wrap">
            <text class="menu-icon">🧾</text>
          </view>
          <text class="menu-text">我的订单</text>
        </view>
        
        <view class="menu-item" @tap="navigateTo('face')">
          <view class="menu-icon-wrap">
            <text class="menu-icon">👤</text>
          </view>
          <text class="menu-text">人脸管理</text>
        </view>
        
        <view class="menu-item" @tap="navigateTo('address')">
          <view class="menu-icon-wrap">
            <text class="menu-icon">📍</text>
          </view>
          <text class="menu-text">地址管理</text>
        </view>
        
        <view class="menu-item" @tap="handleLogout">
          <view class="menu-icon-wrap logout">
            <text class="menu-icon">⚙</text>
          </view>
          <text class="menu-text">退出登录</text>
        </view>
      </view>
    </view>

    <!-- 会员权益 -->
    <view class="vip-banner" v-if="isLoggedIn">
      <view class="vip-glow"></view>
      <view class="vip-content">
        <view class="vip-left">
          <text class="vip-title">🎮 会员权益</text>
          <text class="vip-desc">享受更多专属优惠和服务</text>
        </view>
        <view class="vip-btn">
          <text>查看</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { getUserImageUrl } from '@/utils/imageUrl';
import { mapGetters, mapActions } from 'vuex';

export default {
  data() {
    return {
      statusBarHeight: 20
    };
  },
  
  computed: {
    ...mapGetters(['userInfo', 'isLoggedIn', 'getToken']),
    
    avatarUrl() {
      if (this.userInfo && this.userInfo.avatar) {
        return getUserImageUrl(this.userInfo.avatar);
      }
      return '/static/default-avatar.png';
    },
    
    displayName() {
      if (!this.userInfo) return '点击登录';
      if (this.userInfo.nickname) {
        return this.userInfo.nickname;
      }
      if (this.userInfo.username) {
        return this.userInfo.username;
      }
      return '点击登录';
    },
    
    displayBalance() {
      return (this.userInfo && this.userInfo.balance) || '0.00';
    }
  },
  
  created() {
    const sysInfo = uni.getSystemInfoSync();
    if (sysInfo.statusBarHeight) {
      this.statusBarHeight = sysInfo.statusBarHeight;
    }
  },
  
  onShow() {
    if (!this.isLoggedIn) {
      uni.showToast({
        title: '请先登录',
        icon: 'none'
      });
      setTimeout(() => {
        uni.reLaunch({
          url: '/pages/auth/login'
        });
      }, 1000);
      return;
    }
  },
  
  methods: {
    ...mapActions(['logout']),
    
    handleUserInfo() {
      if (!this.isLoggedIn) {
        uni.navigateTo({
          url: '/pages/auth/login'
        });
      } else {
        uni.showToast({
          title: '个人资料编辑功能开发中',
          icon: 'none'
        });
      }
    },
    
    handleRecharge() {
      if (!this.isLoggedIn) {
        uni.showToast({ title: '请先登录', icon: 'none' });
        return;
      }
      uni.showToast({ title: '充值功能开发中', icon: 'none' });
    },
    
    navigateTo(type) {
      if (!this.isLoggedIn && ['order', 'address', 'face'].includes(type)) {
        uni.showToast({
          title: '请先登录',
          icon: 'none'
        });
        setTimeout(() => {
          uni.navigateTo({ url: '/pages/auth/login' });
        }, 1500);
        return;
      }
      
      const urls = {
        order: '/pages/order/index',
        face: '/pages/mine/face-manage',
        address: '/pages/address/index'
      };
      
      if(urls[type]) {
        uni.navigateTo({ url: urls[type] });
      } else {
        uni.showToast({ title: '开发中', icon: 'none' });
      }
    },
    
    handleLogout() {
      if (!this.isLoggedIn) {
        uni.showToast({
          title: '您还未登录',
          icon: 'none'
        });
        return;
      }
      
      uni.showModal({
        title: '提示',
        content: '确定要退出登录吗?',
        confirmColor: '#ff0080',
        success: (res) => {
          if (res.confirm) {
            this.logout();
            uni.removeStorageSync('faceId');
            uni.showToast({ 
              title: '已退出登录', 
              icon: 'success' 
            });
          }
        }
      });
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
$bg-card: rgba(20, 20, 35, 0.95);
$text-primary: #ffffff;
$text-secondary: rgba(255, 255, 255, 0.85);
$text-muted: rgba(255, 255, 255, 0.5);
$border-color: rgba(255, 255, 255, 0.08);
$gradient-primary: linear-gradient(135deg, $neon-purple 0%, $neon-cyan 100%);
$gradient-vip: linear-gradient(135deg, #ffea00 0%, #ff8a00 100%);

.page-container {
  min-height: 100vh;
  background-color: $bg-primary;
  position: relative;
  padding-bottom: 40rpx;
}

.page-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: 
      linear-gradient(rgba(0, 245, 255, 0.02) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 245, 255, 0.02) 1px, transparent 1px);
    background-size: 60px 60px;
  }
  
  &::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 50% 0%, rgba(176, 38, 255, 0.1) 0%, transparent 50%);
  }
}

// 导航栏
.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 100;
  background: rgba(10, 10, 15, 0.85);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid $border-color;
}

.status-bar {
  background: rgba(10, 10, 15, 0.85);
  width: 100%;
}

.nav-content {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  
  .nav-title {
    font-size: 34rpx;
    font-weight: 800;
    color: $text-primary;
    letter-spacing: 1px;
  }
}

// 用户信息卡片
.profile-card {
  margin: 32rpx;
  background: $bg-card;
  border: 1px solid $border-color;
  border-radius: 32rpx;
  padding: 40rpx;
  display: flex;
  align-items: center;
  position: relative;
  backdrop-filter: blur(20px);
  overflow: hidden;
  
  .card-glow {
    position: absolute;
    top: -50%;
    right: -20%;
    width: 300rpx;
    height: 300rpx;
    background: radial-gradient(circle, rgba(176, 38, 255, 0.2) 0%, transparent 70%);
  }
  
  .avatar-wrap {
    position: relative;
    margin-right: 32rpx;
    
    .avatar {
      width: 120rpx;
      height: 120rpx;
      border-radius: 50%;
      border: 2rpx solid rgba(255, 255, 255, 0.1);
    }
    
    .avatar-ring {
      position: absolute;
      inset: -4rpx;
      border-radius: 50%;
      border: 2rpx solid rgba(0, 245, 255, 0.3);
      animation: pulse-ring 2s ease-in-out infinite;
    }
  }
  
  .profile-info {
    flex: 1;
    
    .name-row {
      display: flex;
      align-items: center;
      gap: 16rpx;
      margin-bottom: 12rpx;
      
      .nickname {
        font-size: 36rpx;
        font-weight: 800;
        color: $text-primary;
      }
      
      .verify-badge {
        display: flex;
        align-items: center;
        gap: 6rpx;
        font-size: 20rpx;
        color: $neon-cyan;
        background: rgba(0, 245, 255, 0.1);
        padding: 6rpx 14rpx;
        border-radius: 12rpx;
        border: 1px solid rgba(0, 245, 255, 0.2);
        
        .badge-icon {
          font-size: 16rpx;
          font-weight: 700;
        }
      }
    }
    
    .uid {
      font-size: 24rpx;
      color: $text-muted;
      font-family: monospace;
    }
  }
  
  .arrow {
    color: $text-muted;
    font-size: 40rpx;
    font-weight: 300;
  }
}

@keyframes pulse-ring {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.05); opacity: 0.5; }
}

// 资产卡片
.asset-card {
  margin: 0 32rpx 32rpx;
  background: linear-gradient(135deg, rgba(176, 38, 255, 0.2) 0%, rgba(0, 245, 255, 0.1) 100%);
  border: 1px solid rgba(176, 38, 255, 0.2);
  border-radius: 32rpx;
  padding: 40rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  overflow: hidden;
  
  .asset-glow {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 30% 50%, rgba(0, 245, 255, 0.1) 0%, transparent 60%);
  }
  
  .asset-content {
    position: relative;
    z-index: 1;
    
    .asset-label {
      display: flex;
      align-items: center;
      gap: 12rpx;
      font-size: 26rpx;
      color: $text-muted;
      margin-bottom: 16rpx;
      
      .label-icon {
        font-size: 28rpx;
      }
    }
    
    .balance-row {
      display: flex;
      align-items: baseline;
      
      .balance-symbol {
        font-size: 32rpx;
        font-weight: 700;
        color: $neon-cyan;
        margin-right: 8rpx;
      }
      .balance-value {
        font-size: 56rpx;
        font-weight: 800;
        color: $neon-cyan;
        font-family: 'DIN Alternate', 'Helvetica Neue', Arial, sans-serif;
      }
    }
  }
  
  .recharge-btn {
    position: relative;
    z-index: 1;
    margin: 0;
    background: $gradient-primary;
    color: #fff;
    font-size: 26rpx;
    padding: 0 40rpx;
    height: 72rpx;
    line-height: 72rpx;
    border-radius: 36rpx;
    border: none;
    display: flex;
    align-items: center;
    gap: 8rpx;
    box-shadow: 0 8rpx 30rpx rgba(176, 38, 255, 0.4);
    
    .btn-arrow {
      font-size: 20rpx;
    }
    
    &:active { 
      transform: scale(0.95);
      box-shadow: 0 4rpx 15rpx rgba(176, 38, 255, 0.3);
    }
  }
}

// 菜单区域
.menu-section {
  margin: 0 32rpx 32rpx;
  background: $bg-card;
  border: 1px solid $border-color;
  border-radius: 32rpx;
  padding: 32rpx;
  backdrop-filter: blur(20px);
  
  .menu-title {
    display: flex;
    align-items: center;
    gap: 12rpx;
    font-size: 30rpx;
    font-weight: 800;
    color: $text-primary;
    margin-bottom: 32rpx;
    letter-spacing: 1px;
    
    .title-icon {
      color: $neon-cyan;
      font-size: 24rpx;
    }
  }
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
}

.menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  padding: 24rpx 0;
  border-radius: 20rpx;
  transition: all 0.3s ease;
  
  &:active {
    background: rgba(255, 255, 255, 0.03);
    transform: scale(0.95);
  }
  
  .menu-icon-wrap {
    width: 96rpx;
    height: 96rpx;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 24rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(255, 255, 255, 0.08);
    
    &.logout {
      background: rgba(255, 0, 128, 0.1);
      border-color: rgba(255, 0, 128, 0.2);
    }
    
    .menu-icon {
      font-size: 44rpx;
    }
  }
  
  .menu-text {
    font-size: 24rpx;
    color: $text-secondary;
    font-weight: 600;
  }
}

// VIP 横幅
.vip-banner {
  margin: 0 32rpx;
  background: linear-gradient(135deg, rgba(255, 234, 0, 0.15) 0%, rgba(255, 138, 0, 0.1) 100%);
  border: 1px solid rgba(255, 234, 0, 0.2);
  border-radius: 32rpx;
  padding: 32rpx;
  position: relative;
  overflow: hidden;
  
  .vip-glow {
    position: absolute;
    top: -50%;
    right: -20%;
    width: 300rpx;
    height: 300rpx;
    background: radial-gradient(circle, rgba(255, 234, 0, 0.2) 0%, transparent 70%);
  }
  
  .vip-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    z-index: 1;
  }
  
  .vip-left {
    .vip-title {
      display: block;
      font-size: 32rpx;
      font-weight: 800;
      color: #ffea00;
      margin-bottom: 8rpx;
    }
    .vip-desc {
      font-size: 24rpx;
      color: rgba(255, 234, 0, 0.7);
    }
  }
  
  .vip-btn {
    background: $gradient-vip;
    color: #000;
    font-size: 24rpx;
    font-weight: 700;
    padding: 16rpx 32rpx;
    border-radius: 24rpx;
    box-shadow: 0 4rpx 20rpx rgba(255, 234, 0, 0.3);
  }
}
</style>