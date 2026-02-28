<template>
  <view class="page-container">
    <view class="page-bg"></view>
    
    <!-- 加载状态 -->
    <view v-if="loading" class="loading-screen">
      <view class="loading-spinner-large"></view>
      <text class="loading-text">正在加载游戏...</text>
    </view>

    <block v-else-if="game">
      <!-- 顶部轮播 -->
      <view class="hero-section">
        <swiper class="hero-swiper" autoplay circular interval="5000">
          <swiper-item>
            <image :src="getGameImageUrl(game.coverUrl || game.cover_url)" mode="aspectFill" class="hero-image" />
            <view class="hero-overlay">
              <view class="hero-glow"></view>
            </view>
          </swiper-item>
        </swiper>
        <view class="back-btn" @tap="handleBack">
          <text class="back-icon">‹</text>
        </view>
      </view>

      <!-- 核心信息卡片 -->
      <view class="info-card">
        <view class="card-header">
          <view class="price-section">
            <text class="price-label">日租金</text>
            <view class="price-display">
              <text class="price-symbol">¥</text>
              <text class="price-amount">{{ game.dailyRentPrice || game.daily_rent_price }}</text>
              <text class="price-unit">/天</text>
            </view>
          </view>
          <view class="stock-badge" :class="{ 'out': (game.availableStock || game.available_stock) === 0 }">
            <text class="stock-icon">📦</text>
            <text>{{ (game.availableStock || game.available_stock) > 0 ? `库存 ${game.availableStock || game.available_stock}` : '暂时售罄' }}</text>
          </view>
        </view>
        
        <text class="game-title">{{ game.title }}</text>
        
        <view class="tags-row">
          <view class="platform-tag" :class="game.platform">{{ game.platform }}</view>
          <view class="feature-tag" v-for="(tag, index) in gameTags" :key="index">{{ tag }}</view>
        </view>
        
        <view class="stats-row">
          <view class="stat-item">
            <text class="stat-value">{{ game.totalRentCount || game.total_rent_count || 0 }}</text>
            <text class="stat-label">累计租赁</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-value">¥{{ game.depositPrice || game.deposit_price }}</text>
            <text class="stat-label">押金</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-value">4.9</text>
            <text class="stat-label">评分</text>
          </view>
        </view>
      </view>

      <!-- 租赁周期选择 -->
      <view class="section-card">
        <view class="section-title">
          <text class="title-icon">◆</text>
          <text>选择租赁周期</text>
        </view>
        <view class="duration-grid">
          <view 
            class="duration-item" 
            v-for="days in [3, 7, 15, 30]" 
            :key="days"
            :class="{ active: selectedDays === days }"
            @tap="selectDuration(days)"
          >
            <text class="duration-days">{{ days }}天</text>
            <text class="duration-price">¥{{ ((game.dailyRentPrice || game.daily_rent_price) * days).toFixed(0) }}</text>
            <view class="discount-tag" v-if="days >= 15">省</view>
          </view>
        </view>
      </view>

      <!-- 游戏详情 -->
      <view class="section-card">
        <view class="section-title">
          <text class="title-icon">◆</text>
          <text>游戏详情</text>
        </view>
        <text class="description">{{ game.description || '暂无详细介绍' }}</text>
      </view>

      <!-- 用户评价 -->
      <view class="section-card">
        <view class="section-header">
          <view class="section-title">
            <text class="title-icon">◆</text>
            <text>用户评价</text>
          </view>
          <text class="view-all" @tap="viewAllReviews">查看全部 ➤</text>
        </view>
        
        <view v-if="reviewsLoading" class="reviews-loading">
          <view class="loading-spinner-small"></view>
          <text>加载中...</text>
        </view>
        
        <view v-else-if="reviews.length === 0" class="no-reviews">
          <text class="no-reviews-icon">💬</text>
          <text>暂无评价，快来抢沙发吧~</text>
        </view>
        
        <view v-else class="reviews-list">
          <view class="review-item" v-for="review in reviews.slice(0, 3)" :key="review.id">
            <view class="review-header">
              <image class="review-avatar" :src="review.avatar || '/static/icons/default-avatar.png'" mode="aspectFill" />
              <view class="review-meta">
                <text class="review-name">{{ review.nickname || '匿名玩家' }}</text>
                <view class="review-rating">
                  <text v-for="star in 5" :key="star" class="star" :class="{ filled: star <= review.rating }">★</text>
                </view>
              </view>
              <text class="review-date">{{ formatDate(review.createdAt) }}</text>
            </view>
            <text class="review-content">{{ review.content }}</text>
          </view>
        </view>
      </view>

      <view style="height: 180rpx;"></view>

      <!-- 底部操作栏 -->
      <view class="action-bar">
        <view class="action-side">
          <view class="action-btn" @tap="handleHome">
            <text class="action-icon">🏠</text>
            <text class="action-text">首页</text>
          </view>
          <view class="action-btn" @tap="goToCart">
            <text class="action-icon">🛒</text>
            <text class="action-text">购物车</text>
            <view class="cart-badge" v-if="cartCount > 0">{{ cartCount > 99 ? '99+' : cartCount }}</view>
          </view>
        </view>
        <view 
          class="main-action-btn" 
          :class="{ disabled: (game.availableStock || game.available_stock) === 0 }"
          @tap="handleAddToCart"
        >
          <text class="btn-icon">🎮</text>
          <text>{{ (game.availableStock || game.available_stock) > 0 ? '加入购物车' : '到货通知' }}</text>
        </view>
      </view>
    </block>
  </view>
