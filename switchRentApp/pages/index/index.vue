<template>
  <view class="page-container">
    <view class="home-bg">
      <view class="bg-grid"></view>
      <view class="bg-glow orb-1"></view>
      <view class="bg-glow orb-2"></view>
    </view>

    <!-- 顶部 -->
    <view class="nav-bar">
      <view class="status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
      <view class="nav-content" :class="{ searching: isSearching }">
        <view class="brand" :class="{ hidden: isSearching }">
          <text class="brand-text">JoyRent</text>
        </view>
        <view class="search-box" :class="{ expanded: isSearching }" @tap="openSearch">
          <text class="search-icon">🔍</text>
          <input
            class="search-input"
            v-model="searchKeyword"
            :placeholder="isSearching ? '搜游戏名，例如 塞尔达' : '搜索游戏'"
            :focus="isSearching"
            confirm-type="search"
            @focus="onSearchFocus"
            @confirm="doSearch"
            @blur="onSearchBlur"
          />
          <text
            v-if="isSearching && searchKeyword"
            class="search-clear"
            @tap.stop="clearSearch"
          >✕</text>
          <text v-if="isSearching" class="search-action" @tap.stop="doSearch">搜索</text>
        </view>
      </view>

      <transition name="search-suggest-drop">
        <view v-if="isSearching" class="search-suggest">
          <text class="suggest-label">热门：</text>
          <text
            v-for="keyword in hotKeywords"
            :key="keyword"
            class="suggest-chip"
            @tap="doSearch(keyword)"
          >
            {{ keyword }}
          </text>
        </view>
      </transition>
    </view>

    <view :style="{ height: (statusBarHeight + (isSearching ? 82 : 44)) + 'px' }"></view>
    <transition name="search-mask-fade">
      <view v-if="isSearching" class="search-mask" @tap="cancelSearch"></view>
    </transition>

    <!-- 主内容 -->
    <scroll-view scroll-y class="main-content">
      <!-- Banner -->
      <swiper class="banner" circular autoplay interval="4000" indicator-dots>
        <swiper-item v-for="banner in banners" :key="banner.id" @tap="handleBanner(banner)">
          <view class="banner-item" :style="{ background: banner.color }">
            <text class="banner-title">{{ banner.title }}</text>
          </view>
        </swiper-item>
      </swiper>

      <!-- 平台入口 -->
      <view class="platforms">
        <view class="platform-item" @tap="goToPlatform('switch')">
          <image class="platform-icon" src="/static/platform/Switch.png" mode="aspectFit" />
          <text class="platform-name">Switch</text>
        </view>
        <view class="platform-item" @tap="goToPlatform('ps5')">
          <image class="platform-icon" src="/static/platform/PlayStation.png" mode="aspectFit" />
          <text class="platform-name">PS5</text>
        </view>
      </view>

      <!-- 热门榜单 -->
      <view class="section">
        <view class="section-title">热门租赁</view>
        
        <view v-if="loading" class="loading">加载中...</view>
        
        <view v-else class="game-list">
          <view 
            class="game-card" 
            v-for="game in hotList" 
            :key="game.id"
            @tap="goToDetail(game)"
          >
            <image class="game-cover" :src="getGameImageUrl(game.coverUrl || game.cover_url)" mode="aspectFill" />
            <view class="game-info">
              <text class="game-title">{{ game.title }}</text>
              <view class="game-price">
                <text class="price">¥{{ game.dailyRentPrice || game.daily_rent_price }}</text>
                <text class="unit">/天</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <view style="height: 100rpx;"></view>
    </scroll-view>

    <!-- AI客服 -->
    <AiFab ref="aiFab" />
  </view>
</template>

<script>
import { getTopRentedGames } from '../../api/game';
import { getGameImageUrl } from '../../utils/imageUrl';
import AiFab from '@/components/AiFab/AiFab.vue';

