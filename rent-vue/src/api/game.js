import server from "../utils/request.js";

/**
 * 游戏相关接口封装
 * 调用统一的 axios 实例 server，默认 baseURL 为 /api
 */

/**
 * 获取全部游戏列表
 * @returns {Promise} 请求 /games/all 的响应
 */
export function getGameList() {
  return server({
    url: "/games/all",
    method: "get",
  });
}

/**
 * 按名称模糊搜索游戏
 * @param {string} name 游戏名称关键词
 */
export function searchGamesByName(name) {
  return server({
    url: `/games/searchByName/${encodeURIComponent(name)}`,
    method: "get",
  });
}

/**
 * 根据平台筛选游戏
 * @param {string} platform 平台标识（如 Switch、PS5 等）
 */
export function searchGamesByPlatform(platform) {
  return server({
    url: `/games/searchByPlatform/${encodeURIComponent(platform)}`,
    method: "get",
  });
}

/**
 * 新增游戏
 * @param {Object} payload 与后端 Game DTO 对齐的数据
 */
export function createGame(payload) {
  return server({
    url: "/games/create",
    method: "post",
    data: payload,
  });
}

/**
 * 更新游戏信息
 * @param {Object} payload 包含游戏 ID 及更新字段
 */
export function updateGame(payload) {
  return server({
    url: "/games/update",
    method: "put",
    data: payload,
  });
}

/**
 * 删除指定游戏
 * @param {number|string} id 游戏 ID
 */
export function deleteGame(id) {
  return server({
    url: `/games/delete/${id}`,
    method: "delete",
  });
}