</template>

<script>
import { getGameDetail } from '../../api/game';
import { addToCart, getCartList } from '../../api/cart';
import { getReviewsByGameId } from '../../api/gameReview';
import { getGameImageUrl } from '../../utils/imageUrl';

export default {
  data() {
    return {
      loading: true,
      gameId: null,
      game: null,
      selectedDays: 7,
      gameTags: ['支持中文', '高分推荐', '动作冒险'],
      cartCount: 0,
      reviews: [],
      reviewsLoading: false
    };
  },
  onLoad(options) {
    this.gameId = options.id;
    this.loadGameDetail();
  },
  onShow() {
    this.fetchCartCount();
    if (this.gameId) {
      this.loadReviews();
    }
  },
  methods: {
    getGameImageUrl,
    handleBack() {
      uni.navigateBack({ delta: 1 });
    },
    async loadGameDetail() {
      if (!this.gameId) return;
      this.loading = true;
      try {
        const res = await getGameDetail(this.gameId);
        if (res && res.code === 200) {
          this.game = res.data;
        }
      } catch (error) {
        uni.showToast({ title: '加载失败', icon: 'none' });
      } finally {
        this.loading = false;
      }
    },
    async loadReviews() {
      this.reviewsLoading = true;
      try {
        const res = await getReviewsByGameId(this.gameId);
        if (res && res.code === 200) {
          this.reviews = res.data || [];
        }
      } catch (e) {
        console.error('加载评价失败', e);
      } finally {
        this.reviewsLoading = false;
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      const month = date.getMonth() + 1;
      const day = date.getDate();
      return `${month}月${day}日`;
    },
    
    viewAllReviews() {
      uni.navigateTo({
        url: `/pages/index/gameReviews?gameId=${this.gameId}`
      });
    },
    selectDuration(days) {
      this.selectedDays = days;
    },
    handleHome() {
      uni.switchTab({ url: '/pages/index/index' });
    },
    goToCart() {
      uni.navigateTo({ url: '/pages/cart/index' });
    },
    async fetchCartCount() {
      const token = uni.getStorageSync('token');
      if (!token) {
        this.cartCount = 0;
        return;
      }
      try {
        const res = await getCartList();
        if (res && res.code === 200) {
          this.cartCount = res.data ? res.data.length : 0;
        }
      } catch (e) {
        this.cartCount = 0;
      }
    },
    async handleAddToCart() {
      if (!this.game || (this.game.availableStock || this.game.available_stock) === 0) return;
      
      try {
        const res = await addToCart({
          gameId: this.gameId,
          rentDays: this.selectedDays
        });
        if (res && res.code === 200) {
          uni.showToast({ title: '已加入购物车', icon: 'success' });
          this.cartCount++;
        } else {
          uni.showToast({ title: res.msg || '添加失败', icon: 'none' });
        }
      } catch (e) {
        // 401 会自动跳转登录
      }
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
$ease-out-back: cubic-bezier(0.34, 1.56, 0.64, 1);

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

// 加载状态
.loading-screen {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  
  .loading-spinner-large {
    width: 80rpx;
    height: 80rpx;
    border: 6rpx solid rgba(255, 255, 255, 0.1);
    border-top-color: $neon-cyan;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  .loading-text {
    margin-top: 32rpx;
    font-size: 28rpx;
    color: $text-muted;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

// Hero 区域
.hero-section {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  
  .hero-swiper {
    width: 100%;
    height: 100%;
  }
  
  .hero-image {
    width: 100%;
    height: 100%;
  }
  
  .hero-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 200rpx;
    background: linear-gradient(to top, $bg-primary 0%, transparent 100%);
    pointer-events: none;
  }
  
  .hero-glow {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at center, rgba(0, 245, 255, 0.05) 0%, transparent 70%);
  }
  
  .back-btn {
    position: absolute;
    top: calc(var(--status-bar-height, 0) + 20rpx);
    left: 32rpx;
    width: 72rpx;
    height: 72rpx;
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(10px);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
    
    .back-icon {
      font-size: 48rpx;
      color: white;
      font-weight: 300;
      line-height: 1;
    }
  }
}

// 信息卡片
.info-card {
  margin: -60rpx 32rpx 32rpx;
  background: $bg-card;
  border: 1px solid $border-color;
  border-radius: 32rpx;
  padding: 40rpx;
  position: relative;
  z-index: 10;
  backdrop-filter: blur(20px);
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24rpx;
  }
  
  .price-section {
    .price-label {
      font-size: 22rpx;
      color: $text-muted;
      margin-bottom: 8rpx;
      display: block;
    }
    
    .price-display {
      display: flex;
      align-items: baseline;
      
      .price-symbol {
        font-size: 32rpx;
        font-weight: 700;
        color: $neon-cyan;
      }
      .price-amount {
        font-size: 64rpx;
        font-weight: 800;
        color: $neon-cyan;
        margin: 0 8rpx;
      }
      .price-unit {
        font-size: 26rpx;
        color: $text-muted;
      }
    }
  }
  
  .stock-badge {
    display: flex;
    align-items: center;
    gap: 8rpx;
    font-size: 22rpx;
    padding: 12rpx 24rpx;
    background: rgba(0, 255, 136, 0.15);
    color: #00ff88;
    border-radius: 99rpx;
    font-weight: 600;
    
    &.out {
      background: rgba(255, 0, 128, 0.15);
      color: $neon-pink;
    }
    
    .stock-icon {
      font-size: 20rpx;
    }
  }
}

.game-title {
  font-size: 40rpx;
  font-weight: 800;
  color: $text-primary;
  line-height: 1.3;
  margin-bottom: 24rpx;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 32rpx;
  
  .platform-tag {
    padding: 8rpx 24rpx;
    border-radius: 12rpx;
    font-size: 22rpx;
    font-weight: 800;
    color: white;
    
    &.Switch { background: rgba(230, 0, 18, 0.9); }
    &.PlayStation { background: rgba(0, 112, 209, 0.9); }
  }
  
  .feature-tag {
    padding: 8rpx 24rpx;
    border-radius: 12rpx;
    font-size: 22rpx;
    background: rgba(255, 255, 255, 0.05);
    color: $text-secondary;
    font-weight: 600;
    border: 1px solid rgba(255, 255, 255, 0.08);
  }
}

.stats-row {
  display: flex;
  align-items: center;
  padding-top: 32rpx;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  
  .stat-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    
    .stat-value {
      font-size: 36rpx;
      font-weight: 800;
      color: $text-primary;
      margin-bottom: 8rpx;
    }
    .stat-label {
      font-size: 22rpx;
      color: $text-muted;
    }
  }
  
  .stat-divider {
    width: 1rpx;
    height: 60rpx;
    background: rgba(255, 255, 255, 0.08);
  }
}

// 区块卡片
.section-card {
  margin: 0 32rpx 32rpx;
  background: $bg-card;
  border: 1px solid $border-color;
  border-radius: 32rpx;
  padding: 32rpx;
  backdrop-filter: blur(20px);
  
  .section-title {
    display: flex;
    align-items: center;
    gap: 12rpx;
    font-size: 32rpx;
    font-weight: 800;
    color: $text-primary;
    margin-bottom: 24rpx;
    letter-spacing: 1rpx;
    
    .title-icon {
      color: $neon-cyan;
      font-size: 24rpx;
    }
  }
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24rpx;
    
    .section-title {
      margin-bottom: 0;
    }
    
    .view-all {
      font-size: 24rpx;
      color: $neon-cyan;
    }
  }
}

// 租赁周期
.duration-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16rpx;
  
  .duration-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 28rpx 0;
    border-radius: 20rpx;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    position: relative;
    overflow: hidden;
    transition: all 0.3s $ease-out-back;

    &:active { transform: scale(0.95); }

    &.active {
      background: rgba(176, 38, 255, 0.15);
      border-color: rgba(176, 38, 255, 0.5);
      box-shadow: 0 0 30rpx rgba(176, 38, 255, 0.2);
      
      .duration-days { 
        color: $neon-cyan; 
        font-weight: 800; 
      }
      .duration-price { 
        color: $neon-purple; 
        font-weight: 700; 
      }
    }

    .duration-days { 
      font-size: 30rpx; 
      color: $text-primary; 
      margin-bottom: 8rpx; 
      font-weight: 700;
    }
    .duration-price { 
      font-size: 24rpx; 
      color: $text-muted; 
      font-weight: 600;
    }
    .discount-tag {
      position: absolute;
      top: 0;
      right: 0;
      background: $neon-pink;
      color: white;
      font-size: 16rpx;
      padding: 4rpx 10rpx;
      border-bottom-left-radius: 12rpx;
      font-weight: 700;
    }
  }
}

