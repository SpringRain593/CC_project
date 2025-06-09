<template>
    <v-dialog v-model="dialog" max-width="550px" persistent>
        <v-card class="rename-card elevation-12" :loading="loading">
            <!-- 頂部裝飾 -->
            <div class="card-header-decoration"></div>

            <!-- 標題 -->
            <v-card-title class="rename-title py-6">
                <div class="title-content">
                    <v-icon class="title-icon mr-3" color="blue-lighten-1">mdi-file-edit</v-icon>
                    <span class="title-text">✏️ 重新命名作戰檔案</span>
                </div>
            </v-card-title>

            <!-- 內容 -->
            <v-card-text class="rename-content">
                <v-form @submit.prevent="save">
                    <!-- 目前檔名 -->
                    <div class="current-name-section">
                        <span class="current-name-label">目前檔案名稱 :</span>
                        <span class="current-name-value">{{ props.currentFilename }}</span>
                    </div>

                    <!-- 新檔名輸入 -->
                    <v-text-field v-model="newFilename" label="新的檔案名稱"
                        :rules="[rules.required, rules.noSpaces, rules.validFilename]" variant="outlined"
                        color="blue-lighten-1" prepend-inner-icon="mdi-pencil-box-outline" class="ocean-input mt-4"
                        autofocus @keydown.enter="save">
                        <template #prepend-inner>
                            <v-icon color="blue-lighten-2">mdi-pencil</v-icon>
                        </template>
                    </v-text-field>
                </v-form>

                <!-- 錯誤提示 -->
                <v-alert v-if="props.errorMessage" type="error" density="compact" class="custom-alert mt-3"
                    variant="tonal">
                    {{ props.errorMessage }}
                </v-alert>
            </v-card-text>

            <!-- 動作區塊 -->
            <v-card-actions class="rename-actions py-5">
                <v-spacer></v-spacer>
                <v-btn class="cancel-btn" variant="outlined" @click="closeDialog" :disabled="loading">
                    <v-icon class="mr-2">mdi-close-circle-outline</v-icon>
                    取消
                </v-btn>
                <v-btn class="save-btn" @click="save" :loading="loading" :disabled="!isValid">
                    <v-icon class="mr-2">mdi-content-save-edit</v-icon>
                    儲存變更
                </v-btn>
            </v-card-actions>

            <!-- 底部裝飾波浪 -->
            <div class="card-footer-wave"></div>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { ref, watch, defineModel, defineProps, defineEmits, computed } from 'vue';

const dialog = defineModel({ type: Boolean });

const props = defineProps({
    currentFilename: { type: String, required: true },
    loading: { type: Boolean, default: false },
    errorMessage: { type: String, default: '' }
});

const emit = defineEmits(['save']);
const newFilename = ref('');

const rules = {
    required: v => !!v || '檔案名稱不可為空.',
    noSpaces: v => !/\s/.test(v) || '檔案名稱不可包含空格.',
    validFilename: v => !(/[\\/:*?"<>|]/.test(v)) || '檔案名稱包含無效字元.'
};

// 表單有效性
const isValid = computed(() =>
    newFilename.value &&
    !rules.required(newFilename.value) &&
    !rules.noSpaces(newFilename.value) &&
    !rules.validFilename(newFilename.value)
);

watch(dialog, val => {
    if (val) newFilename.value = props.currentFilename;
});

function closeDialog() {
    if (props.loading) return;
    dialog.value = false;
}

function save() {
    if (props.loading || !isValid.value) return;
    emit('save', newFilename.value);
}
</script>

<style scoped>
/*********************************
  *  共用漸層與邊框設定            *
  *********************************/
.rename-card {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.96) 0%, rgba(240, 248, 255, 0.92) 100%);
    border-radius: 22px;
    border: 2px solid rgba(33, 150, 243, 0.28);
    overflow: hidden;
    backdrop-filter: blur(10px);
}

/*********************************
  *  頂部與底部裝飾              *
  *********************************/
.card-header-decoration {
    height: 4px;
    background: linear-gradient(90deg, #2196f3 0%, #03a9f4 50%, #00bcd4 100%);
    animation: shimmer 2.5s infinite;
}

.card-footer-wave {
    height: 18px;
    position: relative;
    background: linear-gradient(90deg, #e1f5fe 0%, #b3e5fc 50%, #e1f5fe 100%);
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
    animation: wave-slide 4s ease-in-out infinite;
}

/*********************************
  *  標題                          *
  *********************************/
.rename-title {
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

/*********************************
  *  內容                          *
  *********************************/
.rename-content {
    padding: 1.75rem 2rem;
}

.current-name-section {
    background: rgba(227, 242, 253, 0.55);
    border-radius: 10px;
    border: 1px solid rgba(33, 150, 243, 0.18);
    padding: 0.8rem 1rem;
}

.current-name-label {
    color: #0288d1;
    font-weight: 500;
    margin-right: .5rem;
}

.current-name-value {
    color: #01579b;
    font-weight: 600;
    word-break: break-all;
}

/*********************************
  *  表單輸入                      *
  *********************************/
.ocean-input :deep(.v-field) {
    background: rgba(227, 242, 253, 0.8);
    border-radius: 12px;
    border: 2px solid rgba(33, 150, 243, 0.2);
    transition: all .3s ease;
}

.ocean-input :deep(.v-field--focused) {
    border-color: #2196f3;
    background: rgba(227, 242, 253, 1);
    box-shadow: 0 4px 18px rgba(33, 150, 243, .22);
}

.ocean-input :deep(.v-field__input) {
    color: #01579b;
    font-weight: 500;
}

.ocean-input :deep(.v-label) {
    color: #0288d1;
    font-weight: 500;
}

/*********************************
  *  按鈕                          *
  *********************************/
.rename-actions {
    gap: 1rem;
}

.cancel-btn {
    color: #0288d1;
    border-color: rgba(33, 150, 243, 0.3);
    border-radius: 12px;
    font-weight: 500;
}

.cancel-btn:hover {
    background: rgba(33, 150, 243, 0.08);
}

.save-btn {
    background: linear-gradient(135deg, #2196f3 0%, #03a9f4 50%, #00bcd4 100%);
    color: #fff;
    border-radius: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.save-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(33, 150, 243, 0.35);
}

.save-btn:disabled {
    background: rgba(0, 0, 0, 0.12) !important;
    color: rgba(0, 0, 0, 0.26) !important;
}

/*********************************
  *  通用動畫                      *
  *********************************/
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
</style>