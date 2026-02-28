import request from '../utils/request';

/**
 * 用户登录(使用手机号和密码)
 * @param {Object} data - { phone, password }
 * @returns {Promise}
 */
export function userLogin(data) {
    return request({
        url: '/auth/login/user',
        method: 'POST',
        data
    });
}

/**
 * 获取用户信息
 * @returns {Promise}
 */
export function getUserInfo() {
    return request({
        url: '/user/info',
        method: 'GET'
    });
}

/**
 * 更新用户信息
 * @param {Object} data - 用户信息对象
 * @returns {Promise}
 */
export function updateUserInfo(data) {
    return request({
        url: '/user/update',
        method: 'PUT',
        data
    });
}

/**
 * 退出登录
 * @returns {Promise}
 */
export function logout() {
    return request({
        url: '/auth/logout',
        method: 'POST'
    });
}
