<template>
    <v-container class="fill-height login-container">
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

        <v-card class="login-card elevation-12">
            <!-- 頂部裝飾 -->
            <div class="card-header">
                <div class="anchor-decoration">⚓</div>
                <div class="title-section">
                    <h2 class="main-title">艦隊指揮官登入</h2>
                    <div class="subtitle">S11159045 陳楓鎧</div>
                </div>
                <div class="compass-decoration">🧭</div>
            </div>

            <v-card-text class="form-container">
                <v-form @submit.prevent="handleLogin" class="login-form">
                    <div class="input-wrapper">
                        <v-text-field v-model="username" label="指揮官代號" prepend-inner-icon="mdi-account-outline"
                            :rules="[rules.required]" required variant="outlined" class="ocean-input"
                            color="blue-lighten-1">
                            <template #prepend-inner>
                                <v-icon color="blue-lighten-2">mdi-account-circle</v-icon>
                            </template>
                        </v-text-field>
                    </div>

                    <div class="input-wrapper">
                        <v-text-field v-model="password" label="機密密碼" type="password"
                            prepend-inner-icon="mdi-lock-outline" :rules="[rules.required]" required variant="outlined"
                            class="ocean-input" color="blue-lighten-1">
                            <template #prepend-inner>
                                <v-icon color="blue-lighten-2">mdi-shield-key</v-icon>
                            </template>
                        </v-text-field>
                    </div>

                    <v-alert v-if="errorMessage" type="error" density="compact" class="mb-4 custom-alert"
                        variant="tonal">
                        {{ errorMessage }}
                    </v-alert>

                    <v-btn type="submit" :loading="loading" class="login-btn" size="large" block elevation="4">
                        <v-icon left class="mr-2">mdi-ship-wheel</v-icon>
                        啟航入港
                        <div class="btn-ripple"></div>
                    </v-btn>
                </v-form>
            </v-card-text>

            <v-card-actions class="card-actions">
                <router-link to="/register" class="register-link">
                    <v-icon class="mr-1" size="small">mdi-anchor</v-icon>
                    新艦隊招募 → 立即加入
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
        </div>
    </v-container>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';

const username = ref('');
const password = ref('');
const loading = ref(false);
const errorMessage = ref('');
const authStore = useAuthStore();

const rules = {
    required: value => !!value || '此欄位為必填項目',
};

async function handleLogin() {
    if (!username.value || !password.value) return;

    loading.value = true;
    errorMessage.value = '';
    try {
        await authStore.login({
            username: username.value,
            password: password.value,
        });
    } catch (error) {
        errorMessage.value = '指揮官身份驗證失敗，請重新確認代號與密碼';
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

.login-container {
    background: linear-gradient(180deg, #e3f2fd 0%, #81d4fa 30%, #4fc3f7 70%, #29b6f6 100%) !important;
    min-height: 100vh;
    position: relative;
    overflow: hidden;
    z-index: 1;
    display: flex; /* Added */
    align-items: center; /* Added */
    justify-content: center; /* Added */
}

/* 如果上面還是黑色，試試這個更強制的方式 */
.v-container.login-container {
    background: linear-gradient(180deg, #87ceeb 0%, #4fc3f7 50%, #29b6f6 100%) !important;
}

/* 或者加上這個確保整個頁面背景 */
html, body {
    background: linear-gradient(180deg, #e3f2fd 0%, #81d4fa 30%, #4fc3f7 70%, #29b6f6 100%) !important;
    min-height: 100vh;
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
    animation: float-cloud 20s infinite linear;
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
    top: 20%;
    left: -100px;
    animation-duration: 25s;
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
    top: 40%;
    left: -80px;
    animation-duration: 30s;
    animation-delay: 10s;
}

.cloud3 {
    width: 100px;
    height: 50px;
    top: 15%;
    left: -120px;
    animation-duration: 35s;
    animation-delay: 15s;
}

/* 登入卡片 */
.login-card {
    width: 450px;
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
    font-size: 0.95rem;
}

.form-container {
    padding: 2rem;
}

.input-wrapper {
    margin-bottom: 1.5rem;
    position: relative;
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

.login-btn {
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

.login-btn:hover {
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

.register-link {
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

.register-link:hover {
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
    animation: fly 15s infinite linear;
}

.seagull1 {
    top: 15%;
    left: -50px;
    animation-duration: 18s;
}

.seagull2 {
    top: 25%;
    left: -50px;
    animation-duration: 22s;
    animation-delay: 8s;
}

.ship-icon {
    position: absolute;
    bottom: 100px;
    right: -50px;
    font-size: 2rem;
    animation: sail 20s infinite linear;
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

/* 響應式設計 */
@media (max-width: 500px) {
    .login-card {
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