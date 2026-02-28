/**
 * 获取游戏封面图片的完整路径
 * @param {string} filename - 图片文件名 (例如: "zelda.jpg") 或完整 URL
 * @returns {string} - 图片的完整 URL
 */
export const getGameCover = (filename) => {
    if (!filename) {
        // 返回默认占位图
        return new URL('../assets/gameImage/default.png', import.meta.url).href;
    }
    try {
        // 使用 Vite 的 new URL 处理静态资源
        // 注意：这里假设图片都在 ../assets/gameImage/ 目录下
        return new URL(`../assets/gameImage/${filename}`, import.meta.url).href;
    } catch (e) {
        console.error('Image load failed:', e);
        // 返回默认占位图
        return new URL('../assets/gameImage/default.png', import.meta.url).href;
    }
};

export const getUserAvatar = (filename) => {
    if (!filename) {
        // 默认头像
        return new URL('../assets/userAvatar/default.png', import.meta.url).href;
    }
    try {
        // 注意：这里假设图片都在 ../assets/avatar/ 目录下
        return new URL(`../assets/userAvatar/${filename}`, import.meta.url).href;
    } catch (e) {
        console.error('Image load failed:', e);
    }
}
