<template>
    <div class="user-management-container">
        <div class="force-background"></div>
        <div class="main-content">
    <v-container fluid class="user-container d-flex justify-center align-start pa-0">
        <v-card class="user-card elevation-12">
            <div class="card-header-decoration"></div>

            <v-card-title class="user-title py-6">
                <div class="w-100 d-flex align-center">
                    <v-icon class="title-icon mr-3" color="blue-lighten-1">mdi-account-group</v-icon>
                    <span class="title-text">使用者管理面板</span>
                    <v-spacer></v-spacer>
                    <v-btn class="create-btn" prepend-icon="mdi-account-plus" @click="promptCreateUser">
                        建立使用者
                    </v-btn>
                </div>
            </v-card-title>

            <v-card-text class="table-container px-0">
                <v-data-table :headers="headers" :items="users" :loading="isLoading" class="ocean-table light-table"
                    item-value="id" density="comfortable" :items-per-page="10">
                    <template #item.role="{ item }">
                        <v-chip :color="getRoleColor(item.role)" size="small" label class="font-weight-bold">
                            {{ item.role }}
                        </v-chip>
                    </template>

                    <template #item.is_active="{ item }">
                        <v-icon :color="item.is_active ? 'success' : 'grey-darken-1'">
                            {{ item.is_active ? 'mdi-check-circle' : 'mdi-minus-circle' }}
                        </v-icon>
                    </template>

                    <template #item.actions="{ item }">
                        <v-btn variant="text" size="small" icon="mdi-pencil" @click="promptEditUser(item)" title="編輯" />
                        <v-btn variant="text" size="small" icon="mdi-lock-reset" @click="promptResetPassword(item)"
                            title="重設密碼" />
                        <v-btn variant="text" size="small" icon="mdi-delete" color="error"
                            @click="promptDeleteUser(item)" title="刪除" />
                    </template>
                </v-data-table>
            </v-card-text>

            <v-card-actions class="card-actions py-5 px-6">
                <v-spacer></v-spacer>
                <v-btn class="back-btn" to="/dashboard" prepend-icon="mdi-arrow-left">
                    返回儀表板
                </v-btn>
            </v-card-actions>
        </v-card>

        <CreateUserDialog v-model="dialogs.create" :loading="actionLoading" :error-message="actionError"
            @save="executeCreateUser" />

        <EditUserDialog v-model="dialogs.edit" :user="selectedUser" :loading="actionLoading"
            :error-message="actionError" @save="executeEditUser" />

        <ResetPasswordDialog v-model="dialogs.resetPassword" :username="selectedUser ? selectedUser.username : ''"
            :loading="actionLoading" :error-message="actionError" @save="executeResetPassword" />

        <ConfirmDialog v-model="dialogs.delete" title="確認刪除使用者" :message="confirmMessage" confirm-text="確認刪除"
            confirm-color="error" @confirm="executeDeleteUser" />
</v-container>
        </div> <!-- end main-content -->
    </div> <!-- end user-management-container -->
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import apiClient from '@/plugins/axios';
import CreateUserDialog from '@/components/CreateUserDialog.vue';
import EditUserDialog from '@/components/EditUserDialog.vue';
import ResetPasswordDialog from '@/components/ResetPasswordDialog.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';

const users = ref([]);
const isLoading = ref(false);
const actionLoading = ref(false);
const actionError = ref('');
const selectedUser = ref(null);
const confirmMessage = ref('');

const dialogs = reactive({ create: false, edit: false, delete: false, resetPassword: false });

const headers = [
    { title: 'ID', key: 'id', align: 'start', width: '60px', headerClass: 'col-id' },
    { title: '使用者名稱', key: 'username' },
    { title: 'Email', key: 'email' },
    { title: '角色', key: 'role', align: 'center', width: '110px', headerClass: 'col-role' },
    { title: '啟用', key: 'is_active', align: 'center', width: '80px', headerClass: 'col-active' },
    { title: '操作', key: 'actions', sortable: false, align: 'end', width: '300px', headerClass: 'col-actions' }
];

onMounted(fetchUsers);

async function fetchUsers() {
    isLoading.value = true;
    try {
        const { data } = await apiClient.get('/api/v1/users/');
        users.value = data;
    } catch (e) {
        console.error('無法獲取使用者列表:', e);
    } finally {
        isLoading.value = false;
    }
}

function getRoleColor(role) {
    return { admin: 'red-darken-1', manager: 'amber-darken-2' }[role] || 'blue-darken-1';
}

function resetActionState() {
    actionLoading.value = false;
    actionError.value = '';
    selectedUser.value = null;
}

/* ----------------------------- Create ----------------------------- */
function promptCreateUser() {
    resetActionState();
    dialogs.create = true;
}
async function executeCreateUser(userData) {
    actionLoading.value = true;
    actionError.value = '';
    try {
        await apiClient.post('/api/v1/users/', userData);
        dialogs.create = false;
        await fetchUsers();
    } catch (e) {
        actionError.value = e.response?.data?.detail || '建立失敗';
    } finally {
        actionLoading.value = false;
    }
}

