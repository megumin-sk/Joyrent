<template>
  <scroll-view class="page" scroll-y>
    <!-- 顶部Banner -->
    <view class="banner">
      <view class="banner-content">
        <text class="banner-title">PlayStation 5</text>
        <text class="banner-desc">硬核主机 · 高帧体验</text>
        <view class="banner-tag">4K HDR · DualSense</view>
      </view>
    </view>



    <!-- 游戏列表 -->
    <view class="section">
      <view class="section-title">旗舰作品</view>
      <view class="game-list">
        <view 
          class="game-item" 
          v-for="game in games" 
          :key="game.id"
          @tap="handleRent(game)"
        >
          <image class="game-cover" :src="getGameImageUrl(game.coverUrl)" mode="aspectFill" />
          <view class="game-info">
            <text class="game-title">{{ game.title }}</text>
            <text class="game-desc">{{ game.description || '暂无描述' }}</text>
            <view class="game-footer">
              <view class="price-tag">
                <text class="price">¥{{ game.dailyRentPrice }}</text>
                <text class="unit">/天</text>
              </view>
              <view :class="['status', game.availableStock > 0 ? 'in-stock' : 'out-stock']">
                {{ game.availableStock > 0 ? '现货' : '预约' }}
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="bottom-padding" />
  </scroll-view>
</template>

<script>
import { searchGamesByPlatform } from '@/api/game';
import { getGameImageUrl } from '@/utils/imageUrl';

export default {
  data() {
    return {
      stats: [
        { label: 'PS5 在库', value: '28套' },
        { label: '平均排队', value: '0.5天' },
        { label: '付费会员', value: '2,430+' }
      ],
      games: [],
      loading: true
    };
  },
  onLoad() {
    this.fetchGames();
  },
  methods: {
    getGameImageUrl,
    async fetchGames() {
      try {
        const res = await searchGamesByPlatform('PlayStation');
        if (res && res.code === 200) {
          this.games = res.data || [];
        }
      } catch (e) {
        console.error(e);
      } finally {
        this.loading = false;
      }
    },
    handleRent(game) {
      uni.navigateTo({
        url: `/pages/index/gameDetail?id=${game.id}`
      });
    }
  }
};
</script>

<style lang="scss" scoped>
/* Theme Mode B: PlayStation - Sleek & Flow */
$ps-blue: #0070D1;
$deep-space: #0B0D15;
$glass-border: rgba(255, 255, 255, 0.1);
$flow-curve: cubic-bezier(0.25, 0.1, 0.25, 1);

.page {
  min-height: 100vh;
  background-color: $deep-space;
  background-image: radial-gradient(circle at 50% 0%, rgba(0, 112, 209, 0.15) 0%, transparent 60%);
  box-sizing: border-box;
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  color: #F8FAFC;
}

.banner {
  margin: 32rpx;
  padding: 48rpx 40rpx;
  background: linear-gradient(180deg, #00439C 0%, #003067 100%);
  border-radius: 12rpx; /* Sharp & Sleek */
  box-shadow: 0 8rpx 32rpx rgba(0, 70, 160, 0.3);
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);

  // 标志性符号 (○ × □ △)
  &::before {
    content: '○ × □ △';
    position: absolute;
    right: 20rpx;
    bottom: 20rpx;
    font-size: 60rpx;
    font-weight: 200; /* 更细的线条 */
    color: rgba(255, 255, 255, 0.08);
    letter-spacing: 16rpx;
    transform: rotate(0deg);
    font-family: sans-serif;
  }
}

.banner-content {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  position: relative;
  z-index: 1;
}

.banner-title {
  font-size: 52rpx;
  font-weight: 300; /* 更优雅 */
  color: #fff;
  letter-spacing: 2rpx; /* 宽敞字间距 */
  text-shadow: 0 0 20rpx rgba(0, 112, 209, 0.5);
}

.banner-desc {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 24rpx;
  font-weight: 400;
  letter-spacing: 1rpx;
}

.banner-tag {
  display: inline-flex;
  align-self: flex-start;
  padding: 8rpx 24rpx;
  background: rgba(0, 112, 209, 0.2);
  border: 1px solid rgba(0, 112, 209, 0.4);
  color: #60A5FA;
  border-radius: 4rpx; /* 极小的圆角 */
  font-size: 24rpx;
  font-weight: 500;
  backdrop-filter: blur(4rpx);
}

/* Removed redundant .stats-row and .stat-item styles */

.section {
  margin: 0 32rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 300;
  color: #fff;
  margin-bottom: 32rpx;
  letter-spacing: 2rpx;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  
  &::before {
    content: '';
    display: block;
    width: 4rpx;
    height: 24rpx;
    background: $ps-blue;
    margin-right: 16rpx;
    box-shadow: 0 0 12rpx $ps-blue;
  }
}

.game-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.game-item {
  display: flex;
  background: rgba(20, 25, 40, 0.6);
  border-radius: 12rpx; /* Sharp & Sleek */
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.4s $flow-curve;
  
  &:active {
    background: rgba(30, 40, 60, 0.8);
    border-color: rgba(0, 112, 209, 0.3);
    box-shadow: 0 0 24rpx rgba(0, 112, 209, 0.1);
  }
}

.game-cover {
  width: 200rpx;
  height: 260rpx;
  flex-shrink: 0;
  background: #111;
  opacity: 0.9;
}

.game-info {
  flex: 1;
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 0;
}

.game-title {
  font-size: 30rpx;
  font-weight: 500;
  color: #E2E8F0;
  margin-bottom: 12rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: 1rpx;
}

.game-desc {
  font-size: 24rpx;
  color: #64748B;
  line-height: 1.6;
  margin-bottom: 24rpx;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.game-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.price-tag {
  display: flex;
  align-items: baseline;
}

.price {
  font-size: 36rpx;
  font-weight: 400;
  color: #93C5FD;
  font-family: 'DIN Alternate', sans-serif;
}

.unit {
  font-size: 22rpx;
  color: #475569;
  margin-left: 8rpx;
}

.status {
  padding: 6rpx 20rpx;
  border-radius: 4rpx;
  font-size: 22rpx;
  font-weight: 500;
  letter-spacing: 1rpx;
  border: 1px solid transparent;
}

.in-stock {
  background: rgba(0, 112, 209, 0.1);
  color: #60A5FA;
  border-color: rgba(0, 112, 209, 0.3);
}

.out-stock {
  background: rgba(255, 255, 255, 0.05);
  color: #94A3B8;
  border-color: rgba(255, 255, 255, 0.1);
}

.bottom-padding {
  height: 60rpx;
}
</style>