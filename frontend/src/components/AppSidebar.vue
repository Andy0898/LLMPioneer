<template>
  <el-aside 
    :width="collapsed ? '64px' : '240px'" 
    class="app-sidebar" 
    :class="{ collapsed, [portalClass]: true }"
  >
    <div class="sidebar-content">
      <!-- Collapse Toggle -->
      <div class="collapse-toggle" @click="toggleCollapse">
        <el-icon>
          <component :is="collapsed ? 'Expand' : 'Fold'" />
        </el-icon>
      </div>

      <!-- Navigation Menu -->
      <el-menu
        :default-active="activeRoute"
        :collapse="collapsed"
        :unique-opened="true"
        :collapse-transition="false"
        class="sidebar-menu"
        @select="handleMenuSelect"
      >
        <template v-for="item in menuItems" :key="item.id">
          <!-- Menu Item with Children -->
          <el-sub-menu 
            v-if="item.children && item.children.length > 0"
            :index="item.id"
            :disabled="!hasPermission(item.permission)"
          >
            <template #title>
              <el-icon v-if="item.icon">
                <component :is="item.icon" />
              </el-icon>
              <span>{{ item.label }}</span>
              <el-badge 
                v-if="item.badge && !collapsed" 
                :value="item.badge" 
                class="menu-badge"
              />
            </template>
            
            <el-menu-item
              v-for="child in item.children"
              :key="child.id"
              :index="child.route || child.id"
              :disabled="!hasPermission(child.permission)"
            >
              <el-icon v-if="child.icon">
                <component :is="child.icon" />
              </el-icon>
              <span>{{ child.label }}</span>
              <el-badge 
                v-if="child.badge" 
                :value="child.badge" 
                class="menu-badge"
              />
            </el-menu-item>
          </el-sub-menu>

          <!-- Single Menu Item -->
          <el-menu-item
            v-else
            :index="item.route || item.id"
            :disabled="!hasPermission(item.permission)"
          >
            <el-icon v-if="item.icon">
              <component :is="item.icon" />
            </el-icon>
            <template #title>
              <span>{{ item.label }}</span>
              <el-badge 
                v-if="item.badge && !collapsed" 
                :value="item.badge" 
                class="menu-badge"
              />
            </template>
          </el-menu-item>
        </template>
      </el-menu>

      <!-- Footer Info -->
      <div v-if="!collapsed" class="sidebar-footer">
        <div class="user-info">
          <el-avatar :size="32" :src="user?.avatar">
            <el-icon><User /></el-icon>
          </el-avatar>
          <div class="user-details">
            <div class="user-name">{{ user?.full_name || user?.username }}</div>
            <div class="user-role">{{ primaryRole }}</div>
          </div>
        </div>
        
        <div class="app-version">
          <span class="version-text">Version {{ appVersion }}</span>
        </div>
      </div>
    </div>
  </el-aside>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { MenuItem } from '@/types'
import { 
  Expand, 
  Fold, 
  User,
  House,
  ChatDotRound,
  EditPen,
  Document,
  UserFilled,
  Setting,
  FolderOpened,
  Dashboard
} from '@element-plus/icons-vue'

interface Props {
  menuItems: MenuItem[]
  portal?: 'admin' | 'consumer'
  defaultCollapsed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  portal: 'consumer',
  defaultCollapsed: false
})

const emit = defineEmits<{
  collapse: [collapsed: boolean]
  menuSelect: [route: string]
}>()

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Reactive state
const collapsed = ref(props.defaultCollapsed)
const appVersion = ref('1.0.0')

// Computed properties
const user = computed(() => authStore.user)
const portalClass = computed(() => `portal-${props.portal}`)
const activeRoute = computed(() => route.path)
const primaryRole = computed(() => {
  const roles = user.value?.roles || []
  return roles.length > 0 ? roles[0].name : 'User'
})

// Methods
const toggleCollapse = () => {
  collapsed.value = !collapsed.value
  emit('collapse', collapsed.value)
  
  // Store preference in localStorage
  localStorage.setItem('sidebar-collapsed', collapsed.value.toString())
}

const handleMenuSelect = (route: string) => {
  if (route.startsWith('/')) {
    router.push(route)
    emit('menuSelect', route)
  }
}

const hasPermission = (permission?: string) => {
  if (!permission) return true
  return authStore.checkPermission(permission)
}

