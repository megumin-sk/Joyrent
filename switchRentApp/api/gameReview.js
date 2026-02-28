import request from '../utils/request';

/**
 * 获取游戏评价列表
 * @param {number} gameId 游戏ID
 */
export function getReviewsByGameId(gameId) {
    return request({
        url: `/reviews/game/${gameId}`,
        method: 'GET'
    });
}

/**
 * 提交评价
 * @param {object} data { orderId, gameId, rating, content }
 */
export function submitReview(data) {
    return request({
        url: '/reviews/submit',
        method: 'POST',
        data
    });
}
