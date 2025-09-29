<template>
  <div class="user-table">
    <!-- Table Header Actions -->
    <div class="table-header">
      <div class="header-left">
        <el-input
          v-model="searchQuery"
          placeholder="Search users..."
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="statusFilter" placeholder="Status" style="width: 120px">
          <el-option label="All" value="" />
          <el-option label="Active" value="active" />
          <el-option label="Inactive" value="inactive" />
        </el-select>
        
        <el-select v-model="roleFilter" placeholder="Role" style="width: 150px">
          <el-option label="All Roles" value="" />
          <el-option
            v-for="role in availableRoles"
            :key="role.id"
            :label="role.name"
            :value="role.id"
          />
        </el-select>
      </div>
      
      <div class="header-right">
        <el-button type="primary" @click="handleCreateUser">
          <el-icon><Plus /></el-icon>
          Add User
        </el-button>
        
        <el-dropdown @command="handleBulkAction">
          <el-button :disabled="selectedUsers.length === 0">
            Bulk Actions
            <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="activate">Activate</el-dropdown-item>
              <el-dropdown-item command="deactivate">Deactivate</el-dropdown-item>
              <el-dropdown-item command="export">Export</el-dropdown-item>
              <el-dropdown-item command="delete" divided>Delete</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <!-- Users Table -->
    <el-table
      v-loading="loading"
      :data="tableData"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
      stripe
      style="width: 100%"
    >
      <el-table-column type="selection" width="55" />
      
      <el-table-column label="User" min-width="200" sortable="custom" prop="username">
        <template #default="{ row }">
          <div class="user-info">
            <el-avatar :size="32" :src="row.avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <div class="user-details">
              <div class="user-name">{{ row.full_name || row.username }}</div>
              <div class="user-email">{{ row.email }}</div>
            </div>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column label="Roles" width="200">
        <template #default="{ row }">
          <div class="roles-container">
            <el-tag
              v-for="role in row.roles"
              :key="role.id"
              size="small"
              :type="getRoleTagType(role.name)"
              style="margin-right: 4px; margin-bottom: 4px;"
            >
              {{ role.name }}
            </el-tag>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column label="Status" width="100" sortable="custom" prop="is_active">
        <template #default="{ row }">
          <el-switch
            v-model="row.is_active"
            @change="handleStatusChange(row)"
            :loading="row.statusChanging"
          />
        </template>
      </el-table-column>
      
      <el-table-column label="Last Login" width="150" sortable="custom" prop="last_login_at">
        <template #default="{ row }">
          <span v-if="row.last_login_at">
            {{ formatDate(row.last_login_at) }}
          </span>
          <span v-else class="text-muted">Never</span>
        </template>
      </el-table-column>
      
      <el-table-column label="Created" width="150" sortable="custom" prop="created_at">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      
      <el-table-column label="Actions" width="150" fixed="right">
        <template #default="{ row }">
          <el-dropdown @command="(command) => handleAction(command, row)">
            <el-button text>
              Actions
              <el-icon><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="view">
                  <el-icon><View /></el-icon>
                  View Details
                </el-dropdown-item>
                <el-dropdown-item command="edit">
                  <el-icon><Edit /></el-icon>
                  Edit User
                </el-dropdown-item>
                <el-dropdown-item command="roles">
                  <el-icon><UserFilled /></el-icon>
                  Manage Roles
                </el-dropdown-item>
                <el-dropdown-item command="reset-password">
                  <el-icon><Key /></el-icon>
                  Reset Password
                </el-dropdown-item>
                <el-dropdown-item command="delete" divided>
                  <el-icon><Delete /></el-icon>
                  Delete User
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- Pagination -->
    <div class="table-pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { User, Role } from '@/types'
import { userApi, roleApi } from '@/api'
import {
  Search,
  Plus,
  ArrowDown,
  User as UserIcon,
  View,
  Edit,
  UserFilled,
  Key,
  Delete
} from '@element-plus/icons-vue'

interface Props {
  searchable?: boolean
  selectable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  searchable: true,
  selectable: true
})

const emit = defineEmits<{
  userSelect: [user: User]
  userCreate: []
  userEdit: [user: User]
  userDelete: [user: User]
}>()

// Reactive state
const loading = ref(false)
const users = ref<User[]>([])
const availableRoles = ref<Role[]>([])
const selectedUsers = ref<User[]>([])
const searchQuery = ref('')
const statusFilter = ref('')
const roleFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortField = ref('')
const sortOrder = ref('')

// Computed
const tableData = computed(() => {
  let filtered = [...users.value]
  
  // Apply filters
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(user => 
      user.username.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query) ||
      (user.full_name?.toLowerCase().includes(query))
    )
  }
  
  if (statusFilter.value) {
    filtered = filtered.filter(user => 
      statusFilter.value === 'active' ? user.is_active : !user.is_active
    )
  }
  
  if (roleFilter.value) {
    filtered = filtered.filter(user =>
      user.roles.some(role => role.id === roleFilter.value)
    )
  }
  
  return filtered
})

