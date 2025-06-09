<template>
    <div class="dashboard-container">
        <!-- 強制背景層 -->
        <div class="force-background"></div>

        <!-- 背景動畫海浪 -->
        <div class="ocean-bg">
            <div class="wave wave1"></div>
            <div class="wave wave2"></div>
            <div class="wave wave3"></div>
        </div>

        <!-- 浮雲效果 -->
        <div class="clouds">
            <div class="cloud cloud1"></div>
            <div class="cloud cloud2"></div>
            <div class="cloud cloud3"></div>
        </div>

        <!-- 主要內容 -->
        <div class="main-content">
            <!-- 頂部標題區域 -->
            <div class="header-section">
                <div class="title-card">
                    <div class="title-decoration">
                        <div class="anchor-icon">⚓</div>
                        <div class="title-content">
                            <h1 v-if="authStore.userRole === 'admin'" class="main-title">
                                🌟 艦隊司令部檔案庫 (總司令)
                            </h1>
                            <h1 v-else class="main-title">
                                📁 指揮官專屬檔案庫
                            </h1>
                            <div class="subtitle">資源管理 · 戰略部署 · 機密檔案</div>
                        </div>
                        <div class="compass-icon">🧭</div>
                    </div>
                </div>

                <div class="action-buttons">
                    <v-btn v-if="authStore.userRole === 'admin'" class="admin-btn mr-4"
                        @click="$router.push('/admin/users')" prepend-icon="mdi-account-group" elevation="4">
                        <v-icon class="mr-2">mdi-shield-crown</v-icon>
                        艦隊管理
                    </v-btn>
                    <v-btn class="upload-btn" @click="uploadDialog = true" prepend-icon="mdi-upload" elevation="4">
                        <v-icon class="mr-2">mdi-file-upload</v-icon>
                        機密上傳
                    </v-btn>
                </div>
            </div>

            <!-- 檔案列表卡片 -->
            <div class="file-list-card">
                <div class="card-header">
                    <h3 class="card-title">
                        <v-icon class="mr-2" color="blue-lighten-1">mdi-folder-multiple</v-icon>
                        檔案總覽
                    </h3>
                    <div class="file-count-badge" v-if="files.length > 0">
                        {{ files.length }} 個檔案
                    </div>
                </div>

                <FileList :files="files" :loading="isLoading" :user-role="authStore.userRole"
                    @delete-file="promptDeleteFile" @rename-file="promptRenameFile"
                    @download-file="handleDownloadFile" />
            </div>
        </div>

        <!-- 對話框 -->
        <UploadDialog v-model="uploadDialog" @upload-success="fetchFiles" />
        <ConfirmDialog v-model="isConfirmDialogOpen" title="🚨 確認刪除作戰檔案" :message="confirmDialogMessage"
            confirm-text="執行刪除" confirm-color="error" @confirm="executeDelete" />
        <RenameDialog v-model="isRenameDialogOpen" :current-filename="fileToRename ? fileToRename.filename : ''"
            :loading="isRenaming" :error-message="renameError" @save="executeRename" />

        <!-- 浮動元素 -->
        <div class="floating-elements">
            <div class="seagull seagull1">🕊️</div>
            <div class="seagull seagull2">🕊️</div>
            <div class="ship-icon">⛵</div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import apiClient from '@/plugins/axios';
import FileList from '@/components/FileList.vue';
import UploadDialog from '@/components/UploadDialog.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import RenameDialog from '@/components/RenameDialog.vue';

const authStore = useAuthStore();
const files = ref([]);
const isLoading = ref(false);
const uploadDialog = ref(false);
const isConfirmDialogOpen = ref(false);
const fileToDelete = ref(null);
const confirmDialogMessage = ref('');
const isRenameDialogOpen = ref(false);
const fileToRename = ref(null);
const isRenaming = ref(false);
const renameError = ref('');

onMounted(() => {
    fetchFiles();
});

async function fetchFiles() {
    isLoading.value = true;
    try {
        let response;
        if (authStore.userRole === 'admin') {
            response = await apiClient.get('/api/v1/files/all');
        } else {
            response = await apiClient.get('/api/v1/files/');
        }
        files.value = response.data;
    } catch (error) {
        console.error('無法獲取檔案列表:', error);
        alert('📡 通訊中斷！無法載入檔案庫，請稍後再試。');
    } finally {
        isLoading.value = false;
    }
}

