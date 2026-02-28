import request from '../utils/request';

/**
 * 用户登录
 * @param {Object} data - { phone, password }
 */
export function login(data) {
    return request({
        url: '/auth/login',
        method: 'POST',
        data
    });
}

/**
 * 用户注册
 * @param {Object} data - { phone, password, code }
 */
export function register(data) {
    return request({
        url: '/auth/register',
        method: 'POST',
        data
    });
}

/**
 * 发送验证码
 * @param {String} phone - 手机号
 */
export function sendCode(phone) {
    return request({
        url: '/auth/sendCode',
        method: 'POST',
        data: { phone }
    });
}

/**
 * 获取用户信息
 */
export function getUserInfo() {
    return request({
        url: '/auth/userInfo',
        method: 'GET'
    });
}

/**
 * 退出登录
 */
export function logout() {
    return request({
        url: '/auth/logout',
        method: 'POST'
    });
}
