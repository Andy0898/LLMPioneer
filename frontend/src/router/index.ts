import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { h } from 'vue'

// Simple render function components for testing
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: {
      render() {
        return h('div', {
          style: {
            padding: '20px',
            textAlign: 'center',
            fontFamily: 'Arial, sans-serif'
          }
        }, [
          h('h1', { style: { color: '#52c41a' } }, '🌟 LLM Pioneer'),
          h('p', {}, 'Welcome! Router is working perfectly!'),
          h('div', { style: { margin: '20px 0' } }, [
            h('a', {
              href: '/user/login',
              style: {
                margin: '0 10px',
                padding: '10px 20px',
                background: '#52c41a',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '5px'
              }
            }, 'User Login'),
            h('a', {
              href: '/admin/login',
              style: {
                margin: '0 10px',
                padding: '10px 20px',
                background: '#1890ff',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '5px'
              }
            }, 'Admin Login')
          ])
        ])
      }
    }
  },
  {
    path: '/user/login',
    name: 'UserLogin',
    component: {
      render() {
        return h('div', {
          style: {
            minHeight: '100vh',
            background: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
            fontFamily: 'Arial, sans-serif'
          }
        }, [
          h('div', {
            style: {
              background: 'white',
              borderRadius: '12px',
              padding: '40px',
              boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
              maxWidth: '400px',
              width: '100%'
            }
          }, [
            h('h1', {
              style: {
                textAlign: 'center',
                color: '#52c41a',
                marginBottom: '20px'
              }
            }, '🎉 User Login'),
            h('p', {
              style: {
                textAlign: 'center',
                marginBottom: '30px'
              }
            }, 'Render function working!'),
            h('div', { style: { textAlign: 'center' } }, [
              h('input', {
                type: 'text',
                placeholder: 'Username',
                style: {
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  marginBottom: '15px'
                }
              }),
              h('input', {
                type: 'password',
                placeholder: 'Password',
                style: {
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  marginBottom: '15px'
                }
              }),
              h('button', {
                style: {
                  width: '100%',
                  padding: '12px',
                  background: '#52c41a',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer'
                },
                onClick: () => alert('Login clicked!')
              }, 'Sign In')
            ]),
            h('div', {
              style: {
                textAlign: 'center',
                marginTop: '20px'
              }
            }, [
              h('a', {
                href: '/',
                style: {
                  color: '#666',
                  textDecoration: 'none'
                }
              }, '← Back to Home')
            ])
          ])
        ])
      }
    }
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: {
      render() {
        return h('div', {
          style: {
            minHeight: '100vh',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
            fontFamily: 'Arial, sans-serif'
          }
        }, [
          h('div', {
            style: {
              background: 'white',
              borderRadius: '12px',
              padding: '40px',
              boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
              maxWidth: '400px',
              width: '100%'
            }
          }, [
            h('h1', {
              style: {
                textAlign: 'center',
                color: '#1890ff',
                marginBottom: '20px'
              }
            }, '🔧 Admin Login'),
            h('p', {
              style: {
                textAlign: 'center',
                marginBottom: '30px'
              }
            }, 'Administrator portal'),
            h('div', { style: { textAlign: 'center' } }, [
              h('input', {
                type: 'text',
                placeholder: 'Admin Username',
                style: {
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  marginBottom: '15px'
                }
              }),
              h('input', {
                type: 'password',
                placeholder: 'Password',
                style: {
                  width: '100%',
                  padding: '12px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  marginBottom: '15px'
                }
              }),
              h('button', {
                style: {
                  width: '100%',
                  padding: '12px',
                  background: '#1890ff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer'
                },
                onClick: () => alert('Admin login clicked!')
              }, 'Admin Sign In')
            ]),
            h('div', {
              style: {
                textAlign: 'center',
                marginTop: '20px'
              }
            }, [
              h('a', {
                href: '/',
                style: {
                  color: '#666',
                  textDecoration: 'none'
                }
              }, '← Back to Home')
            ])
          ])
        ])
      }
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards - temporarily disabled for testing
/*
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Set page title
  if (to.meta.title) {
    document.title = `${to.meta.title} - LLM Pioneer`
  }
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // Redirect to appropriate login page based on portal
      const portal = to.meta.portal || 'consumer'
      next({ name: portal === 'admin' ? 'AdminLogin' : 'ConsumerLogin' })
      return
    }
    
    // Check portal access
    if (to.meta.portal && to.meta.portal !== authStore.portal) {
      // Redirect to correct portal dashboard
      const correctPortal = authStore.portal === 'admin' ? 'AdminDashboard' : 'ConsumerDashboard'
      next({ name: correctPortal })
      return
    }
    
    // Check role requirements
    if (to.meta.requiresRole) {
      const hasRequiredRole = authStore.user?.roles.some((role: any) => 
        role.name === to.meta.requiresRole
      )
      if (!hasRequiredRole) {
        next({ name: 'NotFound' })
        return
      }
    }
  }
  
  // If user is authenticated and trying to access login page, redirect to dashboard
  if (to.name?.toString().includes('Login') && authStore.isAuthenticated) {
    const dashboard = authStore.portal === 'admin' ? 'AdminDashboard' : 'ConsumerDashboard'
    next({ name: dashboard })
    return
  }
  
  next()
})
*/

export default router