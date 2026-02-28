<template>
  <view class="container">
    <!-- 1. 沉浸式导航栏 -->
    <view class="nav-header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-content">
        <view class="back-area" @tap="handleBack">
          <text class="back-icon">✕</text>
        </view>
        <text class="nav-title">订单凭证</text>
        <view class="nav-right"></view>
      </view>
    </view>

    <!-- 主滚动区域 -->
    <scroll-view scroll-y class="main-scroll" :show-scrollbar="false">
      <!-- Loading 态 -->
      <view class="loading-state" v-if="loading || !order">
        <view class="loading-spinner"></view>
        <text>正在同步全息数据...</text>
      </view>

      <!-- 只要 order 是 null，下面都不会渲染，杜绝报错 -->
      <view class="content-wrapper" v-else>
        <!-- 2. 状态英雄区 -->
        <view class="status-hero" :class="'state-' + (order ? order.status : 10)">
          <view class="hero-bg-shapes">
            <view class="shape-1"></view>
            <view class="shape-2"></view>
          </view>
          <view class="hero-body">
            <view class="status-badge">
              <text class="dot"></text>
              <text>{{ statusMap[order ? order.status : 10] }}</text>
            </view>
            <text class="status-title">{{ statusDesc[order ? order.status : 10] }}</text>
            <view class="order-id-copy" @tap="copyText(order.id)">
              <text>ORD-NO. {{ order ? order.id : '----------' }}</text>
              <text class="copy-tag">COPY</text>
            </view>
          </view>
        </view>

        <!-- 3. 物流/地址 混合卡片 -->
        <view class="delivery-card glass-panel" v-if="order && order.address">
          <view class="delivery-header">
            <view class="info-group">
              <text class="label">配送至</text>
              <text class="value-main">{{ order.address.receiverName }}</text>
              <text class="value-sub">{{ order.address.receiverPhone }}</text>
            </view>
            <view class="location-icon">
              <view class="pulse-ring"></view>
              <view class="point"></view>
            </view>
          </view>
          <view class="address-detail">
            <text>{{ order.address.province }}{{ order.address.city }}{{ order.address.district }}{{ order.address.detailAddress }}</text>
          </view>
          
          <view class="tracking-mini" v-if="order.trackingNumberSend" @tap="copyText(order.trackingNumberSend)">
            <view class="truck-icon">🚚</view>
            <view class="tm-body">
              <text class="tm-lbl">物流单号</text>
              <text class="tm-val">{{ order.trackingNumberSend }}</text>
            </view>
            <text class="tm-copy">复制</text>
          </view>
        </view>

        <!-- 4. 租赁商品阵列 -->
        <view class="games-section section-header">
          <text class="section-label">租赁阵列 / RENT ARRAY</text>
        </view>
        
        <view class="game-array">
          <view class="game-card glass-panel" v-for="item in gameList" :key="item.id" @click="handleGameDetail(item.gameId)">
            <view class="game-cover-wrap">
              <image :src="getGameImageUrl(item.coverUrl)" mode="aspectFill" class="game-cover" />
              <view class="cover-glow"></view>
            </view>
            <view class="game-details">
              <text class="game-name">{{ item.title }}</text>
              <view class="rent-tag">
                <text class="days">{{ item.rentDays }}D</text>
                <text class="label">RENTAL DURATION</text>
              </view>
              <view class="game-bottom">
                <view class="item-price">
                  <text class="unit">¥</text>
                  <text class="val">{{ item.subTotal }}</text>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- 5. 财务清算 -->
        <view class="finance-card glass-panel" v-if="order">
          <view class="finance-row">
            <text class="lbl">租金总计</text>
            <view class="val"><text class="unit">¥</text>{{ order.totalRentFee }}</view>
          </view>
          <view class="finance-row">
            <text class="lbl">押金保障</text>
            <view class="val"><text class="unit">¥</text>{{ order.totalDeposit }}</view>
          </view>
          <view class="finance-divider"></view>
          <view class="finance-row total">
            <text class="lbl">实付清算</text>
            <view class="val-total">
               <text class="unit">¥</text>
               <text class="amount">{{ order.totalRentFee }}</text>
            </view>
          </view>
        </view>

        <!-- 6. 订单元数据 -->
        <view class="metadata-grid" v-if="order">
          <view class="meta-item">
            <text class="lbl">创建时刻</text>
            <text class="val">{{ formatDate(order.createdAt) }}</text>
          </view>
          <view class="meta-item" v-if="order.payTime">
            <text class="lbl">支付完成</text>
            <text class="val">{{ formatDate(order.payTime) }}</text>
          </view>
        </view>

        <view class="safe-area-bottom"></view>
      </view>
    </scroll-view>

    <!-- 底部量子操作栏 -->
    <view class="action-footer" v-if="order && showActions">
      <view class="blur-bg"></view>
      <view class="actions-container">
        <button 
          v-if="order.status === 10" 
          class="btn-checkout" 
          @tap="handlePay"
        >
          <text class="btn-txt">立即结算数据</text>
          <view class="btn-ripple"></view>
        </button>
        
        <view class="multi-actions" v-else>
          <button v-if="order.status === 30" class="btn-secondary" @tap="handleReturn">申请归还</button>
          <button v-if="order.status === 50" class="btn-primary-neon" @tap="handleReview">发表测评</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { getOrderDetail, payOrder } from '../../api/order';
