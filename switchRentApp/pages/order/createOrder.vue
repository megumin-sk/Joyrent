<template>
  <view class="page">
    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
      <view class="nav-content">
        <view class="nav-left" @tap="handleBack">
          <text class="back-icon">‹</text>
        </view>
        <view class="nav-title">确认订单</view>
        <view class="nav-right"></view>
      </view>
    </view>

    <view :style="{ height: (statusBarHeight + 44) + 'px' }"></view>

    <scroll-view scroll-y class="content">
      <!-- 1. 收货地址 -->
      <view class="section address-section" @tap="selectAddress">
        <view v-if="selectedAddress" class="address-info">
          <view class="address-header">
            <text class="receiver-name">{{ selectedAddress.receiverName }}</text>
            <text class="receiver-phone">{{ selectedAddress.receiverPhone }}</text>
          </view>
          <text class="address-detail">
            {{ selectedAddress.province }}{{ selectedAddress.city }}{{ selectedAddress.district }}{{ selectedAddress.detailAddress }}
          </text>
        </view>
        <view v-else class="no-address">
          <text class="icon">📍</text>
          <text>请选择收货地址</text>
        </view>
        <text class="arrow">›</text>
      </view>

      <!-- 2. 商品列表 -->
      <view class="section goods-section">
        <view class="section-title">租赁清单</view>
        <view class="goods-item" v-for="item in orderItems" :key="item.id">
          <image class="goods-cover" :src="getGameImageUrl(item.game.coverUrl || item.game.cover_url)" mode="aspectFill" />
          <view class="goods-info">
            <text class="goods-title">{{ item.game.title }}</text>
            <view class="goods-meta">
              <text class="platform" :class="item.game.platform">{{ item.game.platform }}</text>
              <text class="rent-days">租期 {{ item.rentDays }} 天</text>
            </view>
            <view class="goods-price">
              <text class="price">¥{{ item.game.dailyRentPrice || item.game.daily_rent_price }}/天</text>
              <text class="subtotal">小计 ¥{{ ((item.game.dailyRentPrice || item.game.daily_rent_price) * item.rentDays).toFixed(0) }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 3. 费用明细 -->
      <view class="section fee-section">
        <view class="section-title">费用明细</view>
        <view class="fee-row">
          <text class="fee-label">租金合计</text>
          <text class="fee-value">¥{{ totalRentFee }}</text>
        </view>
        <view class="fee-row">
          <text class="fee-label">押金合计</text>
          <text class="fee-value">¥{{ totalDeposit }}</text>
        </view>
        <view class="fee-row highlight">
          <text class="fee-label">🎉 信用免押</text>
          <text class="fee-value discount">-¥{{ totalDeposit }}</text>
        </view>
        <view class="fee-divider"></view>
        <view class="fee-row total">
          <text class="fee-label">实付金额</text>
          <view class="pay-amount">
            <text class="symbol">¥</text>
            <text class="amount">{{ payAmount }}</text>
          </view>
        </view>
      </view>

      <!-- 4. 订单备注 -->
      <view class="section remark-section">
        <text class="section-title">订单备注</text>
        <input 
          class="remark-input" 
          v-model="remark" 
          placeholder="选填，如有特殊需求请备注"
          maxlength="100"
        />
      </view>

      <view style="height: 160rpx;"></view>
    </scroll-view>

    <!-- 底部提交栏 -->
    <view class="submit-bar">
      <view class="total-display">
        <text class="label">合计:</text>
        <view class="amount">
          <text class="symbol">¥</text>
          <text class="number">{{ payAmount }}</text>
        </view>
      </view>
      <view 
        class="submit-btn" 
        :class="{ disabled: !canSubmit }"
        @tap="handleSubmit"
      >
        {{ submitting ? '提交中...' : '提交订单' }}
      </view>
    </view>
  </view>
</template>

<script>
import { getCartList } from '../../api/cart';
import { createOrder } from '../../api/order';
import { getAddressList } from '../../api/address';
import { getGameImageUrl } from '../../utils/imageUrl';

export default {
  data() {
    return {
      statusBarHeight: 20,
      cartIds: [],
      orderItems: [],
      selectedAddress: null,
      remark: '',
      submitting: false
    };
  },
  // ... computed ...
  computed: {
    totalRentFee() {
      return this.orderItems.reduce((sum, item) => {
        const price = item.game.dailyRentPrice || item.game.daily_rent_price || 0;
        return sum + price * item.rentDays;
      }, 0).toFixed(0);
    },
    totalDeposit() {
      return this.orderItems.reduce((sum, item) => {
        return sum + (item.game.depositPrice || item.game.deposit_price || 0);
      }, 0).toFixed(0);
    },
    payAmount() {
      // 信用免押，实付 = 租金
      return this.totalRentFee;
    },
    canSubmit() {
      return this.selectedAddress && this.orderItems.length > 0 && !this.submitting;
    }
  },
  created() {
    const sysInfo = uni.getSystemInfoSync();
    if (sysInfo.statusBarHeight) {
      this.statusBarHeight = sysInfo.statusBarHeight;
    }
  },
  onLoad(options) {
    if (options.cartIds) {
      this.cartIds = options.cartIds.split(',').map(Number);
      this.fetchOrderItems();
    }
    this.fetchDefaultAddress();
  },
  methods: {
    getGameImageUrl,
    handleBack() {
      uni.navigateBack({ delta: 1 });
    },
    async fetchOrderItems() {
      try {
        const res = await getCartList();
        if (res && res.code === 200) {
          // 筛选出本次结算的商品
          this.orderItems = (res.data || []).filter(item => 
            this.cartIds.includes(item.id)
          );
        }
      } catch (e) {
        uni.showToast({ title: '加载失败', icon: 'none' });
      }
    },

    async fetchDefaultAddress() {
      try {
        const res = await getAddressList();
        if (res && res.code === 200 && res.data && res.data.length > 0) {
          // 优先找默认地址，找不到取第一个
          this.selectedAddress = res.data.find(item => item.isDefault === 1) || res.data[0];
        } else {
          this.selectedAddress = null;
        }
      } catch (e) {
        // ignore
      }
    },
    selectAddress() {
      uni.navigateTo({
        url: '/pages/address/index?select=1',
        events: {
          // 监听来自地址列表页的选择事件
          acceptAddressSelect: (data) => {
            this.selectedAddress = data;
          }
        }
      });
    },
    async handleSubmit() {
      if (!this.canSubmit) return;
      
      this.submitting = true;
      try {
        const res = await createOrder({
          addressId: this.selectedAddress.id,
          cartIds: this.cartIds,
          remark: this.remark
        });
        
        if (res && res.code === 200) {
          uni.showToast({ title: '下单成功', icon: 'success' });
          // 跳转到订单列表
          setTimeout(() => {
            uni.redirectTo({ url: '/pages/order/index' });
          }, 1500);
        } else {
          uni.showToast({ title: res.msg || '下单失败', icon: 'none' });
        }
      } catch (e) {
        uni.showToast({ title: '网络错误', icon: 'none' });
      } finally {
        this.submitting = false;
      }
    }
  }
};
</script>

<style lang="scss" scoped>
$primary-color: #FF3D00;
$primary-gradient: linear-gradient(135deg, #FF3D00 0%, #FF8A00 100%);
$text-main: #0F172A;
$text-sub: #64748B;
$bg-color: #F8FAFC;

.page {
  min-height: 100vh;
  background: $bg-color;
}

/* 导航栏 */
.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background: white;
  z-index: 100;
}
.status-bar { width: 100%; }
.nav-content {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32rpx;
}
.nav-left, .nav-right { width: 80rpx; }
.back-icon { font-size: 48rpx; color: #333; }
.nav-title { font-size: 34rpx; font-weight: 700; color: $text-main; }

.content {
  height: calc(100vh - 100rpx);
  padding: 24rpx;
}

/* 通用 Section */
.section {
  background: white;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
}
.section-title {
  font-size: 30rpx;
  font-weight: 700;
  color: $text-main;
  margin-bottom: 24rpx;
}

/* 地址区域 */
.address-section {
  display: flex;
  align-items: center;
}
.address-info {
  flex: 1;
  .address-header {
    margin-bottom: 8rpx;
  }
  .receiver-name {
    font-size: 32rpx;
    font-weight: 700;
    color: $text-main;
    margin-right: 24rpx;
  }
  .receiver-phone {
    font-size: 28rpx;
    color: $text-sub;
  }
  .address-detail {
    font-size: 26rpx;
    color: $text-sub;
    line-height: 1.5;
  }
}
.no-address {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16rpx;
  color: $text-sub;
  font-size: 28rpx;
  .icon { font-size: 36rpx; }
}
.arrow {
  font-size: 40rpx;
  color: #CBD5E1;
}

/* 商品列表 */
.goods-item {
  display: flex;
  padding: 20rpx 0;
  border-bottom: 1px solid #F1F5F9;
  
  &:last-child { border-bottom: none; }
}
.goods-cover {
  width: 140rpx;
  height: 140rpx;
  border-radius: 16rpx;
  margin-right: 24rpx;
}
.goods-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  
  .goods-title {
    font-size: 28rpx;
    font-weight: 600;
    color: $text-main;
  }
  
  .goods-meta {
    display: flex;
    align-items: center;
    gap: 16rpx;
    
    .platform {
      font-size: 18rpx;
      padding: 4rpx 12rpx;
      border-radius: 6rpx;
      color: white;
      &.Switch { background: #E60012; }
      &.PlayStation { background: #0070D1; }
    }
    .rent-days {
      font-size: 24rpx;
      color: $text-sub;
    }
  }
  
  .goods-price {
    display: flex;
    justify-content: space-between;
    
    .price {
      font-size: 24rpx;
      color: $text-sub;
    }
    .subtotal {
      font-size: 26rpx;
      font-weight: 600;
      color: $primary-color;
    }
  }
}

/* 费用明细 */
.fee-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12rpx 0;
  
  .fee-label {
    font-size: 28rpx;
    color: $text-sub;
  }
  .fee-value {
    font-size: 28rpx;
    color: $text-main;
    
    &.discount {
      color: #10B981;
    }
  }
  
  &.highlight {
    background: #F0FDF4;
    margin: 0 -32rpx;
    padding: 16rpx 32rpx;
  }
  
  &.total {
    padding-top: 24rpx;
    .fee-label {
      font-size: 30rpx;
      color: $text-main;
      font-weight: 600;
    }
    .pay-amount {
      color: $primary-color;
      font-weight: 800;
      .symbol { font-size: 28rpx; }
      .amount { font-size: 44rpx; }
    }
  }
}
.fee-divider {
  height: 1px;
  background: #F1F5F9;
  margin: 16rpx 0;
}

/* 备注输入 */
.remark-input {
  width: 100%;
  height: 80rpx;
  background: #F8FAFC;
  border-radius: 12rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
}

/* 底部提交栏 */
.submit-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100rpx;
  background: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32rpx;
  box-sizing: border-box;
  box-shadow: 0 -4px 20px rgba(0,0,0,0.06);
  padding-bottom: env(safe-area-inset-bottom);
}

.total-display {
  display: flex;
  align-items: baseline;
  
  .label {
    font-size: 28rpx;
    color: $text-sub;
    margin-right: 8rpx;
  }
  .amount {
    color: $primary-color;
    font-weight: 800;
    .symbol { font-size: 26rpx; }
    .number { font-size: 44rpx; }
  }
}

.submit-btn {
  padding: 0 64rpx;
  height: 80rpx;
  line-height: 80rpx;
  background: $primary-gradient;
  color: white;
  font-size: 32rpx;
  font-weight: 700;
  border-radius: 40rpx;
  box-shadow: 0 8px 20px rgba(255, 61, 0, 0.25);
  
  &.disabled {
    background: #E2E8F0;
    color: #94A3B8;
    box-shadow: none;
  }
}
</style>