function promptDeleteFile(file) {
    fileToDelete.value = file;
    confirmDialogMessage.value = `您確定要永久銷毀檔案 "<b>${file.filename}</b>" 嗎？<br>⚠️ 此作戰檔案將無法復原！`;
    isConfirmDialogOpen.value = true;
}

async function executeDelete() {
    if (!fileToDelete.value) return;
    try {
        await apiClient.delete(`/api/v1/files/${fileToDelete.value.id}`);
        alert(`🗑️ 作戰檔案 "${fileToDelete.value.filename}" 已成功銷毀。`);
        fetchFiles();
    } catch (error) {
        console.error('刪除檔案失敗:', error);
        alert('❌ 檔案銷毀失敗，請稍後再試。');
    } finally {
        fileToDelete.value = null;
    }
}

function promptRenameFile(file) {
    fileToRename.value = file;
    renameError.value = '';
    isRenameDialogOpen.value = true;
}

async function executeRename(newFilename) {
    if (!fileToRename.value || !newFilename) return;
    isRenaming.value = true;
    renameError.value = '';
    try {
        await apiClient.patch(`/api/v1/files/${fileToRename.value.id}/rename`, {
            new_filename: newFilename
        });
        isRenameDialogOpen.value = false;
        alert('✏️ 檔案重新命名成功！');
        fetchFiles();
    } catch (error) {
        console.error('重新命名失敗:', error);
        renameError.value = error.response?.data?.detail || '重新命名時發生錯誤，請稍後再試。';
    } finally {
        isRenaming.value = false;
    }
}

async function handleDownloadFile(file) {
    alert(`📥 正在準備下載 ${file.filename}，請稍候...`);
    try {
        const response = await apiClient.post(`/api/v1/files/${file.id}/generate-share-link`);
        const link = document.createElement('a');
        link.href = response.data.url;
        link.setAttribute('download', response.data.filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (error) {
        console.error('準備下載連結失敗:', error);
        alert('❌ 無法下載檔案，請稍後再試。');
    }
}
</script>

<style scoped>
.dashboard-container {
    min-height: 100vh;
    position: relative;
    overflow-x: hidden;
    padding: 1rem;
}

.force-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: linear-gradient(180deg, #e3f2fd 0%, #81d4fa 30%, #4fc3f7 70%, #29b6f6 100%);
    z-index: -1;
}

/* 海洋背景動畫 */
.ocean-bg {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 200px;
    overflow: hidden;
    z-index: 0;
}

.wave {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 200%;
    height: 100px;
    background: linear-gradient(180deg, transparent 0%, rgba(255, 255, 255, 0.2) 100%);
    border-radius: 50%;
    animation: wave-animation 8s ease-in-out infinite;
}

.wave1 {
    animation-delay: 0s;
    opacity: 0.6;
}

.wave2 {
    animation-delay: 2.5s;
    opacity: 0.4;
    height: 80px;
}

.wave3 {
    animation-delay: 5s;
    opacity: 0.3;
    height: 60px;
}

/* 浮雲效果 */
.clouds {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
}

.cloud {
    position: absolute;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 50px;
    animation: float-cloud 30s infinite linear;
}

.cloud::before,
.cloud::after {
    content: '';
    position: absolute;
    background: rgba(255, 255, 255, 0.5);
    border-radius: 50%;
}

.cloud1 {
    width: 60px;
    height: 30px;
    top: 10%;
    left: -80px;
    animation-duration: 35s;
}

.cloud2 {
    width: 80px;
    height: 40px;
    top: 25%;
    left: -100px;
    animation-duration: 40s;
    animation-delay: 15s;
}

.cloud3 {
    width: 50px;
    height: 25px;
    top: 40%;
    left: -60px;
    animation-duration: 32s;
    animation-delay: 25s;
}

.main-content {
    position: relative;
    z-index: 2;
    max-width: 1200px;
    margin: 0 auto;
}

/* 標題區域 */
.header-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    gap: 1rem;
}

.title-card {
    flex: 1;
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.9) 0%, rgba(240, 248, 255, 0.8) 100%);
    border-radius: 20px;
    padding: 1.5rem 2rem;
    border: 2px solid rgba(33, 150, 243, 0.3);
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.title-decoration {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.anchor-icon,
.compass-icon {
    font-size: 2rem;
    opacity: 0.7;
    animation: gentle-bounce 4s ease-in-out infinite;
}

.compass-icon {
    animation-delay: 2s;
}

.title-content {
    text-align: center;
    flex: 1;
}

.main-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #0277bd;
    margin: 0;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    letter-spacing: 1px;
}

