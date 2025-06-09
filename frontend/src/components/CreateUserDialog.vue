<template>
    <v-dialog v-model="dialog" max-width="600px" persistent>
        <v-card :loading="loading">
            <v-card-title>建立新使用者</v-card-title>
            <v-card-text>
                <v-form ref="form">
                    <v-text-field v-model="userData.username" label="使用者名稱" :rules="[rules.required]"></v-text-field>
                    <v-text-field v-model="userData.email" label="電子郵件" type="email"
                        :rules="[rules.required, rules.email]"></v-text-field>
                    <v-text-field v-model="userData.password" label="密碼" type="password"
                        :rules="[rules.required, rules.minLength]"></v-text-field>
                    <v-select v-model="userData.role" :items="['user', 'manager', 'admin']" label="角色"
                        :rules="[rules.required]"></v-select>
                    <v-switch v-model="userData.is_active" label="啟用帳號" color="primary"></v-switch>
                </v-form>
                <div v-if="errorMessage" class="text-error text-caption mt-2">{{ errorMessage }}</div>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="grey-darken-1" variant="text" @click="closeDialog">取消</v-btn>
                <v-btn color="primary" variant="elevated" @click="save">建立</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { ref, watch, defineModel, defineProps, defineEmits } from 'vue';

const dialog = defineModel({ type: Boolean });
defineProps({
    loading: Boolean,
    errorMessage: String
});
const emit = defineEmits(['save']);

const form = ref(null);
const initialData = { username: '', email: '', password: '', role: 'user', is_active: true };
const userData = ref({ ...initialData });

const rules = {
    required: v => !!v || '此欄位為必填.',
    email: v => /.+@.+\..+/.test(v) || 'E-mail 格式不正確.',
    minLength: v => (v && v.length >= 6) || '密碼長度至少需 6 個字元.',
};

watch(dialog, (isOpen) => {
    if (isOpen) {
        userData.value = { ...initialData }; // 每次打開都重設表單
    }
});

function closeDialog() {
    dialog.value = false;
}

async function save() {
    const { valid } = await form.value.validate();
    if (valid) {
        emit('save', { ...userData.value });
    }
}
</script>