export default {
  components: { AiFab },
  data() {
    return {
      statusBarHeight: 20,
      isSearching: false,
      searchKeyword: '',
      hotKeywords: ['塞尔达', '马里奥', '宝可梦', '双人成行'],
      loading: false,
      banners: [
        { id: 1, title: '年度最佳游戏', color: '#667eea' },
        { id: 2, title: 'Switch新机首发', color: '#e60012' },
        { id: 3, title: 'PS5独占大作', color: '#0070d1' }
      ],
      hotList: []
    };
  },
  onLoad() {
    this.fetchHotGames();
  },
  methods: {
    getGameImageUrl,
    
    openSearch() {
      this.isSearching = true;
    },

    onSearchFocus() {
      this.isSearching = true;
    },

    onSearchBlur() {
      setTimeout(() => {
        if (!this.searchKeyword) {
          this.isSearching = false;
        }
      }, 120);
    },

    clearSearch() {
      this.searchKeyword = '';
    },

    cancelSearch() {
      this.searchKeyword = '';
      this.isSearching = false;
    },

    doSearch(keyword) {
      const finalKeyword = (keyword || this.searchKeyword).trim();
      if (!finalKeyword) return;
      uni.navigateTo({ 
        url: `/pages/index/gameList?keyword=${encodeURIComponent(finalKeyword)}` 
      });
      this.isSearching = false;
      this.searchKeyword = '';
    },
    
    handleBanner(banner) {
      uni.showToast({ title: banner.title, icon: 'none' });
    },
    
    goToPlatform(platform) {
      const url = platform === 'switch' 
        ? '/pages/index/game/switchGame' 
        : '/pages/index/game/playstationGame';
      uni.navigateTo({ url });
    },
    
    goToDetail(game) {
      uni.navigateTo({ url: `/pages/index/gameDetail?id=${game.id}` });
    },
    
    fetchHotGames() {
      this.loading = true;
      getTopRentedGames().then(res => {
        if (res && res.code === 200 && res.data) {
          this.hotList = res.data.slice(0, 6);
        }
      }).finally(() => {
        this.loading = false;
      });
    }
  }
};
</script>

<style lang="scss" scoped>
$neon-purple: #b026ff;
$neon-cyan: #00f5ff;
$bg-primary: #0a0a0f;
$bg-secondary: #12121a;
$text-primary: #ffffff;
$text-secondary: rgba(255, 255, 255, 0.82);
$text-muted: rgba(255, 255, 255, 0.58);

.page-container {
  min-height: 100vh;
  background: $bg-primary;
  position: relative;
  overflow: hidden;
}

.home-bg {
  position: fixed;
  inset: 0;
  pointer-events: none;

  .bg-grid {
    position: absolute;
    inset: 0;
    background:
      linear-gradient(rgba(0, 245, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 245, 255, 0.03) 1px, transparent 1px);
    background-size: 56px 56px;
  }

  .bg-glow {
    position: absolute;
    border-radius: 50%;
    filter: blur(80rpx);
    opacity: 0.42;
  }

  .orb-1 {
    width: 420rpx;
    height: 420rpx;
    top: -120rpx;
    right: -100rpx;
    background: radial-gradient(circle, rgba(176, 38, 255, 0.6), transparent 70%);
  }

  .orb-2 {
    width: 360rpx;
    height: 360rpx;
    left: -140rpx;
    bottom: 120rpx;
    background: radial-gradient(circle, rgba(0, 245, 255, 0.45), transparent 70%);
  }
}

.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(10, 10, 15, 0.84);
  backdrop-filter: blur(12px);
}

.status-bar {
  width: 100%;
  background: transparent;
}

.nav-content {
  display: flex;
  align-items: center;
  height: 44px;
  width: 100%;
  padding: 0 32rpx;
  box-sizing: border-box;

  &.searching {
    .search-box {
      flex: 1;
    }
  }
}

.brand {
  flex-shrink: 0;
  width: 176rpx;
  position: relative;
  z-index: 2;
  transition: width 320ms cubic-bezier(0.22, 0.78, 0.26, 1), margin-right 320ms cubic-bezier(0.22, 0.78, 0.26, 1), opacity 220ms ease, transform 220ms ease;
  margin-right: 8rpx;
  overflow: hidden;
  
  &.hidden {
    width: 0;
    margin-right: 0;
    opacity: 0;
    transform: translateX(-8rpx);
  }
  
  .brand-text {
    font-size: 36rpx;
    font-weight: 900;
    letter-spacing: 2rpx;
    color: $text-primary;
    text-shadow: 0 0 14rpx rgba(176, 38, 255, 0.5);
  }
}

