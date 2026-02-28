import request from '../utils/request';

export function loginByFace(imageBase64) {
    return request({
        url: '/face/login',
        method: 'post',
        data: {
            imageBase64
        }
    });
}

export function registerFace(imageBase64, userId) {
    return request({
        url: '/face/register',
        method: 'post',
        data: {
            imageBase64,
            userId
        }
    });
}

export function deleteFace(userId) {
    return request({
        url: `/face/delete/${userId}`,
        method: 'get'
    });
}

export function getFaceStatus(userId) {
    return request({
        url: `/face/status/${userId}`,
        method: 'get'
    });
}
