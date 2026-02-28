import request from '../utils/request';

/**
 * 创建订单
 * @param {Object} data - { addressId, cartIds: [1, 2, 3] }
 */
export function createOrder(data) {
    return request({
        url: '/orders/create',
        method: 'POST',
        data
    });
}

/**
 * 获取用户订单列表
 * @param {Number} status - 订单状态筛选 (可选)
 */
export function getMyOrders(status) {
    return request({
        url: '/orders/my',
        method: 'GET',
        data: status ? { status } : {}
    });
}

/**
 * 获取订单详情
 * @param {Number} id - 订单ID
 */
export function getOrderDetail(id) {
    return request({
        url: `/orders/${id}`,
        method: 'GET'
    });
}

/**
 * 取消订单
 * @param {Number} id - 订单ID
 */
export function cancelOrder(id) {
    return request({
        url: `/orders/${id}/cancel`,
        method: 'POST'
    });
}

/**
 * 模拟支付（测试用）
 * @param {Number} id - 订单ID
 */
export function payOrder(id) {
    return request({
        url: `/orders/${id}/pay`,
        method: 'POST'
    });
}