.description {
  font-size: 28rpx;
  color: $text-secondary;
  line-height: 1.8;
}

// 评价区
.reviews-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48rpx 0;
  color: $text-muted;
  font-size: 26rpx;
  
  .loading-spinner-small {
    width: 48rpx;
    height: 48rpx;
    border: 4rpx solid rgba(255, 255, 255, 0.1);
    border-top-color: $neon-cyan;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 16rpx;
  }
}

.no-reviews {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 64rpx 0;
  color: $text-muted;
  font-size: 28rpx;
  
  .no-reviews-icon {
    font-size: 64rpx;
    margin-bottom: 16rpx;
    opacity: 0.5;
  }
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 32rpx;
}

.review-item {
  padding-bottom: 32rpx;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  
  &:last-child {
    padding-bottom: 0;
    border-bottom: none;
  }
  
  .review-header {
    display: flex;
    align-items: center;
    margin-bottom: 16rpx;
    
    .review-avatar {
      width: 72rpx;
      height: 72rpx;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.05);
      margin-right: 20rpx;
      border: 2rpx solid rgba(255, 255, 255, 0.08);
    }
    
    .review-meta {
      flex: 1;
      
      .review-name {
        font-size: 28rpx;
        font-weight: 700;
        color: $text-primary;
        display: block;
        margin-bottom: 4rpx;
      }
      
      .review-rating {
        display: flex;
        gap: 4rpx;
        
        .star {
          font-size: 22rpx;
          color: rgba(255, 255, 255, 0.2);
          
          &.filled {
            color: #ffd700;
          }
        }
      }
    }
    
    .review-date {
      font-size: 22rpx;
      color: $text-muted;
    }
  }
  
  .review-content {
    font-size: 28rpx;
    color: $text-secondary;
    line-height: 1.6;
    padding-left: 92rpx;
  }
}

