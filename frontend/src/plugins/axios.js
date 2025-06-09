import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

// 建立一個 Axios 的實例
const apiClient = axios.create({
  // CHANGED: 從環境變數讀取後端 API 的基礎 URL
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 設定請求攔截器 (Request Interceptor)
apiClient.interceptors.request.use(
  (config) => {
    // 在這裡取得 auth store
    const authStore = useAuthStore();
    
    // 如果 token 存在，則在每個請求的 Header 中加入 Authorization
    if (authStore.token) {
      config.headers['Authorization'] = `Bearer ${authStore.token}`;
    }
    
    return config;
  },
  (error) => {
    // 對請求錯誤做些什麼
    return Promise.reject(error);
  }
);

export default apiClient;