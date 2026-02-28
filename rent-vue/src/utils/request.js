import axios from "axios";
import store from '@/store/index.js'
import router from '@/router/index.js'
import { ElMessage } from 'element-plus'

const server = axios.create({
    // 访问后端的通用路径 - 使用代理避免 CORS 问题
    baseURL: '/api',
    // 请求超时时间
    timeout: 60000
})

// 请求拦截器
server.interceptors.request.use(
    config => {
        const token = store.getters.authToken
        if (token) {
            config.headers['Authorization'] = 'Bearer ' + token
        }
        return config
    },
    error => {
        console.log(error)
        return Promise.reject(error)
    }
)

// 响应拦截器
server.interceptors.response.use(
    response => {
        const res = response.data
        // 如果后端返回的状态码不是 200，则判断为错误
        // 注意：这里假设后端成功时 code 为 200，具体根据后端 ResponseEnum 调整
        // 如果后端直接返回数据没有 code 包装，则直接返回 response
        return response
    },
    error => {
        console.log('err' + error)
        if (error.response) {
            switch (error.response.status) {
                case 401:
                    // 未授权，清除 token 并跳转登录页
                    store.dispatch('logout')
                    router.push('/login')
                    ElMessage.error('登录已过期，请重新登录')
                    break
                default:
                    ElMessage.error(error.message || '请求失败')
            }
        }
        return Promise.reject(error)
    }
)

export default server