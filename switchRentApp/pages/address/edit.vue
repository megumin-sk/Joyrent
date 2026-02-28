<template>
  <view class="page">
    <view class="form-group">
      <view class="form-item">
        <text class="label">收货人</text>
        <input class="input" v-model="form.receiverName" placeholder="请填写收货人姓名" />
      </view>
      <view class="form-item">
        <text class="label">手机号码</text>
        <input class="input" type="number" v-model="form.receiverPhone" maxlength="11" placeholder="请填写收货人手机号" />
      </view>
      <view class="form-item">
        <text class="label">所在地区</text>
        <picker mode="region" @change="onRegionChange" :value="regionValue">
          <view class="picker-view" :class="{ 'placeholder': !form.province }">
            {{ regionDisplay || '请选择省/市/区' }}
          </view>
        </picker>
      </view>
      <view class="form-item no-border">
        <text class="label">详细地址</text>
        <textarea class="textarea" v-model="form.detailAddress" placeholder="街道、楼牌号等" auto-height />
      </view>
    </view>

    <view class="form-group" style="margin-top: 24rpx;">
      <view class="form-item switch-item">
        <text class="label">设为默认地址</text>
        <switch :checked="form.isDefault === 1" color="#FF3D00" @change="onDefaultChange" />
      </view>
    </view>

    <button class="save-btn" @tap="handleSave" :loading="submitting">保存</button>
  </view>
</template>

<script>
import { addAddress, updateAddress } from '@/api/address';

export default {
  data() {
    return {
      form: {
        id: null,
        receiverName: '',
        receiverPhone: '',
        province: '',
        city: '',
        district: '',
        detailAddress: '',
        isDefault: 0
      },
      regionValue: [],
      submitting: false
    };
  },
  computed: {
    regionDisplay() {
      if (this.form.province) {
        return `${this.form.province} ${this.form.city} ${this.form.district}`;
      }
      return '';
    }
  },
  onLoad(options) {
    if (options.data) {
      try {
        const data = JSON.parse(decodeURIComponent(options.data));
        this.form = { ...this.form, ...data };
        // 初始化 regionValue 用于 picker 回显 (有些平台需要)
        this.regionValue = [this.form.province, this.form.city, this.form.district];
        uni.setNavigationBarTitle({ title: '编辑收货地址' });
      } catch (e) {
        console.error(e);
      }
    } else {
      uni.setNavigationBarTitle({ title: '新增收货地址' });
    }
  },
  methods: {
    onRegionChange(e) {
      const { value } = e.detail; // ["广东省", "深圳市", "南山区"]
      this.form.province = value[0];
      this.form.city = value[1];
      this.form.district = value[2];
      this.regionValue = value;
    },
    onDefaultChange(e) {
      this.form.isDefault = e.detail.value ? 1 : 0;
    },
    async handleSave() {
      if (!this.form.receiverName) return uni.showToast({ title: '请填写收货人', icon: 'none' });
      if (!this.form.receiverPhone) return uni.showToast({ title: '请填写手机号', icon: 'none' });
      if (!/^1\d{10}$/.test(this.form.receiverPhone)) return uni.showToast({ title: '手机号格式不正确', icon: 'none' });
      if (!this.form.province) return uni.showToast({ title: '请选择地区', icon: 'none' });
      if (!this.form.detailAddress) return uni.showToast({ title: '请填写详细地址', icon: 'none' });

      this.submitting = true;
      try {
        let res;
        if (this.form.id) {
          res = await updateAddress(this.form);
        } else {
          res = await addAddress(this.form);
        }

        if (res && res.code === 200) {
          uni.showToast({ title: '保存成功', icon: 'success' });
          setTimeout(() => {
            uni.navigateBack();
          }, 1500);
        } else {
          uni.showToast({ title: res.msg || '保存失败', icon: 'none' });
        }
      } catch (e) {
        // request.js handles network errors
      } finally {
        this.submitting = false;
      }
    }
  }
};
</script>

<style lang="scss" scoped>
$primary-gradient: linear-gradient(135deg, #FF3D00 0%, #FF8A00 100%);
$bg-color: #F8FAFC;
$text-main: #0F172A;
$input-bg: #F1F5F9;
$transition-physics: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);

.page {
  min-height: 100vh;
  background-color: $bg-color;
  padding: 32rpx;
  box-sizing: border-box;
}

.form-group {
  background: #fff;
  border-radius: 32rpx;
  padding: 16rpx 32rpx;
  box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05), 0 0 0 1px rgba(0, 0, 0, 0.02);
  margin-bottom: 32rpx;
}

.form-item {
  display: flex;
  align-items: center;
  padding: 32rpx 0;
  border-bottom: 1rpx solid #F1F5F9;
  
  &.no-border { border-bottom: none; }
  &.switch-item { justify-content: space-between; padding: 24rpx 0; }
  
  .label {
    width: 180rpx;
    font-size: 28rpx;
    color: $text-main;
    font-weight: 600;
  }
  
  .input {
    flex: 1;
    font-size: 28rpx;
    color: #334155;
    font-weight: 500;
  }
  
  .textarea {
    flex: 1;
    font-size: 28rpx;
    color: #334155;
    min-height: 48rpx;
    width: auto;
    font-weight: 500;
    line-height: 1.5;
    padding-top: 4rpx;
  }
  
  picker {
    flex: 1;
  }
  
  .picker-view {
    font-size: 28rpx;
    color: #334155;
    font-weight: 500;
    
    &.placeholder {
      color: #94A3B8;
    }
  }
}

.save-btn {
  margin-top: 64rpx;
  background: $primary-gradient;
  color: #fff;
  border-radius: 56rpx;
  font-size: 32rpx;
  font-weight: 700;
  height: 100rpx;
  line-height: 100rpx;
  border: none;
  box-shadow: 0 8rpx 32rpx rgba(255, 61, 0, 0.25);
  letter-spacing: 0.02em;
  transition: $transition-physics;
  
  &:active { 
    transform: scale(0.96); 
    box-shadow: 0 4rpx 12rpx rgba(255, 61, 0, 0.15); 
    opacity: 0.95;
  }
  
  &[disabled] {
    opacity: 0.6;
    background: #CBD5E1;
    box-shadow: none;
  }
}
</style>