.subtitle {
    color: #0288d1;
    font-weight: 500;
    margin-top: 0.5rem;
    font-size: 0.95rem;
    opacity: 0.8;
}

.action-buttons {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.admin-btn {
    background: linear-gradient(135deg, #7b1fa2 0%, #9c27b0 50%, #e91e63 100%);
    color: white;
    border-radius: 15px;
    height: 48px;
    font-weight: 600;
    text-transform: none;
    letter-spacing: 0.5px;
}

.admin-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(123, 31, 162, 0.4);
}

.upload-btn {
    background: linear-gradient(135deg, #2196f3 0%, #03a9f4 50%, #00bcd4 100%);
    color: white;
    border-radius: 15px;
    height: 48px;
    font-weight: 600;
    text-transform: none;
    letter-spacing: 0.5px;
}

.upload-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(33, 150, 243, 0.4);
}

/* 檔案列表卡片 */
.file-list-card {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(240, 248, 255, 0.9) 100%);
    border-radius: 20px;
    border: 2px solid rgba(33, 150, 243, 0.3);
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem;
    background: linear-gradient(135deg, #e1f5fe 0%, #b3e5fc 100%);
    border-bottom: 1px solid rgba(33, 150, 243, 0.2);
}

.card-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: #0277bd;
    margin: 0;
    display: flex;
    align-items: center;
}

.file-count-badge {
    background: linear-gradient(135deg, #2196f3, #03a9f4);
    color: white;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
}

/* 浮動元素 */
.floating-elements {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 1;
}

.seagull {
    position: absolute;
    font-size: 1.2rem;
    animation: fly 20s infinite linear;
    opacity: 0.8;
}

.seagull1 {
    top: 15%;
    left: -50px;
    animation-duration: 25s;
}

.seagull2 {
    top: 30%;
    left: -50px;
    animation-duration: 30s;
    animation-delay: 12s;
}

.ship-icon {
    position: absolute;
    bottom: 150px;
    right: -50px;
    font-size: 1.8rem;
    animation: sail 25s infinite linear;
    opacity: 0.6;
}

/* 動畫定義 */
@keyframes wave-animation {

    0%,
    100% {
        transform: translateX(0) translateY(0);
    }

    50% {
        transform: translateX(-25%) translateY(-15px);
    }
}

@keyframes float-cloud {
    from {
        transform: translateX(-100px);
    }

    to {
        transform: translateX(calc(100vw + 100px));
    }
}

@keyframes gentle-bounce {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-8px);
    }
}

@keyframes fly {
    from {
        transform: translateX(-50px) translateY(0);
    }

    to {
        transform: translateX(calc(100vw + 50px)) translateY(-30px);
    }
}

@keyframes sail {
    from {
        transform: translateX(50px);
    }

    to {
        transform: translateX(calc(-100vw - 50px));
    }
}

/* 響應式設計 */
@media (max-width: 768px) {
    .header-section {
        flex-direction: column;
        gap: 1rem;
    }

    .action-buttons {
        width: 100%;
        justify-content: center;
    }

    .title-card {
        padding: 1rem 1.5rem;
    }

    .main-title {
        font-size: 1.4rem;
    }

    .anchor-icon,
    .compass-icon {
        font-size: 1.5rem;
    }

    .card-header {
        padding: 1rem 1.5rem;
        flex-direction: column;
        gap: 0.5rem;
    }

    .admin-btn,
    .upload-btn {
        width: 100%;
        max-width: 200px;
    }
}

@media (max-width: 480px) {
    .dashboard-container {
        padding: 0.5rem;
    }

    .title-decoration {
        flex-direction: column;
        gap: 1rem;
    }

    .main-title {
        font-size: 1.2rem;
    }

    .action-buttons {
        flex-direction: column;
        width: 100%;
    }

    .admin-btn,
    .upload-btn {
        width: 100%;
    }
}
</style>