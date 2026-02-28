import server from "../utils/request.js";

/**
 * 认证相关接口封装
 * 调用统一的 axios 实例 server，默认 baseURL 为 /api
 */

/**
 * 管理员登录
 * @param {Object} payload 登录信息（用户名、密码等）
 * @returns {Promise} 请求 /auth/login/admin 的响应
 */
export function adminLogin(payload) {
    return server({
        url: "/auth/login/admin",
        method: "post",
        data: payload,
    });
}

/**
 * 查询用户数量
 */
export function queryUserCount() {
    return server({
        url: "/auth/user/number",
        method: "get",
    })
}