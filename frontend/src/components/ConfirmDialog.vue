<template>
    <v-dialog v-model="dialog" max-width="480px" persistent>
        <v-card class="confirm-card elevation-12" :loading="loading">
            <!-- 頂部裝飾 -->
            <div class="card-header-decoration"></div>

            <!-- 標題 -->
            <v-card-title class="confirm-title py-6">
                <div class="title-content">
                    <v-icon class="title-icon mr-3" color="blue-lighten-1">mdi-help-circle-outline</v-icon>
                    <span class="title-text">{{ title }}</span>
                </div>
            </v-card-title>

            <!-- 內容 -->
            <v-card-text class="confirm-content">
                <div class="message" v-html="message" />
            </v-card-text>

            <!-- 動作區塊 -->
            <v-card-actions class="confirm-actions py-5">
                <v-spacer></v-spacer>
                <v-btn class="cancel-btn" variant="outlined" @click="closeDialog" :disabled="loading">
                    <v-icon class="mr-2">mdi-close-circle-outline</v-icon>
                    {{ cancelText }}
                </v-btn>
                <v-btn class="confirm-btn" :color="confirmColor" @click="confirmAction" :disabled="loading">
                    <v-icon class="mr-2">mdi-check-decagram</v-icon>
                    {{ confirmText }}
                </v-btn>
            </v-card-actions>

            <!-- 底部波浪 -->
            <div class="card-footer-wave"></div>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { defineModel, defineProps, defineEmits } from 'vue';

// v-model 控制開關
const dialog = defineModel({ type: Boolean });

// props
const props = defineProps({
    title: { type: String, default: '確認操作' },
    message: { type: String, required: true },
    confirmText: { type: String, default: '確認' },
    cancelText: { type: String, default: '取消' },
    confirmColor: { type: String, default: 'primary' },
    loading: { type: Boolean, default: false }
});

const emit = defineEmits(['confirm']);

function closeDialog() {
    if (props.loading) return;
    dialog.value = false;
}

function confirmAction() {
    if (props.loading) return;
    emit('confirm');
    closeDialog();
}
</script>

<style scoped>
/*********************************
  *  共用漸層與邊框設定            *
  *********************************/
.confirm-card {
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
.confirm-title {
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
.confirm-content {
    padding: 1.75rem 2rem;
}

.message {
    color: #01579b;
    font-weight: 500;
    line-height: 1.5;
}

/*********************************
  *  按鈕                          *
  *********************************/
.confirm-actions {
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

.confirm-btn {
    border-radius: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.confirm-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(33, 150, 243, 0.35);
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