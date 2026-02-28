<template>
  <view class="page">
    <view class="premium-header">
      <view class="header-glass">
        <text class="page-title">{{ pageTitle }}</text>
        <text class="page-sub">为您甄选高品质正版游戏内容</text>
      </view>
    </view>

    <view class="content-body">
      <view class="state-container" v-if="loading">
        <view class="loading-spinner"></view>
        <text>正在检索最佳游戏...</text>
      </view>

      <view class="game-feed" v-else-if="gameList.length">
        <view 
          class="game-card" 
          v-for="game in gameList" 
          :key="game.id" 
          @tap="handleGameClick(game)"
        >
          <view class="cover-wrapper">
            <image class="cover" :src="getGameImageUrl(game.coverUrl || game.cover_url)" mode="aspectFill" />
            <view class="platform-tag" :class="game.platform">{{ game.platform }}</view>
          </view>
          
          <view class="info">
            <view class="info-top">
              <text class="title">{{ game.title }}</text>
              <text class="subtitle">{{ game.genre || '热门推荐 · 支持中文' }}</text>
            </view>
            
            <view class="rent-row">
              <view class="price-container">
                <text class="symbol">¥</text>
                <text class="price">{{ game.dailyRentPrice || game.daily_rent_price }}</text>
                <text class="unit">/天</text>
              </view>
              
              <view :class="['stock-badge', (game.availableStock || game.available_stock) > 0 ? 'in-stock' : 'out-of-stock']">
                {{ (game.availableStock || game.available_stock) > 0 ? '立即租赁' : '到货通知' }}
              </view>
            </view>
          </view>
        </view>
      </view>

      <view class="state-container empty" v-else>
        <text class="empty-icon">📂</text>
        <text class="empty-text">{{ errorMessage || '暂无相关资源，换个关键词试试？' }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import { getGameList, searchGamesByPlatform, searchGamesByName } from '../../api/game';
import { getGameImageUrl } from '../../utils/imageUrl';

export default {
  data() {
    return {
      platformTabs: [
        { label: '全部', value: 'all' },
        { label: 'Switch', value: 'Switch' },
        { label: 'PlayStation', value: 'PlayStation' }
      ],
      currentPlatform: 'all',
      keyword: '',
      gameList: [],
      loading: false,
      errorMessage: ''
    };
  },
  computed: {
    pageTitle() {
      if (this.keyword) {
        return `"${this.keyword}"`;
      }
      const target = this.platformTabs.find(tab => tab.value === this.currentPlatform);
      return target ? target.label + '精选' : '全库精选';
    }
  },
  onLoad(query) {
    if (query?.name || query?.keyword) {
      this.keyword = decodeURIComponent(query.name || query.keyword);
    } else {
      const incoming = decodeURIComponent(query?.platform || '');
      this.currentPlatform = this.normalizePlatform(incoming);
    }
    this.fetchGames();
  },
  methods: {
    getGameImageUrl,
    handleGameClick(game) {
      uni.navigateTo({
        url: `/pages/index/gameDetail?id=${game.id}`
      });
    },
    normalizePlatform(value) {
      const whitelist = this.platformTabs.map(tab => tab.value);
      return whitelist.includes(value) ? value : 'all';
    },
    async fetchGames() {
      this.loading = true;
      this.errorMessage = '';
      try {
        let response;
        if (this.keyword) {
          response = await searchGamesByName(this.keyword);
        } else {
          response = this.currentPlatform === 'all'
            ? await getGameList()
            : await searchGamesByPlatform(this.currentPlatform);
        }
        
        this.gameList = this.normalizeGames(response);
        if (!this.gameList.length) {
          this.errorMessage = this.keyword ? `没有搜索到与 "${this.keyword}" 相关的游戏` : '该平台暂未上新，敬请期待';
        }
      } catch (error) {
        this.gameList = [];
        this.errorMessage = error?.message || '网络连接异常，请重试';
      } finally {
        this.loading = false;
      }
    },
    normalizeGames(response) {
      if (!response) return [];
      if (Array.isArray(response)) return response;
      if (Array.isArray(response.data)) return response.data;
      return [];
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
}

.premium-header {
  padding: 40rpx 32rpx;
  background: white;
  border-bottom: 1px solid rgba(0,0,0,0.03);
  
  .header-glass {
    .page-title {
      font-size: 48rpx;
      font-weight: 900;
      color: $text-main;
      letter-spacing: -0.04em;
    }
    .page-sub {
      display: block;
      margin-top: 8rpx;
      font-size: 24rpx;
      color: $text-sub;
      font-weight: 500;
    }
  }
}

.content-body {
  padding: 32rpx;
}

.game-feed {
  display: flex;
  flex-direction: column;
  gap: 32rpx;
}

.game-card {
  display: flex;
  background: #ffffff;
  border-radius: 32rpx;
  padding: 24rpx;
  box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.06), 0 0 0 1px rgba(0, 0, 0, 0.02);
  transition: $transition-physics;
  
  &:active {
    transform: scale(0.97);
    box-shadow: 0 2px 10px -2px rgba(0, 0, 0, 0.04);
  }
}

.cover-wrapper {
  position: relative;
  width: 220rpx;
  height: 280rpx;
  flex-shrink: 0;
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 8rpx 16rpx rgba(0,0,0,0.1);

  .cover {
    width: 100%;
    height: 100%;
  }

  .platform-tag {
    position: absolute;
    top: 12rpx;
    right: 12rpx;
    padding: 4rpx 12rpx;
    font-size: 18rpx;
    font-weight: 800;
    border-radius: 8rpx;
    color: white;
    backdrop-filter: blur(4px);
    
    &.Switch { background: #E60012; }
    &.PlayStation { background: #0070D1; }
  }
}

.info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-left: 28rpx;
  padding-top: 8rpx;
  padding-bottom: 8rpx;

  .title {
    font-size: 32rpx;
    font-weight: 800;
    color: $text-main;
    line-height: 1.3;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    overflow: hidden;
  }

  .subtitle {
    display: block;
    margin-top: 12rpx;
    font-size: 24rpx;
    color: $text-sub;
    font-weight: 500;
  }
}

.rent-row {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .price-container {
    color: #FF3D00;
    font-weight: 900;
    
    .symbol { font-size: 24rpx; }
    .price { font-size: 40rpx; margin: 0 4rpx; }
    .unit { font-size: 22rpx; color: $text-sub; font-weight: 500; }
  }

  .stock-badge {
    padding: 10rpx 24rpx;
    font-size: 22rpx;
    font-weight: 700;
    border-radius: 99rpx;
    
    &.in-stock {
      background: $primary-gradient;
      color: white;
      box-shadow: 0 4rpx 12rpx rgba(255, 61, 0, 0.2);
    }
    &.out-of-stock {
      background: #F1F5F9;
      color: #94A3B8;
    }
  }
}

.state-container {
  padding: 120rpx 0;
  text-align: center;
  color: $text-sub;

  &.empty {
    .empty-icon { font-size: 80rpx; display: block; margin-bottom: 24rpx; opacity: 0.5; }
    .empty-text { font-size: 28rpx; font-weight: 500; }
  }

  .loading-spinner {
    width: 60rpx;
    height: 60rpx;
    border: 6rpx solid #F1F5F9;
    border-top-color: #FF3D00;
    border-radius: 50%;
    margin: 0 auto 32rpx;
    animation: spin 0.8s linear infinite;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>


