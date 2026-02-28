<template>
  <div class="dashboard">
    <section class="hero">
      <div class="hero-copy">
        <p class="hero-kicker">今日概览</p>
        <h1 class="hero-title">JoyRent 运营控制台</h1>
        <p class="hero-subtitle">从收入到履约，全局把控租赁节奏与风险信号。</p>
        <div class="hero-actions">
          <button class="btn btn-primary">新建订单</button>
          <button class="btn btn-ghost">查看实时物流</button>
        </div>
      </div>
      <div class="hero-panel">
        <div class="hero-panel-header">
          <span>更新于 {{ todayLabel }}</span>
          <span class="hero-panel-tag">最近 24 小时</span>
        </div>
        <div class="hero-stats">
          <div class="hero-stat">
            <span>今日收入</span>
            <strong>{{ metricState.todayMoney }}</strong>
          </div>
          <div class="hero-stat">
            <span>今日订单</span>
            <strong>{{ metricState.todayOrders }}</strong>
          </div>
          <div class="hero-stat">
            <span>租赁中</span>
            <strong>{{ metricState.inRent }}</strong>
          </div>
          <div class="hero-stat">
            <span>总用户</span>
            <strong>{{ metricState.totalUsers }}</strong>
          </div>
        </div>
      </div>
    </section>

    <div class="dashboard-tabs" role="tablist" aria-label="首页模块切换">
      <button
        v-for="tab in dashboardTabs"
        :key="tab.key"
        class="dashboard-tab"
        :class="{ active: activeTab === tab.key }"
        type="button"
        @click="activeTab = tab.key"
      >
        <span>{{ tab.icon }}</span>
        {{ tab.label }}
      </button>
    </div>

    <section v-show="activeTab === 'overview'" class="tab-panel">
      <div class="section-head">
        <h2>关键指标</h2>
        <p>核心运营指标随时掌控</p>
      </div>
      <div class="metrics-grid">
        <div class="metric-card" v-for="metric in metrics" :key="metric.label">
          <div class="metric-icon">{{ metric.icon }}</div>
          <div class="metric-content">
            <div class="metric-label">{{ metric.label }}</div>
            <div class="metric-value">{{ metric.value }}</div>
          </div>
        </div>
      </div>

      <div class="charts-section">
        <div class="chart-card">
          <div class="card-title">
            <span>收入趋势</span>
            <em>最近 7 天</em>
          </div>
          <div class="chart-container">
            <div class="line-chart">
              <svg class="line-chart-svg" viewBox="0 0 100 40" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="lineFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="var(--color-accent)" stop-opacity="0.35" />
                    <stop offset="100%" stop-color="var(--color-accent)" stop-opacity="0" />
                  </linearGradient>
                </defs>
                <polygon
                  v-if="areaPoints"
                  :points="areaPoints"
                  fill="url(#lineFill)"
                  opacity="0.6"
                />
                <polyline
                  v-if="linePoints"
                  :points="linePoints"
                  fill="none"
                  stroke="var(--color-accent)"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <g v-for="(point, idx) in lineChartPoints" :key="'point-'+idx">
                  <circle
                    :cx="point.x"
                    :cy="point.y"
                    r="1.3"
                    fill="#fff"
                    stroke="var(--color-accent)"
                    stroke-width="0.5"
                  />
                  <text
                    :x="point.x"
                    :y="point.y - 1.5"
                    text-anchor="middle"
                    class="line-chart-label"
                  >
                    ¥{{ point.value }}
                  </text>
                </g>
              </svg>
              <div class="line-chart-dates">
                <span v-for="(item, index) in revenueData" :key="'date-'+index">
                  {{ item.date }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <h3 class="card-title">订单状态分布</h3>
          <div class="status-stats">
            <div
              v-for="status in orderStatus"
              :key="status.label"
              class="status-item"
            >
              <div class="status-bar-wrapper">
                <div class="status-info">
                  <span class="status-label">{{ status.label }}</span>
                  <span class="status-count">{{ status.count }}</span>
                </div>
                <div class="status-bar">
                  <div
                    class="status-bar-fill"
                    :style="{ width: (status.count / totalOrders * 100) + '%', backgroundColor: status.color }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section v-show="activeTab === 'ops'" class="tab-panel">
      <div class="section-head">
        <h2>履约与风险</h2>
        <p>关注待处理事项与订单状态</p>
      </div>

      <div class="info-section single-col">
        <div class="info-card">
          <h3 class="card-title">待处理事项</h3>
          <div class="todo-list">
            <div
              v-for="todo in todoList"
              :key="todo.label"
              class="todo-item"
              :class="todo.urgent ? 'urgent' : ''"
            >
              <span class="todo-label">{{ todo.label }}</span>
              <span class="todo-count">{{ todo.count }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="recent-orders-card">
        <h3 class="card-title">最近订单</h3>
        <table class="orders-table">
          <thead>
            <tr>
              <th>订单号</th>
              <th>用户</th>
              <th>游戏</th>
              <th>金额</th>
              <th>状态</th>
              <th>时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in recentOrders" :key="order.id">
              <td>{{ order.id }}</td>
              <td>{{ order.user }}</td>
              <td>{{ order.game }}</td>
              <td class="amount">¥{{ order.amount }}</td>
              <td>
                <span class="status-badge" :class="'status-' + order.statusClass">
                  {{ order.status }}
                </span>
              </td>
              <td class="time">{{ order.time }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-show="activeTab === 'games'" class="tab-panel">
      <div class="section-head">
        <h2>热门游戏</h2>
        <p>租赁热度排行与游戏表现</p>
      </div>

      <div class="info-section single-col">
        <div class="info-card">
          <h3 class="card-title">热门游戏 TOP5</h3>
          <div class="game-list">
            <div
              v-for="(game, index) in topGames"
              :key="game.id"
              class="game-item"
            >
              <span class="game-rank">{{ index + 1 }}</span>
              <img :src="game.cover" alt="" class="game-cover">
              <div class="game-info">
                <div class="game-title">{{ game.title }}</div>
                <div class="game-count">租赁 {{ game.rentCount }} 次</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { queryDailyTurnover, queryTodayMoney, queryTodayOrders } from '@/api/order.js';
import { queryUserCount } from '@/api/auth.js';

const METRIC_CONFIG = [
  { key: 'todayOrders', icon: '📝', label: '今日订单', fallback: '--' },
  { key: 'todayMoney', icon: '💰', label: '今日收入', fallback: '--' },
  { key: 'inRent', icon: '🎮', label: '租赁中', fallback: 0 },
  { key: 'totalUsers', icon: '👥', label: '总用户', fallback: '--' }
];

export default {
  name: 'Dashboard',
  data() {
    return {
      activeTab: 'overview',
      dashboardTabs: [
        { key: 'overview', label: '总览', icon: '📊' },
        { key: 'ops', label: '履约', icon: '⚠️' },
        { key: 'games', label: '游戏', icon: '🎮' }
      ],
      metricState: {
        todayOrders: '--',
        todayMoney: '--',
        inRent: 45,
        totalUsers: '--'
      },
      revenueData: [
        { date: '11-13', value: 320 },
        { date: '11-14', value: 280 },
        { date: '11-15', value: 450 },
        { date: '11-16', value: 380 },
        { date: '11-17', value: 520 },
        { date: '11-18', value: 410 },
        { date: '11-19', value: 356 }
      ],
      orderStatus: [
        { label: '待支付', count: 8, color: '#f59e0b' },
        { label: '待发货', count: 5, color: '#8b5cf6' },
        { label: '租赁中', count: 45, color: '#10b981' },
        { label: '归还中', count: 3, color: '#3b82f6' },
        { label: '已完成', count: 123, color: '#6b7280' }
      ],
      todoList: [
        { label: '待发货订单', count: 5, urgent: true },
        { label: '即将逾期', count: 3, urgent: true },
        { label: '库存告警', count: 2, urgent: true },
        { label: '待退押金', count: 8, urgent: false }
      ],
      topGames: [
        {
          id: 1,
          title: '塞尔达传说：王国之泪',
          cover: 'https://assets.nintendo.com/image/upload/ar_16:9,c_lpad,w_120/b_white/f_auto/q_auto/ncom/software/switch/70010000063714/14f6e677ac29e9e3e9697a7ac2f96469e31d2751178764c6c0418b8d87e6516a',
          rentCount: 89
        },
        {
          id: 2,
          title: '马里奥赛车8 豪华版',
          cover: 'https://assets.nintendo.com/image/upload/ar_16:9,c_lpad,w_120/b_white/f_auto/q_auto/ncom/software/switch/70010000000141/5b45d70a71b0b9a14a9f283ac7374e195e41027b68446a10028e3966d1575027',
          rentCount: 76
        },
        {
          id: 3,
          title: '超级马力欧兄弟 惊奇',
          cover: 'https://assets.nintendo.com/image/upload/ar_16:9,c_lpad,w_120/b_white/f_auto/q_auto/ncom/software/switch/70010000068683/5b2ac7f73506d82d0a2789e16239ef48050663612680310a306298da44043723',
          rentCount: 64
        },
        {
          id: 4,
          title: '斯普拉遁3',
          cover: 'https://via.placeholder.com/120x68?text=Splatoon+3',
          rentCount: 58
        },
        {
          id: 5,
          title: '宝可梦 朱/紫',
          cover: 'https://via.placeholder.com/120x68?text=Pokemon',
          rentCount: 52
        }
      ],
      recentOrders: [
        { id: 'ORD20251119001', user: '张三', game: '塞尔达传说', amount: 335.00, status: '租赁中', statusClass: 'active', time: '2小时前' },
        { id: 'ORD20251119002', user: '李四', game: '马里奥赛车8', amount: 215.00, status: '待发货', statusClass: 'pending', time: '3小时前' },
        { id: 'ORD20251118003', user: '王五', game: '超级马力欧', amount: 280.00, status: '已完成', statusClass: 'completed', time: '1天前' }
      ]
    };
  },
  computed: {
    todayLabel() {
      const now = new Date();
      return now.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'short'
      });
    },
    metrics() {
      return METRIC_CONFIG.map(item => ({
        icon: item.icon,
        label: item.label,
        value: this.metricState[item.key] ?? item.fallback
      }));
    },
    maxRevenue() {
      return Math.max(...this.revenueData.map(d => d.value));
    },
    lineChartPoints() {
      if (!this.revenueData.length) return [];
      const max = this.maxRevenue || 1;
      const chartHeight = 30;
      const baseY = 35;
      const stepX = this.revenueData.length > 1 ? 100 / (this.revenueData.length - 1) : 0;
      return this.revenueData.map((item, index) => {
        const ratio = item.value / max;
        const y = baseY - ratio * chartHeight;
        const x = stepX * index;
        return { x: Number(x.toFixed(2)), y: Number(y.toFixed(2)), value: item.value };
      });
    },
    linePoints() {
      if (!this.lineChartPoints.length) return '';
      return this.lineChartPoints.map(point => `${point.x},${point.y}`).join(' ');
    },
    areaPoints() {
      if (!this.lineChartPoints.length) return '';
      const start = `0,35`;
      const mid = this.lineChartPoints.map(point => `${point.x},${point.y}`).join(' ');
      const end = `100,35`;
      return `${start} ${mid} ${end}`;
    },
    totalOrders() {
      return this.orderStatus.reduce((sum, s) => sum + s.count, 0);
    }
  },
  mounted() {
    // 可以在这里调用API获取真实数据
    this.fetchDashboardData();
  },
  methods: {
    async fetchDashboardData() {
      try {
        const [turnoverResp, todayMoneyResp, todayOrdersResp, userCountResp] = await Promise.all([
          queryDailyTurnover(),
          queryTodayMoney(),
          queryTodayOrders(),
          queryUserCount()
        ]);
        this.updateRevenueData(turnoverResp);
        this.updateTodayMoneyMetric(todayMoneyResp);
        this.updateTodayOrders(todayOrdersResp);
        this.updateTotalUsersMetric(userCountResp);
      } catch (error) {
        console.error('Failed to fetch dashboard data', error);
      }
    },
    updateRevenueData(response) {
      const payload = this.unwrapResponseData(response);
      if (!payload || typeof payload !== 'object') return;
      const entries = Object.entries(payload);
      const fullDatePattern = /^\d{4}-\d{2}-\d{2}$/;
      const sorted = entries.sort(([a], [b]) => {
        const aIsFull = fullDatePattern.test(a);
        const bIsFull = fullDatePattern.test(b);
        if (aIsFull && bIsFull) {
          return new Date(a).getTime() - new Date(b).getTime();
        }
        return a.localeCompare(b);
      });
      this.revenueData = sorted.map(([date, value]) => ({
        date: fullDatePattern.test(date) ? date.slice(5) : date,
        value: Number(value) || 0
      }));
    },
    updateTodayMoneyMetric(response) {
      const todayMoney = Number(this.unwrapResponseData(response));
      if (!Number.isFinite(todayMoney)) return;
      this.metricState.todayMoney = this.formatCurrency(todayMoney);
    },
    updateTodayOrders(response) {
      const payload = this.unwrapResponseData(response);
      const orders = Array.isArray(payload) ? payload : [];
      this.metricState.todayOrders = orders.length;
      if (!orders.length) {
        this.recentOrders = [];
        return;
      }
      this.recentOrders = orders.slice(0, 6).map(order => this.mapOrderToRow(order));
    },
    updateTotalUsersMetric(response) {
      const totalUsers = Number(this.unwrapResponseData(response));
      if (!Number.isFinite(totalUsers)) return;
      this.metricState.totalUsers = totalUsers.toLocaleString();
    },
    mapOrderToRow(order) {
      const statusInfo = this.formatOrderStatus(order?.status);
      return {
        id: order?.id ?? '--',
        user: order?.userId ? `用户#${order.userId}` : '--',
        game: order?.gameTitle || '—',
        amount: this.formatAmountValue(order?.payAmount ?? order?.totalRentFee ?? 0),
        status: statusInfo.text,
        statusClass: statusInfo.className,
        time: this.formatOrderTime(order?.createdAt)
      };
    },
    formatOrderStatus(status) {
      const mapping = {
        10: { text: '待支付', className: 'pending' },
        20: { text: '待发货', className: 'pending' },
        30: { text: '租赁中', className: 'active' },
        40: { text: '归还中', className: 'active' },
        50: { text: '已完成', className: 'completed' },
        60: { text: '已取消', className: 'completed' }
      };
      return mapping[status] || { text: '未知', className: 'pending' };
    },
    formatOrderTime(dateValue) {
      if (!dateValue) return '--';
      const date = new Date(dateValue);
      if (Number.isNaN(date.getTime())) return '--';
      return date.toLocaleString('zh-CN', { hour12: false });
    },
    formatAmountValue(amount) {
      const num = Number(amount);
      if (!Number.isFinite(num)) return '0.00';
      return num.toFixed(2);
    },
    formatCurrency(amount) {
      return `¥${amount.toFixed(2)}`;
    },
    unwrapResponseData(response) {
      let payload = response;
      if (payload && typeof payload === 'object' && 'data' in payload) {
        payload = payload.data;
      }
      let depth = 0;
      while (payload && typeof payload === 'object' && 'data' in payload && depth < 3) {
        payload = payload.data;
        depth += 1;
      }
      return payload;
    }
  }
};
</script>

<style scoped>
.dashboard {
  color: var(--color-text-primary);
  position: relative;
}

.dashboard::before {
  content: '';
  position: absolute;
  inset: -40px;
  background:
    radial-gradient(circle at 10% 20%, rgba(139, 92, 246, 0.22), transparent 42%),
    radial-gradient(circle at 90% 10%, rgba(59, 130, 246, 0.16), transparent 38%);
  z-index: 0;
  pointer-events: none;
}

.dashboard::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(148, 163, 184, 0.12) 0.5px, transparent 0.5px);
  background-size: 6px 6px;
  opacity: 0.35;
  pointer-events: none;
  z-index: 0;
}

