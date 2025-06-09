<template>
    <v-container class="fill-height register-container">
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

        <v-card class="register-card elevation-12">
            <!-- 頂部裝飾 -->
            <div class="card-header">
                <div class="anchor-decoration">🌟</div>
                <div class="title-section">
                    <h2 class="main-title">新艦隊招募</h2>
                    <div class="subtitle">加入碧藍航線 - 成為指揮官</div>
                </div>
                <div class="compass-decoration">⭐</div>
            </div>

            <v-card-text class="form-container">
                <v-form @submit.prevent="handleRegister" class="register-form">
                    <div class="input-wrapper">
                        <v-text-field v-model="username" label="指揮官代號" prepend-inner-icon="mdi-account-outline"
                            :rules="[rules.required]" required variant="outlined" class="ocean-input"
                            color="blue-lighten-1">
                            <template #prepend-inner>
                                <v-icon color="blue-lighten-2">mdi-account-star</v-icon>
                            </template>
                        </v-text-field>
                    </div>

                    <div class="input-wrapper">
                        <v-text-field v-model="email" label="通訊電子郵件" type="email" prepend-inner-icon="mdi-email-outline"
                            :rules="[rules.required, rules.email]" required variant="outlined" class="ocean-input"
                            color="blue-lighten-1">
                            <template #prepend-inner>
                                <v-icon color="blue-lighten-2">mdi-email-fast</v-icon>
                            </template>
                        </v-text-field>
                    </div>

                    <div class="input-wrapper">
                        <v-text-field v-model="password" label="機密密碼" type="password"
                            prepend-inner-icon="mdi-lock-outline" :rules="[rules.required, rules.minLength]" required
                            variant="outlined" class="ocean-input" color="blue-lighten-1">
                            <template #prepend-inner>
                                <v-icon color="blue-lighten-2">mdi-shield-star</v-icon>
                            </template>
                        </v-text-field>
                        <div class="password-hint">
                            <v-icon size="small" color="blue-lighten-3">mdi-information</v-icon>
                            密碼需至少6個字元
                        </div>
                    </div>

                    <v-alert v-if="errorMessage" type="error" density="compact" class="mb-4 custom-alert"
                        variant="tonal">
                        {{ errorMessage }}
                    </v-alert>

                    <v-btn type="submit" :loading="loading" class="register-btn" size="large" block elevation="4">
                        <v-icon left class="mr-2">mdi-anchor</v-icon>
                        加入艦隊
                        <div class="btn-ripple"></div>
                    </v-btn>
                </v-form>
            </v-card-text>

            <v-card-actions class="card-actions">
                <router-link to="/login" class="login-link">
                    <v-icon class="mr-1" size="small">mdi-ship-wheel</v-icon>
                    已是指揮官？返回登入
                </router-link>
            </v-card-actions>

            <!-- 底部裝飾波浪 -->
            <div class="card-footer-wave"></div>
        </v-card>

        <!-- 浮動元素 -->
        <div class="floating-elements">
            <div class="seagull seagull1">🕊️</div>
            <div class="seagull seagull2">🕊️</div>
            <div class="ship-icon">⛵</div>
            <div class="star star1">✨</div>
            <div class="star star2">⭐</div>
        </div>
    </v-container>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';

const username = ref('');
const email = ref('');
const password = ref('');
const loading = ref(false);
const errorMessage = ref('');
const authStore = useAuthStore();

const rules = {
    required: value => !!value || '此欄位為必填項目',
    email: value => /.+@.+\..+/.test(value) || '請輸入有效的電子郵件格式',
    minLength: value => (value && value.length >= 6) || '密碼長度至少需6個字元',
};

async function handleRegister() {
    if (!email.value || !password.value || !username.value) return;

    loading.value = true;
    errorMessage.value = '';
    try {
        await authStore.register({
            username: username.value,
            email: email.value,
            password: password.value,
        });
    } catch (error) {
        errorMessage.value = '招募失敗，該指揮官代號或通訊郵件可能已被使用';
        console.error(error);
    } finally {
        loading.value = false;
    }
}
</script>

<style scoped>
.force-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: linear-gradient(180deg, #e3f2fd 0%, #81d4fa 30%, #4fc3f7 70%, #29b6f6 100%);
    z-index: -1;
}

