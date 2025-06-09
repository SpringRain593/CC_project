<template>
    <v-dialog v-model="dialog" max-width="500px" persistent>
        <v-card class="reset-card" :loading="loading">
            <div class="card-header-decoration"></div>

            <v-card-title class="reset-title">
                <v-icon class="title-icon mr-3" color="amber-darken-2">mdi-lock-reset</v-icon>
                <span class="title-text">重設密碼</span>
            </v-card-title>

            <v-card-text class="reset-content">
                <p class="mb-6 text-center text-medium-emphasis">
                    您正在為使用者
                    <span class="username-highlight">{{ username }}</span>
                    設定新的密碼。
                </p>

                <v-form ref="form" @submit.prevent="save">
                    <v-text-field v-model="newPassword" label="新的密碼" variant="outlined" color="amber-darken-2"
                        :type="isPasswordVisible ? 'text' : 'password'"
                        :append-inner-icon="isPasswordVisible ? 'mdi-eye' : 'mdi-eye-off'"
                        prepend-inner-icon="mdi-key-variant" :rules="[rules.required, rules.minLength]"
                        @click:append-inner="isPasswordVisible = !isPasswordVisible"></v-text-field>
                </v-form>

                <v-alert v-if="errorMessage" type="error" density="compact" class="mt-2" variant="tonal">
                    {{ errorMessage }}
                </v-alert>

            </v-card-text>

            <v-card-actions class="reset-actions">
                <v-spacer></v-spacer>
                <v-btn class="cancel-btn" variant="outlined" @click="closeDialog" :disabled="loading">
                    取消
                </v-btn>
                <v-btn class="confirm-btn" @click="save" :loading="loading">
                    <v-icon class="mr-2">mdi-check-circle-outline</v-icon>
                    確認重設
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { ref, watch, defineModel, defineProps, defineEmits } from 'vue';

const dialog = defineModel({ type: Boolean });
const props = defineProps({
    username: { type: String, default: '' },
    loading: Boolean,
    errorMessage: String,
});
const emit = defineEmits(['save']);

const form = ref(null);
const newPassword = ref('');
const isPasswordVisible = ref(false);

const rules = {
    required: v => !!v || '此欄位為必填.',
    minLength: v => (v && v.length >= 6) || '密碼長度至少需 6 個字元.',
};

watch(dialog, (isOpen) => {
    if (isOpen) {
        newPassword.value = '';
        isPasswordVisible.value = false;
        // 重設表單的驗證狀態
        form.value?.resetValidation();
    }
});

function closeDialog() {
    if (props.loading) return;
    dialog.value = false;
}

async function save() {
    const { valid } = await form.value.validate();
    if (valid) {
        emit('save', newPassword.value);
    }
}
</script>

<style scoped>
.reset-card {
    border-radius: 16px;
    border: 1px solid rgba(255, 179, 0, 0.3);
    overflow: hidden;
    background: #FFFCF5;
    /* 淡米色背景 */
}

.card-header-decoration {
    height: 4px;
    background: linear-gradient(90deg, #FFB300 0%, #FFC107 50%, #FFCA28 100%);
}

.reset-title {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1.5rem 1rem;
    background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
}

.title-icon {
    font-size: 1.8rem;
}

.title-text {
    font-size: 1.4rem;
    font-weight: 600;
    color: #FF8F00;
}

.reset-content {
    padding: 2rem;
}

.username-highlight {
    font-weight: 700;
    color: #FFA000;
    background-color: #FFF3E0;
    padding: 2px 8px;
    border-radius: 6px;
}

.reset-actions {
    padding: 1rem 1.5rem 1.5rem;
    gap: 0.75rem;
}

.cancel-btn {
    color: #616161;
    border-color: #E0E0E0;
    font-weight: 500;
}

.confirm-btn {
    background: linear-gradient(135deg, #FFB300 0%, #FFC107 100%);
    color: white;
    font-weight: 600;
    text-transform: none;
    letter-spacing: 0.5px;
}

.confirm-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(255, 179, 0, 0.4);
}
</style>