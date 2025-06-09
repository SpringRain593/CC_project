<template>
    <v-dialog v-model="dialog" max-width="600px" persistent>
        <v-card class="upload-card" :loading="isUploading">
            <div class="card-header-decoration"></div>

            <v-card-title class="upload-title">
                <div class="title-content">
                    <v-icon class="title-icon mr-3" color="blue-lighten-1">mdi-cloud-upload</v-icon>
                    <span class="title-text">📁 機密檔案上傳</span>
                </div>
            </v-card-title>

            <v-card-text class="upload-content">
                <div class="upload-zone" :class="{ 'drag-over': isDragOver, 'has-file': selectedFile }"
                    @drop.prevent="handleDrop" @dragover.prevent="handleDragOver" @dragleave="handleDragLeave">

                    <v-file-input v-model="selectedFile" class="file-input-overlay" variant="plain" prepend-icon=""
                        @change="handleFileSelect" />

                    <div v-if="!selectedFile" class="upload-hint">
                        <div class="hint-icon">☁️</div>
                        <p class="hint-text">點擊或拖曳檔案到此處</p>
                        <p class="hint-subtext">最大檔案大小: 100MB</p>
                    </div>

                    <div v-else class="file-preview">
                        <div class="preview-card">
                            <v-icon class="preview-icon" :color="getFileIconColor(getFileExtension(selectedFile.name))">
                                {{ getFileIcon(getFileExtension(selectedFile.name)) }}
                            </v-icon>
                            <div class="preview-info">
                                <div class="preview-name">{{ selectedFile.name }}</div>
                                <div class="preview-size">{{ formatBytes(selectedFile.size) }}</div>
                            </div>
                            <v-btn icon size="small" class="remove-btn" @click.stop="removeFile"
                                :disabled="isUploading">
                                <v-icon>mdi-close</v-icon>
                            </v-btn>
                        </div>
                    </div>
                </div>

                <v-alert v-if="errorMessage" type="error" density="compact" class="mt-4 custom-alert" variant="tonal">
                    {{ errorMessage }}
                </v-alert>

                <v-progress-linear v-if="isUploading" indeterminate color="blue-lighten-1"
                    class="mt-4"></v-progress-linear>
            </v-card-text>

            <v-card-actions class="upload-actions">
                <v-spacer></v-spacer>
                <v-btn class="cancel-btn" variant="outlined" @click="closeDialog" :disabled="isUploading">
                    <v-icon class="mr-2">mdi-close</v-icon>
                    取消
                </v-btn>
                <v-btn class="upload-btn" @click="handleUpload" :loading="isUploading" :disabled="!selectedFile">
                    <v-icon class="mr-2">mdi-rocket-launch</v-icon>
                    開始上傳
                </v-btn>
            </v-card-actions>

            <div class="card-footer-wave"></div>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { ref, defineEmits, defineModel } from 'vue';
import apiClient from '@/plugins/axios';

const dialog = defineModel({ type: Boolean });
const emit = defineEmits(['upload-success']);

const selectedFile = ref(null);
const isUploading = ref(false);
const errorMessage = ref('');
const isDragOver = ref(false);

function closeDialog() {
    if (isUploading.value) return;
    dialog.value = false;
    selectedFile.value = null;
    errorMessage.value = '';
    isDragOver.value = false;
}

function removeFile() {
    selectedFile.value = null;
    errorMessage.value = '';
}

function handleFileSelect() {
    errorMessage.value = '';
}

function handleDrop(e) {
    isDragOver.value = false;
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        selectedFile.value = files[0];
        errorMessage.value = '';
    }
}

function handleDragOver(e) {
    isDragOver.value = true;
}

function handleDragLeave() {
    isDragOver.value = false;
}