// Restore collapse state from localStorage
const restoreCollapseState = () => {
  const stored = localStorage.getItem('sidebar-collapsed')
  if (stored) {
    collapsed.value = stored === 'true'
  }
}

// Watch for responsive behavior
watch(() => collapsed.value, (newValue) => {
  emit('collapse', newValue)
})

// Initialize
restoreCollapseState()
</script>

<style scoped>
.app-sidebar {
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color);
  transition: width 0.3s ease;
  overflow: visible;
  position: relative;
}

.portal-admin {
  background: linear-gradient(180deg, #f0f8ff, #ffffff);
  border-right: 1px solid #1890ff;
}

.portal-consumer {
  background: linear-gradient(180deg, #f6ffed, #ffffff);
  border-right: 1px solid #52c41a;
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.collapse-toggle {
  position: absolute;
  top: 20px;
  right: -12px;
  z-index: 10;
  width: 24px;
  height: 24px;
  background: var(--el-color-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.collapse-toggle:hover {
  background: var(--el-color-primary-dark-2);
  transform: scale(1.1);
}

.sidebar-menu {
  flex: 1;
  border: none;
  padding-top: 60px;
}

.sidebar-menu:not(.el-menu--collapse) {
  padding: 60px 12px 0;
}

.sidebar-menu .el-menu-item,
.sidebar-menu .el-sub-menu > .el-sub-menu__title {
  height: 48px;
  line-height: 48px;
  margin-bottom: 4px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.portal-admin .sidebar-menu .el-menu-item:hover,
.portal-admin .sidebar-menu .el-sub-menu > .el-sub-menu__title:hover {
  background: rgba(24, 144, 255, 0.1);
  color: #1890ff;
}

.portal-consumer .sidebar-menu .el-menu-item:hover,
.portal-consumer .sidebar-menu .el-sub-menu > .el-sub-menu__title:hover {
  background: rgba(82, 196, 26, 0.1);
  color: #52c41a;
}

.portal-admin .sidebar-menu .el-menu-item.is-active {
  background: #1890ff;
  color: white;
}

.portal-consumer .sidebar-menu .el-menu-item.is-active {
  background: #52c41a;
  color: white;
}

.sidebar-menu .el-menu-item.is-active .el-icon,
.sidebar-menu .el-menu-item.is-active span {
  color: inherit;
}

.menu-badge {
  margin-left: 8px;
}

.menu-badge :deep(.el-badge__content) {
  background: var(--el-color-danger);
  border: none;
  font-size: 10px;
  height: 16px;
  line-height: 16px;
  padding: 0 5px;
  min-width: 16px;
}

.sidebar-footer {
  padding: 16px 12px;
  border-top: 1px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-extra-light);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.user-details {
  flex: 1;
  overflow: hidden;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-role {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-version {
  text-align: center;
}

.version-text {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
}

/* Collapsed state */
.collapsed .sidebar-menu {
  padding-top: 60px;
}

.collapsed .sidebar-footer {
  display: none;
}

.collapsed .menu-badge {
  display: none;
}

/* Sub-menu styles */
.sidebar-menu .el-sub-menu .el-menu-item {
  height: 40px;
  line-height: 40px;
  margin-bottom: 2px;
  margin-left: 8px;
  margin-right: 8px;
  background: var(--el-fill-color-lighter);
}

.sidebar-menu .el-sub-menu .el-menu-item:hover {
  background: var(--el-fill-color);
}

/* Icon spacing */
.sidebar-menu .el-icon {
  margin-right: 8px;
  font-size: 16px;
}

.collapsed .sidebar-menu .el-icon {
  margin-right: 0;
}

/* Responsive design */
@media (max-width: 768px) {
  .app-sidebar {
    position: fixed;
    left: 0;
    top: 60px;
    bottom: 0;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .app-sidebar.mobile-open {
    transform: translateX(0);
  }
  
  .collapse-toggle {
    display: none;
  }
}

/* Smooth transitions */
.sidebar-menu .el-menu-item,
.sidebar-menu .el-sub-menu__title {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Custom scrollbar for menu */
.sidebar-content::-webkit-scrollbar {
  width: 4px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: var(--el-border-color);
  border-radius: 2px;
}

.sidebar-content::-webkit-scrollbar-thumb:hover {
  background: var(--el-border-color-darker);
}
</style>