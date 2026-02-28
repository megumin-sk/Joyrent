<template>
  <view class="ai-fab-container">
    <!-- 可拖拽的悬浮球 -->
    <movable-area class="movable-area" v-if="!isChatOpen">
      <movable-view
        class="movable-view"
        :x="x"
        :y="y"
        direction="all"
        :inertia="true"
        @click="toggleChat"
      >
        <view class="fab-outer">
          <view class="fab-glow"></view>
          <view class="fab-circle">
            <text class="fab-icon">🎮</text>
          </view>
          <view class="fab-ring"></view>
          <view class="fab-ring ring-2"></view>
        </view>
        <!-- 未读消息指示 -->
        <view v-if="hasUnread" class="fab-badge">
          <text class="badge-num">1</text>
        </view>
      </movable-view>
    </movable-area>

    <!-- 聊天弹窗 -->
    <uni-popup ref="chatPopup" type="bottom" background-color="transparent" @change="onPopupChange">
      <view class="chat-window">
        <!-- 装饰背景 -->
        <view class="chat-bg">
          <view class="grid-pattern"></view>
          <view class="gradient-orb orb-1"></view>
          <view class="gradient-orb orb-2"></view>
        </view>
        
        <!-- 标题栏 -->
        <view class="chat-header">
          <view class="header-left">
            <view class="bot-avatar">
              <text class="bot-icon">🎮</text>
              <view class="status-dot"></view>
            </view>
            <view class="header-info">
              <text class="title">JoyRent 智能助手</text>
              <text class="subtitle">{{ statusText }}</text>
            </view>
          </view>
          <view class="header-actions">
            <view class="action-btn" @click="clearChat" title="清空对话">
              <text class="btn-icon">🗑️</text>
            </view>
            <view class="action-btn close-btn" @click="closeChat">
              <text class="btn-icon">✕</text>
            </view>
          </view>
        </view>

        <!-- 快捷问题区 -->
        <view class="quick-actions" v-if="messages.length <= 1">
          <text class="quick-title">✨ 猜你想问</text>
          <view class="quick-tags">
            <view 
              v-for="(item, idx) in quickQuestions" 
              :key="idx"
              class="quick-tag"
              @click="sendQuickQuestion(item.text)"
              :style="{ animationDelay: idx * 0.08 + 's' }"
            >
              <text class="tag-icon">{{ item.icon }}</text>
              <text class="tag-text">{{ item.text }}</text>
            </view>
          </view>
        </view>

        <!-- 消息列表 -->
        <scroll-view class="msg-list" scroll-y :scroll-top="scrollTop" :scroll-with-animation="true">
          <view 
            v-for="(msg, index) in messages" 
            :key="index" 
            :class="['msg-row', msg.role === 'user' ? 'msg-right' : 'msg-left']"
          >
            <!-- AI 头像 -->
            <view v-if="msg.role === 'assistant'" class="avatar ai-avatar">
              <text class="avatar-icon">🎮</text>
            </view>
            
            <!-- 消息气泡 -->
            <view :class="['bubble', msg.role === 'user' ? 'user-bubble' : 'ai-bubble']">
              <text :user-select="true" class="msg-text">{{ msg.content }}</text>
              <!-- 意图标签(仅 AI 回复 且有标签时展示) -->
              <view v-if="msg.intentTag" class="intent-badge">
                <text class="intent-icon">{{ msg.intentIcon }}</text>
                <text class="intent-label">{{ msg.intentTag }}</text>
              </view>
            </view>
            
            <!-- 用户头像 -->
            <view v-if="msg.role === 'user'" class="avatar user-avatar">
              <text class="avatar-icon">我</text>
            </view>
          </view>
          
          <!-- 加载状态 -->
          <view v-if="loading" class="msg-row msg-left loading-row">
            <view class="avatar ai-avatar">
              <text class="avatar-icon">🎮</text>
            </view>
            <view class="bubble ai-bubble typing-bubble">
              <view class="typing-indicator">
                <view class="typing-dot"></view>
                <view class="typing-dot"></view>
                <view class="typing-dot"></view>
              </view>
              <text class="typing-hint">思考中...</text>
            </view>
          </view>
          
          <!-- 底部留白 -->
          <view style="height: 24px;"></view>
        </scroll-view>

        <!-- 输入框 -->
        <view class="input-area">
          <view class="input-wrapper" :class="{ 'input-focus': isInputFocused }">
            <input 
              class="input-box" 
              v-model="inputContent" 
              placeholder="输入问题，如：押金怎么退？" 
              confirm-type="send"
              @confirm="sendMessage"
              @focus="isInputFocused = true"
              @blur="isInputFocused = false"
              :disabled="loading"
            />
            <view 
              class="send-btn" 
              :class="{ 'send-active': inputContent.trim() && !loading }"
              @click="sendMessage"
            >
              <text class="send-icon">➤</text>
            </view>
          </view>
          <text class="input-hint">AI 回答仅供参考 · Powered by JoyRent Agent</text>
        </view>
      </view>
    </uni-popup>
  </view>
