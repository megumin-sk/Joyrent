<template>
  <view class="page-container">
    <view class="page-bg"></view>
    
    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
      <view class="nav-content">
        <view class="nav-left" @tap="handleBack">
          <text class="back-icon">‹</text>
        </view>
        <view class="nav-title">我的订单</view>
        <view class="nav-right"></view>
      </view>
    </view>

    <view :style="{ height: (statusBarHeight + 44) + 'px' }"></view>

    <!-- Tabs -->
    <view class="tabs-container" :style="{ top: (statusBarHeight + 44) + 'px' }">
      <view class="tabs-wrapper">
        <view
          v-for="(item, index) in tabList"
          :key="item.name"
          :class="['tab-item', currentTab === index ? 'active' : '']"
          @tap="onTabChange(index)"
        >
          {{ item.name }}
          <view class="tab-glow" v-if="currentTab === index"></view>
        </view>
      </view>
    </view>
    
    <view style="height: 44px;"></view>

    <!-- 订单列表 -->
    <scroll-view scroll-y class="order-list">
      <view class="order-card" v-for="order in filteredOrders" :key="order.id">
        <view class="card-header">
          <view class="order-info">
            <text class="order-no">单号 {{ order.id }}</text>
            <text class="order-date">2024-01-15</text>
          </view>
          <view class="status-badge" :class="'status-' + order.status">
            {{ statusMap[order.status] }}
          </view>
        </view>

        <view class="card-body" @tap="handleDetail(order)">
          <view class="info-row">
            <text class="label">总租金</text>
            <view class="price">
              <text class="price-symbol">¥</text>
              <text class="price-value">{{ order.total_rent_fee }}</text>
            </view>
          </view>
          
          <view class="info-row" v-if="order.tracking_number_send">
            <text class="label">发货物流</text>
            <text class="value">{{ order.tracking_number_send }}</text>
          </view>
        </view>

        <view class="card-actions" v-if="[10, 30, 50].includes(order.status)">
          <button 
            v-if="order.status === 10" 
            class="action-btn primary" 
            @tap.stop="handlePay(order)"
          >
            立即支付
          </button>
          
          <button 
            v-else-if="order.status === 30" 
            class="action-btn ghost" 
            @tap.stop="handleReturn(order)"
          >
            归还
          </button>
          
          <button 
            v-else-if="order.status === 50" 
            class="action-btn secondary" 
            @tap.stop="handleReview(order)"
          >
            评价
          </button>
        </view>
      </view>

      <view v-if="!filteredOrders.length && !loading" class="empty-state">
        <view class="empty-icon">📋</view>
        <text>暂无订单</text>
      </view>
      
      <view style="height: 40px;"></view>
    </scroll-view>
  </view>
</template>

<script>
import { getMyOrders, payOrder } from '../../api/order';

export default {
  data() {
    return {
      statusBarHeight: 20,
      currentTab: 0,
      loading: false,
      tabList: [
        { name: '全部', status: null },
        { name: '待支付', status: 10 },
        { name: '待发货', status: 20 },
        { name: '租赁中', status: 30 },
        { name: '归还中', status: 40 },
        { name: '已完成', status: 50 }
      ],
      statusMap: {
        10: '待支付',
        20: '待发货',
        30: '租赁中',
        40: '归还中',
        50: '已完成'
      },
      orderList: []
    };
  },
  computed: {
    filteredOrders() {
      const target = this.tabList[this.currentTab].status;
      if (!target) return this.orderList;
      return this.orderList.filter(item => item.status === target);
    }
  },
  created() {
    const sysInfo = uni.getSystemInfoSync();
    if (sysInfo.statusBarHeight) {
      this.statusBarHeight = sysInfo.statusBarHeight;
    }
  },
  onShow() {
    this.fetchOrders();
  },
  methods: {
    handleBack() {
      uni.navigateBack({ delta: 1 });
    },
    onTabChange(index) {
      this.currentTab = index;
    },
    async fetchOrders() {
      this.loading = true;
      try {
        const res = await getMyOrders();
        if (res && res.code === 200) {
          this.orderList = res.data || [];
        }
      } catch (e) {
        console.error('获取订单列表失败', e);
      } finally {
        this.loading = false;
      }
    },
    async handlePay(order) {
      try {
        const res = await payOrder(order.id);
        if (res && res.code === 200) {
          uni.showToast({ title: '支付成功', icon: 'success' });
          this.fetchOrders();
        } else {
          uni.showToast({ title: res.msg || '支付失败', icon: 'none' });
        }
      } catch (e) {
        uni.showToast({ title: '支付失败', icon: 'none' });
      }
    },
    handleReturn(order) {
      uni.showToast({ title: '归还申请功能开发中', icon: 'none' });
    },
    handleReview(order) {
      uni.navigateTo({
        url: `/pages/order/submitReview?orderId=${order.id}`
      });
    },
    handleDetail(order) {
      uni.navigateTo({
        url: `/pages/order/orderDetail?id=${order.id}`
      });
    }
  }
};
</script>

