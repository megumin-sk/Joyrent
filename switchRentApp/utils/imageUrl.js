/**
 * 图片路径处理工具类
 */

/**
 * 通用的获取图片完整URL的内部方法
 * @param {String} url - 图片文件名或路径
 * @param {String} basePath - 基础存储路径 (如 /static/game/)
 * @param {String} defaultImage - 默认兜底图路径
 * @returns {String} 完整的图片路径
 */
function _getImageUrl(url, basePath, defaultImage) {
    // 1. 如果 url 为空，返回默认图
    if (!url) {
        return defaultImage;
    }

    // 2. 如果已经是完整网络链接 (http/https)，直接返回
    if (url.startsWith('http://') || url.startsWith('https://')) {
        return url;
    }

    // 3. 如果已经是 /static 开头的路径，直接返回 (防止重复拼接)
    // 注意：这里假设 basePath 也是以 /static 开头的，所以只需检查 /static
    if (url.startsWith('/static/')) {
        return url;
    }

    // 4. 处理 basePath 末尾的斜杠，确保拼接正确
    // 保证 basePath 以 / 结尾
    if (!basePath.endsWith('/')) {
        basePath += '/';
    }

    // 5. 拼接本地静态资源路径
    // 确保文件名不带前导斜杠
    const filename = url.startsWith('/') ? url.substring(1) : url;
    return `${basePath}${filename}`;
}

/**
 * 获取游戏图片的完整URL
 * 路径: /static/game/
 * @param {String} url - 图片文件名
 * @returns {String}
 */
export function getGameImageUrl(url) {
    return _getImageUrl(url, '/static/game/', '/static/game/default.png');
}

/**
 * 获取用户头像的完整URL
 * 路径: /static/user_img/
 * @param {String} url - 图片文件名
 * @returns {String}
 */
export function getUserImageUrl(url) {
    return _getImageUrl(url, '/static/user_img/', '/static/user_img/default.png');
}
