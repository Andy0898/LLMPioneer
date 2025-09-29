<template>
  <div class="user-list-view">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">User Management</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        Add User
      </el-button>
    </div>

    <div class="bg-white rounded-lg shadow">
      <div class="p-6">
        <el-table :data="users" v-loading="loading">
          <el-table-column prop="username" label="Username" />
          <el-table-column prop="email" label="Email" />
          <el-table-column prop="isActive" label="Status">
            <template #default="{ row }">
              <el-tag :type="row.isActive ? 'success' : 'danger'">
                {{ row.isActive ? 'Active' : 'Inactive' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="Created At">
            <template #default="{ row }">
              {{ formatDate(row.createdAt) }}
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="120">
            <template #default="{ row }">
              <el-button size="small" @click="editUser(row)">Edit</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- Create/Edit User Dialog -->
    <el-dialog v-model="showCreateDialog" title="Add New User" width="500px">
      <el-form :model="newUser" label-width="120px">
        <el-form-item label="Username">
          <el-input v-model="newUser.username" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="newUser.email" type="email" />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="newUser.password" type="password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="createUser">Create</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'

const users = ref([])
const loading = ref(false)
const showCreateDialog = ref(false)
const newUser = ref({
  username: '',
  email: '',
  password: ''
})

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

const editUser = (user: any) => {
  // TODO: Implement edit user functionality
  console.log('Edit user:', user)
}

const createUser = () => {
  // TODO: Implement create user functionality
  console.log('Create user:', newUser.value)
  showCreateDialog.value = false
}

onMounted(() => {
  // TODO: Load users from API
  users.value = []
})
</script>

<style scoped>
.user-list-view {
  padding: 24px;
}
</style>