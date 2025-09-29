<template>
  <div class="role-selector">
    <div class="selector-header">
      <h3>{{ title }}</h3>
      <div class="header-actions">
        <el-input
          v-if="searchable"
          v-model="searchQuery"
          placeholder="Search roles..."
          size="small"
          style="width: 200px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-button
          v-if="showCreateButton"
          type="primary"
          size="small"
          @click="handleCreateRole"
        >
          <el-icon><Plus /></el-icon>
          New Role
        </el-button>
      </div>
    </div>
    
    <!-- Role Selection Mode -->
    <div v-if="mode === 'select'" class="role-selection">
      <div class="available-roles">
        <h4>Available Roles</h4>
        <div class="roles-grid">
          <div
            v-for="role in filteredAvailableRoles"
            :key="role.id"
            class="role-card available"
            :class="{ 'selected': selectedRoleIds.includes(role.id) }"
            @click="handleRoleToggle(role)"
          >
            <div class="role-header">
              <div class="role-icon">
                <el-icon :color="getRoleColor(role.name)">
                  <component :is="getRoleIcon(role.name)" />
                </el-icon>
              </div>
              <div class="role-info">
                <div class="role-name">{{ role.name }}</div>
                <div class="role-description">{{ role.description || 'No description' }}</div>
              </div>
              <div class="role-action">
                <el-icon v-if="selectedRoleIds.includes(role.id)" color="#52c41a">
                  <Check />
                </el-icon>
                <el-icon v-else color="#d9d9d9">
                  <Plus />
                </el-icon>
              </div>
            </div>
            
            <div class="role-permissions">
              <div class="permission-count">
                {{ role.permissions?.length || 0 }} permissions
              </div>
              <div class="permission-preview">
                <el-tag
                  v-for="permission in role.permissions?.slice(0, 3)"
                  :key="permission.id"
                  size="small"
                  type="info"
                >
                  {{ permission.name }}
                </el-tag>
                <span v-if="(role.permissions?.length || 0) > 3" class="more-permissions">
                  +{{ (role.permissions?.length || 0) - 3 }} more
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Selected Roles -->
      <div v-if="selectedRoles.length > 0" class="selected-roles">
        <h4>Selected Roles ({{ selectedRoles.length }})</h4>
        <div class="selected-roles-list">
          <div
            v-for="role in selectedRoles"
            :key="role.id"
            class="selected-role-item"
          >
            <el-icon :color="getRoleColor(role.name)">
              <component :is="getRoleIcon(role.name)" />
            </el-icon>
            <span class="role-name">{{ role.name }}</span>
            <el-button
              text
              size="small"
              type="danger"
              @click="handleRoleRemove(role)"
            >
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Role Management Mode -->
    <div v-else-if="mode === 'manage'" class="role-management">
      <div class="roles-table">
        <el-table :data="filteredRoles" stripe>
          <el-table-column label="Role" min-width="200">
            <template #default="{ row }">
              <div class="role-info">
                <el-icon :color="getRoleColor(row.name)">
                  <component :is="getRoleIcon(row.name)" />
                </el-icon>
                <div>
                  <div class="role-name">{{ row.name }}</div>
                  <div class="role-description">{{ row.description || 'No description' }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="Permissions" min-width="300">
            <template #default="{ row }">
              <div class="permissions-list">
                <el-tag
                  v-for="permission in row.permissions?.slice(0, 5)"
                  :key="permission.id"
                  size="small"
                  type="info"
                  style="margin-right: 4px; margin-bottom: 4px;"
                >
                  {{ permission.name }}
                </el-tag>
                <span v-if="(row.permissions?.length || 0) > 5" class="more-permissions">
                  +{{ (row.permissions?.length || 0) - 5 }} more
                </span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="Users" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="success">{{ row.userCount || 0 }}</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="Status" width="100" align="center">
            <template #default="{ row }">
              <el-switch
                v-model="row.is_active"
                @change="handleRoleStatusChange(row)"
              />
            </template>
          </el-table-column>
          
          <el-table-column label="Actions" width="150" align="center">
            <template #default="{ row }">
              <el-dropdown @command="(command) => handleRoleAction(command, row)">
                <el-button text>
                  Actions
                  <el-icon><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="edit">
                      <el-icon><Edit /></el-icon>
                      Edit Role
                    </el-dropdown-item>
                    <el-dropdown-item command="permissions">
                      <el-icon><Key /></el-icon>
                      Manage Permissions
                    </el-dropdown-item>
                    <el-dropdown-item command="users">
                      <el-icon><User /></el-icon>
                      View Users
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" divided>
                      <el-icon><Delete /></el-icon>
                      Delete Role
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
    
    <!-- Actions -->
    <div v-if="showActions" class="selector-actions">
      <el-button @click="handleCancel">Cancel</el-button>
      <el-button type="primary" @click="handleConfirm" :disabled="!hasChanges">
        {{ confirmText }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Role, Permission } from '@/types'
import { roleApi } from '@/api'
import {
  Search,
  Plus,
  Check,
  Close,
  ArrowDown,
  Edit,
  Key,
  User,
  Delete,
  Crown,
  Shield,
  UserFilled,
  Tools
} from '@element-plus/icons-vue'

interface Props {
  mode?: 'select' | 'manage'
  title?: string
  selectedRoleIds?: string[]
  searchable?: boolean
  showCreateButton?: boolean
  showActions?: boolean
  confirmText?: string
  multiple?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'select',
  title: 'Role Selector',
  selectedRoleIds: () => [],
  searchable: true,
  showCreateButton: false,
  showActions: true,
  confirmText: 'Confirm',
  multiple: true
})

