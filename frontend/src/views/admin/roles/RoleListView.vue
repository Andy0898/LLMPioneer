<template>
  <div class="role-list-view">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Role Management</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        Add Role
      </el-button>
    </div>

    <div class="bg-white rounded-lg shadow">
      <div class="p-6">
        <el-table :data="roles" v-loading="loading">
          <el-table-column prop="name" label="Role Name" />
          <el-table-column prop="description" label="Description" />
          <el-table-column prop="permissionCount" label="Permissions">
            <template #default="{ row }">
              <el-tag>{{ row.permissions?.length || 0 }} permissions</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="Created At">
            <template #default="{ row }">
              {{ formatDate(row.createdAt) }}
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="120">
            <template #default="{ row }">
              <el-button size="small" @click="editRole(row)">Edit</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- Create/Edit Role Dialog -->
    <el-dialog v-model="showCreateDialog" title="Add New Role" width="500px">
      <el-form :model="newRole" label-width="120px">
        <el-form-item label="Role Name">
          <el-input v-model="newRole.name" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="newRole.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="createRole">Create</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'

const roles = ref([])
const loading = ref(false)
const showCreateDialog = ref(false)
const newRole = ref({
  name: '',
  description: ''
})

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

const editRole = (role: any) => {
  // TODO: Implement edit role functionality
  console.log('Edit role:', role)
}

const createRole = () => {
  // TODO: Implement create role functionality
  console.log('Create role:', newRole.value)
  showCreateDialog.value = false
}

onMounted(() => {
  // TODO: Load roles from API
  roles.value = []
})
</script>

<style scoped>
.role-list-view {
  padding: 24px;
}
</style>