/* ----------------------------- Edit ----------------------------- */
function promptEditUser(user) {
    resetActionState();
    selectedUser.value = { ...user };
    dialogs.edit = true;
}
async function executeEditUser(userData) {
    actionLoading.value = true;
    actionError.value = '';
    try {
        await apiClient.patch(`/api/v1/users/${selectedUser.value.id}`, userData);
        dialogs.edit = false;
        await fetchUsers();
    } catch (e) {
        actionError.value = e.response?.data?.detail || '更新失敗';
    } finally {
        actionLoading.value = false;
    }
}

/* ----------------------------- Delete ----------------------------- */
function promptDeleteUser(user) {
    selectedUser.value = user;
    confirmMessage.value = `您確定要刪除使用者 <b>${user.username} (${user.email})</b> 嗎？此操作無法復原。`;
    dialogs.delete = true;
}
async function executeDeleteUser() {
    actionLoading.value = true;
    try {
        await apiClient.delete(`/api/v1/users/${selectedUser.value.id}`);
        dialogs.delete = false;
        await fetchUsers();
    } catch (e) {
        alert('刪除失敗');
    } finally {
        resetActionState();
    }
}

/* ----------------------------- Reset Password ----------------------------- */
function promptResetPassword(user) {
    resetActionState();
    selectedUser.value = user;
    dialogs.resetPassword = true;
}
async function executeResetPassword(newPassword) {
    actionLoading.value = true;
    actionError.value = '';
    try {
        await apiClient.patch(`/api/v1/users/${selectedUser.value.id}/reset-password`, { new_password: newPassword });
        dialogs.resetPassword = false;
        alert(`使用者 ${selectedUser.value.username} 的密碼已成功重設。`);
    } catch (e) {
        actionError.value = e.response?.data?.detail || '重設密碼失敗';
    } finally {
        actionLoading.value = false;
    }
}
</script>

/*********************************
  * Fixed background & layout    *
  *********************************/
.user-management-container {
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

.main-content {
    position: relative;
    z-index: 2;
    max-width: 1200px;
    margin: 0 auto;
}

<style scoped>
/*********************************
  * 背景容器                      *
  *********************************/
.user-container {
    min-height: 100vh;
    padding: 1rem 0;
    display: flex;
    justify-content: flex-start;
    align-items: center;
}

/*********************************
  * 卡片 & 裝飾                  *
  *********************************/
.user-card {
    width: 100%;
    max-width: 1280px;
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.96) 0%, rgba(240, 248, 255, 0.92) 100%);
    border-radius: 24px;
    border: 1px solid rgba(33, 150, 243, 0.18);
    overflow: hidden;
    backdrop-filter: blur(10px);
}

.card-header-decoration {
    height: 4px;
    background: linear-gradient(90deg, #2196f3 0%, #03a9f4 50%, #00bcd4 100%);
    animation: shimmer 2.5s infinite;
}

/*********************************
  * 標題                          *
  *********************************/
.user-title {
    background: linear-gradient(135deg, #e1f5fe 0%, #b3e5fc 100%);
}

.title-icon {
    font-size: 1.8rem;
}

.title-text {
    font-size: 1.45rem;
    font-weight: 700;
    color: #0277bd;
    letter-spacing: 0.6px;
}

/*********************************
  * 建立按鈕                      *
  *********************************/
.create-btn {
    background: linear-gradient(135deg, #2196f3 0%, #03a9f4 50%, #00bcd4 100%);
    color: #fff;
    border-radius: 12px;
    font-weight: 600;
    text-transform: none;
    min-width: 130px;
}

.create-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(33, 150, 243, 0.35);
}

/*********************************
  * DataTable                     *
  *********************************/
.table-container {
    padding: 0 8px;
    /* 增加左右 padding */
    overflow-x: auto;
}

.light-table {
    background-color: transparent !important;
}

.light-table :deep(thead th) {
    background: rgba(227, 242, 253, 0.9) !important;
    color: #01579b !important;
    font-weight: 700 !important;
    font-size: 0.875rem !important;
}

.light-table :deep(tbody tr) {
    background: rgba(255, 255, 255, 0.7);
    transition: background-color 0.2s ease;
}

.light-table :deep(tbody tr:hover) {
    background: rgba(227, 242, 253, 1) !important;
}

.light-table :deep(tbody tr:nth-child(even)) {
    background: rgba(227, 242, 253, 0.45);
}

.light-table :deep(th),
.light-table :deep(td) {
    border-bottom: 1px solid rgba(33, 150, 243, 0.15) !important;
}

.light-table :deep(.v-chip) {
    text-transform: uppercase;
}

/*********************************
  * 底部按鈕                      *
  *********************************/
.back-btn {
    font-weight: 500;
    color: #0277bd;
    border: 1px solid rgba(33, 150, 243, 0.3);
    background-color: rgba(255, 255, 255, 0.5);
    transition: background-color 0.2s ease;
}

.back-btn:hover {
    background-color: rgba(225, 245, 254, 1);
}

/*********************************
  * 動畫                          *
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
/* Enforce Data Table column widths */
:deep(.col-id) { width: 60px; }
:deep(.col-role) { width: 110px; }
:deep(.col-active) { width: 80px; }
:deep(.col-actions) { width: 300px; }
</style>