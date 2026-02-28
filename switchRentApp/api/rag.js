import request from '../utils/request';

// 基础地址配置
// 注意：真机调试时请将 localhost 换成电脑的局域网 IP (如 192.168.1.x)
const AGENT_BASE_URL = 'http://localhost:8001';

/**
 * 向 JoyRent 智能 Agent 提问
 * @param {String} message - 用户输入的消息
 * @param {String|null} user_id - 用户ID（从存储或状态获取）
 * @returns {Promise<Object>}
 */
export function askAgent(message, user_id = null) {
    const data = { message };
    if (user_id) {
        data.user_id = user_id.toString();
    }

    return request({
        url: `${AGENT_BASE_URL}/chat`,
        method: 'POST',
        data: data
    });
}

/**
 * 向 RAG 服务提问 (旧版兼容)
 * @deprecated 建议迁移到 askAgent
 */
export function askRag(query, game_id = null) {
    return askAgent(query, null);
}
