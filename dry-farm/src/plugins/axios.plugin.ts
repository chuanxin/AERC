import axios from 'axios';
import type { App } from 'vue';

// Default axios config
axios.defaults.withCredentials = true;
axios.defaults.baseURL = '/api';  // FastAPI backend (docker-compose)
// axios.defaults.headers.common['Authorization'] = `Bearer ${process.env.VUE_APP_API_TOKEN}`;

export const axiosInstance = {
  install: (app: App) => {
    app.config.globalProperties.$axios = axios;
  },
};
