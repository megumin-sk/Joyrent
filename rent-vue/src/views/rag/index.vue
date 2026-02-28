<template>
  <div class="rag-container">
    <div class="rag-header">
      <h2>知识库管理 Center</h2>
      <p>管理 RAG 系统的知识源，涵盖游戏攻略、平台规则与玩家评价。</p>
    </div>

    <div class="rag-content">
      <el-card class="rag-card" shadow="never">
        <el-tabs v-model="activeName" class="custom-tabs">
          <!-- Tab 1: 添加知识 -->
          <el-tab-pane label="📝 添加知识" name="add">
            <div class="tab-content">
              <el-form :model="form" label-position="top" size="large">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="关联游戏 (Game)">
                      <el-select
                        v-model="form.game_id"
                        filterable
                        remote
                        reserve-keyword
                        placeholder="搜索游戏名称 (如: 塞尔达)"
                        :remote-method="searchGameRemote"
                        :loading="searchGameLoading"
                        clearable
                        style="width: 100%"
                        popper-class="custom-select-popper"
                      >
                        <el-option
                          v-for="item in gameOptions"
                          :key="item.id"
                          :label="item.title"
                          :value="item.id"
                        >
                            <span class="option-title">{{ item.title }}</span>
                            <span class="option-id">ID: {{ item.id }}</span>
                        </el-option>
                      </el-select>
                      <div class="form-tip">未选择则默认为“通用/平台规则”</div>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                     <el-form-item label="内容分类 (Category)">
                      <el-select v-model="form.category" placeholder="选择分类" style="width: 100%" popper-class="custom-select-popper">
                        <el-option label="📜 平台规则 (Rule)" value="rule"></el-option>
                        <el-option label="🎮 游戏内容 (Game)" value="game"></el-option>
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
                
                <el-form-item label="详细内容 (Content)">
                  <el-input 
                    v-model="form.content" 
                    type="textarea" 
                    :rows="15" 
                    placeholder="请输入详细的知识内容。支持 Markdown 格式..."
                    class="custom-textarea"
                  ></el-input>
                </el-form-item>
                
                <el-form-item>
                  <el-button color="#8b5cf6" type="primary" @click="onSubmit" :loading="loading" class="submit-btn" size="large">
                    ✨ 提交入库
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>

          <!-- Tab 2: 检索测试 -->
          <el-tab-pane label="🔍 检索测试" name="search">
             <div class="tab-content">
                <div class="search-bar">
                   <el-input 
                    v-model="searchQuery" 
                    placeholder="输入检索关键词..." 
                    size="large"
                    @keyup.enter="onSearch"
                    clearable
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                    <template #append>
                      <el-button @click="onSearch" :loading="searchLoading">搜索</el-button>
                    </template>
                  </el-input>
                </div>

                <div v-if="searchResults.length" class="results-list">
                   <div class="section-title">
                      检索意图: <span class="intent-badge">{{ searchIntent }}</span>
                   </div>
                   
                   <div v-for="(item, index) in searchResults" :key="index" class="result-card">
                      <div class="result-header">
                        <div class="left">
                           <el-tag effect="dark" :type="getCategoryTagType(item.category)" size="small">{{ item.category }}</el-tag>
                           <span v-if="item.game_id" class="game-id-badge">Game #{{ item.game_id }}</span>
                        </div>
                        <div class="right">
                           <span class="similarity">相似度: {{ (item.similarity * 100).toFixed(1) }}%</span>
                        </div>
                      </div>
                      <div class="result-body">
                         {{ item.content }}
                      </div>
                   </div>
                </div>
                <div v-else-if="!searchLoading && hasSearched" class="empty-state">
                  暂无相关数据
                </div>
             </div>
          </el-tab-pane>

          <!-- Tab 3: 问答测试 -->
          <el-tab-pane label="🤖 智能问答" name="ask">
             <div class="tab-content chat-layout">
                <div class="chat-input-area">
                   <el-input 
                    v-model="askQuery" 
                    placeholder="向 JoyRent AI 提问 (例如：塞尔达传说有什么好玩的？)" 
                    size="large"
                    @keyup.enter="onAsk"
                  >
                     <template #prefix>
                        <el-icon><Microphone /></el-icon>
                     </template>
                     <template #append>
                      <el-button @click="onAsk" :loading="askLoading">提问</el-button>
                     </template>
                  </el-input>
                </div>
                
                <div v-if="answerResult" class="chat-response fade-in">
                  <div class="joy-avatar">
                     🤖
                  </div>
                  <div class="joy-bubble">
                     <div class="joy-name">JoyRent AI</div>
                     <div class="joy-text">{{ answerResult.answer }}</div>
                     
                     <div v-if="answerResult.sources && answerResult.sources.length" class="joy-sources">
                        <el-collapse>
                          <el-collapse-item title="📚 参考来源" name="1">
                            <div v-for="(source, idx) in answerResult.sources" :key="idx" class="source-row">
                              <p class="source-text">{{ source.content }}</p>
                              <span class="source-score">Match: {{ (source.similarity * 100).toFixed(0) }}%</span>
                            </div>
                          </el-collapse-item>
                        </el-collapse>
                     </div>
                  </div>
                </div>
             </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Microphone } from '@element-plus/icons-vue'
