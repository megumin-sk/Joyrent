import request from '../utils/request';

export function getGameList() {
  return request({ url: '/games/all' });
}

export function searchGamesByPlatform(platform) {
  return request({
    url: `/games/searchByPlatform/${encodeURIComponent(platform)}`,
    method: 'GET'
  });
}

export function searchGamesByName(name) {
  return request({
    url: `/games/searchByName/${encodeURIComponent(name)}`,
    method: 'GET'
  });
}

export function getTopRentedGames() {
  return request({
    url: '/games/top-rented',
    method: 'GET'
  });
}

/**
 * 根据ID获取游戏详情
 * @param {Number} id 游戏ID
 * @returns {Promise}
 */
export function getGameDetail(id) {
  return request({
    url: `/games/${id}`,
    method: 'GET'
  });
}