.dashboard > * {
  position: relative;
  z-index: 1;
}

/* Hero */
.hero {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 2rem;
  margin-bottom: 2.5rem;
  align-items: stretch;
}

.dashboard-tabs {
  display: inline-flex;
  gap: 0.5rem;
  background: rgba(30, 41, 59, 0.72);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0.35rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 10px 24px rgba(2, 6, 23, 0.48);
}

.dashboard-tab {
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  border-radius: 10px;
  padding: 0.5rem 0.9rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  transition: all 0.2s ease;
}

.dashboard-tab:hover {
  color: var(--color-text-primary);
  background: rgba(148, 163, 184, 0.14);
}

.dashboard-tab.active {
  color: #fff;
  background: var(--color-accent);
  box-shadow: 0 8px 20px var(--color-accent-glow);
}

.tab-panel {
  animation: fadeInUp 0.35s ease;
}

.hero-copy {
  padding: 2rem;
  background: linear-gradient(140deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.82));
  border: 1px solid var(--border-color);
  border-radius: 24px;
  box-shadow: 0 20px 42px rgba(2, 6, 23, 0.55);
}

.hero-kicker {
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-size: 0.7rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.75rem;
}

.hero-title {
  font-family: var(--font-display);
  font-size: 2.4rem;
  margin-bottom: 0.75rem;
  color: var(--color-text-primary);
}

