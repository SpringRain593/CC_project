<template>
    <div class="file-list-container">
        <v-data-table :headers="headers" :items="files" :loading="loading" item-value="id"
            class="ocean-table elevation-0" :loading-text="'🌊 資料載入中...'" :no-data-text="''">
            <!-- 檔案名稱欄位 -->
            <template v-slot:item.filename="{ item }">
                <div class="filename-cell">
                    <v-icon class="file-icon mr-2" :color="getFileIconColor(item.file_type)">
                        {{ getFileIcon(item.file_type) }}
                    </v-icon>
                    <span class="filename-text">{{ item.filename }}</span>
                </div>
            </template>

            <!-- 檔案大小欄位 -->
            <template v-slot:item.size="{ item }">
                <v-chip :color="getSizeChipColor(item.size)" size="small" variant="tonal" class="size-chip">
                    {{ formatBytes(item.size) }}
                </v-chip>
            </template>

            <!-- 檔案類型欄位 -->
            <template v-slot:item.file_type="{ item }">
                <v-chip :color="getTypeChipColor(item.file_type)" size="small" variant="outlined" class="type-chip">
                    {{ item.file_type.toUpperCase() }}
                </v-chip>
            </template>

            <!-- 上傳時間欄位 -->
            <template v-slot:item.uploaded_at="{ item }">
                <div class="date-cell">
                    <v-icon size="small" class="mr-1" color="blue-lighten-2">mdi-clock-outline</v-icon>
                    <span class="date-text">{{ formatDate(item.uploaded_at) }}</span>
                </div>
            </template>

            <!-- 操作按鈕欄位 -->
            <template v-slot:item.actions="{ item }">
                <div class="action-buttons">
                    <v-tooltip text="下載檔案" location="top">
                        <template v-slot:activator="{ props }">
                            <v-btn v-bind="props" icon size="small" class="action-btn download-btn"
                                @click="emitDownload(item)">
                                <v-icon size="18">mdi-download</v-icon>
                            </v-btn>
                        </template>
                    </v-tooltip>

                    <template v-if="userRole === 'admin' || userRole === 'manager'">
                        <v-tooltip text="重新命名" location="top">
                            <template v-slot:activator="{ props }">
                                <v-btn v-bind="props" icon size="small" class="action-btn rename-btn ml-1"
                                    @click="emitRename(item)">
                                    <v-icon size="18">mdi-pencil</v-icon>
                                </v-btn>
                            </template>
                        </v-tooltip>

                        <v-tooltip text="刪除檔案" location="top">
                            <template v-slot:activator="{ props }">
                                <v-btn v-bind="props" icon size="small" class="action-btn delete-btn ml-1"
                                    @click="emitDelete(item)">
                                    <v-icon size="18">mdi-delete</v-icon>
                                </v-btn>
                            </template>
                        </v-tooltip>
                    </template>
                </div>
            </template>

            <!-- 空資料狀態 -->
            <template v-slot:no-data>
                <div class="empty-state">
                    <div class="empty-icon">📂</div>
                    <h3 class="empty-title">檔案庫暫時空無一物</h3>
                    <p class="empty-subtitle">
                        <template v-if="userRole === 'admin'">
                            🌟 總司令，所有艦隊的檔案庫都是空的
                        </template>
                        <template v-else>
                            ⚓ 指揮官，您的個人檔案庫還沒有任何檔案
                        </template>
                    </p>
                    <p class="empty-hint">點擊上方的「機密上傳」按鈕開始添加檔案吧！</p>
                </div>
            </template>

            <!-- 載入狀態 -->
            <template v-slot:loading>
                <div class="loading-state">
                    <div class="loading-waves">
                        <div class="wave-dot wave-dot-1"></div>
                        <div class="wave-dot wave-dot-2"></div>
                        <div class="wave-dot wave-dot-3"></div>
                    </div>
                    <p class="loading-text">🌊 檔案資料載入中...</p>
                </div>
            </template>
        </v-data-table>
    </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
    files: {
        type: Array,
        required: true,
        default: () => []
    },
    loading: {
        type: Boolean,
        default: false
    },
    userRole: {
        type: String,
        required: true
    }
});

const emit = defineEmits(['download-file', 'rename-file', 'delete-file']);

const headers = [
    { title: '📋 檔案名稱', key: 'filename', sortable: true, width: '35%' },
    { title: '📏 檔案大小', key: 'size', sortable: true, width: '15%' },
    { title: '🏷️ 檔案類型', key: 'file_type', sortable: true, width: '15%' },
    { title: '⏰ 上傳時間', key: 'uploaded_at', sortable: true, width: '20%' },
    { title: '⚙️ 操作', key: 'actions', sortable: false, width: '15%' },
];

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-TW') + ' ' + date.toLocaleTimeString('zh-TW', {
        hour: '2-digit',
        minute: '2-digit'
    });
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
    return iconMap[fileType.toLowerCase()] || 'mdi-file-outline';
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
    return colorMap[fileType.toLowerCase()] || 'blue-grey-lighten-1';
}

function getSizeChipColor(size) {
    if (size < 1024 * 1024) return 'green'; // < 1MB
    if (size < 10 * 1024 * 1024) return 'blue'; // < 10MB
    if (size < 100 * 1024 * 1024) return 'orange'; // < 100MB
    return 'red'; // >= 100MB
}