.register-container {
    background: linear-gradient(180deg, #e3f2fd 0%, #81d4fa 30%, #4fc3f7 70%, #29b6f6 100%) !important;
    min-height: 100vh;
    position: relative;
    overflow: hidden;
    z-index: 1;
    display: flex; /* Added */
    align-items: center; /* Added */
    justify-content: center; /* Added */
    padding: 1rem; /* Added for some spacing on smaller screens */
}

/* 海洋背景動畫 */
.ocean-bg {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 200px;
    overflow: hidden;
}

.wave {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 200%;
    height: 100px;
    background: linear-gradient(180deg, transparent 0%, rgba(255, 255, 255, 0.3) 100%);
    border-radius: 50%;
    animation: wave-animation 6s ease-in-out infinite;
}

.wave1 {
    animation-delay: 0s;
    opacity: 0.8;
}

.wave2 {
    animation-delay: 2s;
    opacity: 0.6;
    height: 80px;
}

.wave3 {
    animation-delay: 4s;
    opacity: 0.4;
    height: 60px;
}

/* 浮雲效果 */
.clouds {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

.cloud {
    position: absolute;
    background: rgba(255, 255, 255, 0.7);
    border-radius: 50px;
    animation: float-cloud 25s infinite linear;
}

.cloud::before,
.cloud::after {
    content: '';
    position: absolute;
    background: rgba(255, 255, 255, 0.7);
    border-radius: 50%;
}

.cloud1 {
    width: 80px;
    height: 40px;
    top: 15%;
    left: -100px;
    animation-duration: 28s;
}

.cloud1::before {
    width: 50px;
    height: 50px;
    top: -25px;
    left: 10px;
}

.cloud1::after {
    width: 60px;
    height: 40px;
    top: -15px;
    right: 10px;
}

.cloud2 {
    width: 60px;
    height: 30px;
    top: 35%;
    left: -80px;
    animation-duration: 32s;
    animation-delay: 12s;
}

.cloud3 {
    width: 100px;
    height: 50px;
    top: 10%;
    left: -120px;
    animation-duration: 38s;
    animation-delay: 18s;
}

/* 註冊卡片 */
.register-card {
    width: 480px;
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(240, 248, 255, 0.9) 100%);
    border-radius: 25px;
    border: 2px solid rgba(33, 150, 243, 0.3);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(10px);
}

.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 2rem 2rem 1rem;
    background: linear-gradient(135deg, #e1f5fe 0%, #b3e5fc 100%);
    position: relative;
}

.anchor-decoration,
.compass-decoration {
    font-size: 2rem;
    opacity: 0.7;
    animation: gentle-bounce 3s ease-in-out infinite;
}

.compass-decoration {
    animation-delay: 1.5s;
}

.title-section {
    text-align: center;
    flex: 1;
}

.main-title {
    font-size: 1.6rem;
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
    font-size: 0.9rem;
}

.form-container {
    padding: 2rem;
}

.input-wrapper {
    margin-bottom: 1.5rem;
    position: relative;
}

.password-hint {
    display: flex;
    align-items: center;
    margin-top: 0.5rem;
    color: #0288d1;
    font-size: 0.85rem;
    opacity: 0.8;
}

.ocean-input :deep(.v-field) {
    background: rgba(227, 242, 253, 0.8);
    border-radius: 15px;
    border: 2px solid rgba(33, 150, 243, 0.2);
    transition: all 0.3s ease;
}

.ocean-input :deep(.v-field--focused) {
    border-color: #2196f3;
    background: rgba(227, 242, 253, 1);
    box-shadow: 0 4px 20px rgba(33, 150, 243, 0.2);
}

.ocean-input :deep(.v-field__input) {
    color: #01579b;
    font-weight: 500;
}

.ocean-input :deep(.v-label) {
    color: #0288d1;
    font-weight: 500;
}

.custom-alert {
    background: rgba(255, 235, 238, 0.9);
    border: 1px solid rgba(244, 67, 54, 0.3);
    border-radius: 12px;
}

.register-btn {
    background: linear-gradient(135deg, #2196f3 0%, #03a9f4 50%, #00bcd4 100%);
    color: white;
    border-radius: 15px;
    height: 55px;
    font-weight: 600;
    font-size: 1.1rem;
    letter-spacing: 1px;
    text-transform: none;
    position: relative;
    overflow: hidden;
    margin-top: 1rem;
}

.register-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(33, 150, 243, 0.4);
}

.btn-ripple {
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    animation: button-shine 3s infinite;
}

.card-actions {
    justify-content: center;
    padding: 0 2rem 2rem;
}

.login-link {
    text-decoration: none;
    color: #0277bd;
    font-weight: 600;
    display: flex;
    align-items: center;
    padding: 0.8rem 1.5rem;
    border-radius: 25px;
    background: rgba(227, 242, 253, 0.6);
    transition: all 0.3s ease;
    border: 1px solid rgba(33, 150, 243, 0.2);
}

.login-link:hover {
    background: rgba(227, 242, 253, 1);
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.2);
}

.card-footer-wave {
    height: 20px;
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
    animation: wave-slide 4s ease-in-out infinite;
}

/* 浮動元素 */
.floating-elements {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

.seagull {
    position: absolute;
    font-size: 1.5rem;
    animation: fly 18s infinite linear;
}

.seagull1 {
    top: 20%;
    left: -50px;
    animation-duration: 20s;
}

.seagull2 {
    top: 30%;
    left: -50px;
    animation-duration: 25s;
    animation-delay: 10s;
}

.ship-icon {
    position: absolute;
    bottom: 120px;
    right: -50px;
    font-size: 2rem;
    animation: sail 22s infinite linear;
}

.star {
    position: absolute;
    font-size: 1.2rem;
    animation: twinkle 4s ease-in-out infinite;
}

.star1 {
    top: 25%;
    right: 20%;
    animation-delay: 0s;
}

.star2 {
    top: 60%;
    left: 15%;
    animation-delay: 2s;
}

/* 動畫定義 */
@keyframes wave-animation {

    0%,
    100% {
        transform: translateX(0) translateY(0);
    }

    50% {
        transform: translateX(-25%) translateY(-10px);
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
        transform: translateY(-5px);
    }
}

@keyframes button-shine {
    0% {
        left: -100%;
    }

    100% {
        left: 100%;
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

@keyframes fly {
    from {
        transform: translateX(-50px) translateY(0);
    }

    to {
        transform: translateX(calc(100vw + 50px)) translateY(-20px);
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

@keyframes twinkle {

    0%,
    100% {
        opacity: 0.6;
        transform: scale(1);
    }

    50% {
        opacity: 1;
        transform: scale(1.2);
    }
}

/* 響應式設計 */
@media (max-width: 520px) {
    .register-card {
        width: 90%;
        margin: 1rem;
    }

    .card-header {
        padding: 1.5rem 1.5rem 1rem;
    }

    .form-container {
        padding: 1.5rem;
    }

    .main-title {
        font-size: 1.4rem;
    }

    .anchor-decoration,
    .compass-decoration {
        font-size: 1.5rem;
    }
}
</style>