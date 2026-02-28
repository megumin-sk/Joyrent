<template>
  <view class="container">
    <!-- 顶部评分概览 -->
    <view class="header-card">
      <view class="score-section">
        <text class="score">4.8</text>
        <view class="stars">
          <text class="star-icon">★★★★★</text>
        </view>
        <text class="total-reviews">基于 128 条评价</text>
      </view>
      <view class="ai-summary">
        <view class="ai-title">
          <text class="ai-icon">🤖</text>
          <text>AI 智能分析摘要</text>
        </view>
        <view class="ai-tags">
          <view class="ai-tag positive">画面精美 (89%)</view>
          <view class="ai-tag positive">剧情感人 (92%)</view>
          <view class="ai-tag negative">物流稍慢 (15%)</view>
        </view>
      </view>
    </view>

    <!-- 筛选标签 -->
    <scroll-view scroll-x class="filter-scroll" :show-scrollbar="false">
      <view class="filter-list">
        <view 
          v-for="(item, index) in filters" 
          :key="index"
          :class="['filter-item', currentFilter === index ? 'active' : '']"
          @click="currentFilter = index"
        >
          {{ item }}
        </view>
      </view>
    </scroll-view>

    <!-- 评价列表 -->
    <view class="review-list">
      <view class="review-item" v-for="(review, index) in reviews" :key="index">
        <view class="user-info">
          <image class="avatar" :src="review.avatar" mode="aspectFill"></image>
          <view class="user-meta">
            <text class="nickname">{{ review.nickname }}</text>
            <view class="rating-row">
              <text class="stars">{{ '★'.repeat(review.rating) }}</text>
              <text class="date">{{ review.date }}</text>
            </view>
          </view>
        </view>

        <view class="content">
          {{ review.content }}
        </view>

        <!-- AI 情感分析展示 -->
        <view class="ai-analysis-box" v-if="review.aiEmotion">
          <view class="ai-label">AI 深度分析:</view>
          <view class="dimension-grid">
            <view 
              v-for="(sentiment, dim) in review.aiEmotion" 
              :key="dim" 
              class="dim-item"
              :class="sentiment === 'POSITIVE' ? 'positive' : 'negative'"
              v-if="sentiment !== 'NONE' && sentiment !== 'NEUTRAL'"
            >
              <text class="dim-name">{{ getDimName(dim) }}</text>
              <text class="dim-val">{{ getSentimentLabel(sentiment) }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部评论输入框 -->
    <view class="comment-bar">
      <!-- 星级选择 -->
      <view class="star-selector">
        <text v-for="star in 5"
              :key="star"
              class="star"
              :class="{filled: star <= newReview.rating}"
              @tap="newReview.rating = star">★</text>
      </view>

      <!-- 文本输入 -->
      <textarea v-model="newReview.content"
                placeholder="写下你的评价..."
                class="comment-input"
                maxlength="200"
                auto-height
                :adjust-position="false"/>

      <!-- 发送按钮 -->
      <button class="send-btn"
              @tap="submitReview"
              :disabled="!newReview.content.trim()">发送</button>
    </view>
  </view>
</template>

<script>
import { getReviewsByGameId, submitReview } from '../../api/gameReview';

export default {
  data() {
    return {
      gameId: null,
      currentFilter: 0,
      filters: ['全部', '最新', '好评', '差评', '有图'],
      reviews: [],
      // 新增：用户待提交的评论模型
      newReview: {
        rating: 5,
        content: ''
      }
    };
  },
  onLoad(options) {
    // 读取路由传来的 gameId
    this.gameId = Number(options.gameId) || null;
    if (this.gameId) {
      this.loadReviews();
    }
  },
  methods: {
    // 加载评论列表
    async loadReviews() {
      if (!this.gameId) return;
      try {
        const res = await getReviewsByGameId(this.gameId);
        if (res && res.code === 200) {
          this.reviews = res.data || [];
        } else {
          uni.showToast({ title: res.msg || '加载失败', icon: 'none' });
        }
      } catch (e) {
        console.error('加载评论异常', e);
        uni.showToast({ title: '网络异常', icon: 'none' });
      }
    },

    // 提交新评论
    async submitReview() {
      if (!this.newReview.content.trim()) return;
      try {
        const payload = {
          gameId: this.gameId,
          rating: this.newReview.rating,
          content: this.newReview.content.trim()
        };
        const res = await submitReview(payload);
        if (res && res.code === 200) {
          uni.showToast({ title: '评论成功', icon: 'success' });
          // 清空输入框
          this.newReview.rating = 5;
          this.newReview.content = '';
          // 重新加载评论列表
          this.loadReviews();
        } else {
          uni.showToast({ title: res.msg || '提交失败', icon: 'none' });
        }
      } catch (e) {
        console.error('提交评论异常', e);
        uni.showToast({ title: '网络异常', icon: 'none' });
      }
    },

    getDimName(key) {
      const map = {
        visuals: '画面',
        story: '剧情',
        audio: '音效',
        gameplay: '玩法',
        price: '价格',
        logistics: '物流',
        service: '服务',
        condition: '成色'
      };
      return map[key] || key;
    },
    getSentimentClass(sentiment) {
      if (sentiment === 'POSITIVE') return 'positive';
      if (sentiment === 'NEGATIVE') return 'negative';
      return 'neutral';
    },
    getSentimentLabel(sentiment) {
      if (sentiment === 'POSITIVE') return '👍 好评';
      if (sentiment === 'NEGATIVE') return '👎 差评';
      return '😐 一般';
    }
  }
};
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding-bottom: 40rpx;
}

