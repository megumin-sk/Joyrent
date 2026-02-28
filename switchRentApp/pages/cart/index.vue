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
        <view class="nav-title">购物车</view>
        <view class="nav-right" @tap="handleClearAll" v-if="cartList.length">
          <text class="clear-text">清空</text>
        </view>
      </view>
    </view>

    <view :style="{ height: (statusBarHeight + 44) + 'px' }"></view>

    <!-- 加载状态 -->
    <view v-if="loading" class="loading-container">
      <view class="loading-spinner"></view>
      <text class="loading-text">加载中...</text>
    </view>

    <!-- 购物车列表 -->
    <scroll-view v-else-if="cartList.length" scroll-y class="cart-list">
      <view class="cart-item" v-for="item in cartList" :key="item.id">
        <view class="checkbox-area" @tap="toggleSelect(item)">
          <view class="checkbox" :class="{ checked: item.selected }">
            <text v-if="item.selected" class="check-icon">✓</text>
          </view>
        </view>
        
        <image class="game-cover" :src="getGameImageUrl(item.game.coverUrl || item.game.cover_url)" mode="aspectFill" />
        
        <view class="item-info">
          <text class="game-title">{{ item.game.title }}</text>
          <view class="platform-badge" :class="item.game.platform">{{ item.game.platform }}</view>
          
          <view class="price-row">
            <view class="price">
              <text class="price-symbol">¥</text>
              <text class="price-value">{{ item.game.dailyRentPrice || item.game.daily_rent_price }}</text>
              <text class="price-unit">/天</text>
            </view>
            
            <view class="days-control">
              <view class="control-btn" @tap="changeDays(item, -1)">−</view>
              <text class="days-value">{{ item.rentDays }}天</text>
              <view class="control-btn" @tap="changeDays(item, 1)">+</view>
            </view>
          </view>
          
          <view class="sub-total">
            小计: <text class="sub-total-value">¥{{ ((item.game.dailyRentPrice || item.game.daily_rent_price) * item.rentDays).toFixed(0) }}</text>
          </view>
        </view>

        <view class="delete-btn" @tap="handleDelete(item)">
          <text class="delete-icon">🗑️</text>
        </view>
      </view>

      <view style="height: 200rpx;"></view>
    </scroll-view>

    <!-- 空状态 -->
    <view v-else class="empty-state">
      <view class="empty-icon">🛒</view>
      <text class="empty-text">购物车空空如也</text>
      <view class="empty-btn" @tap="goShopping">去逛逛</view>
    </view>

    <!-- 底部结算栏 -->
    <view class="checkout-bar" v-if="cartList.length">
      <view class="select-all" @tap="toggleSelectAll">
        <view class="checkbox" :class="{ checked: isAllSelected }">
          <text v-if="isAllSelected" class="check-icon">✓</text>
        </view>
        <text>全选</text>
      </view>
      
      <view class="total-section">
        <text class="total-label">合计:</text>
        <view class="total-price">
          <text class="price-symbol">¥</text>
          <text class="price-value">{{ totalAmount }}</text>
        </view>
      </view>
      
      <view 
        class="checkout-btn" 
        :class="{ disabled: selectedCount === 0 }"
        @tap="handleCheckout"
      >
        结算({{ selectedCount }})
      </view>
    </view>
  </view>
</template>

<script>
import { getCartList, updateCartItem, deleteCartItem, clearCart } from '../../api/cart';
import { getGameImageUrl } from '../../utils/imageUrl';

