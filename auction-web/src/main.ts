import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import App from './App.vue'

import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import '@fontsource/roboto'

const vuetify = createVuetify({
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: { mdi },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1565C0',
          secondary: '#FF6F00',
          accent: '#00BFA5',
          error: '#D32F2F',
          warning: '#F9A825',
          success: '#2E7D32',
        },
      },
    },
  },
})

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('./pages/index.vue') },
    { path: '/auctions', component: () => import('./pages/auctions/index.vue') },
    { path: '/auctions/:id', component: () => import('./pages/auctions/[id].vue') },
    { path: '/auctions/create', component: () => import('./pages/auctions/create.vue') },
    { path: '/login', component: () => import('./pages/login.vue') },
    { path: '/register', component: () => import('./pages/register.vue') },
    { path: '/user/my-bids', component: () => import('./pages/user/my-bids.vue') },
    { path: '/user/my-auctions', component: () => import('./pages/user/my-auctions.vue') },
  ],
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(vuetify)
app.mount('#app')
