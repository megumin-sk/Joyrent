import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    port: 8010, // 端口
    open: true, // 自动打开
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8080', // 代理目标地址
        changeOrigin: true, // 是否改变请求头中的 origin
        rewrite: (path) => path.replace(/^\/api/, ''), // 重写路径
      },
    },
  },
  plugins: [vue()], // vue 插件 
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  }
})
