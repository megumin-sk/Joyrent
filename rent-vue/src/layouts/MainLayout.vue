<script setup>
import { useRouter, useRoute } from 'vue-router';
import { useStore } from 'vuex';
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { getUserAvatar } from '../utils/imgurl.js';

const router = useRouter();
const route = useRoute();
const store = useStore();

const currentUser = computed(() => store.getters.currentUser || {});
const displayName = computed(() => currentUser.value.nickname || currentUser.value.username || 'Admin');
const userAvatar = computed(() => {
  return getUserAvatar(currentUser.value.avatar);
});

const searchInputRef = ref(null);
const searchKeyword = ref('');
const showSearchPanel = ref(false);

const menuItems = [
  { name: '控制台', path: '/dashboard', icon: '📊' },
  { name: '游戏管理', path: '/game', icon: '🎮' },
  { name: '订单管理', path: '/order', icon: '📦' },
  { name: '用户管理', path: '/user', icon: '👥' },
  { name: '评价管理', path: '/review', icon: '⭐' },
  { name: '知识库管理', path: '/rag', icon: '📚' },
];

const quickActions = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase();
  const actions = menuItems.map(item => ({
    ...item,
    description: `前往 ${item.name}`
  }));
  if (!keyword) return actions;
  return actions.filter(item => item.name.toLowerCase().includes(keyword) || item.path.toLowerCase().includes(keyword));
});

const focusSearch = () => {
  if (!searchInputRef.value) return;
  searchInputRef.value.focus();
  showSearchPanel.value = true;
};

const submitSearch = () => {
  const firstAction = quickActions.value[0];
  if (!firstAction) return;
  router.push(firstAction.path);
  showSearchPanel.value = false;
  searchKeyword.value = '';
};

const selectAction = (action) => {
  router.push(action.path);
  showSearchPanel.value = false;
  searchKeyword.value = '';
};

const handleGlobalShortcut = (event) => {
  const isShortcut = (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k';
  if (!isShortcut) return;
  event.preventDefault();
  focusSearch();
};

onMounted(() => {
  window.addEventListener('keydown', handleGlobalShortcut);
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleGlobalShortcut);
});

const handleLogout = () => {
  store.dispatch('logout');
  router.push('/login');
};
</script>

<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="logo-area">
        <span class="logo-joy">Joy</span><span class="logo-rent">Rent</span>
        <span class="badge">Admin</span>
      </div>
      
      <nav class="menu">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path" 
          :to="item.path" 
          class="menu-item"
          :class="{ active: route.path.startsWith(item.path) }"
        >
          <span class="icon">{{ item.icon }}</span>
          <span class="label">{{ item.name }}</span>
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <div class="main-wrapper">
      <header class="top-bar">
        <h2 class="page-title">{{ menuItems.find(i => route.path.startsWith(i.path))?.name || 'Dashboard' }}</h2>

        <div class="top-tools">
          <div class="search-box" @focusin="showSearchPanel = true" @focusout="() => setTimeout(() => { showSearchPanel = false; }, 120)">
            <span class="search-icon">⌕</span>
            <input
              ref="searchInputRef"
              v-model="searchKeyword"
              class="search-input"
              type="text"
              placeholder="搜索页面或输入路径..."
              @keydown.enter.prevent="submitSearch"
              @keydown.esc="showSearchPanel = false"
            />
            <span class="search-shortcut">Ctrl K</span>

            <transition name="fade">
              <div v-if="showSearchPanel" class="search-panel">
                <div class="search-panel-title">快速导航</div>
                <button
                  v-for="item in quickActions"
                  :key="item.path"
                  class="search-item"
                  @click="selectAction(item)"
                >
                  <span class="search-item-icon">{{ item.icon }}</span>
                  <span class="search-item-main">
                    <strong>{{ item.name }}</strong>
                    <em>{{ item.description }}</em>
                  </span>
                  <span class="search-item-path">{{ item.path }}</span>
                </button>

                <p v-if="!quickActions.length" class="search-empty">没有匹配结果，试试“game”或“rag”</p>
              </div>
            </transition>
          </div>

          <div class="user-info">
            <span>{{ displayName }}</span>
            <img :src="userAvatar" :alt="displayName" class="avatar" />
            <button @click="handleLogout" class="logout-btn" title="退出登录">🚪</button>
          </div>
        </div>
      </header>

      <main class="content-area">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--color-bg-primary);
}

