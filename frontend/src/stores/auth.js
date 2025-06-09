import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import apiClient from '@/plugins/axios';
import router from '@/router';

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref(localStorage.getItem('token') || null);
  const user = ref(JSON.parse(localStorage.getItem('user')) || null);

  // Getters
  const isAuthenticated = computed(() => !!token.value);
  const userRole = computed(() => user.value?.role || 'user');

  // Actions
  async function fetchUser() {
    if (token.value) {
      try {
        const response = await apiClient.get('/api/v1/auth/users/me');
        user.value = response.data;
        localStorage.setItem('user', JSON.stringify(user.value));
      } catch (error) {
        console.error('無法獲取使用者資訊:', error);
        // 如果 token 失效，直接登出
        logout();
      }
    }
  }
  
  // NEW & UPDATED: 根據 OpenAPI 規格重寫登入邏輯
  async function login(credentials) {
    // API 要求 application/x-www-form-urlencoded
    const params = new URLSearchParams();
    params.append('username', credentials.username); // API 使用 username 登入
    params.append('password', credentials.password);

    try {
      const response = await apiClient.post('/api/v1/auth/login/access-token', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      // 根據 OAuth2 標準，token 通常在 access_token 欄位
      token.value = response.data.access_token;
      localStorage.setItem('token', token.value);

      // 登入成功後，馬上獲取使用者資訊
      await fetchUser();

      router.push('/dashboard');
    } catch (error) {
      console.error('登入失敗:', error);
      throw error;
    }
  }

  // UPDATED: 根據 OpenAPI 規格更新註冊邏輯
  async function register(userInfo) {
    try {
      // API 需要 email, username, password
      await apiClient.post('/api/v1/auth/register', userInfo);
      // 註冊成功後，引導使用者去登入頁面
      alert('註冊成功！請使用您的帳號密碼登入。');
      router.push('/login');
    } catch (error) {
      console.error('註冊失敗:', error);
      throw error;
    }
  }

  // UPDATED: 根據 OpenAPI 規格更新登出邏輯
  async function logout() {
    try {
        // 先呼叫後端登出 API
        await apiClient.post('/api/v1/auth/logout');
    } catch (error) {
        console.error("呼叫登出 API 失敗:", error);
    } finally {
        // 無論後端是否成功，前端都清除使用者資料並跳轉
        token.value = null;
        user.value = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        router.push('/login');
    }
  }

  return { token, user, isAuthenticated, userRole, login, register, logout, fetchUser };
});