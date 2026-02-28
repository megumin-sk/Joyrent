<template>
  <view class="page">
    <scroll-view scroll-y class="content-area" v-if="list.length > 0">
      <view class="address-card" v-for="(item, index) in list" :key="item.id">
        <view class="card-body" @tap="onAddressTap(item)">
          <view class="user-row">
            <text class="name">{{ item.receiverName }}</text>
            <text class="phone">{{ item.receiverPhone }}</text>
            <view class="default-badge" v-if="item.isDefault === 1">默认</view>
          </view>
          <text class="address-detail">
            {{ item.province }}{{ item.city }}{{ item.district }} {{ item.detailAddress }}
          </text>
        </view>
        
        <view class="card-footer">
          <view class="radio-wrap" @tap="handleSetDefault(item)">
            <view class="radio-circle" :class="{ checked: item.isDefault === 1 }">
              <view class="inner" v-if="item.isDefault === 1"></view>
            </view>
            <text class="def-text">{{ item.isDefault === 1 ? '默认地址' : '设为默认' }}</text>
          </view>
          
          <view class="actions">
            <view class="action-btn" @tap.stop="handleEdit(item)">
              <text>编辑</text>
            </view>
            <view class="action-btn delete" @tap.stop="handleDelete(item)">
              <text>删除</text>
            </view>
          </view>
        </view>
      </view>
      <view style="height: 120rpx;"></view>
    </scroll-view>

    <view class="empty-state" v-else-if="!loading">
      <text class="empty-icon">📍</text>
      <text class="empty-text">您还没有添加收货地址</text>
    </view>

    <view class="footer-bar safe-area-bottom">
      <button class="add-btn" @tap="handleAdd">+ 新建收货地址</button>
    </view>
  </view>
</template>

<script>
import { getAddressList, deleteAddress, setDefaultAddress } from '@/api/address';

export default {
  data() {
    return {
      list: [],
      loading: true,
      isSelectMode: false
    };
  },
  onLoad(options) {
    if (options.select) {
      this.isSelectMode = true;
      uni.setNavigationBarTitle({ title: '选择收货地址' });
    }
  },
  onShow() {
    this.fetchList();
  },
  methods: {
    async fetchList() {
      this.loading = true;
      try {
        const res = await getAddressList();
        if (res && res.code === 200) {
          this.list = res.data || [];
        }
      } catch (e) {
        // quiet fail or login redirect handled by request.js
      } finally {
        this.loading = false;
      }
    },
    handleAdd() {
      uni.navigateTo({ url: '/pages/address/edit' });
    },
    handleEdit(item) {
      // 传递对象需要编码
      const dataStr = encodeURIComponent(JSON.stringify(item));
      uni.navigateTo({ url: `/pages/address/edit?data=${dataStr}` });
    },
    handleDelete(item) {
      uni.showModal({
        title: '提示',
        content: '确定要删除该地址吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              const apiRes = await deleteAddress(item.id);
              if (apiRes && apiRes.code === 200) {
                uni.showToast({ title: '已删除', icon: 'success' });
                this.fetchList();
              } else {
                uni.showToast({ title: apiRes.msg || '删除失败', icon: 'none' });
              }
            } catch (e) {}
          }
        }
      });
    },
    async handleSetDefault(item) {
      if (item.isDefault === 1) return;
      
      try {
        const res = await setDefaultAddress(item.id);
        if (res && res.code === 200) {
          uni.showToast({ title: '设置成功', icon: 'success' });
          this.fetchList();
        }
      } catch (e) {}
    },
    onAddressTap(item) {
      if (this.isSelectMode) {
        const eventChannel = this.getOpenerEventChannel();
        eventChannel.emit('acceptAddressSelect', item);
        uni.navigateBack();
      }
    }
  }
};
</script>

<style lang="scss" scoped>
$primary-gradient: linear-gradient(135deg, #FF3D00 0%, #FF8A00 100%);
$bg-color: #F8FAFC;
$text-main: #0F172A;
$text-sub: #64748B;
$transition-physics: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);