async function handleUpload() {
    if (!selectedFile.value) {
        errorMessage.value = '⚠️ 請先選擇一個檔案！';
        return;
    }

    // 檔案大小檢查 (100MB)
    if (selectedFile.value.size > 100 * 1024 * 1024) {
        errorMessage.value = '❌ 檔案大小超過100MB限制！';
        return;
    }

    isUploading.value = true;
    errorMessage.value = '';

    const formData = new FormData();
    formData.append('uploaded_file', selectedFile.value);

    try {
        await apiClient.post('/api/v1/files/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        emit('upload-success');
        alert('🎉 檔案上傳成功！已加入您的檔案庫。');
        closeDialog();

    } catch (error) {
        errorMessage.value = '❌ 上傳失敗，請檢查網路連線或稍後再試。';
        console.error('上傳錯誤:', error);
    } finally {
        isUploading.value = false;
    }
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function getFileExtension(filename) {
    return filename.split('.').pop().toLowerCase();
}

function getFileIcon(fileType) {
    const iconMap = {
        'pdf': 'mdi-file-pdf-box',
        'doc': 'mdi-file-word-box',
        'docx': 'mdi-file-word-box',
        'xls': 'mdi-file-excel-box',
        'xlsx': 'mdi-file-excel-box',
        'ppt': 'mdi-file-powerpoint-box',
        'pptx': 'mdi-file-powerpoint-box',
        'txt': 'mdi-file-document-outline',
        'jpg': 'mdi-file-image',
        'jpeg': 'mdi-file-image',
        'png': 'mdi-file-image',
        'gif': 'mdi-file-image',
        'mp4': 'mdi-file-video',
        'avi': 'mdi-file-video',
        'mp3': 'mdi-file-music',
        'wav': 'mdi-file-music',
        'zip': 'mdi-folder-zip',
        'rar': 'mdi-folder-zip',
    };
    return iconMap[fileType] || 'mdi-file-outline';
}

function getFileIconColor(fileType) {
    const colorMap = {
        'pdf': 'red-lighten-1',
        'doc': 'blue-lighten-1',
        'docx': 'blue-lighten-1',
        'xls': 'green-lighten-1',
        'xlsx': 'green-lighten-1',
        'ppt': 'orange-lighten-1',
        'pptx': 'orange-lighten-1',
        'txt': 'grey-lighten-1',
        'jpg': 'purple-lighten-1',
        'jpeg': 'purple-lighten-1',
        'png': 'purple-lighten-1',
        'gif': 'purple-lighten-1',
        'mp4': 'indigo-lighten-1',
        'avi': 'indigo-lighten-1',
        'mp3': 'pink-lighten-1',
        'wav': 'pink-lighten-1',
        'zip': 'amber-lighten-1',
        'rar': 'amber-lighten-1',
    };
    return colorMap[fileType] || 'blue-grey-lighten-1';
}
</script>

<style scoped>
/* 將 v-file-input 整個墊到底，完整覆蓋 upload-zone */
.file-input-overlay {
    position: absolute;
    inset: 0;
    /* top/right/bottom/left = 0 */
    opacity: 0;
    /* 完全透明 */
    cursor: pointer;
    /* 仍顯示可點擊 */
    z-index: 10;
    /* 確保在預覽卡片之上 */
}

.file-input-overlay :deep(.v-field) {
    height: 100%;
    border: none;
}

.upload-card {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(240, 248, 255, 0.9) 100%);
    border-radius: 20px;
    border: 2px solid rgba(33, 150, 243, 0.3);
    overflow: hidden;
    backdrop-filter: blur(10px);
}

.card-header-decoration {
    height: 4px;
    background: linear-gradient(90deg, #2196f3 0%, #03a9f4 50%, #00bcd4 100%);
    animation: shimmer 2s infinite;
}

.upload-title {
    padding: 1.5rem 2rem 1rem;
    background: linear-gradient(135deg, #e1f5fe 0%, #b3e5fc 100%);
}

.title-content {
    display: flex;
    align-items: center;
    justify-content: center;
}

.title-icon {
    font-size: 1.8rem;
}

.title-text {
    font-size: 1.4rem;
    font-weight: 600;
    color: #0277bd;
    letter-spacing: 0.5px;
}

.upload-content {
    padding: 2rem;
}

.upload-zone {
    position: relative;
    /* 讓子元素 absolute 以自己為基準 */
    border: 2px dashed rgba(33, 150, 243, 0.3);
    border-radius: 15px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
    background: rgba(227, 242, 253, 0.3);
    min-height: 200px;
    display: flex;
    /* 使用 flex 讓內容置中 */
    justify-content: center;
    align-items: center;
}

.upload-zone.drag-over {
    border-color: #2196f3;
    background: rgba(33, 150, 243, 0.1);
    transform: scale(1.02);
}

.upload-zone.has-file {
    border-style: solid;
    border-color: #4caf50;
    background: rgba(76, 175, 80, 0.1);
}

/* [修正2] 移除此處空的 .upload-hint 規則集 */

.hint-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.7;
}

.hint-text {
    color: #0288d1;
    font-weight: 500;
    margin: 0.5rem 0;
}

.hint-subtext {
    color: #0288d1;
    font-size: 0.9rem;
    opacity: 0.7;
    margin: 0;
}

.file-preview {
    width: 100%;
    /* 讓預覽卡片佔滿寬度 */
    z-index: 5;
    /* 確保在 input 下方，避免移除按鈕被遮擋 */
    position: relative;
}

.preview-card {
    display: flex;
    align-items: center;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 12px;
    border: 1px solid rgba(33, 150, 243, 0.2);
    backdrop-filter: blur(5px);
}

.preview-icon {
    font-size: 2.5rem;
    margin-right: 1rem;
}

.preview-info {
    flex: 1;
    text-align: left;
}

.preview-name {
    font-weight: 600;
    color: #0277bd;
    margin-bottom: 0.25rem;
    word-break: break-all;
}

.preview-size {
    color: #0288d1;
    font-size: 0.9rem;
    opacity: 0.8;
}

.remove-btn {
    background: rgba(244, 67, 54, 0.1);
    color: #f44336;
    /* 確保移除按鈕的 z-index 比覆蓋層高 */
    z-index: 15;
}

.remove-btn:hover {
    background: rgba(244, 67, 54, 0.2);
}

.custom-alert {
    background: rgba(255, 235, 238, 0.9);
    border: 1px solid rgba(244, 67, 54, 0.3);
    border-radius: 12px;
}

.upload-actions {
    padding: 1rem 2rem 1.5rem;
    gap: 1rem;
}

.cancel-btn {
    color: #0288d1;
    border-color: rgba(33, 150, 243, 0.3);
    border-radius: 12px;
    font-weight: 500;
}

.cancel-btn:hover {
    background: rgba(33, 150, 243, 0.1);
}

.upload-btn {
    background: linear-gradient(135deg, #2196f3 0%, #03a9f4 50%, #00bcd4 100%);
    color: white;
    border-radius: 12px;
    font-weight: 600;
    text-transform: none;
    letter-spacing: 0.5px;
}

.upload-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(33, 150, 243, 0.4);
}

.upload-btn:disabled {
    background: rgba(0, 0, 0, 0.12) !important;
    color: rgba(0, 0, 0, 0.26) !important;
}

.card-footer-wave {
    height: 15px;
    background: linear-gradient(90deg, #e1f5fe 0%, #b3e5fc 50%, #e1f5fe 100%);
    position: relative;
    overflow: hidden;
}

.card-footer-wave::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 200%;
    height: 100%;
    background: linear-gradient(90deg, transparent 0%, rgba(33, 150, 243, 0.3) 50%, transparent 100%);
    animation: wave-slide 3s ease-in-out infinite;
}

@keyframes shimmer {
    0% {
        background-position: -200% 0;
    }

    100% {
        background-position: 200% 0;
    }
}

@keyframes wave-slide {
    0% {
        transform: translateX(-50%);
    }

    100% {
        transform: translateX(0);
    }
}

/* 響應式設計 */
@media (max-width: 600px) {
    .upload-content {
        padding: 1.5rem;
    }

    .upload-zone {
        padding: 1.5rem;
        min-eta: 150px;
    }

    .title-text {
        font-size: 1.2rem;
    }

    .hint-icon {
        font-size: 2.5rem;
    }

    .preview-card {
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }

    .preview-icon {
        margin-right: 0;
    }
}
</style>