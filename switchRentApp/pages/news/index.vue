<template>
    <view class="page">
      <view class="nav-bar">
        <view class="status-bar" :style="{ height: statusBarHeight + 'px' }"></view>
        <view class="nav-content">
          <text class="nav-title">游戏讯息</text>
        </view>
      </view>
  
      <view :style="{ height: (statusBarHeight + 44) + 'px' }"></view>
  
      <scroll-view
        class="body"
        scroll-y
        refresher-enabled
        :refresher-triggered="isRefreshing"
        @refresherrefresh="onPullDownRefresh"
      >
        <view class="hero">
          <view class="hero-top">
            <text class="badge">今日推荐</text>
            <text class="meta">共 {{ newsList.length }} 条更新</text>
          </view>
          <text class="hero-title">热门游戏情报速递</text>
          <text class="hero-sub">上新预告 · 活动福利 · 深度攻略</text>
          <view class="hero-tags">
            <view class="tag" v-for="chip in heroChips" :key="chip">{{ chip }}</view>
          </view>
        </view>
  
        <view class="filter-row">
          <view
            v-for="filter in filters"
            :key="filter.value"
            :class="['filter', currentFilter === filter.value ? 'active' : '']"
            @tap="changeFilter(filter.value)"
          >
            {{ filter.label }}
          </view>
        </view>
  
        <view class="state" v-if="loading">
          <text>资讯加载中...</text>
        </view>
        <view class="state" v-else-if="!filteredNews.length">
          <text>暂无相关资讯，稍后再来看看</text>
        </view>
        <view class="news-feed" v-else>
          <view
            class="news-card"
            v-for="news in filteredNews"
            :key="news.id"
            @tap="handleNewsTap(news)"
          >
            <image class="cover" :src="news.cover" mode="aspectFill" />
            <view class="content">
              <view class="title-row">
                <text class="tag-label">{{ news.tag }}</text>
                <text class="time">{{ news.publish_time }}</text>
              </view>
              <text class="title">{{ news.title }}</text>
              <text class="summary">{{ news.summary }}</text>
              <view class="footer">
                <view class="highlight">
                  <text class="dot"></text>
                  <text>热度 {{ news.hot }}%</text>
                </view>
                <view class="cta">查看详情</view>
              </view>
            </view>
          </view>
        </view>
  
        <view style="height: 40px;"></view>
      </scroll-view>
    </view>
  </template>
  
  <script>
  const MOCK_NEWS = [
    {
      id: 1,
      title: '《马里奥派对：巨星盛会》国庆档租赁预约开启',
      tag: '上新预告',
      summary: '双人/多人派对新作 9.28 上架，支持 Joy-Con 共享，预定即送彩带礼包。',
      cover: 'https://via.placeholder.com/400x260/ff5a5f/fff?text=Party',
      publish_time: '09-12',
      type: 'new',
      hot: 92
    },
    {
      id: 2,
      title: 'PS5 秋季折扣季：13 款独占大作租赁立减 30%',
      tag: '福利活动',
      summary: '神秘海域、战神、宇宙机器人等均可参与活动，顺丰包邮。',
      cover: 'https://via.placeholder.com/400x260/0070d1/fff?text=PS5',
      publish_time: '09-11',
      type: 'promo',
      hot: 88
    },
    {
      id: 3,
      title: '上手指南：如何 15 分钟搞定 Switch 首租体验',
      tag: '租赁攻略',
      summary: '从下单、押金到收货安装，一篇文章教你快速完成首次租赁体验。',
      cover: 'https://via.placeholder.com/400x260/7c4dff/fff?text=Guide',
      publish_time: '09-10',
      type: 'guide',
      hot: 80
    }
  ];
  
  export default {
    data() {
      return {
        statusBarHeight: 20,
        isRefreshing: false,
        loading: false,
        heroChips: ['顺丰包邮', '当天发货', '官方正版'],
        filters: [
          { label: '全部', value: 'all' },
          { label: '上新预告', value: 'new' },
          { label: '福利活动', value: 'promo' },
          { label: '租赁攻略', value: 'guide' }
        ],
        currentFilter: 'all',
        newsList: []
      };
    },
    computed: {
      filteredNews() {
        if (this.currentFilter === 'all') {
          return this.newsList;
        }
        return this.newsList.filter(item => item.type === this.currentFilter);
      }
    },
    created() {
      const info = uni.getSystemInfoSync();
      if (info.statusBarHeight) {
        this.statusBarHeight = info.statusBarHeight;
      }
    },
    onLoad() {
      this.fetchNews();
    },
    methods: {
      onPullDownRefresh() {
        this.isRefreshing = true;
        this.fetchNews(() => {
          this.isRefreshing = false;
          uni.stopPullDownRefresh();
        });
      },
      fetchNews(done) {
        this.loading = true;
        setTimeout(() => {
          this.newsList = MOCK_NEWS;
          this.loading = false;
          done && done();
        }, 400);
      },
      changeFilter(value) {
        if (value === this.currentFilter) return;
        this.currentFilter = value;
      },
      handleNewsTap(news) {
        uni.showToast({ title: `查看：${news.title}`, icon: 'none' });
      }
    }
  };
  </script>
  
  <style lang="scss" scoped>
  // 定义主色调
  $brand-primary: #7c4dff; // 紫色
  $brand-secondary: #ff5a5f; // 红色 (热度用)
  $bg-page: #f5f7fa;
  
  .page {
    min-height: 100vh;
    background-color: $bg-page;
    display: flex;
    flex-direction: column;
  }
  
  /* 导航栏 (统一风格) */
  .nav-bar {
    background: #fff; // 改为白色背景
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 100;
    border-bottom: 1rpx solid #f0f0f0;
  }
  .status-bar {
    background: #fff;
    width: 100%;
  }
  .nav-content {
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    .nav-title {
      font-size: 32rpx;
      font-weight: bold;
      color: #333;
    }
  }
  
  /* 主体滚动区 */
  .body {
    flex: 1;
    height: 0;
    padding: 24rpx 28rpx 40rpx; // 增加顶部 padding
    box-sizing: border-box;
  }
  
  /* Hero 深色卡片 */
  .hero {
    padding: 32rpx;
    border-radius: 28rpx;
    // 使用更契合主题的深紫色渐变
    background: linear-gradient(135deg, #3a364a 0%, #5e5875 100%);
    color: #fff;
    box-shadow: 0 20rpx 35rpx rgba(58, 54, 74, 0.25);
  }
  
  .hero-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12rpx;
    font-size: 24rpx;
  }
  
  .badge {
    padding: 6rpx 16rpx;
    border-radius: 999rpx;
    background: rgba(255, 255, 255, 0.2);
    font-weight: 600;
  }
  
  .meta { opacity: 0.8; }
  .hero-title { font-size: 40rpx; font-weight: 700; margin-bottom: 8rpx; }
  .hero-sub { font-size: 26rpx; opacity: 0.9; }
  
  .hero-tags {
    margin-top: 24rpx;
    display: flex;
    flex-wrap: wrap;
    gap: 12rpx;
    .tag {
      font-size: 22rpx;
      padding: 8rpx 18rpx;
      border-radius: 999rpx;
      background: rgba(255, 255, 255, 0.15);
    }
  }
  
  /* 筛选 Tabs */
  .filter-row {
    margin: 32rpx 0 24rpx;
    display: flex;
    gap: 16rpx;
  }
  
  .filter {
    flex: 1;
    text-align: center;
    padding: 14rpx 0;
    border-radius: 18rpx;
    background: #fff; // 白底
    color: #666;
    font-size: 26rpx;
    box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.04);
    transition: all 0.3s;
  }
  
  .filter.active {
    background: $brand-primary; // 激活使用主色
    color: #fff;
    font-weight: 600;
    box-shadow: 0 8rpx 20rpx rgba(124, 77, 255, 0.25);
  }
  
  /* 新闻列表 */
  .news-feed {
    display: flex;
    flex-direction: column;
    gap: 24rpx;
  }
  
  .news-card {
    display: flex;
    gap: 20rpx;
    background: #fff;
    border-radius: 24rpx;
    padding: 20rpx;
    box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04); // 统一阴影
  }
  
  .cover {
    width: 200rpx;
    height: 200rpx; // 稍微调小一点，更紧凑
    border-radius: 16rpx;
    flex-shrink: 0;
  }
  
  .content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  
  .title-row {
    display: flex;
    align-items: center;
    margin-bottom: 8rpx;
  }
  
  .tag-label {
    font-size: 20rpx;
    color: $brand-primary;
    background: rgba(124, 77, 255, 0.1);
    padding: 4rpx 10rpx;
    border-radius: 6rpx;
    margin-right: 12rpx;
  }
  
  .time { font-size: 22rpx; color: #ccc; }
  
  .title {
    font-size: 30rpx;
    font-weight: 600;
    color: #333;
    line-height: 1.4;
    margin-bottom: 8rpx;
    display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden;
  }
  
  .summary {
    font-size: 24rpx;
    color: #888;
    line-height: 1.5;
    display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden;
  }
  
  .footer {
    margin-top: 12rpx;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .highlight {
    display: flex;
    align-items: center;
    font-size: 22rpx;
    color: $brand-secondary; // 使用红色系
  }
  
  .dot {
    width: 10rpx; height: 10rpx;
    border-radius: 50%;
    background: $brand-secondary;
    margin-right: 8rpx;
  }
  
  .cta {
    padding: 6rpx 18rpx;
    border-radius: 999rpx;
    border: 1rpx solid #eee;
    font-size: 22rpx;
    color: #999;
  }
  
  .state {
    padding: 80rpx 0;
    text-align: center;
    color: #ccc;
    font-size: 26rpx;
  }
  </style>