/* Sidebar */
.sidebar {
  width: 260px;
  background-color: var(--color-bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  position: fixed;
  height: 100vh;
  z-index: 10;
  background-image:
    linear-gradient(180deg, rgba(15, 23, 42, 0.65), rgba(30, 41, 59, 0.65)),
    radial-gradient(circle at 20% 20%, rgba(139, 92, 246, 0.2), transparent 52%);
}

.logo-area {
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 3rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: var(--font-display);
  letter-spacing: 0.02em;
}

.logo-joy { color: var(--color-text-primary); }
.logo-rent { color: var(--color-accent); }

.badge {
  font-size: 0.7rem;
  background-color: var(--color-accent);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  vertical-align: middle;
}

.menu {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem 1rem;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-weight: 500;
  transition: all 0.2s;
}

.menu-item:hover {
  background-color: var(--color-muted);
  color: var(--color-text-primary);
}

.menu-item.active {
  background-color: var(--color-accent);
  color: white;
  box-shadow: 0 10px 20px var(--color-accent-glow);
}

.icon {
  font-size: 1.2rem;
}

/* Main Wrapper */
.main-wrapper {
  flex: 1;
  margin-left: 260px; /* Sidebar width */
  display: flex;
  flex-direction: column;
}

/* Top Bar */
.top-bar {
  height: 70px;
  background-color: rgba(15, 23, 42, 0.78);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  position: sticky;
  top: 0;
  z-index: 5;
}

.top-tools {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.search-box {
  min-width: 360px;
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(30, 41, 59, 0.85);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0.5rem 0.75rem;
  transition: all 0.2s ease;
}

.search-box:focus-within {
  border-color: var(--color-accent);
  box-shadow: 0 8px 20px var(--color-accent-glow);
  transform: translateY(-1px);
}

.search-icon {
  color: var(--color-text-secondary);
}

.search-input {
  border: none;
  background: transparent;
  color: var(--color-text-primary);
  width: 100%;
  outline: none;
  font-size: 0.92rem;
}

.search-shortcut {
  font-size: 0.72rem;
  color: var(--color-text-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.1rem 0.4rem;
  white-space: nowrap;
}

.search-panel {
  position: absolute;
  top: calc(100% + 10px);
  left: 0;
  right: 0;
  background: rgba(15, 23, 42, 0.96);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  box-shadow: 0 18px 38px rgba(2, 6, 23, 0.7);
  padding: 0.6rem;
  z-index: 20;
}

.search-panel-title {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  letter-spacing: 0.08em;
  margin: 0.2rem 0.3rem 0.5rem;
}

.search-item {
  width: 100%;
  border: none;
  background: transparent;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.55rem;
  border-radius: 10px;
  text-align: left;
}

.search-item:hover {
  background-color: var(--color-muted);
}

.search-item-icon {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: rgba(139, 92, 246, 0.2);
  display: grid;
  place-items: center;
}

.search-item-main {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  flex: 1;
}

.search-item-main strong {
  font-size: 0.9rem;
  color: var(--color-text-primary);
}

.search-item-main em {
  font-style: normal;
  color: var(--color-text-secondary);
  font-size: 0.78rem;
}

.search-item-path {
  font-size: 0.78rem;
  color: var(--color-text-secondary);
}

.search-empty {
  color: var(--color-text-secondary);
  font-size: 0.85rem;
  padding: 0.65rem;
}

.page-title {
  font-size: 1.25rem;
  color: var(--color-text-primary);
  font-family: var(--font-display);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: var(--color-text-primary);
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid var(--border-color);
  object-fit: cover;
  background-color: rgba(15, 23, 42, 0.9);
}

.logout-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
  margin-left: 0.5rem;
}

.logout-btn:hover {
  background-color: var(--color-muted);
}

/* Content Area */
.content-area {
  padding: 2rem;
  flex: 1;
}

@media (max-width: 1100px) {
  .sidebar {
    width: 220px;
  }

  .main-wrapper {
    margin-left: 220px;
  }

  .search-box {
    min-width: 280px;
  }
}

@media (max-width: 900px) {
  .sidebar {
    position: static;
    width: 100%;
    height: auto;
    flex-direction: row;
    align-items: center;
    gap: 1rem;
  }

  .menu {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .main-wrapper {
    margin-left: 0;
  }

  .top-bar {
    height: auto;
    flex-direction: column;
    align-items: stretch;
    gap: 0.8rem;
    padding: 1rem;
  }

  .top-tools {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    width: 100%;
    min-width: 0;
  }
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
