<template>
  <div class="game-manage-container">
    <!-- Toolbar with Search, Filter and Add Button -->
    <div class="toolbar">
      <div class="left-actions">
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="搜索游戏名称..." 
            class="input-field"
            @keyup.enter="handleSearch"
          >
        </div>
        
        <div class="filter-box">
          <select v-model="selectedPlatform" class="input-field select-field">
            <option value="">全部平台</option>
            <option value="Switch">Switch</option>
            <option value="PlayStation">PlayStation</option>
          </select>
        </div>

        <button class="btn btn-outline" @click="handleSearch">搜索</button>
      </div>

      <button class="btn btn-primary" @click="openAddModal">
        <span class="icon">+</span> 新增游戏
      </button>
    </div>

    <!-- Data Table -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>封面</th>
            <th>游戏名称</th>
            <th>平台</th>
            <th>日租金</th>
            <th>押金</th>
            <th>库存</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="game in filteredGames" :key="game.id">
            <td>{{ game.id }}</td>
            <td>
              <img :src="getCoverUrl(game.coverUrl)" alt="Cover" class="table-cover">
            </td>
            <td class="game-title-cell">{{ game.title }}</td>
            <td>
              <span :class="['badge', 'platform-badge', game.platform.toLowerCase()]">
                {{ game.platform }}
              </span>
            </td>
            <td class="price-text">¥{{ game.dailyRentPrice }}</td>
            <td class="price-text">¥{{ game.depositPrice }}</td>
            <td>
              <span :class="['stock-text', getStockClass(game.availableStock)]">
                {{ game.availableStock }}
              </span>
            </td>
            <td>
              <span :class="['status-badge', game.status === 1 ? 'status-active' : 'status-inactive']">
                {{ game.status === 1 ? '上架' : '下架' }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <button class="btn-icon edit" @click="openEditModal(game)">编辑</button>
                <button class="btn-icon delete" @click="handleDelete(game)">删除</button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredGames.length === 0">
            <td colspan="9" class="empty-text">暂无数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modals -->
    <add-game 
      :visible="showAddModal" 
      @close="showAddModal = false" 
      @save="handleSaveNewGame"
    />
    
    <edit-game 
      :visible="showEditModal" 
      :game-data="currentGame"
      @close="showEditModal = false"
      @save="handleUpdateGame"
    />
  </div>
</template>

<script>
import AddGame from './pop-window/addGame.vue';
import EditGame from './pop-window/editGame.vue';
import { getGameCover } from '../../utils/imgurl';
import { getGameList, createGame, updateGame, deleteGame } from '../../api/game.js';

export default {
  name: 'GameManage',
  components: {
    AddGame,
    EditGame
  },
  data() {
    return {
      searchQuery: '',
      selectedPlatform: '',
      games: [],
      showAddModal: false,
      showEditModal: false,
      currentGame: {}
    };
  },
  computed: {
    filteredGames() {
      return this.games.filter(game => {
        const matchName = game.title.toLowerCase().includes(this.searchQuery.toLowerCase());
        const matchPlatform = this.selectedPlatform ? game.platform === this.selectedPlatform : true;
        return matchName && matchPlatform;
      });
    }
  },
  created() {
    this.fetchGames();
  },
  methods: {
    normalizeGame(game) {
      if (!game) return {};
      return {
        ...game,
        availableStock: game.availableStock ?? game.available_stock ?? 0
      };
    },
    async fetchGames() {
      try {
        const { data } = await getGameList();
        const list = data?.data || [];
        this.games = list.map(this.normalizeGame);
      } catch (error) {
        console.error('Failed to fetch games', error);
        alert('获取游戏列表失败，请稍后再试');
      }
    },
    handleSearch() {
      // Triggered by enter key or button, but computed property handles filtering automatically
    },
    openAddModal() {
      this.showAddModal = true;
    },
    openEditModal(game) {
      this.currentGame = { ...game }; // Deep copy
      this.showEditModal = true;
    },
    async handleSaveNewGame(gameData) {
      try {
        await createGame(gameData);
        await this.fetchGames();
        this.showAddModal = false;
      } catch (error) {
        console.error('Failed to create game', error);
        alert('新增游戏失败，请稍后重试');
      }
    },
    async handleUpdateGame(gameData) {
      try {
        await updateGame(gameData);
        await this.fetchGames();
        this.showEditModal = false;
      } catch (error) {
        console.error('Failed to update game', error);
        alert('更新游戏失败，请稍后重试');
      }
    },
    async handleDelete(game) {
      if (!confirm(`确定要删除 "${game.title}" 吗？`)) {
        return;
      }
      try {
        await deleteGame(game.id);
        await this.fetchGames();
      } catch (error) {
        console.error('Failed to delete game', error);
        alert('删除失败，请稍后重试');
      }
    },
    getCoverUrl(filename) {
      return getGameCover(filename);
    },
    getStockClass(stock) {
      const value = Number(stock) || 0;
      if (value < 10) return 'stock-low';
      if (value < 30) return 'stock-medium';
      return 'stock-high';
    }
  }
};
</script>

<style scoped>
.game-manage-container {
  color: var(--color-text-primary);
}

/* Toolbar */
.toolbar {
  position: sticky;
  top: 70px;
  z-index: 100;
  margin-bottom: 1.5rem;
  background-color: var(--color-bg-card);
  padding: 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.left-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex: 1;
}

.search-box {
  width: 300px;
}

.filter-box {
  width: 150px;
}

.input-field {
  background-color: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-color);
  color: var(--color-text-primary);
  padding: 0.6rem 1rem;
  border-radius: var(--radius-sm);
  width: 100%;
  font-size: 0.9rem;
}

.input-field:focus {
  outline: none;
  border-color: var(--color-accent);
}

.select-field {
  cursor: pointer;
}

/* Table */
.table-container {
  background-color: var(--color-bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.data-table th {
  background-color: rgba(0, 0, 0, 0.2);
  font-weight: 600;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table tr:hover {
  background-color: rgba(255, 255, 255, 0.02);
}

.table-cover {
  width: 100px;
  height: 56px;
  object-fit: cover;
  border-radius: 4px;
  background-color: #000;
}

.game-title-cell {
  font-weight: 500;
}

.badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.platform-badge {
  background-color: #333;
  color: white;
}

.platform-badge.switch {
  background-color: #e60012;
}

.platform-badge.playstation {
  background-color: #003791;
}

.price-text {
  font-family: monospace;
  color: var(--color-accent);
}

.stock-text {
  font-weight: 600;
}

.stock-low { color: var(--color-danger); }
.stock-medium { color: #fbbf24; }
.stock-high { color: var(--color-success); }

.status-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
}

.status-active {
  background-color: rgba(16, 185, 129, 0.2);
  color: var(--color-success);
}

.status-inactive {
  background-color: rgba(239, 68, 68, 0.2);
  color: var(--color-danger);
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.85rem;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.btn-icon.edit {
  color: var(--color-accent);
}

.btn-icon.edit:hover {
  background-color: rgba(139, 92, 246, 0.1);
}

.btn-icon.delete {
  color: var(--color-danger);
}

.btn-icon.delete:hover {
  background-color: rgba(239, 68, 68, 0.1);
}
</style>