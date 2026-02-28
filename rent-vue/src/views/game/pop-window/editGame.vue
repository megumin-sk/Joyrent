<template>
  <div class="modal-overlay" v-if="visible" @click.self="handleClose">
    <div class="modal-content">
      <div class="modal-header">
        <h3>编辑游戏</h3>
        <button class="close-btn" @click="handleClose">×</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>游戏名称</label>
          <input type="text" v-model="form.title" class="input-field">
        </div>
        
        <div class="form-group">
          <label>封面文件名</label>
          <input type="text" v-model="form.coverUrl" class="input-field" placeholder="例如: zelda.jpg">
          <div class="image-preview" v-if="form.coverUrl">
            <img :src="previewUrl" alt="Preview" @error="$event.target.style.display='none'" @load="$event.target.style.display='block'">
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>日租金 (¥)</label>
            <input type="number" v-model.number="form.dailyRentPrice" class="input-field" step="0.1">
          </div>
          <div class="form-group">
            <label>押金 (¥)</label>
            <input type="number" v-model.number="form.depositPrice" class="input-field" step="1">
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>库存数量 <span class="readonly-tag">(系统统计)</span></label>
            <input 
              type="text" 
              :value="form.availableStock" 
              class="input-field stock-display" 
              disabled 
              readonly
            >
          </div>
          <div class="form-group">
            <label>状态</label>
            <select v-model="form.status" class="input-field">
              <option :value="1">上架</option>
              <option :value="0">下架</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>平台</label>
          <select v-model="form.platform" class="input-field">
            <option value="Switch">Switch</option>
            <option value="PlayStation">PlayStation</option>
          </select>
        </div>

        <div class="form-group">
          <label>描述</label>
          <textarea v-model="form.description" class="input-field textarea" rows="3"></textarea>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-outline" @click="handleClose">取消</button>
        <button class="btn btn-primary" @click="handleSave">保存修改</button>
      </div>
    </div>
  </div>
</template>

<script>
import { getGameCover } from '../../../utils/imgurl';

const createDefaultForm = () => ({
  id: null,
  title: '',
  platform: 'Switch',
  coverUrl: '',
  dailyRentPrice: 0,
  depositPrice: 0,
  availableStock: 0,
  status: 1,
  description: ''
});

export default {
  name: 'EditGame',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    gameData: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      form: createDefaultForm()
    };
  },
  computed: {
    previewUrl() {
      return getGameCover(this.form.coverUrl);
    }
  },
  watch: {
    // Watch for changes in gameData when modal opens
    gameData: {
      handler(newVal) {
        if (newVal && Object.keys(newVal).length) {
          this.form = {
            ...createDefaultForm(),
            ...newVal
          };
        } else {
          this.form = createDefaultForm();
        }
      },
      immediate: true,
      deep: true
    }
  },
  methods: {
    handleClose() {
      this.$emit('close');
    },
    handleSave() {
      if (!this.form.title) {
        alert('请输入游戏名称');
        return;
      }
      
      // 复制表单数据
      const submitData = { ...this.form };
      
      // 【重要】剔除库存字段。
      // 因为库存是只读的统计数据，不应通过此接口更新。
      // 实际库存更新应通过"入库/出库"操作影响 game_items 表。
      delete submitData.availableStock;

      this.$emit('save', submitData);
    }
  }
};
</script>

<style scoped>
/* Reusing styles from parent for consistency */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background-color: var(--color-bg-card);
  width: 640px;
  max-width: 90vw;
  max-height: 90vh;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  animation: modalSlideIn 0.3s ease;
  color: var(--color-text-primary);
  display: flex;
  flex-direction: column;
}

@keyframes modalSlideIn {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.close-btn {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: 1.5rem;
  cursor: pointer;
}

.close-btn:hover {
  color: var(--color-text-primary);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.form-group {
  margin-bottom: 1rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-row .form-group {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
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

.textarea {
  resize: vertical;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.image-preview {
  margin-top: 0.5rem;
  width: 240px;
  height: 135px;
  border-radius: 8px;
  overflow: hidden;
  background-color: #000;
  border: 1px solid var(--border-color);
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 新增：只读库存的特殊样式 */
.stock-display {
  background-color: rgba(255, 255, 255, 0.05) !important;
  border-color: transparent !important;
  color: var(--color-accent) !important; /* 假设这里是金色/亮色 */
  font-family: monospace;
  font-weight: bold;
  cursor: not-allowed;
  text-align: center;
}

.readonly-tag {
  font-size: 0.8em;
  color: var(--color-text-secondary);
  opacity: 0.7;
  margin-left: 4px;
}
</style>