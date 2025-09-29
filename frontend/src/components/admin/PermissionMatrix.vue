<template>
  <div class="permission-matrix">
    <div class="matrix-header">
      <h3>{{ title }}</h3>
      <div class="header-actions">
        <el-select
          v-model="selectedRole"
          placeholder="Select Role"
          style="width: 200px"
          @change="handleRoleChange"
        >
          <el-option
            v-for="role in roles"
            :key="role.id"
            :label="role.name"
            :value="role.id"
          />
        </el-select>
        
        <el-button
          v-if="showSaveButton"
          type="primary"
          :loading="saving"
          :disabled="!hasChanges"
          @click="handleSave"
        >
          Save Changes
        </el-button>
      </div>
    </div>
    
    <!-- Permission Matrix -->
    <div v-if="selectedRole" class="matrix-content">
      <!-- Resource Filter -->
      <div class="matrix-filters">
        <el-input
          v-model="searchQuery"
          placeholder="Search permissions..."
          style="width: 250px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="resourceFilter"
          placeholder="Filter by resource"
          style="width: 150px"
          clearable
        >
          <el-option label="All Resources" value="" />
          <el-option
            v-for="resource in availableResources"
            :key="resource"
            :label="resource"
            :value="resource"
          />
        </el-select>
        
        <div class="bulk-actions">
          <el-button size="small" @click="selectAll">Select All</el-button>
          <el-button size="small" @click="selectNone">Select None</el-button>
        </div>
      </div>
      
      <!-- Matrix Table -->
      <div class="matrix-table">
        <el-table
          :data="filteredPermissions"
          :show-header="true"
          stripe
          @select="handlePermissionSelect"
          @select-all="handleSelectAll"
        >
          <el-table-column type="selection" width="55" />
          
          <el-table-column label="Resource" width="150" prop="resource">
            <template #default="{ row }">
              <el-tag :type="getResourceTagType(row.resource)">
                {{ row.resource }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="Permission" min-width="200">
            <template #default="{ row }">
              <div class="permission-info">
                <div class="permission-name">{{ row.name }}</div>
                <div class="permission-description">{{ row.description || 'No description' }}</div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="Action" width="100" prop="action">
            <template #default="{ row }">
              <el-tag size="small" :type="getActionTagType(row.action)">
                {{ row.action }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="Access Level" width="150">
            <template #default="{ row }">
              <el-tag
                size="small"
                :type="getAccessLevelType(row.resource, row.action)"
              >
                {{ getAccessLevel(row.resource, row.action) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="Status" width="100" align="center">
            <template #default="{ row }">
              <el-switch
                :model-value="isPermissionSelected(row)"
                @change="(value) => handlePermissionToggle(row, value)"
                :disabled="!canModifyPermission(row)"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- Permission Summary -->
      <div class="permission-summary">
        <el-card>
          <template #header>
            <span>Permission Summary</span>
          </template>
          
          <div class="summary-stats">
            <div class="stat-item">
              <div class="stat-value">{{ selectedPermissions.length }}</div>
              <div class="stat-label">Selected Permissions</div>
            </div>
            
            <div class="stat-item">
              <div class="stat-value">{{ totalPermissions }}</div>
              <div class="stat-label">Total Permissions</div>
            </div>
            
            <div class="stat-item">
              <div class="stat-value">{{ coveragePercentage }}%</div>
              <div class="stat-label">Coverage</div>
            </div>
          </div>
          
          <div class="resource-breakdown">
            <h4>By Resource</h4>
            <div class="resource-stats">
              <div
                v-for="resource in resourceStats"
                :key="resource.name"
                class="resource-stat"
              >
                <div class="resource-name">{{ resource.name }}</div>
                <div class="resource-progress">
                  <el-progress
                    :percentage="resource.percentage"
                    :stroke-width="6"
                    :show-text="false"
                  />
                  <span class="progress-text">
                    {{ resource.selected }}/{{ resource.total }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- Empty State -->
    <div v-else class="empty-state">
      <el-icon size="64" color="var(--el-text-color-placeholder)">
        <Lock />
      </el-icon>
      <h3>Select a Role</h3>
      <p>Choose a role from the dropdown to view and manage its permissions.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { Role, Permission } from '@/types'
import { roleApi, permissionApi } from '@/api'
import { Search, Lock } from '@element-plus/icons-vue'

interface Props {
  title?: string
  roleId?: string
  showSaveButton?: boolean
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Permission Matrix',
  showSaveButton: true,
  readonly: false
})

const emit = defineEmits<{
  save: [roleId: string, permissionIds: string[]]
  change: [roleId: string, permissionIds: string[]]
}>()

// Reactive state
const loading = ref(false)
const saving = ref(false)
const roles = ref<Role[]>([])
const permissions = ref<Permission[]>([])
const selectedRole = ref(props.roleId || '')
const selectedPermissions = ref<string[]>([])
const originalPermissions = ref<string[]>([])
const searchQuery = ref('')
const resourceFilter = ref('')

// Computed
const filteredPermissions = computed(() => {
  let filtered = [...permissions.value]
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(permission =>
      permission.name.toLowerCase().includes(query) ||
      permission.resource.toLowerCase().includes(query) ||
      permission.action.toLowerCase().includes(query) ||
      (permission.description?.toLowerCase().includes(query))
    )
  }
  
  if (resourceFilter.value) {
    filtered = filtered.filter(permission =>
      permission.resource === resourceFilter.value
    )
  }
  
  return filtered
})

const availableResources = computed(() => {
  const resources = new Set(permissions.value.map(p => p.resource))
  return Array.from(resources).sort()
})

const totalPermissions = computed(() => permissions.value.length)

const coveragePercentage = computed(() => {
  if (totalPermissions.value === 0) return 0
  return Math.round((selectedPermissions.value.length / totalPermissions.value) * 100)
})

const resourceStats = computed(() => {
  const stats: Record<string, { total: number; selected: number }> = {}
  
  permissions.value.forEach(permission => {
    if (!stats[permission.resource]) {
      stats[permission.resource] = { total: 0, selected: 0 }
    }
    stats[permission.resource].total++
    
    if (selectedPermissions.value.includes(permission.id)) {
      stats[permission.resource].selected++
    }
  })
  
  return Object.entries(stats).map(([name, data]) => ({
    name,
    total: data.total,
    selected: data.selected,
    percentage: data.total > 0 ? Math.round((data.selected / data.total) * 100) : 0
  })).sort((a, b) => a.name.localeCompare(b.name))
})

const hasChanges = computed(() => {
  return selectedPermissions.value.length !== originalPermissions.value.length ||
    !selectedPermissions.value.every(id => originalPermissions.value.includes(id))
})

// Methods
const fetchRoles = async () => {
  try {
    roles.value = await roleApi.getRoles()
  } catch (error) {
    ElMessage.error('Failed to fetch roles')
  }
}

const fetchPermissions = async () => {
  try {
    permissions.value = await permissionApi.getPermissions()
  } catch (error) {
    ElMessage.error('Failed to fetch permissions')
  }
}

const fetchRolePermissions = async (roleId: string) => {
  try {
    const rolePermissions = await roleApi.getRolePermissions(roleId)
    selectedPermissions.value = rolePermissions.map(p => p.id)
    originalPermissions.value = [...selectedPermissions.value]
  } catch (error) {
    ElMessage.error('Failed to fetch role permissions')
  }
}

const handleRoleChange = async (roleId: string) => {
  if (roleId) {
    await fetchRolePermissions(roleId)
  } else {
    selectedPermissions.value = []
    originalPermissions.value = []
  }
}

const isPermissionSelected = (permission: Permission) => {
  return selectedPermissions.value.includes(permission.id)
}

const handlePermissionToggle = (permission: Permission, value: boolean) => {
  if (props.readonly) return
  
  const index = selectedPermissions.value.indexOf(permission.id)
  
  if (value && index === -1) {
    selectedPermissions.value.push(permission.id)
  } else if (!value && index > -1) {
    selectedPermissions.value.splice(index, 1)
  }
  
  emit('change', selectedRole.value, selectedPermissions.value)
}

const handlePermissionSelect = (selection: Permission[], row: Permission) => {
  const isSelected = selection.includes(row)
  handlePermissionToggle(row, isSelected)
}

const handleSelectAll = (selection: Permission[]) => {
  if (props.readonly) return
  
  filteredPermissions.value.forEach(permission => {
    const isSelected = selection.includes(permission)
    const index = selectedPermissions.value.indexOf(permission.id)
    
    if (isSelected && index === -1) {
      selectedPermissions.value.push(permission.id)
    } else if (!isSelected && index > -1) {
      selectedPermissions.value.splice(index, 1)
    }
  })
  
  emit('change', selectedRole.value, selectedPermissions.value)
}

const selectAll = () => {
  if (props.readonly) return
  
  filteredPermissions.value.forEach(permission => {
    if (!selectedPermissions.value.includes(permission.id)) {
      selectedPermissions.value.push(permission.id)
    }
  })
  
  emit('change', selectedRole.value, selectedPermissions.value)
}

const selectNone = () => {
  if (props.readonly) return
  
  const filteredIds = filteredPermissions.value.map(p => p.id)
  selectedPermissions.value = selectedPermissions.value.filter(id => 
    !filteredIds.includes(id)
  )
  
  emit('change', selectedRole.value, selectedPermissions.value)
}

const handleSave = async () => {
  try {
    saving.value = true
    
    await roleApi.assignRolePermissions(selectedRole.value, selectedPermissions.value)
    originalPermissions.value = [...selectedPermissions.value]
    
    ElMessage.success('Permissions updated successfully')
    emit('save', selectedRole.value, selectedPermissions.value)
  } catch (error) {
    ElMessage.error('Failed to update permissions')
  } finally {
    saving.value = false
  }
}

const canModifyPermission = (permission: Permission) => {
  return !props.readonly
}

const getResourceTagType = (resource: string) => {
  const types: Record<string, string> = {
    'user': 'primary',
    'role': 'warning',
    'permission': 'danger',
    'document': 'success',
    'conversation': 'info',
    'system': 'danger'
  }
  return types[resource] || 'default'
}

const getActionTagType = (action: string) => {
  const types: Record<string, string> = {
    'read': 'info',
    'create': 'success',
    'update': 'warning',
    'delete': 'danger',
    'manage': 'primary'
  }
  return types[action] || 'default'
}

const getAccessLevel = (resource: string, action: string) => {
  if (action === 'read') return 'View'
  if (action === 'create') return 'Create'
  if (action === 'update') return 'Edit'
  if (action === 'delete') return 'Delete'
  if (action === 'manage') return 'Full Access'
  return action
}

const getAccessLevelType = (resource: string, action: string) => {
  if (action === 'read') return 'info'
  if (action === 'create') return 'success'
  if (action === 'update') return 'warning'
  if (action === 'delete') return 'danger'
  if (action === 'manage') return 'primary'
  return 'default'
}

// Watch for prop changes
watch(() => props.roleId, (newRoleId) => {
  if (newRoleId) {
    selectedRole.value = newRoleId
    fetchRolePermissions(newRoleId)
  }
})

// Initialize
onMounted(async () => {
  await Promise.all([fetchRoles(), fetchPermissions()])
  
  if (props.roleId) {
    selectedRole.value = props.roleId
    await fetchRolePermissions(props.roleId)
  }
})
</script>

<style scoped>
.permission-matrix {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.matrix-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.matrix-header h3 {
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

.matrix-content {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
}

.matrix-filters {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.bulk-actions {
  display: flex;
  gap: 8px;
}

.matrix-table {
  flex: 1;
}

.permission-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.permission-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
  font-size: 14px;
}

.permission-description {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

.permission-summary {
  position: sticky;
  top: 20px;
  height: fit-content;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-color-primary);
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.resource-breakdown h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.resource-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.resource-stat {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.resource-name {
  font-size: 12px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.resource-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.resource-progress .el-progress {
  flex: 1;
}

.progress-text {
  font-size: 11px;
  color: var(--el-text-color-secondary);
  white-space: nowrap;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: var(--el-text-color-secondary);
}

.empty-state h3 {
  margin: 16px 0 8px 0;
  font-size: 18px;
  color: var(--el-text-color-primary);
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  max-width: 300px;
  line-height: 1.5;
}

@media (max-width: 1200px) {
  .matrix-content {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }
  
  .permission-summary {
    position: static;
    order: -1;
  }
  
  .summary-stats {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .matrix-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: space-between;
  }
  
  .matrix-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .bulk-actions {
    justify-content: center;
  }
  
  .summary-stats {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style>