</template>

<script>
import { askAgent } from '@/api/rag.js';
import { mapGetters } from 'vuex';

// 意图 → 展示映射
const INTENT_MAP = {
  game:    { icon: '🎮', label: '游戏查询' },
  rule:    { icon: '📋', label: '规则解答' },
  order:   { icon: '📦', label: '订单服务' },
  clarify: { icon: '💡', label: '引导澄清' },
};

export default {
  computed: {
    ...mapGetters(['userInfo']),
    statusText() {
      if (this.loading) return '正在思考...';
      return '在线 · 可回答租赁问题';
    }
  },
  data() {
    return {
      x: 300,
      y: 500,
      inputContent: '',
      loading: false,
      isChatOpen: false,
      isInputFocused: false,
      hasUnread: false,
      scrollTop: 0,
      messages: [
        {
          role: 'assistant',
          content: '嗨！我是 JoyRent 智能助手 🎮\n\n我可以帮你：\n• 查询游戏库存和价格\n• 说明租赁 / 归还规则\n• 查看押金退款流程\n• 管理你的租赁订单\n\n直接问我任何问题吧！'
        }
      ],
      quickQuestions: [
        { icon: '🔍', text: '塞尔达今天有货吗？' },
        { icon: '💰', text: '押金多久能退回？' },
        { icon: '⏰', text: '超期一天怎么计费？' },
        { icon: '📦', text: '我的订单到哪了？' },
      ]
    };
  },
  methods: {
    toggleChat() {
      this.hasUnread = false;
      this.$refs.chatPopup.open();
    },
    onPopupChange(e) {
      this.isChatOpen = e.show;
    },
    closeChat() {
      this.$refs.chatPopup.close();
    },
    clearChat() {
      uni.showModal({
        title: '清空对话',
        content: '确定要清空所有对话记录吗？',
        confirmColor: '#FF3D00',
        success: (res) => {
          if (res.confirm) {
            this.messages = [
              {
                role: 'assistant',
                content: '嗨！我是 JoyRent 智能助手 🎮\n\n我可以帮你：\n• 查询游戏库存和价格\n• 说明租赁 / 归还规则\n• 查看押金退款流程\n• 管理你的租赁订单\n\n直接问我任何问题吧！'
              }
            ];
          }
        }
      });
    },
    sendQuickQuestion(question) {
      this.inputContent = question;
      this.sendMessage();
    },
    async sendMessage() {
      const query = this.inputContent.trim();
      if (!query || this.loading) return;

      // 用户消息入列
      this.messages.push({ role: 'user', content: query });
      this.inputContent = '';
      this.loading = true;
      this.scrollToBottom();

      try {
        const userId = this.userInfo ? this.userInfo.id : null;
        const data = await askAgent(query, userId);

        if (data && data.answer) {
          // 解析意图标签
          const intentInfo = INTENT_MAP[data.intent] || null;

          this.messages.push({
            role: 'assistant',
            content: data.answer,
            intentTag: intentInfo ? intentInfo.label : null,
            intentIcon: intentInfo ? intentInfo.icon : null,
          });
        } else {
          this.messages.push({
            role: 'assistant',
            content: '抱歉，我暂时没获取到结果，请稍后再试。'
          });
        }
      } catch (e) {
        console.error('[AiFab] sendMessage error:', e);
        this.messages.push({
          role: 'assistant',
          content: '当前网络异常或服务暂不可用，请稍后重试。'
        });
      } finally {
        this.loading = false;
        this.scrollToBottom();
      }
    },
    scrollToBottom() {
      this.$nextTick(() => {
        this.scrollTop = this.scrollTop === 99999 ? 99998 : 99999;
      });
    }
  },
  mounted() {
    const sys = uni.getSystemInfoSync();
    this.x = sys.windowWidth - 80;
    this.y = sys.windowHeight - 200;
  }
};
</script>

<style lang="scss" scoped>
// ========================================
// 设计令牌 — JoyRent 赛博霓虹
// ========================================
$neon-purple: #5d5fef;
$neon-cyan: #1cc8ff;
$accent-orange: #FF3D00;
$dark-bg: #0B1120;
$darker-bg: #060a14;
$card-bg: rgba(11, 17, 32, 0.96);
$glass-bg: rgba(255, 255, 255, 0.04);
$text-primary: #F8FAFC;
$text-secondary: rgba(248, 250, 252, 0.72);
$text-muted: rgba(248, 250, 252, 0.48);
$border-subtle: rgba(255, 255, 255, 0.08);