import { getGameImageUrl } from '../../utils/imageUrl';

export default {
  data() {
    return {
      statusBarHeight: 44,
      loading: true,
      orderId: null,
      order: null,
      statusMap: {
        10: 'UNPAID',
        20: 'PENDING',
        30: 'DURING',
        40: 'RETURNING',
        50: 'COMPLETED'
      },
      statusDesc: {
        10: '待安全支付 / AWAITING PAYMENT',
        20: '同步物流中 / PREPARING DELIVERY',
        30: '租赁体验中 / ACTIVE RENTAL',
        40: '逻辑回滚中 / RETURN VERIFICATION',
        50: '历程已封存 / TRANSACTION SECURED'
      }
    };
  },
  computed: {
    showActions() {
      return [10, 30, 50].includes(this.order?.status);
    },
    gameList() {
      return this.order && this.order.items ? this.order.items : [];
    }
  },
  onLoad(options) {
    const sysInfo = uni.getSystemInfoSync();
    this.statusBarHeight = sysInfo.statusBarHeight || 20;
    this.orderId = options.id;
    this.loadOrderDetail();
  },
  methods: {
    getGameImageUrl,
    handleBack() {
      uni.navigateBack();
    },
    async loadOrderDetail() {
      if (!this.orderId) return;
      this.loading = true;
      try {
        const res = await getOrderDetail(this.orderId);
        if (res && res.code === 200) {
          this.order = res.data;
        }
      } catch (e) {
        uni.showToast({ title: '数据流同步失败', icon: 'none' });
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '--';
      const d = new Date(dateStr);
      return `${d.getFullYear()}.${String(d.getMonth()+1).padStart(2,'0')}.${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
    },
    copyText(text) {
      if(!text) return;
      uni.setClipboardData({
        data: String(text),
        success: () => uni.showToast({ title: '已同步至剪贴板', icon: 'none' })
      });
    },
    async handlePay() {
      uni.showLoading({ title: '通讯中...' });
      try {
        const res = await payOrder(this.orderId);
        if (res && res.code === 200) {
          uni.showToast({ title: '支付验证成功', icon: 'success' });
          this.loadOrderDetail();
        }
      } catch (e) {
        uni.showToast({ title: '支付失败', icon: 'none' });
      } finally {
        uni.hideLoading();
      }
    },
    handleReturn() {
      uni.showToast({ title: '归还协议模块开发中', icon: 'none' });
    },
    handleReview() {
      uni.navigateTo({
        url: `/pages/order/submitReview?orderId=${this.orderId}`
      });
    },
    handleGameDetail(gameId) {
      console.log('点击游戏卡片，GameID:', gameId);
      if (gameId) {
        uni.navigateTo({
          url: `/pages/index/gameDetail?id=${gameId}`,
          fail: (err) => {
            console.error('跳转失败:', err);
            uni.showToast({ title: '无法跳转游戏详情', icon: 'none' });
          }
        });
      } else {
        console.warn('GameID 为空，无法跳转');
      }
    }
  }
};
</script>

<style lang="scss" scoped>
/* Color System */
$quantum-blue: #00F2FF;
$cyber-purple: #7000FF;
$neo-red: #FF2E2E;
$safe-green: #00FF94;
$deep-space: #030712;
$glass-bg: rgba(255, 255, 255, 0.05);
$glass-border: rgba(255, 255, 255, 0.1);

.container {
  min-height: 100vh;
  background-color: $deep-space;
  color: #FFFFFF;
  display: flex;
  flex-direction: column;
}

/* 导航 */
.nav-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1001;
  background: rgba(3, 7, 18, 0.8);
  backdrop-filter: blur(10px);

  .nav-content {
    height: 44px;
    display: flex;
    align-items: center;
    padding: 0 40rpx;
    
    .back-area {
      width: 60rpx;
      height: 60rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      background: $glass-bg;
      border-radius: 16rpx;
      border: 1px solid $glass-border;
    }
    
    .back-icon {
      font-size: 32rpx;
      color: #FFFFFF;
      font-weight: bold;
    }
    
    .nav-title {
      flex: 1;
      text-align: center;
      font-size: 28rpx;
      font-weight: 800;
      letter-spacing: 4rpx;
      color: rgba(255, 255, 255, 0.9);
    }
    .nav-right { width: 60rpx; }
  }
}

.main-scroll {
  flex: 1;
}

.content-wrapper {
  padding: 40rpx 32rpx 200rpx;
}

/* 状态 Hero 区 */
.status-hero {
  position: relative;
  border-radius: 48rpx;
  padding: 60rpx 48rpx;
  margin-top: 140rpx;
  margin-bottom: 40rpx;
  overflow: hidden;
  background: #111827;
  border: 1px solid rgba(255, 255, 255, 0.05);

  &.state-10 { .status-badge { background: rgba($neo-red, 0.2); color: $neo-red; .dot { background: $neo-red; } } }
  &.state-30 { .status-badge { background: rgba($quantum-blue, 0.2); color: $quantum-blue; .dot { background: $quantum-blue; } } }
  &.state-50 { .status-badge { background: rgba($safe-green, 0.2); color: $safe-green; .dot { background: $safe-green; } } }

  .hero-bg-shapes {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: 0;
    
    .shape-1 {
      position: absolute;
      top: -100rpx; right: -100rpx;
      width: 300rpx; height: 300rpx;
      background: radial-gradient(circle, rgba($cyber-purple, 0.15) 0%, transparent 70%);
    }
    .shape-2 {
      position: absolute;
      bottom: -150rpx; left: -100rpx;
      width: 400rpx; height: 400rpx;
      background: radial-gradient(circle, rgba($quantum-blue, 0.1) 0%, transparent 70%);
    }
  }

  .hero-body {
    position: relative;
    z-index: 1;
  }

  .status-badge {
    display: inline-flex;
    align-items: center;
    padding: 8rpx 24rpx;
    border-radius: 99rpx;
    font-size: 20rpx;
    font-weight: 900;
    letter-spacing: 2rpx;
    margin-bottom: 24rpx;
    
    .dot {
      width: 10rpx; height: 10rpx;
      border-radius: 50%;
      margin-right: 12rpx;
      box-shadow: 0 0 10rpx currentColor;
    }
  }

  .status-title {
    font-size: 40rpx;
    font-weight: 900;
    line-height: 1.2;
    display: block;
    margin-bottom: 24rpx;
  }

  .order-id-copy {
    display: flex;
    align-items: center;
    background: rgba(0,0,0,0.3);
    padding: 12rpx 24rpx;
    border-radius: 12rpx;
    font-family: monospace;
    font-size: 22rpx;
    color: rgba(255,255,255,0.4);
    width: fit-content;
    
    .copy-tag {
      margin-left: 20rpx;
      color: $quantum-blue;
      font-weight: bold;
    }
  }
}

/* 玻璃面板通用 */
.glass-panel {
  background: $glass-bg;
  backdrop-filter: blur(8px);
  border: 1px solid $glass-border;
  border-radius: 32rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;
}

/* 地址卡片 */
.delivery-card {
  .delivery-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20rpx;
    
    .info-group {
      .label { font-size: 18rpx; color: rgba(255,255,255,0.4); font-weight: 900; display: block; margin-bottom: 4rpx; }
      .value-main { font-size: 32rpx; font-weight: 800; margin-right: 16rpx; }
      .value-sub { font-size: 24rpx; color: rgba(255,255,255,0.6); }
    }
    
    .location-icon {
      width: 80rpx; height: 80rpx;
      position: relative;
      .point {
        position: absolute;
        top: 50%; left: 50%; transform: translate(-50%, -50%);
        width: 12rpx; height: 12rpx; background: $quantum-blue; border-radius: 50%;
      }
      .pulse-ring {
        position: absolute;
        top: 50%; left: 50%; transform: translate(-50%, -50%);
        width: 100%; height: 100%; border: 2rpx solid $quantum-blue; border-radius: 50%;
        opacity: 0.3; animation: pulse 2s infinite;
      }
    }
  }

  .address-detail {
    font-size: 26rpx;
    color: rgba(255,255,255,0.8);
    line-height: 1.6;
    margin-bottom: 32rpx;
  }

  .tracking-mini {
    background: rgba(0,0,0,0.4);
    border-radius: 20rpx;
    padding: 24rpx;
    display: flex;
    align-items: center;
    border-left: 4rpx solid $quantum-blue;
    
    .truck-icon { font-size: 32rpx; margin-right: 20rpx; }
    .tm-body {
      flex: 1;
      .tm-lbl { font-size: 18rpx; color: rgba(255,255,255,0.4); display: block; }
      .tm-val { font-size: 24rpx; font-weight: bold; font-family: monospace; }
    }
    .tm-copy { font-size: 20rpx; color: $quantum-blue; font-weight: bold; }
  }
}

/* 游戏卡片 */
.section-header {
  padding: 20rpx 0 32rpx;
  .section-label { font-size: 20rpx; font-weight: 900; color: rgba(255,255,255,0.2); letter-spacing: 4rpx; }
}

.game-array {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin-bottom: 40rpx;
}

.game-card {
  display: flex;
  align-items: center;
  padding: 24rpx;
  margin-bottom: 0;
  position: relative; /* 确保层级 */
  z-index: 10;
  
  &:active {
    background: rgba(255, 255, 255, 0.1);
    transform: scale(0.98);
    transition: all 0.1s;
  }
  
  .game-cover-wrap {
    position: relative;
    width: 130rpx;
    height: 180rpx;
    margin-right: 32rpx;
    
    .game-cover { width: 100%; height: 100%; border-radius: 12rpx; z-index: 1; position: relative; }
    .cover-glow { 
      position: absolute; top: 0; left: 0; right: 0; bottom: 0;
      box-shadow: 0 10rpx 30rpx rgba(0,0,0,0.5);
    }
  }
  
  .game-details {
    flex: 1;
    .game-name { font-size: 30rpx; font-weight: 800; display: block; margin-bottom: 12rpx; }
    
    .rent-tag {
      display: inline-flex;
      align-items: center;
      background: rgba(255,255,255,0.05);
      border-radius: 8rpx;
      overflow: hidden;
      margin-bottom: 16rpx;
      
      .days { background: $quantum-blue; color: $deep-space; font-size: 18rpx; font-weight: 900; padding: 4rpx 12rpx; }
      .label { color: rgba(255,255,255,0.4); font-size: 16rpx; font-weight: bold; padding: 4rpx 12rpx; }
    }
    
    .game-bottom {
      .item-price {
        .unit { font-size: 20rpx; margin-right: 4rpx; }
        .val { font-size: 32rpx; font-weight: 900; font-family: monospace; color: $safe-green; }
      }
    }
  }
}

/* 费用 */
.finance-card {
  .finance-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12rpx 0;
    
    .lbl { font-size: 24rpx; color: rgba(255,255,255,0.5); }
    .val { font-size: 28rpx; font-weight: bold; font-family: monospace; }
    .unit { font-size: 18rpx; margin-right: 4rpx; }
    
    &.total {
      margin-top: 20rpx;
      .lbl { color: #FFFFFF; font-weight: 800; font-size: 28rpx; }
      .val-total {
        .unit { color: $neo-red; font-size: 24rpx; font-weight: bold; }
        .amount { color: $neo-red; font-size: 48rpx; font-weight: 900; font-family: monospace; }
      }
    }
  }
  
  .finance-divider {
    height: 1px;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 100%);
    margin: 10rpx 0;
  }
}

/* 元数据 */
.metadata-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
  
  .meta-item {
    padding: 24rpx;
    background: rgba(255,255,255,0.02);
    border-radius: 20rpx;
    
    .lbl { color: rgba(255,255,255,0.3); font-size: 18rpx; display: block; margin-bottom: 8rpx; }
    .val { color: rgba(255,255,255,0.7); font-size: 20rpx; font-weight: bold; }
  }
}

/* 底部操作 */
.action-footer {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  height: 180rpx;
  z-index: 1000;
  
  .blur-bg {
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(to top, rgba(3,7,18,0.95) 60%, transparent);
    backdrop-filter: blur(10px);
  }
  
  .actions-container {
    padding: 0 40rpx;
    padding-top: 20rpx;
    position: relative;
    
    .btn-checkout {
      height: 100rpx;
      background: $quantum-blue;
      border-radius: 30rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 20rpx 40rpx rgba($quantum-blue, 0.2);
      
      .btn-txt { color: $deep-space; font-size: 30rpx; font-weight: 900; letter-spacing: 4rpx; }
      &::after { border: none; }
    }
    
    .multi-actions {
      display: flex;
      gap: 24rpx;
      
      button { 
        flex: 1; height: 100rpx; border-radius: 30rpx; 
        display: flex; align-items: center; justify-content: center;
        font-size: 28rpx; font-weight: 800;
        &::after { border: none; }
      }
      
      .btn-secondary { background: rgba(255,255,255,0.05); color: #FFFFFF; border: 1px solid rgba(255,255,255,0.1); }
      .btn-primary-neon { background: $cyber-purple; color: white; box-shadow: 0 16rpx 32rpx rgba($cyber-purple, 0.2); }
    }
  }
}

/* 动画 */
@keyframes pulse {
  0% { transform: translate(-50%, -50%) scale(0.8); opacity: 0.5; }
  100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  color: rgba(255,255,255,0.5);
  font-size: 26rpx;
  
  .loading-spinner {
    width: 60rpx;
    height: 60rpx;
    border: 4rpx solid rgba(255,255,255,0.1);
    border-top-color: $quantum-blue;
    border-radius: 50%;
    margin-bottom: 30rpx;
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
