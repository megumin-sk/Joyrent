import axios from "axios";

// RAG 服务地址 (Python FastAPI)
// 注意：如果前端产生 CORS 跨域错误，需要在 Python 代码中添加 CORSMiddleware，
// 或者在 vite.config.js 中添加代理配置。
const RAG_BASE_URL = 'http://127.0.0.1:5001';

const ragServer = axios.create({
    baseURL: RAG_BASE_URL,
    timeout: 60000
});

/**
 * 添加文档知识库
 * @param {Object} data { game_id, category, content }
 */
export function addDocument(data) {
    return ragServer({
        url: "/rag/add",
        method: "post",
        data: data,
    });
}

/**
 * 搜索相关文档
 * @param {Object} params { query, game_id }
 */
export function searchDocument(params) {
    return ragServer({
        url: "/rag/search",
        method: "get",
        params: params,
    });
}

/**
 * RAG 智能问答
 * @param {Object} data { query, game_id }
 */
export function askQuestion(data) {
    return ragServer({
        url: "/rag/ask",
        method: "post",
        data: data,
    });
}