.page {
  min-height: 100vh;
  background-color: $bg-color;
  display: flex;
  flex-direction: column;
}

.content-area {
  flex: 1;
  padding: 32rpx;
  box-sizing: border-box;
}

.address-card {
  background: #fff;
  border-radius: 32rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05), 0 0 0 1px rgba(0, 0, 0, 0.02);
  overflow: hidden;
  transition: $transition-physics;
  
  &:active { transform: scale(0.98); }
  
  .card-body {
    padding: 32rpx;
    border-bottom: 1rpx solid #F1F5F9;
    
    .user-row {
      display: flex;
      align-items: center;
      margin-bottom: 16rpx;
      
      .name { 
        font-size: 32rpx; 
        font-weight: 700; 
        color: $text-main; 
        margin-right: 16rpx;
        letter-spacing: -0.02em;
      }
      .phone { 
        font-size: 28rpx; 
        color: $text-sub; 
        margin-right: 16rpx; 
        font-family: 'DIN Alternate', sans-serif; 
        font-weight: 500;
      }
      .default-badge {
        font-size: 20rpx;
        color: #FF3D00;
        background: rgba(255, 61, 0, 0.08);
        padding: 4rpx 12rpx;
        border-radius: 12rpx;
        font-weight: 600;
      }
    }
    
    .address-detail {
      font-size: 28rpx;
      color: #334155;
      line-height: 1.6;
      font-weight: 400;
    }
  }
  
  .card-footer {
    padding: 24rpx 32rpx;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #FAFAFA;
    
    .radio-wrap {
      display: flex;
      align-items: center;
      padding: 8rpx 0;
      
      .radio-circle {
        width: 36rpx;
        height: 36rpx;
        border-radius: 50%;
        border: 3rpx solid #CBD5E1;
        margin-right: 16rpx;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: $transition-physics;
        
        &.checked {
          border-color: #FF3D00;
          background: rgba(255, 61, 0, 0.05);
          .inner {
            width: 18rpx;
            height: 18rpx;
            background: $primary-gradient;
            border-radius: 50%;
            box-shadow: 0 2rpx 8rpx rgba(255, 61, 0, 0.3);
          }
        }
      }
      
      .def-text { 
        font-size: 26rpx; 
        color: $text-sub;
        font-weight: 500;
      }
    }
    
    .actions {
      display: flex;
      gap: 40rpx;
      
      .action-btn {
        font-size: 26rpx;
        color: $text-sub;
        display: flex;
        align-items: center;
        font-weight: 500;
        padding: 8rpx 0;
        transition: $transition-physics;
        
        &.delete { color: #EF4444; }
        
        &:active { opacity: 0.6; transform: scale(0.95); }
      }
    }
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-top: 200rpx;
  
  .empty-icon { 
    font-size: 100rpx; 
    margin-bottom: 32rpx; 
    opacity: 0.8;
    filter: drop-shadow(0 8rpx 16rpx rgba(0,0,0,0.1));
  }
  .empty-text { 
    font-size: 30rpx; 
    color: $text-sub; 
    font-weight: 500;
  }
}

.footer-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 24rpx 48rpx;
  background: transparent; 
  pointer-events: none;
  box-sizing: border-box;
  
  .add-btn {
    pointer-events: auto;
    background: $primary-gradient;
    color: #fff;
    border-radius: 56rpx;
    font-size: 32rpx;
    font-weight: 700;
    height: 100rpx;
    line-height: 100rpx;
    box-shadow: 0 8rpx 32rpx rgba(255, 61, 0, 0.25);
    border: none;
    letter-spacing: 0.02em;
    transition: $transition-physics;
    
    &:active { transform: scale(0.96); box-shadow: 0 4rpx 12rpx rgba(255, 61, 0, 0.15); }
  }
}

.safe-area-bottom {
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}
</style>