import { addDocument, searchDocument, askQuestion } from '@/api/rag'
import { searchGamesByName } from '@/api/game'

const activeName = ref('add')
const loading = ref(false)
const searchLoading = ref(false)
const askLoading = ref(false)
const hasSearched = ref(false)

// 游戏搜索相关
const searchGameLoading = ref(false)
const gameOptions = ref([])

// 表单数据
const form = reactive({
  game_id: null,
  category: 'game',
  content: ''
})

// 搜索数据
const searchQuery = ref('')
const searchResults = ref([])
const searchIntent = ref('')

// 问答数据
const askQuery = ref('')
const answerResult = ref(null)

// 远程搜索游戏
const searchGameRemote = async (query) => {
    if (query) {
        searchGameLoading.value = true
        try {
            const res = await searchGamesByName(query)
            const list = Array.isArray(res.data) ? res.data : (res.data?.data || [])
            gameOptions.value = list
        } catch (error) {
            console.error("Search game error", error)
            gameOptions.value = []
        } finally {
            searchGameLoading.value = false
        }
    } else {
        gameOptions.value = []
    }
}

// 提交入库
const onSubmit = async () => {
    if (!form.content) {
        ElMessage.warning('内容不能为空')
        return
    }
    
    loading.value = true
    try {
        await addDocument(form)
        ElMessage.success('入库成功！')
        form.content = '' 
    } catch (error) {
        if (error.response && error.response.data && error.response.data.detail) {
             ElMessage.error('入库失败: ' + error.response.data.detail)
        } else {
             ElMessage.error('入库失败: ' + (error.message || '未知错误'))
        }
    } finally {
        loading.value = false
    }
}

// 执行搜索
const onSearch = async () => {
    if (!searchQuery.value) return
    
    searchLoading.value = true
    searchResults.value = []
    hasSearched.value = true
    try {
        const res = await searchDocument({ query: searchQuery.value })
        searchResults.value = res.data.results
        searchIntent.value = res.data.intent
    } catch (error) {
        ElMessage.error('搜索失败')
    } finally {
        searchLoading.value = false
    }
}

// 执行问答
const onAsk = async () => {
    if (!askQuery.value) return
    
    askLoading.value = true
    answerResult.value = null
    try {
        const res = await askQuestion({ query: askQuery.value })
        answerResult.value = res.data
    } catch (error) {
         ElMessage.error('提问失败')
    } finally {
        askLoading.value = false
    }
}

// Helper: Tag Color
const getCategoryTagType = (category) => {
    const map = {
        rule: 'danger',
        game: 'success',
        all: 'warning'
    }
    return map[category] || 'primary'
}
</script>

<style scoped>
/* 
  重写 Element Plus 变量以适配暗色主题 
  利用 Vue 的 scoped style penetration 或者直接在 root 元素上定义变量
*/
.rag-container {
    padding: 24px;
    max-width: 1200px;
    margin: 0 auto;
    
    /* 局部覆盖 Element 变量 */
    --el-text-color-primary: #f8fafc;
    --el-text-color-regular: #cbd5e1;
    --el-text-color-secondary: #94a3b8;
    --el-border-color: #334155;
    --el-border-color-light: #475569;
    --el-bg-color: #1e293b;
    --el-bg-color-overlay: #1e293b;
    --el-fill-color-blank: #0f172a;
}

.rag-header h2 {
    color: var(--color-text-primary);
    margin-bottom: 8px;
    font-size: 1.8rem;
}