// 动效曲线
$ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
$ease-smooth: cubic-bezier(0.22, 0.78, 0.26, 1);

// ========================================
// 悬浮球
// ========================================
.movable-area {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 999;
}

.movable-view {
  width: 72px;
  height: 72px;
  pointer-events: auto;
}

.fab-outer {
  position: relative;
  width: 64px;
  height: 64px;
}

.fab-glow {
  position: absolute;
  inset: -6px;
  background: radial-gradient(circle, rgba($neon-cyan, 0.4) 0%, transparent 72%);
  border-radius: 50%;
  animation: glow-pulse 2.4s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% { opacity: 0.48; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.12); }
}

.fab-circle {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, $neon-purple 0%, $neon-cyan 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 2;
  box-shadow:
    0 0 24px rgba($neon-cyan, 0.48),
    0 0 48px rgba($neon-purple, 0.24),
    inset 0 0 24px rgba(255, 255, 255, 0.16);
  animation: float 3.2s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.fab-icon {
  font-size: 28px;
}

.fab-ring {
  position: absolute;
  inset: -8px;
  border: 2px solid rgba($neon-cyan, 0.48);
  border-radius: 50%;
  animation: ring-expand 2.4s ease-out infinite;
}

.ring-2 { animation-delay: 1.2s; }

@keyframes ring-expand {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(1.32); opacity: 0; }
}

// 未读红点
.fab-badge {
  position: absolute;
  top: 0;
  right: 0;
  width: 20px;
  height: 20px;
  background: $accent-orange;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  box-shadow: 0 2px 8px rgba($accent-orange, 0.6);
  animation: badge-bounce 0.4s $ease-bounce;

  .badge-num {
    font-size: 11px;
    color: $text-primary;
    font-weight: 800;
  }
}

@keyframes badge-bounce {
  from { transform: scale(0); }
  to { transform: scale(1); }
}

// ========================================
// 聊天窗口
// ========================================
.chat-window {
  height: 80vh;
  display: flex;
  flex-direction: column;
  background: $card-bg;
  border-top-left-radius: 24px;
  border-top-right-radius: 24px;
  border: 1px solid $border-subtle;
  overflow: hidden;
  position: relative;
  backdrop-filter: blur(16px);
}

.chat-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.grid-pattern {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba($neon-cyan, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba($neon-cyan, 0.02) 1px, transparent 1px);
  background-size: 48px 48px;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.16;
}
.orb-1 {
  width: 280px; height: 280px;
  background: radial-gradient(circle, $neon-purple 0%, transparent 72%);
  top: -96px; right: -96px;
}
.orb-2 {
  width: 240px; height: 240px;
  background: radial-gradient(circle, $neon-cyan 0%, transparent 72%);
  bottom: 96px; left: -80px;
}

// ========================================
// 标题栏
// ========================================
.chat-header {
  padding: 16px;
  background: rgba(6, 10, 20, 0.88);
  border-bottom: 1px solid $border-subtle;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  backdrop-filter: blur(12px);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bot-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, $neon-purple 0%, $neon-cyan 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: 0 0 16px rgba($neon-cyan, 0.32);
}

.bot-icon { font-size: 22px; }

.status-dot {
  position: absolute;
  bottom: 1px; right: 1px;
  width: 10px; height: 10px;
  background: #00ff88;
  border-radius: 50%;
  border: 2px solid $darker-bg;
  animation: status-blink 2s ease-in-out infinite;
}

@keyframes status-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.header-info {
  display: flex;
  flex-direction: column;
}

.title {
  font-size: 15px;
  font-weight: 700;
  color: $text-primary;
  letter-spacing: -0.02em;
}

.subtitle {
  font-size: 11px;
  color: $text-muted;
  margin-top: 2px;
  transition: color 0.3s $ease-smooth;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  background: $glass-bg;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid $border-subtle;
  transition: all 0.2s $ease-bounce;
}

.action-btn:active {
  transform: scale(0.92);
  background: rgba($neon-cyan, 0.12);
}

.btn-icon {
  font-size: 14px;
  color: $text-secondary;
}

// ========================================
// 快捷问题区
// ========================================
.quick-actions {
  padding: 16px;
  border-bottom: 1px solid $border-subtle;
  flex-shrink: 0;
}

.quick-title {
  font-size: 13px;
  color: $text-muted;
  margin-bottom: 12px;
  display: block;
  font-weight: 600;
}

.quick-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-tag {
  background: rgba($neon-cyan, 0.06);
  border: 1px solid rgba($neon-cyan, 0.2);
  padding: 8px 14px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 6px;
  animation: tag-fade-in 0.4s $ease-smooth backwards;
  transition: all 0.2s $ease-bounce;
}

