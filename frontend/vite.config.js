import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'  // 添加此行
import { fileURLToPath } from 'url'  // 添加此行


//const __dirname = path.resolve()

// 获取当前文件目录路径
const __dirname = path.dirname(fileURLToPath(import.meta.url))  // 添加此行

export default defineConfig({
  // 插件配置
  plugins: [vue()],
  base:'./',

  // 构建配置
  build: {
    outDir: path.resolve(__dirname, '../dist'),
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html') // 绝对路径
        
      },
      output: {
        entryFileNames: `assets/[name].[hash].js`,
        assetFileNames: `assets/[name].[hash].[ext]`
      }
    }
  },

  // 开发服务器配置
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        // 新增websocket支持
        ws: true
      }
    },
    // 强制指定端口
    port: 3000,
    // 严格模式
    strictPort: true
  }
})