/* 头部卡片 */
.header-card {
  background: linear-gradient(135deg, #2b32b2 0%, #1488cc 100%);
  color: #fff;
  padding: 40rpx;
  border-radius: 0 0 40rpx 40rpx;
  box-shadow: 0 10rpx 30rpx rgba(20, 136, 204, 0.3);
  margin-bottom: 30rpx;

  .score-section {
    text-align: center;
    margin-bottom: 30rpx;
    
    .score {
      font-size: 80rpx;
      font-weight: bold;
      line-height: 1;
    }
    .stars {
      color: #ffd700;
      font-size: 32rpx;
      margin: 10rpx 0;
    }
    .total-reviews {
      font-size: 24rpx;
      opacity: 0.8;
    }
  }

  .ai-summary {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 20rpx;
    padding: 20rpx;
    
    .ai-title {
      font-size: 28rpx;
      font-weight: bold;
      margin-bottom: 15rpx;
      display: flex;
      align-items: center;
      
      .ai-icon {
        margin-right: 10rpx;
      }
    }

    .ai-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 15rpx;
      
      .ai-tag {
        font-size: 22rpx;
        padding: 6rpx 16rpx;
        border-radius: 30rpx;
        
        &.positive {
          background: rgba(76, 217, 100, 0.2);
          color: #e0ffd6;
          border: 1px solid rgba(76, 217, 100, 0.3);
        }
        &.negative {
          background: rgba(255, 59, 48, 0.2);
          color: #ffd6d6;
          border: 1px solid rgba(255, 59, 48, 0.3);
        }
      }
    }
  }
}

/* 筛选器 */
.filter-scroll {
  white-space: nowrap;
  margin-bottom: 20rpx;
  
  .filter-list {
    padding: 0 30rpx;
    display: flex;
    
    .filter-item {
      display: inline-block;
      padding: 12rpx 30rpx;
      background: #fff;
      border-radius: 40rpx;
      margin-right: 20rpx;
      font-size: 26rpx;
      color: #666;
      box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.03);
      transition: all 0.3s;
      
      &.active {
        background: #007aff;
        color: #fff;
        box-shadow: 0 4rpx 15rpx rgba(0, 122, 255, 0.3);
      }
    }
  }
}

/* 评价列表 */
.review-list {
  padding: 0 30rpx;
  
  .review-item {
    background: #fff;
    border-radius: 24rpx;
    padding: 30rpx;
    margin-bottom: 20rpx;
    box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.04);
    
    .user-info {
      display: flex;
      align-items: center;
      margin-bottom: 20rpx;
      
      .avatar {
        width: 80rpx;
        height: 80rpx;
        border-radius: 50%;
        margin-right: 20rpx;
        background: #eee;
      }
      
      .user-meta {
        .nickname {
          font-size: 28rpx;
          font-weight: bold;
          color: #333;
        }
        .rating-row {
          display: flex;
          align-items: center;
          margin-top: 4rpx;
          
          .stars {
            color: #ffd700;
            font-size: 24rpx;
            margin-right: 15rpx;
          }
          .date {
            font-size: 22rpx;
            color: #999;
          }
        }
      }
    }
    
    .content {
      font-size: 28rpx;
      color: #444;
      line-height: 1.6;
      margin-bottom: 20rpx;
    }
    
    .ai-analysis-box {
      background: #f8f9fc;
      border-radius: 12rpx;
      padding: 20rpx;
      border-left: 6rpx solid #007aff;
      
      .ai-label {
        font-size: 22rpx;
        color: #007aff;
        font-weight: bold;
        margin-bottom: 15rpx;
      }
      
      .dimension-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 15rpx;
        
        .dim-item {
          display: flex;
          align-items: center;
          font-size: 22rpx;
          padding: 6rpx 12rpx;
          border-radius: 8rpx;
          
          .dim-name {
            margin-right: 10rpx;
            font-weight: bold;
          }
          
          &.positive {
            background: #e8fce8;
            color: #27a643;
            .dim-val { color: #27a643; }
          }
          &.negative {
            background: #ffecec;
            color: #d93025;
            .dim-val { color: #d93025; }
          }
          &.neutral {
            background: #f0f0f0;
            color: #666;
          }
        }
      }
    }
  }
}

/* 底部评论输入框 */
.comment-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background: #fff;
  box-shadow: 0 -4rpx 12rpx rgba(0,0,0,0.08);
  display: flex;
  align-items: flex-end;
  gap: 12rpx;
  z-index: 100;
}

.star-selector {
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.star {
  font-size: 32rpx;
  color: #e0e0e0;
  line-height: 1;
  margin: 2rpx 0;
}
.star.filled {
  color: #ffb400;
}

.comment-input {
  flex: 1;
  min-height: 80rpx;
  max-height: 200rpx;
  padding: 12rpx;
  border: 1px solid #eee;
  border-radius: 12rpx;
  font-size: 28rpx;
  background: #fafafa;
  line-height: 1.5;
}

.send-btn {
  background: linear-gradient(135deg, #2b32b2 0%, #1488cc 100%);
  color: #fff;
  padding: 0 30rpx;
  height: 80rpx;
  line-height: 80rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  box-shadow: 0 4rpx 12rpx rgba(20, 136, 204, 0.3);
  border: none;
}
.send-btn:disabled {
  opacity: 0.5;
  background: #ccc;
}
</style>