.search-box {
  flex: 1;
  min-width: 0;
  height: 64rpx;
  background: rgba(255, 255, 255, 0.05);
  border: 1rpx solid rgba(255, 255, 255, 0.12);
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  padding: 0 24rpx;
  box-sizing: border-box;
  transform: scaleX(1);
  transform-origin: left center;
  transition:
    width 320ms cubic-bezier(0.22, 0.78, 0.26, 1),
    transform 320ms cubic-bezier(0.22, 0.78, 0.26, 1),
    background 260ms ease,
    border-color 240ms ease,
    box-shadow 320ms cubic-bezier(0.22, 0.78, 0.26, 1);
  
  &.expanded {
    background: rgba(18, 18, 26, 0.9);
    border-color: rgba(0, 245, 255, 0.4);
    box-shadow: 0 0 26rpx rgba(0, 245, 255, 0.15);
    transform: scaleX(1);
  }
  
  .search-icon {
    font-size: 28rpx;
    margin-right: 12rpx;
  }
  
  .placeholder {
    font-size: 26rpx;
    color: $text-muted;
  }
  
  .search-input {
    flex: 1;
    font-size: 28rpx;
    color: $text-primary;
  }

  .search-clear {
    font-size: 20rpx;
    color: $text-muted;
    width: 30rpx;
    height: 30rpx;
    border-radius: 50%;
    border: 1rpx solid rgba(255, 255, 255, 0.22);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: 10rpx;
  }

  .search-action {
    font-size: 24rpx;
    color: $neon-cyan;
    font-weight: 700;
    padding-left: 16rpx;
  }
}

.search-mask {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 90;
  background: rgba(0, 0, 0, 0.01);
}

.search-suggest {
  padding: 10rpx 32rpx 16rpx;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12rpx;

  .suggest-label {
    font-size: 22rpx;
    color: $text-muted;
  }

  .suggest-chip {
    font-size: 22rpx;
    color: $text-secondary;
    background: rgba(255, 255, 255, 0.08);
    border: 1rpx solid rgba(255, 255, 255, 0.16);
    border-radius: 999rpx;
    padding: 8rpx 18rpx;
  }
}

.search-mask-fade-enter-active,
.search-mask-fade-leave-active {
  transition: opacity 200ms ease;
}

.search-mask-fade-enter-from,
.search-mask-fade-leave-to {
  opacity: 0;
}

.search-suggest-drop-enter-active,
.search-suggest-drop-leave-active {
  transition: all 260ms cubic-bezier(0.22, 0.78, 0.26, 1);
}

.search-suggest-drop-enter-from,
.search-suggest-drop-leave-to {
  opacity: 0;
  transform: translateY(-10rpx);
}



.main-content {
  height: 100vh;
  width: 100%;
  padding: 24rpx;
  box-sizing: border-box;
  position: relative;
  z-index: 1;
}

.banner {
  width: 100%;
  box-sizing: border-box;
  height: 300rpx;
  border-radius: 22rpx;
  margin-bottom: 32rpx;
  overflow: hidden;
  border: 1rpx solid rgba(255, 255, 255, 0.14);
  box-shadow: 0 12rpx 30rpx rgba(0, 0, 0, 0.35);
}

.banner-item {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  
  .banner-title {
    font-size: 40rpx;
    font-weight: bold;
    color: #fff;
    text-shadow: 0 6rpx 18rpx rgba(0, 0, 0, 0.35);
  }
}

.platforms {
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
  display: flex;
  gap: 24rpx;
  margin-bottom: 32rpx;
  background: rgba(255, 255, 255, 0.04);
  border: 1rpx solid rgba(255, 255, 255, 0.12);
  border-radius: 999rpx;
  padding: 10rpx;
}

.platform-item {
  flex: 1;
  min-width: 0;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.03);
  border: 1rpx solid rgba(255, 255, 255, 0.1);
  border-radius: 999rpx;
  padding: 14rpx 20rpx;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 18rpx rgba(0, 0, 0, 0.2);
}

.platform-icon {
  width: 74rpx;
  height: 38rpx;
  margin-right: 12rpx;
}

.platform-name {
  font-size: 26rpx;
  color: $text-primary;
  font-weight: 700;
}

.section {
  width: 100%;
  box-sizing: border-box;
  .section-title {
    font-size: 32rpx;
    font-weight: bold;
    color: $text-primary;
    margin-bottom: 24rpx;
  }
}

.loading {
  text-align: center;
  padding: 60rpx;
  color: $text-muted;
}

.game-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.game-card {
  box-sizing: border-box;
  width: calc(50% - 10rpx);
  background: rgba(18, 18, 26, 0.88);
  border: 1rpx solid rgba(255, 255, 255, 0.12);
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 12rpx 24rpx rgba(0,0,0,0.3);
}

.game-cover {
  width: 100%;
  height: 200rpx;
}

.game-info {
  padding: 20rpx;
}

.game-title {
  font-size: 28rpx;
  color: $text-primary;
  font-weight: 500;
  display: block;
  margin-bottom: 12rpx;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.game-price {
  .price {
    font-size: 32rpx;
    color: #ff3d00;
    font-weight: bold;
  }
  .unit {
    font-size: 22rpx;
    color: $text-muted;
  }
}
</style>