.hero-subtitle {
  font-size: 1rem;
  color: var(--color-text-secondary);
  max-width: 420px;
  margin-bottom: 1.5rem;
}

.hero-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-ghost {
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--color-text-secondary);
  padding: 0.7rem 1.4rem;
  border-radius: var(--radius-md);
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-ghost:hover {
  border-color: var(--color-accent);
  color: var(--color-text-primary);
}

.hero-panel {
  padding: 2rem;
  border-radius: 24px;
  background: linear-gradient(160deg, rgba(139, 92, 246, 0.24), rgba(30, 41, 59, 0.88));
  border: 1px solid rgba(139, 92, 246, 0.35);
  box-shadow: 0 18px 36px rgba(30, 27, 75, 0.45);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.hero-panel-header {
  display: flex;
  justify-content: space-between;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.hero-panel-tag {
  background-color: rgba(139, 92, 246, 0.26);
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.25rem;
}

.hero-stat {
  background-color: rgba(15, 23, 42, 0.55);
  border-radius: 16px;
  padding: 1rem 1.2rem;
  border: 1px solid rgba(148, 163, 184, 0.24);
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.hero-stat span {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.hero-stat strong {
  font-size: 1.5rem;
  font-family: var(--font-display);
  color: var(--color-text-primary);
}

/* Section Head */
.section-head {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.section-head h2 {
  font-family: var(--font-display);
  font-size: 1.6rem;
  color: var(--color-text-primary);
}

.section-head p {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

/* 指标卡片 */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.94), rgba(15, 23, 42, 0.9));
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 10px 24px rgba(2, 6, 23, 0.45);
}

.metric-card:hover {
  transform: translateY(-3px);
  border-color: rgba(139, 92, 246, 0.5);
  box-shadow: 0 16px 30px rgba(30, 27, 75, 0.42);
}

.metric-icon {
  font-size: 1.8rem;
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  background-color: rgba(139, 92, 246, 0.2);
}

.metric-content {
  flex: 1;
}

.metric-label {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.metric-value {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
  font-family: var(--font-display);
}

/* 图表区域 */
.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  background-color: var(--color-bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: 0 10px 24px rgba(2, 6, 23, 0.42);
}

.card-title {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  color: var(--color-text-primary);
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  font-family: var(--font-display);
}

.card-title em {
  font-style: normal;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  font-family: var(--font-body);
}

.line-chart {
  width: 100%;
  height: 220px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.line-chart-svg {
  width: 100%;
  height: 180px;
}

.line-chart-label {
  font-size: 2.4px;
  fill: var(--color-text-secondary);
}

.line-chart-dates {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  text-align: center;
}

/* 订单状态 */
.status-stats {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.status-item {
  width: 100%;
}

.status-bar-wrapper {
  width: 100%;
}

.status-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.status-label {
  color: var(--color-text-secondary);
}

.status-count {
  font-weight: 600;
}

.status-bar {
  width: 100%;
  height: 8px;
  background-color: rgba(148, 163, 184, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.status-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

/* 信息区域 */
.info-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.single-col {
  grid-template-columns: 1fr;
}

.info-card {
  background-color: var(--color-bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: 0 10px 24px rgba(2, 6, 23, 0.42);
}

/* 待处理事项 */
.todo-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.todo-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background-color: rgba(15, 23, 42, 0.45);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--border-color);
}

.todo-item.urgent {
  border-left-color: var(--color-danger);
  background-color: rgba(239, 68, 68, 0.12);
}

.todo-label {
  color: var(--color-text-primary);
}

.todo-count {
  font-weight: 600;
  color: var(--color-accent);
}

/* 热门游戏 */
.game-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.game-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background-color: rgba(15, 23, 42, 0.45);
  border-radius: var(--radius-md);
  transition: background 0.2s;
}

.game-item:hover {
  background-color: rgba(148, 163, 184, 0.14);
}

.game-rank {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-accent);
  min-width: 24px;
}

.game-cover {
  width: 60px;
  height: 34px;
  object-fit: cover;
  border-radius: 4px;
}

.game-info {
  flex: 1;
}

.game-title {
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.game-count {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

/* 最近订单 */
.recent-orders-card {
  background-color: var(--color-bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: 0 10px 24px rgba(2, 6, 23, 0.42);
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.orders-table th,
.orders-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.orders-table th {
  color: var(--color-text-secondary);
  font-weight: 600;
  font-size: 0.9rem;
}

.orders-table tr:last-child td {
  border-bottom: none;
}

.orders-table tr:hover {
  background-color: rgba(148, 163, 184, 0.1);
}

.amount {
  font-family: monospace;
  color: var(--color-accent);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-active {
  background-color: rgba(16, 185, 129, 0.2);
  color: var(--color-success);
}

.status-pending {
  background-color: rgba(199, 132, 43, 0.2);
  color: var(--color-warning);
}

.status-completed {
  background-color: rgba(107, 114, 128, 0.2);
  color: var(--color-text-secondary);
}

.time {
  color: var(--color-text-secondary);
  font-size: 0.85rem;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1200px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-section,
  .info-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 680px) {
  .hero-copy,
  .hero-panel {
    padding: 1.5rem;
  }

  .hero-title {
    font-size: 1.9rem;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .hero-stats {
    grid-template-columns: 1fr;
  }

  .dashboard-tabs {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
  }

  .dashboard-tab {
    justify-content: center;
  }
}
</style>