export default {
  data() {
    return {
      statusBarHeight: 20,
      loading: true,
      cartList: []
    };
  },
  computed: {
    selectedItems() {
      return this.cartList.filter(item => item.selected);
    },
    selectedCount() {
      return this.selectedItems.length;
    },
    isAllSelected() {
      return this.cartList.length > 0 && this.cartList.every(item => item.selected);
    },
    totalAmount() {
      return this.selectedItems.reduce((sum, item) => {
        const price = item.game.dailyRentPrice || item.game.daily_rent_price || 0;
        return sum + price * item.rentDays;
      }, 0).toFixed(0);
    }
  },
  created() {
    const sysInfo = uni.getSystemInfoSync();
    if (sysInfo.statusBarHeight) {
      this.statusBarHeight = sysInfo.statusBarHeight;
    }
  },
  onShow() {
    this.fetchCartList();
  },
  methods: {
    getGameImageUrl,
    handleBack() {
      uni.navigateBack({ delta: 1 });
    },
    async fetchCartList() {
      this.loading = true;
      try {
        const res = await getCartList();
        if (res && res.code === 200) {
          this.cartList = (res.data || []).map(item => ({
            ...item,
            selected: true
          }));
        }
      } catch (e) {
        // 未登录会自动跳转
      } finally {
        this.loading = false;
      }
    },
    toggleSelect(item) {
      item.selected = !item.selected;
    },
    toggleSelectAll() {
      const newVal = !this.isAllSelected;
      this.cartList.forEach(item => item.selected = newVal);
    },
    async changeDays(item, delta) {
      const newDays = item.rentDays + delta;
      if (newDays < 1 || newDays > 90) return;
      
      try {
        const res = await updateCartItem(item.id, newDays);
        if (res && res.code === 200) {
          item.rentDays = newDays;
        }
      } catch (e) {
        uni.showToast({ title: '更新失败', icon: 'none' });
      }
    },
    async handleDelete(item) {
      uni.showModal({
        title: '确认删除',
        content: `确定要移除《${item.game.title}》吗？`,
        confirmColor: '#ff0080',
        success: async (res) => {
          if (res.confirm) {
            try {
              const result = await deleteCartItem(item.id);
              if (result && result.code === 200) {
                this.cartList = this.cartList.filter(i => i.id !== item.id);
                uni.showToast({ title: '已删除', icon: 'success' });
              }
            } catch (e) {
              uni.showToast({ title: '删除失败', icon: 'none' });
            }
          }
        }
      });
    },
    async handleClearAll() {
      uni.showModal({
        title: '清空购物车',
        content: '确定要清空购物车吗？',
        confirmColor: '#ff0080',
        success: async (res) => {
          if (res.confirm) {
            try {
              const result = await clearCart();
              if (result && result.code === 200) {
                this.cartList = [];
                uni.showToast({ title: '已清空', icon: 'success' });
              }
            } catch (e) {
              uni.showToast({ title: '清空失败', icon: 'none' });
            }
          }
        }
      });
    },
    goShopping() {
      uni.switchTab({ url: '/pages/index/index' });
    },
    handleCheckout() {
      if (this.selectedCount === 0) return;
      
      const cartIds = this.selectedItems.map(item => item.id);
      uni.navigateTo({
        url: `/pages/order/createOrder?cartIds=${cartIds.join(',')}`
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
  right: 0;
  z-index: 100;
  background: rgba(10, 10, 15, 0.85);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid $border-color;
}

.status-bar { 
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
}

.nav-title { 
  font-size: 34rpx; 
  font-weight: 800; 
  color: $text-primary; 
}

.clear-text { 
  font-size: 26rpx; 
  color: $neon-pink; 
}

// 加载状态
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
}

.loading-spinner {
  width: 60rpx;
  height: 60rpx;
  border: 4rpx solid rgba(255, 255, 255, 0.1);
  border-top-color: $neon-cyan;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-text { 
  margin-top: 24rpx; 
  color: $text-muted; 
  font-size: 26rpx; 
}

@keyframes spin { 
  to { transform: rotate(360deg); } 
}

// 购物车列表
.cart-list {
  height: calc(100vh - 200rpx);
  padding: 24rpx;
}

.cart-item {
  display: flex;
  align-items: center;
  background: $bg-card;
  border: 1px solid $border-color;
  border-radius: 24rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  backdrop-filter: blur(20px);
}

.checkbox-area {
  padding: 16rpx;
  
  .checkbox {
    width: 44rpx;
    height: 44rpx;
    border: 2rpx solid rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    
    &.checked {
      background: $gradient-primary;
      border-color: transparent;
      box-shadow: 0 0 20rpx rgba(176, 38, 255, 0.4);
    }
    
    .check-icon {
      font-size: 24rpx;
      color: white;
      font-weight: 700;
    }
  }
}

.game-cover {
  width: 160rpx;
  height: 160rpx;
  border-radius: 16rpx;
  margin-right: 24rpx;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.item-info {
  flex: 1;
  
  .game-title {
    font-size: 28rpx;
    font-weight: 700;
    color: $text-primary;
    display: block;
    margin-bottom: 8rpx;
  }
  
  .platform-badge {
    display: inline-block;
    font-size: 18rpx;
    padding: 4rpx 12rpx;
    border-radius: 6rpx;
    color: white;
    margin-bottom: 16rpx;
    
    &.Switch { background: rgba(230, 0, 18, 0.9); }
    &.PlayStation { background: rgba(0, 112, 209, 0.9); }
  }
  
  .price-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8rpx;
  }
  
  .price {
    color: $neon-cyan;
    font-weight: 700;
    
    .price-symbol { font-size: 22rpx; }
    .price-value { font-size: 32rpx; }
    .price-unit { font-size: 20rpx; color: $text-muted; }
  }
  
  .days-control {
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12rpx;
    border: 1px solid rgba(255, 255, 255, 0.08);
    
    .control-btn {
      width: 56rpx;
      height: 56rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28rpx;
      color: $text-primary;
      font-weight: 700;
    }
    
    .days-value {
      min-width: 80rpx;
      text-align: center;
      font-size: 24rpx;
      font-weight: 600;
      color: $text-primary;
    }
  }
  
  .sub-total {
    font-size: 22rpx;
    color: $text-muted;
    
    .sub-total-value {
      color: $neon-cyan;
      font-weight: 700;
    }
  }
}

.delete-btn {
  padding: 16rpx;
  
  .delete-icon {
    font-size: 40rpx;
    opacity: 0.7;
  }
}

// 空状态
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  
  .empty-icon { 
    font-size: 120rpx; 
    margin-bottom: 32rpx; 
    opacity: 0.5;
  }
  .empty-text { 
    font-size: 28rpx; 
    color: $text-muted; 
    margin-bottom: 48rpx; 
  }
  .empty-btn {
    padding: 24rpx 72rpx;
    background: $gradient-primary;
    color: white;
    font-size: 28rpx;
    font-weight: 700;
    border-radius: 48rpx;
    box-shadow: 0 8rpx 30rpx rgba(176, 38, 255, 0.4);
  }
}

// 底部结算栏
.checkout-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100rpx;
  background: rgba(20, 20, 35, 0.98);
  border-top: 1px solid $border-color;
  display: flex;
  align-items: center;
  padding: 0 32rpx;
  box-sizing: border-box;
  backdrop-filter: blur(20px);
  padding-bottom: env(safe-area-inset-bottom);
}

.select-all {
  display: flex;
  align-items: center;
  gap: 16rpx;
  font-size: 26rpx;
  color: $text-primary;
  
  .checkbox {
    width: 40rpx;
    height: 40rpx;
    border: 2rpx solid rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    
    &.checked {
      background: $gradient-primary;
      border-color: transparent;
      box-shadow: 0 0 15rpx rgba(176, 38, 255, 0.4);
    }
    
    .check-icon {
      font-size: 22rpx;
      color: white;
      font-weight: 700;
    }
  }
}

.total-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-right: 24rpx;
  
  .total-label { 
    font-size: 26rpx; 
    color: $text-muted; 
    margin-right: 8rpx;
  }
  
  .total-price {
    color: $neon-cyan;
    font-weight: 800;
    
    .price-symbol { font-size: 24rpx; }
    .price-value { font-size: 40rpx; }
  }
}

.checkout-btn {
  padding: 0 48rpx;
  height: 72rpx;
  line-height: 72rpx;
  background: $gradient-primary;
  color: white;
  font-size: 28rpx;
  font-weight: 700;
  border-radius: 36rpx;
  box-shadow: 0 8rpx 30rpx rgba(176, 38, 255, 0.4);
  
  &.disabled {
    background: rgba(255, 255, 255, 0.1);
    color: $text-muted;
    box-shadow: none;
  }
}
</style>