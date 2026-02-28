
import request from '../utils/request';

// 获取地址列表
export function getAddressList() {
    return request({
        url: '/address/list',
        method: 'GET'
    });
}

// 添加地址
export function addAddress(data) {
    return request({
        url: '/address/add',
        method: 'POST',
        data
    });
}

// 更新地址
export function updateAddress(data) {
    return request({
        url: '/address/update',
        method: 'POST',
        data
    });
}

// 删除地址
export function deleteAddress(id) {
    return request({
        url: `/address/delete/${id}`,
        method: 'POST'
    });
}

// 设为默认地址
export function setDefaultAddress(id) {
    return request({
        url: `/address/setDefault/${id}`,
        method: 'POST'
    });
}