.rag-header p {
    color: var(--color-text-secondary);
    margin-bottom: 24px;
}

.rag-card {
    background-color: var(--color-bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    color: var(--color-text-primary);
}

.tab-content {
    padding: 20px 0;
}

/* Form Styles */
.form-tip {
    font-size: 12px;
    color: var(--color-text-secondary);
    margin-top: 6px;
}

.submit-btn {
    width: 200px;
    font-weight: 600;
}

.option-id {
    float: right;
    color: var(--el-text-color-secondary);
    font-size: 12px;
}

/* Result Card Styles */
.results-list {
    margin-top: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.section-title {
    color: var(--color-text-secondary);
    font-size: 0.9rem;
    margin-bottom: 8px;
}

.intent-badge {
    color: var(--color-accent);
    font-weight: bold;
    text-transform: uppercase;
}

.result-card {
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 16px;
    transition: transform 0.2s;
}

.result-card:hover {
    transform: translateY(-2px);
    background-color: rgba(255, 255, 255, 0.05);
}

.result-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
}

.game-id-badge {
    margin-left: 12px;
    font-size: 0.8rem;
    color: var(--el-text-color-secondary);
    background: rgba(255,255,255,0.1);
    padding: 2px 6px;
    border-radius: 4px;
}

.similarity {
    font-family: monospace;
    color: var(--color-accent);
    font-weight: bold;
}

.result-body {
    color: var(--el-text-color-regular);
    line-height: 1.6;
    font-size: 0.95rem;
    white-space: pre-wrap;
}

.empty-state {
    text-align: center;
    padding: 40px;
    color: var(--color-text-secondary);
}

/* Chat Styles */
.chat-layout {
    max-width: 800px;
    margin: 0 auto;
}

.chat-response {
    margin-top: 30px;
    display: flex;
    gap: 16px;
    animation: fadeIn 0.5s ease;
}

.joy-avatar {
    width: 40px;
    height: 40px;
    background: var(--color-accent);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    flex-shrink: 0;
}

.joy-bubble {
    flex: 1;
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 0 16px 16px 16px;
    padding: 20px;
    border: 1px solid var(--border-color);
}

.joy-name {
    font-weight: bold;
    color: var(--color-accent);
    margin-bottom: 8px;
    font-size: 0.9rem;
}

.joy-text {
    color: var(--color-text-primary);
    line-height: 1.7;
    white-space: pre-wrap;
}

.joy-sources {
    margin-top: 20px;
    padding-top: 10px;
    border-top: 1px solid var(--border-color);
}

.source-row {
    margin-bottom: 8px;
    font-size: 0.85rem;
    color: var(--color-text-secondary);
    padding: 8px;
    background: rgba(0,0,0,0.2);
    border-radius: 4px;
}

.source-score {
    float: right;
    color: var(--color-accent);
    font-size: 0.75rem;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Deep Selector Overrides for Element Plus in Dark Mode */
:deep(.el-card) {
    border: none;
    color: inherit;
}
:deep(.el-card__header) {
    border-bottom: 1px solid var(--border-color);
}
:deep(.el-tabs__item) {
    color: var(--color-text-secondary);
    font-size: 1rem;
}
:deep(.el-tabs__item.is-active) {
    color: var(--color-accent);
}
:deep(.el-tabs__nav-wrap::after) {
    background-color: var(--border-color);
}
:deep(.el-input__wrapper), :deep(.el-textarea__inner) {
    background-color: var(--el-fill-color-blank) !important;
    box-shadow: 0 0 0 1px var(--border-color) inset !important;
}
:deep(.el-input__wrapper.is-focus), :deep(.el-textarea__inner:focus) {
    box-shadow: 0 0 0 1px var(--color-accent) inset !important;
}
:deep(.el-select-dropdown__item) {
    color: var(--el-text-color-regular);
}
:deep(.el-select-dropdown__item.hover), :deep(.el-select-dropdown__item:hover) {
    background-color: var(--border-color);
}
:deep(.el-collapse-item__header) {
    background-color: transparent;
    color: var(--color-text-secondary);
    border-bottom: 1px solid var(--border-color);
}
:deep(.el-collapse-item__wrap) {
    background-color: transparent;
    border-bottom: none;
}
:deep(.el-collapse) {
    border: none;
}
</style>