// 底部操作栏
.action-bar {
  position: fixed;
  bottom: 40rpx;
  left: 32rpx;
  right: 32rpx;
  height: 120rpx;
  background: rgba(20, 20, 35, 0.98);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 60rpx;
  display: flex;
  align-items: center;
  padding: 0 16rpx 0 32rpx;
  backdrop-filter: blur(20px);
  z-index: 100;
  box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.4);

  .action-side {
    display: flex;
    gap: 32rpx;
    margin-right: 32rpx;
    
    .action-btn {
      display: flex;
      flex-direction: column;
      align-items: center;
      position: relative;
      
      &:active { transform: scale(0.9); }
      
      .action-icon { 
        font-size: 40rpx; 
        margin-bottom: 4rpx; 
      }
      .action-text { 
        font-size: 18rpx; 
        color: $text-muted; 
        font-weight: 600;
      }
      
      .cart-badge {
        position: absolute;
        top: -8rpx;
        right: -8rpx;
        min-width: 32rpx;
        height: 32rpx;
        line-height: 32rpx;
        text-align: center;
        background: $neon-pink;
        color: white;
        font-size: 18rpx;
        font-weight: 700;
        border-radius: 16rpx;
        padding: 0 8rpx;
      }
    }
  }

  .main-action-btn {
    flex: 1;
    height: 88rpx;
    border-radius: 44rpx;
    background: $gradient-primary;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12rpx;
    color: white;
    font-size: 28rpx;
    font-weight: 800;
    box-shadow: 0 8rpx 30rpx rgba(176, 38, 255, 0.4);
    transition: all 0.2s;
    
    &:active { 
      transform: scale(0.96); 
      box-shadow: 0 4rpx 15rpx rgba(176, 38, 255, 0.3);
    }
    
    &.disabled { 
      background: rgba(255, 255, 255, 0.1); 
      color: $text-muted; 
      box-shadow: none;
    }
    
    .btn-icon {
      font-size: 32rpx;
    }
  }
}
</style>