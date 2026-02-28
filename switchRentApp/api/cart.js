import request from '../utils/request';

/**
 * 加入购物车
 * @param {Object} data - { gameId, rentDays }
 */
export function addToCart(data) {
    return request({
        url: '/cart/add',
        method: 'POST',
        data
    });
}

/**
 * 获取当前用户购物车列表
 */
export function getCartList() {
    return request({
        url: '/cart/list',
        method: 'GET'
    });
}

/**
 * 更新购物车项租期
 * @param {Number} id - 购物车项ID
 * @param {Number} rentDays - 新的租期
 */
export function updateCartItem(id, rentDays) {
    return request({
        url: `/cart/update/${id}`,
        method: 'POST',
        data: { rentDays }
    });
}

/**
 * 删除购物车项
 * @param {Number} id - 购物车项ID
 */
export function deleteCartItem(id) {
    return request({
        url: `/cart/delete/${id}`,
        method: 'DELETE'
    });
}

/**
 * 清空购物车
 */
export function clearCart() {
    return request({
        url: '/cart/clear',
        method: 'DELETE'
    });
}