function getTypeChipColor(fileType) {
    const type = fileType.toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif'].includes(type)) return 'purple';
    if (['mp4', 'avi', 'mov'].includes(type)) return 'indigo';
    if (['mp3', 'wav', 'flac'].includes(type)) return 'pink';
    if (['pdf'].includes(type)) return 'red';
    if (['doc', 'docx'].includes(type)) return 'blue';
    if (['xls', 'xlsx'].includes(type)) return 'green';
    if (['zip', 'rar', '7z'].includes(type)) return 'amber';
    return 'blue-grey';
}

function emitDownload(file) {
    emit('download-file', file);
}

function emitRename(file) {
    emit('rename-file', file);
}

function emitDelete(file) {
    emit('delete-file', file);
}
</script>

<style scoped>
.file-list-container {
    padding: 1rem;
}

.ocean-table {
    background: transparent !important;
}

.ocean-table :deep(.v-table) {
    background: transparent;
    border-radius: 15px;
    overflow: hidden;
}

.ocean-table :deep(.v-table__wrapper) {
    border-radius: 15px;
    border: 1px solid rgba(33, 150, 243, 0.2);
}

.ocean-table :deep(thead) {
    background: linear-gradient(135deg, #e1f5fe 0%, #b3e5fc 100%);
}

.ocean-table :deep(thead th) {
    background: transparent !important;
    color: #0277bd !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 1rem !important;
    border-bottom: 2px solid rgba(33, 150, 243, 0.3) !important;
}

.ocean-table :deep(tbody tr) {
    background: rgba(255, 255, 255, 0.8);
    transition: all 0.3s ease;
}

.ocean-table :deep(tbody tr:hover) {
    background: rgba(227, 242, 253, 0.9) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.1);
}

.ocean-table :deep(tbody tr:nth-child(even)) {
    background: rgba(240, 248, 255, 0.8);
}

.ocean-table :deep(tbody td) {
    padding: 1rem !important;
    border-bottom: 1px solid rgba(33, 150, 243, 0.1) !important;
}

/* 檔案名稱樣式 */
.filename-cell {
    display: flex;
    align-items: center;
}

.filename-text {
    color: #01579b;
    font-weight: 500;
    word-break: break-word;
}

.file-icon {
    flex-shrink: 0;
}

/* 大小和類型晶片 */
.size-chip,
.type-chip {
    font-weight: 600;
    font-size: 0.75rem;
}

/* 日期欄位 */
.date-cell {
    display: flex;
    align-items: center;
}

.date-text {
    color: #0288d1;
    font-size: 0.85rem;
}

/* 操作按鈕 */
.action-buttons {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.action-btn {
    transition: all 0.3s ease;
    border-radius: 8px;
}

.download-btn {
    background: linear-gradient(135deg, #4caf50, #66bb6a);
    color: white;
}

.download-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
}

.rename-btn {
    background: linear-gradient(135deg, #ff9800, #ffb74d);
    color: white;
}

.rename-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(255, 152, 0, 0.4);
}

.delete-btn {
    background: linear-gradient(135deg, #f44336, #ef5350);
    color: white;
}

.delete-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(244, 67, 54, 0.4);
}

/* 空狀態樣式 */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    color: #0288d1;
}

.empty-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.7;
}

.empty-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #0277bd;
}

.empty-subtitle {
    font-size: 1rem;
    margin-bottom: 0.5rem;
    opacity: 0.8;
}

.empty-hint {
    font-size: 0.9rem;
    opacity: 0.6;
    font-style: italic;
}

/* 載入狀態樣式 */
.loading-state {
    text-align: center;
    padding: 2rem;
}

.loading-waves {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.wave-dot {
    width: 12px;
    height: 12px;
    background: linear-gradient(135deg, #2196f3, #03a9f4);
    border-radius: 50%;
    animation: wave-bounce 1.4s ease-in-out infinite;
}

.wave-dot-1 {
    animation-delay: 0s;
}

.wave-dot-2 {
    animation-delay: 0.2s;
}

.wave-dot-3 {
    animation-delay: 0.4s;
}

.loading-text {
    color: #0288d1;
    font-weight: 500;
    margin: 0;
}

@keyframes wave-bounce {

    0%,
    80%,
    100% {
        transform: scale(0.8);
        opacity: 0.5;
    }

    40% {
        transform: scale(1.2);
        opacity: 1;
    }
}

/* 響應式設計 */
@media (max-width: 768px) {

    .ocean-table :deep(thead th),
    .ocean-table :deep(tbody td) {
        padding: 0.5rem !important;
        font-size: 0.8rem !important;
    }

    .filename-text {
        font-size: 0.85rem;
    }

    .action-buttons {
        flex-direction: column;
        gap: 0.25rem;
    }

    .empty-state {
        padding: 2rem 1rem;
    }

    .empty-icon {
        font-size: 3rem;
    }

    .empty-title {
        font-size: 1.2rem;
    }
}
/* 1️⃣ 讓欄位依內容自動調寬 */
.ocean-table :deep(.v-table) {
    table-layout: auto !important;
}

/* 2️⃣ 檔名欄固定最小寬度，並加省略號 */
.filename-cell {
    min-width: 180px;
}

/* 依需求調整 */
.filename-text {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    word-break: normal;
    /* 避免 break-all 疊加 */
}

/* 3️⃣ 行動裝置仍保持可捲動 */
.file-list-container {
    overflow-x: auto;
}
</style>