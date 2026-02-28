const BASE_URL =
  process.env?.VUE_APP_BASE_API ||
  process.env?.UNI_APP_BASE_API ||
  'http://localhost:8080';

export default function request({ url, method = 'GET', data, header = {} }) {
  if (typeof uni === 'undefined') {
    return Promise.reject(new Error('uni runtime is not available'));
  }

  const finalUrl = /^https?:\/\//i.test(url) ? url : `${BASE_URL}${url}`;

  // 获取 Token (遵循标准 Bearer Token 规范)
  const token = uni.getStorageSync('token');
  const authHeader = token ? { 'Authorization': `Bearer ${token}` } : {};

  return new Promise((resolve, reject) => {
    uni.request({
      url: finalUrl,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...authHeader,
        ...header
      },
      success: res => {
        const { statusCode, data: payload } = res;

        // 处理 401 未登录
        if (statusCode === 401 || (payload && payload.code === 401)) {
          uni.showToast({
            title: '请先登录',
            icon: 'none'
          });
          // 避免重复跳转
          const pages = getCurrentPages();
          const currentPage = pages[pages.length - 1];
          if (currentPage && currentPage.route !== 'pages/auth/login') {
            setTimeout(() => {
              uni.navigateTo({
                url: '/pages/auth/login'
              });
            }, 1500);
          }
          reject(new Error('Unauthorized'));
          return;
        }

        if (statusCode >= 200 && statusCode < 300) {
          resolve(payload);
        } else {
          reject(
            new Error(
              `Request ${method} ${url} failed with status ${statusCode}`
            )
          );
        }
      },
      fail: err => reject(err)
    });
  });
}