.quick-tag:active {
  transform: scale(0.95);
  background: rgba($neon-cyan, 0.16);
  border-color: rgba($neon-cyan, 0.4);
}

.tag-icon { font-size: 14px; }

.tag-text {
  font-size: 13px;
  color: rgba(230, 246, 255, 0.88);
  font-weight: 500;
}

@keyframes tag-fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

// ========================================
// 消息列表
// ========================================
.msg-list {
  flex: 1;
  padding: 16px;
  overflow-y: scroll;
  -webkit-overflow-scrolling: touch;
  box-sizing: border-box;
}

.msg-row {
  display: flex;
  width: 100%;
  margin-bottom: 16px;
  align-items: flex-end;
  gap: 8px;
  animation: msg-slide-in 0.32s $ease-smooth;
}

@keyframes msg-slide-in {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.msg-left { justify-content: flex-start; }
.msg-right { justify-content: flex-end; }

// 头像
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ai-avatar {
  background: linear-gradient(135deg, $neon-purple 0%, $neon-cyan 100%);
  box-shadow: 0 0 12px rgba($neon-cyan, 0.32);
}

.user-avatar {
  background: rgba($neon-cyan, 0.16);
  border: 1px solid rgba($neon-cyan, 0.4);
}

.avatar-icon {
  font-size: 13px;
  color: $text-primary;
  font-weight: 700;
}

// 气泡
.bubble {
  max-width: calc(100% - 56px);
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  position: relative;
  word-break: break-word;
  box-sizing: border-box;
}

.ai-bubble {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: $text-primary;
  border-bottom-left-radius: 4px;
  box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.1), 0 0 0 1px rgba(255, 255, 255, 0.03);
}

.user-bubble {
  background: linear-gradient(135deg, rgba($neon-cyan, 0.2) 0%, rgba($neon-purple, 0.16) 100%);
  border: 1px solid rgba($neon-cyan, 0.32);
  color: $text-primary;
  border-bottom-right-radius: 4px;
  box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.1);
}

.msg-text {
  white-space: pre-wrap;
  color: rgba(248, 250, 252, 0.88);
}

// 意图标签
.intent-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  padding: 3px 10px;
  background: rgba($neon-cyan, 0.08);
  border: 1px solid rgba($neon-cyan, 0.16);
  border-radius: 12px;
}

.intent-icon { font-size: 11px; }

.intent-label {
  font-size: 11px;
  color: $text-muted;
  font-weight: 600;
  letter-spacing: 0.02em;
}

// 打字动画
.loading-row { opacity: 0.88; }

.typing-bubble {
  padding: 14px 18px;
  min-width: 88px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.typing-indicator {
  display: flex;
  gap: 5px;
  align-items: center;
}

.typing-dot {
  width: 7px;
  height: 7px;
  background: $neon-cyan;
  border-radius: 50%;
  animation: typing-bounce 1.4s ease-in-out infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.16s; }
.typing-dot:nth-child(3) { animation-delay: 0.32s; }

@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-8px); opacity: 1; }
}

.typing-hint {
  font-size: 12px;
  color: $text-muted;
  font-weight: 500;
}

// ========================================
// 输入区域
// ========================================
.input-area {
  padding: 12px 16px 4px;
  background: rgba(6, 10, 20, 0.92);
  border-top: 1px solid $border-subtle;
  flex-shrink: 0;
  backdrop-filter: blur(12px);
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 4px 4px 4px 16px;
  transition: all 0.28s $ease-smooth;
}

.input-focus {
  border-color: rgba($neon-cyan, 0.48) !important;
  box-shadow: 0 0 24px rgba($neon-cyan, 0.08);
  background: rgba(255, 255, 255, 0.06);
}

.input-box {
  flex: 1;
  height: 40px;
  font-size: 14px;
  color: $text-primary;
  background: transparent;
}

.send-btn {
  width: 36px;
  height: 36px;
  background: rgba($neon-cyan, 0.08);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.24s $ease-bounce;
}

.send-active {
  background: linear-gradient(135deg, $neon-purple 0%, $neon-cyan 100%);
  box-shadow: 0 0 16px rgba($neon-cyan, 0.4);
  transform: scale(1.04);
}

.send-active:active {
  transform: scale(0.92);
}

.send-icon {
  font-size: 13px;
  color: $text-muted;
  transform: rotate(-45deg) translateY(1px);
}

.send-active .send-icon {
  color: $text-primary;
}

.input-hint {
  font-size: 10px;
  color: rgba(248, 250, 252, 0.28);
  text-align: center;
  margin-top: 4px;
  display: block;
  letter-spacing: 0.04em;
}
</style>