// Methods
const fetchUsers = async () => {
  try {
    loading.value = true
    const response = await userApi.getUsers(currentPage.value, pageSize.value, searchQuery.value)
    users.value = response.items
    total.value = response.total
  } catch (error) {
    ElMessage.error('Failed to fetch users')
  } finally {
    loading.value = false
  }
}

const fetchRoles = async () => {
  try {
    availableRoles.value = await roleApi.getRoles()
  } catch (error) {
    console.error('Failed to fetch roles:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchUsers()
}

const handleSelectionChange = (selection: User[]) => {
  selectedUsers.value = selection
}

const handleSortChange = ({ prop, order }: any) => {
  sortField.value = prop
  sortOrder.value = order
  fetchUsers()
}

const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  fetchUsers()
}

const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage
  fetchUsers()
}

const handleCreateUser = () => {
  emit('userCreate')
}

const handleStatusChange = async (user: User) => {
  try {
    user.statusChanging = true
    if (user.is_active) {
      await userApi.activateUser(user.id)
      ElMessage.success('User activated successfully')
    } else {
      await userApi.deactivateUser(user.id)
      ElMessage.success('User deactivated successfully')
    }
  } catch (error) {
    // Revert the change
    user.is_active = !user.is_active
    ElMessage.error('Failed to update user status')
  } finally {
    user.statusChanging = false
  }
}

const handleAction = async (command: string, user: User) => {
  switch (command) {
    case 'view':
      emit('userSelect', user)
      break
      
    case 'edit':
      emit('userEdit', user)
      break
      
    case 'roles':
      // TODO: Open role management dialog
      ElMessage.info('Role management dialog will be implemented')
      break
      
    case 'reset-password':
      await handleResetPassword(user)
      break
      
    case 'delete':
      await handleDeleteUser(user)
      break
  }
}

const handleResetPassword = async (user: User) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to reset the password for ${user.username}?`,
      'Reset Password',
      {
        confirmButtonText: 'Reset',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )
    
    const result = await userApi.resetUserPassword(user.id)
    
    await ElMessageBox.alert(
      `New temporary password: ${result.temporary_password}`,
      'Password Reset',
      {
        confirmButtonText: 'OK',
        type: 'success'
      }
    )
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to reset password')
    }
  }
}

const handleDeleteUser = async (user: User) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete ${user.username}? This action cannot be undone.`,
      'Delete User',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'error'
      }
    )
    
    await userApi.deleteUser(user.id)
    ElMessage.success('User deleted successfully')
    emit('userDelete', user)
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete user')
    }
  }
}

const handleBulkAction = async (command: string) => {
  if (selectedUsers.value.length === 0) return
  
  switch (command) {
    case 'activate':
      await handleBulkActivate()
      break
    case 'deactivate':
      await handleBulkDeactivate()
      break
    case 'export':
      await handleExportUsers()
      break
    case 'delete':
      await handleBulkDelete()
      break
  }
}

const handleBulkActivate = async () => {
  try {
    const userIds = selectedUsers.value.map(user => user.id)
    await userApi.bulkActivateUsers(userIds)
    ElMessage.success('Users activated successfully')
    fetchUsers()
  } catch (error) {
    ElMessage.error('Failed to activate users')
  }
}

const handleBulkDeactivate = async () => {
  try {
    const userIds = selectedUsers.value.map(user => user.id)
    await userApi.bulkDeactivateUsers(userIds)
    ElMessage.success('Users deactivated successfully')
    fetchUsers()
  } catch (error) {
    ElMessage.error('Failed to deactivate users')
  }
}

const handleBulkDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete ${selectedUsers.value.length} users? This action cannot be undone.`,
      'Delete Users',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'error'
      }
    )
    
    const userIds = selectedUsers.value.map(user => user.id)
    await userApi.bulkDeleteUsers(userIds)
    ElMessage.success('Users deleted successfully')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete users')
    }
  }
}

const handleExportUsers = async () => {
  try {
    const blob = await userApi.exportUsers('csv')
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `users_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('Users exported successfully')
  } catch (error) {
    ElMessage.error('Failed to export users')
  }
}

const getRoleTagType = (roleName: string) => {
  const roleTypes: Record<string, string> = {
    'super_admin': 'danger',
    'admin': 'warning',
    'user': 'success',
    'guest': 'info'
  }
  return roleTypes[roleName] || 'primary'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

// Watch for filter changes
watch([statusFilter, roleFilter], () => {
  currentPage.value = 1
  fetchUsers()
})

// Initialize
onMounted(() => {
  fetchUsers()
  fetchRoles()
})
</script>

<style scoped>
.user-table {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.header-right {
  display: flex;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  flex: 1;
}

.user-name {
  font-weight: 600;
  color: var(--el-text-color-primary);
  font-size: 14px;
}

.user-email {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.roles-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.text-muted {
  color: var(--el-text-color-placeholder);
  font-style: italic;
}

.table-pagination {
  display: flex;
  justify-content: flex-end;
  padding: 16px 0;
}

@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-left,
  .header-right {
    justify-content: center;
  }
  
  .user-info {
    gap: 8px;
  }
  
  .user-name {
    font-size: 13px;
  }
  
  .user-email {
    font-size: 11px;
  }
}
</style>