const emit = defineEmits<{
  confirm: [roleIds: string[]]
  cancel: []
  roleCreate: []
  roleEdit: [role: Role]
  roleDelete: [role: Role]
}>()

// Reactive state
const loading = ref(false)
const roles = ref<Role[]>([])
const searchQuery = ref('')
const selectedRoleIds = ref<string[]>([...props.selectedRoleIds])

// Computed
const filteredRoles = computed(() => {
  if (!searchQuery.value) return roles.value
  
  const query = searchQuery.value.toLowerCase()
  return roles.value.filter(role =>
    role.name.toLowerCase().includes(query) ||
    (role.description?.toLowerCase().includes(query))
  )
})

const filteredAvailableRoles = computed(() => {
  return filteredRoles.value.filter(role => role.is_active)
})

const selectedRoles = computed(() => {
  return roles.value.filter(role => selectedRoleIds.value.includes(role.id))
})

const hasChanges = computed(() => {
  return selectedRoleIds.value.length !== props.selectedRoleIds.length ||
    !selectedRoleIds.value.every(id => props.selectedRoleIds.includes(id))
})

// Methods
const fetchRoles = async () => {
  try {
    loading.value = true
    roles.value = await roleApi.getRoles()
  } catch (error) {
    ElMessage.error('Failed to fetch roles')
  } finally {
    loading.value = false
  }
}

const handleRoleToggle = (role: Role) => {
  const index = selectedRoleIds.value.indexOf(role.id)
  
  if (index > -1) {
    selectedRoleIds.value.splice(index, 1)
  } else {
    if (props.multiple) {
      selectedRoleIds.value.push(role.id)
    } else {
      selectedRoleIds.value = [role.id]
    }
  }
}

const handleRoleRemove = (role: Role) => {
  const index = selectedRoleIds.value.indexOf(role.id)
  if (index > -1) {
    selectedRoleIds.value.splice(index, 1)
  }
}

const handleCreateRole = () => {
  emit('roleCreate')
}

const handleConfirm = () => {
  emit('confirm', selectedRoleIds.value)
}

const handleCancel = () => {
  selectedRoleIds.value = [...props.selectedRoleIds]
  emit('cancel')
}

const handleRoleStatusChange = async (role: Role) => {
  try {
    await roleApi.updateRole(role.id, { is_active: role.is_active })
    ElMessage.success(`Role ${role.is_active ? 'activated' : 'deactivated'} successfully`)
  } catch (error) {
    // Revert the change
    role.is_active = !role.is_active
    ElMessage.error('Failed to update role status')
  }
}

const handleRoleAction = async (command: string, role: Role) => {
  switch (command) {
    case 'edit':
      emit('roleEdit', role)
      break
      
    case 'permissions':
      ElMessage.info('Permission management will be implemented')
      break
      
    case 'users':
      ElMessage.info('User list will be implemented')
      break
      
    case 'delete':
      await handleDeleteRole(role)
      break
  }
}

const handleDeleteRole = async (role: Role) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete the role "${role.name}"? This action cannot be undone.`,
      'Delete Role',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'error'
      }
    )
    
    await roleApi.deleteRole(role.id)
    ElMessage.success('Role deleted successfully')
    emit('roleDelete', role)
    fetchRoles()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to delete role')
    }
  }
}

const getRoleIcon = (roleName: string) => {
  const icons: Record<string, any> = {
    'super_admin': Crown,
    'admin': Shield,
    'manager': Tools,
    'user': UserFilled,
    'guest': User
  }
  return icons[roleName] || UserFilled
}

const getRoleColor = (roleName: string) => {
  const colors: Record<string, string> = {
    'super_admin': '#ff4d4f',
    'admin': '#fa8c16',
    'manager': '#1890ff',
    'user': '#52c41a',
    'guest': '#d9d9d9'
  }
  return colors[roleName] || '#1890ff'
}

// Watch for prop changes
watch(() => props.selectedRoleIds, (newValue) => {
  selectedRoleIds.value = [...newValue]
}, { deep: true })

// Initialize
onMounted(() => {
  fetchRoles()
})
</script>

<style scoped>
.role-selector {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.selector-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.role-selection {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.available-roles h4,
.selected-roles h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
}

.role-card {
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--el-bg-color);
}

.role-card:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.role-card.selected {
  border-color: #52c41a;
  background: #f6ffed;
}

.role-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.role-icon {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-fill-color-light);
  border-radius: 6px;
}

.role-info {
  flex: 1;
}

.role-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.role-description {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

.role-action {
  flex-shrink: 0;
}

.role-permissions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.permission-count {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-weight: 500;
}

.permission-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.more-permissions {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
}

.selected-roles-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.selected-role-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: var(--el-fill-color-light);
  border-radius: 16px;
  font-size: 12px;
}

.selected-role-item .role-name {
  font-weight: 500;
  margin: 0;
}

.role-management .role-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.permissions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.selector-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-light);
}

@media (max-width: 768px) {
  .selector-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: space-between;
  }
  
  .roles-grid {
    grid-template-columns: 1fr;
  }
  
  .role-card {
    padding: 12px;
  }
  
  .selector-actions {
    flex-direction: column-reverse;
  }
}
</style>