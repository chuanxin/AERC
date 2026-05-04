// Plugins
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import Fonts from 'unplugin-fonts/vite'
import Layouts from 'vite-plugin-vue-layouts'
import Vue from '@vitejs/plugin-vue'
import VueRouter from 'unplugin-vue-router/vite'
import Vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
import fs from 'fs';

// Utilities
import { defineConfig, loadEnv } from 'vite'
import { fileURLToPath, URL } from 'node:url'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load environment variables from parent directory (.env)
  // This allows both development (PowerShell script) and production (direct build) to work
  // Use import.meta.url instead of __dirname for ES modules
  const configDir = path.dirname(fileURLToPath(import.meta.url))

  // Auto-detect .env location for different deployment structures
  // Development: AERC/dry-farm -> up 1 level
  // Production:  AERC-Deploy/app/dry-farm -> up 2 levels
  let envDir = path.resolve(configDir, '..')
  if (!fs.existsSync(path.join(envDir, '.env'))) {
    envDir = path.resolve(configDir, '..', '..')
  }

  const envFromFile = loadEnv(mode, envDir, '')

  // Priority: process.env (PowerShell) > .env file > fail with error
  const getRequiredEnv = (key: string): string => {
    const value = process.env[key] || envFromFile[key]
    if (!value) {
      throw new Error(
        `❌ Required environment variable "${key}" is not set!\n` +
        `   Please ensure either:\n` +
        `   1. Run the PowerShell script to set process.env, OR\n` +
        `   2. Create .env file in project root with ${key}=<value>`
      )
    }
    return value
  }

  const API_BASE_URL = getRequiredEnv('FAST_API_BASE_URL')
  const API_TARGET = getRequiredEnv('FAST_API_TARGET')
  const API_VERSION = getRequiredEnv('FAST_API_VERSION')

  // Optional HTTPS configuration - only enable if certificates exist
  const certKeyPath = 'certbot/conf/live/cxin.mynetgear.com/privkey.pem'
  const certPath = 'certbot/conf/live/cxin.mynetgear.com/fullchain.pem'
  const httpsConfig = fs.existsSync(certKeyPath) && fs.existsSync(certPath)
    ? {
        key: fs.readFileSync(certKeyPath),
        cert: fs.readFileSync(certPath),
      }
    : undefined

  return {
    // Keep Vite native import.meta.env (e.g. VITE_*) aligned with project root .env source.
    envDir,
    publicDir: 'public', // 確保 public 資料夾包含 .well-known/acme-challenge
    plugins: [
      VueRouter({
        dts: 'src/typed-router.d.ts',
      }),
      Layouts(),
      AutoImport({
        imports: [
          'vue',
          {
            'vue-router/auto': ['useRoute', 'useRouter'],
          }
        ],
        dts: 'src/auto-imports.d.ts',
        eslintrc: {
          enabled: true,
        },
        vueTemplate: true,
      }),
      Components({
        dts: 'src/components.d.ts',
      }),
      Vue({
        template: { transformAssetUrls },
      }),
      // https://github.com/vuetifyjs/vuetify-loader/tree/master/packages/vite-plugin#readme
      Vuetify({
        autoImport: true,
        styles: {
          configFile: 'src/styles/settings.scss',
        },
      }),
      Fonts({
        google: {
          families: [ {
            name: 'Roboto',
            styles: 'wght@100;300;400;500;700;900',
          }],
          display: 'swap'
        },
      }),
    ],
    define: {
      'process.env': {},
      'import.meta.env.FAST_API_BASE_URL': JSON.stringify(API_BASE_URL),
      'import.meta.env.FAST_API_TARGET': JSON.stringify(API_TARGET),
      'import.meta.env.FAST_API_VERSION': JSON.stringify(API_VERSION),
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        // 'ol': fileURLToPath(new URL('./node_modules/ol', import.meta.url)),
      },
      extensions: [
        '.js',
        '.json',
        '.jsx',
        '.mjs',
        '.ts',
        '.tsx',
        '.vue',
      ],
    },
    server: {
      port: 3000,
      host: '0.0.0.0',
      allowedHosts: [
        'cxin.mynetgear.com',
        'uat-dryfarm.cxin.io',
      ],
      ...(httpsConfig && { https: httpsConfig }),
      fs: {
        allow: [
          // Allow serving files from the project root
          '.',
          // Allow serving files from the runtime node_modules directory
          '../../runtime/node_modules',
        ],
        deny: [
          // 環境和配置檔案
          '**/.env*',
          '**/secrets/**',
          '**/credentials/**',

          // 可執行檔案
          '**/.bin/**',

          // 防止向上遍歷
          '../../../**',

          // 專案特定
          '../../runtime/.env*',
          '../../app/api/**',
          '../../db/**',
        ]
      },
      proxy: {
        [API_BASE_URL]: {
          target: API_TARGET,
          changeOrigin: true,
          rewrite: (path) => path.replace(new RegExp(`^${API_BASE_URL}/${API_VERSION}`), ''),
          configure: (proxy) => {
            proxy.on('error', (err) => {
              console.log('proxy error', err)
            })
            proxy.on('proxyReq', (proxyReq, req) => {
              console.log('Sending Request to the Target:', req.method, req.url)
            })
            proxy.on('proxyRes', (proxyRes, req) => {
              console.log('Received Response from the Target:', proxyRes.statusCode, req.url)
            })
          }
        },
      },
      hmr: {
        overlay: false,
      },
      // hmr: false,
      watch : {
        usePolling: true,
        interval: 1000,
      },
      // watch: {
      //   usePolling: false
      // },
    },
    css: {
      preprocessorOptions: {
        sass: {
          // api: 'modern-compiler',
        },
      },
    },
    build: {
      outDir: '../../release/html', // 輸出到 nginx 目錄
      emptyOutDir: true,
      chunkSizeWarningLimit: 1600,
      // Minification and tree-shaking
      minify: 'esbuild',
      target: 'esnext',
      // Reduce CSS size
      cssCodeSplit: true,
      rollupOptions: {
        output: {
          manualChunks(id) {
            // Vuetify UI framework
            if (id.includes('vuetify')) {
              return 'vuetify'
            }

            // OpenLayers GIS library (heavy dependency)
            if (id.includes('node_modules/ol/')) {
              return 'openlayers'
            }

            // FontAwesome icons (split by type to reduce initial load)
            if (id.includes('@fortawesome/fontawesome-svg-core')) {
              return 'fontawesome-core'
            }
            if (id.includes('@fortawesome/free-solid-svg-icons')) {
              return 'fontawesome-solid'
            }
            if (id.includes('@fortawesome/free-regular-svg-icons')) {
              return 'fontawesome-regular'
            }
            if (id.includes('@fortawesome/free-brands-svg-icons')) {
              return 'fontawesome-brands'
            }

            // Vendor libraries (utilities)
            if (id.includes('node_modules/lodash-es')) {
              return 'lodash'
            }
            if (id.includes('node_modules/axios')) {
              return 'axios'
            }

            // Vue ecosystem (already optimized by Vite, but ensure separation)
            if (id.includes('node_modules/vue-router')) {
              return 'vue-router'
            }
            if (id.includes('node_modules/pinia')) {
              return 'pinia'
            }
          },
        },
      },
    },
    optimizeDeps: {
      include: ['lodash-es'] // 預構建 lodash-es
    },
    esbuild: {
      drop: mode === 'production' ? ['console', 'debugger'] : [], // 生產環境移除 console 和 debugger
    },
  }
})
