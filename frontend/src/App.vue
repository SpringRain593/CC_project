<template>
  <v-app>
    <v-layout>
      <v-app-bar color="primary" density="compact">
        <v-app-bar-title>雲端檔案系統</v-app-bar-title>
        <v-spacer></v-spacer>
        <v-btn v-if="authStore.isAuthenticated" @click="handleLogout">
          登出
        </v-btn>
      </v-app-bar>

      <v-main>
        <v-container>
          <router-view />
        </v-container>
      </v-main>
    </v-layout>
  </v-app>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();

function handleLogout() {
  authStore.logout();
}
</script>

<style scoped>
/* 您可以在這裡添加一些全域或佈局相關的樣式 */
</style>