<style lang="scss">
$neon-purple: #b026ff;
$neon-cyan: #00f5ff;
$neon-pink: #ff0080;
$neon-yellow: #ffea00;
$bg-primary: #0a0a0f;
$bg-secondary: #12121a;
$bg-card: rgba(20, 20, 35, 0.95);
$text-primary: #ffffff;
$text-secondary: rgba(255, 255, 255, 0.85);
$text-muted: rgba(255, 255, 255, 0.5);
$border-color: rgba(255, 255, 255, 0.08);
$gradient-primary: linear-gradient(135deg, $neon-purple 0%, $neon-cyan 100%);

.page-container {
  min-height: 100vh;
  background-color: $bg-primary;
  position: relative;
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
  justify-content: space-between;
  padding: 0 32rpx;
}

.nav-left,
.nav-right {
  width: 80rpx;
}

.back-icon {
  font-size: 48rpx;
  color: $text-primary;
  font-weight: 300;
}

.nav-title {
  flex: 1;
  text-align: center;
  font-size: 34rpx;
  font-weight: 800;
  color: $text-primary;
}

// Tabs
.tabs-container {
  background: rgba(10, 10, 15, 0.9);
  position: fixed;
  left: 0;
  width: 100%;
  z-index: 99;
  border-bottom: 1px solid $border-color;
  height: 44px;
}

.tabs-wrapper {
  display: flex;
  justify-content: space-around;
  height: 100%;
  align-items: center;
  padding: 0 16rpx;
}

.tab-item {
  padding: 0 20rpx;
  height: 100%;
  display: flex;
  align-items: center;
  font-size: 26rpx;
  color: $text-muted;
  position: relative;
  font-weight: 600;
  
  &.active {
    color: $neon-cyan;
    font-weight: 700;
  }
  
  .tab-glow {
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 40rpx;
    height: 4rpx;
    background: $gradient-primary;
    border-radius: 4rpx;
    box-shadow: 0 0 20rpx rgba(0, 245, 255, 0.5);
  }
}

// 订单列表
.order-list {
  flex: 1;
  padding: 24rpx 32rpx;
  box-sizing: border-box;
}

.order-card {
  background: $bg-card;
  border: 1px solid $border-color;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  backdrop-filter: blur(20px);
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24rpx;
    
    .order-info {
      display: flex;
      flex-direction: column;
      gap: 8rpx;
    }
    
    .order-no {
      font-size: 26rpx;
      color: $text-secondary;
      font-family: monospace;
      font-weight: 600;
    }
    
    .order-date {
      font-size: 22rpx;
      color: $text-muted;
    }
    
    .status-badge {
      font-size: 22rpx;
      font-weight: 700;
      padding: 8rpx 20rpx;
      border-radius: 12rpx;
      
      &.status-10 {
        background: rgba(255, 234, 0, 0.15);
        color: $neon-yellow;
      }
      &.status-30 {
        background: rgba(0, 245, 255, 0.15);
        color: $neon-cyan;
      }
      &.status-50 {
        background: rgba(0, 255, 136, 0.15);
        color: #00ff88;
      }
      &.status-20,
      &.status-40 {
        background: rgba(255, 138, 0, 0.15);
        color: #ff8a00;
      }
    }
  }
  
  .card-body {
    padding: 24rpx 0;
    border-top: 1px solid rgba(255, 255, 255, 0.04);
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    
    .info-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16rpx;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .label {
        font-size: 26rpx;
        color: $text-muted;
      }
      
      .value {
        font-size: 26rpx;
        color: $text-secondary;
        font-family: monospace;
      }
      
      .price {
        color: $neon-cyan;
        font-weight: 800;
        
        .price-symbol {
          font-size: 24rpx;
        }
        .price-value {
          font-size: 36rpx;
        }
      }
    }
  }
  
  .card-actions {
    margin-top: 24rpx;
    display: flex;
    justify-content: flex-end;
    gap: 16rpx;
    
    .action-btn {
      margin: 0;
      font-size: 26rpx;
      height: 64rpx;
      line-height: 64rpx;
      padding: 0 32rpx;
      border-radius: 32rpx;
      font-weight: 600;
      
      &::after {
        border: none;
      }
      
      &.primary {
        background: $gradient-primary;
        color: white;
        box-shadow: 0 4rpx 15rpx rgba(176, 38, 255, 0.4);
      }
      
      &.ghost {
        background: transparent;
        border: 1px solid rgba(0, 245, 255, 0.3);
        color: $neon-cyan;
        
        &:active {
          background: rgba(0, 245, 255, 0.1);
        }
      }
      
      &.secondary {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: $text-secondary;
      }
    }
  }
}

.empty-state {
  padding-top: 160rpx;
  text-align: center;
  color: $text-muted;
  font-size: 28rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  
  .empty-icon {
    font-size: 80rpx;
    margin-bottom: 24rpx;
    opacity: 0.5;
  }
}
</style>