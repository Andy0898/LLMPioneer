import { ref, onMounted, onUnmounted } from 'vue'

interface PerformanceMetrics {
  fps: number
  memoryUsage: number
  renderTime: number
  navigationTiming: PerformanceNavigationTiming | null
}

export function usePerformanceMonitor() {
  const metrics = ref<PerformanceMetrics>({
    fps: 0,
    memoryUsage: 0,
    renderTime: 0,
    navigationTiming: null
  })

  let frameCount = 0
  let lastTime = performance.now()
  let animationFrameId: number | null = null

  // FPS calculation
  const calculateFPS = () => {
    frameCount++
    const currentTime = performance.now()
    
    if (currentTime - lastTime >= 1000) {
      metrics.value.fps = Math.round((frameCount * 1000) / (currentTime - lastTime))
      frameCount = 0
      lastTime = currentTime
    }
    
    animationFrameId = requestAnimationFrame(calculateFPS)
  }

  // Memory usage (if available)
  const getMemoryUsage = () => {
    if ('memory' in performance) {
      const memory = (performance as any).memory
      metrics.value.memoryUsage = Math.round(memory.usedJSHeapSize / 1024 / 1024) // MB
    }
  }

  // Navigation timing
  const getNavigationTiming = () => {
    if ('getEntriesByType' in performance) {
      const navigationEntries = performance.getEntriesByType('navigation')
      if (navigationEntries.length > 0) {
        metrics.value.navigationTiming = navigationEntries[0] as PerformanceNavigationTiming
      }
    }
  }

  // Measure render time for a specific operation
  const measureRenderTime = async <T>(operation: () => Promise<T> | T): Promise<T> => {
    const startTime = performance.now()
    const result = await operation()
    const endTime = performance.now()
    metrics.value.renderTime = endTime - startTime
    return result
  }

  // Performance observer for long tasks
  const observeLongTasks = () => {
    if ('PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.duration > 50) { // Tasks longer than 50ms
              console.warn(`Long task detected: ${entry.duration}ms`, entry)
            }
          }
        })
        observer.observe({ entryTypes: ['longtask'] })
        return observer
      } catch (error) {
        console.warn('PerformanceObserver not supported for longtask')
      }
    }
    return null
  }

  // Mark and measure custom events
  const mark = (name: string) => {
    if ('mark' in performance) {
      performance.mark(name)
    }
  }

  const measure = (name: string, startMark: string, endMark?: string) => {
    if ('measure' in performance) {
      try {
        if (endMark) {
          performance.measure(name, startMark, endMark)
        } else {
          performance.measure(name, startMark)
        }
        
        const measures = performance.getEntriesByName(name, 'measure')
        if (measures.length > 0) {
          return measures[measures.length - 1].duration
        }
      } catch (error) {
        console.warn(`Failed to measure ${name}:`, error)
      }
    }
    return 0
  }

  // Get resource timing
  const getResourceTiming = () => {
    if ('getEntriesByType' in performance) {
      return performance.getEntriesByType('resource') as PerformanceResourceTiming[]
    }
    return []
  }

  // Core Web Vitals
  const getCoreWebVitals = () => {
    const vitals = {
      lcp: 0, // Largest Contentful Paint
      fid: 0, // First Input Delay
      cls: 0  // Cumulative Layout Shift
    }

    if ('PerformanceObserver' in window) {
      // LCP
      try {
        new PerformanceObserver((list) => {
          const entries = list.getEntries()
          if (entries.length > 0) {
            vitals.lcp = entries[entries.length - 1].startTime
          }
        }).observe({ entryTypes: ['largest-contentful-paint'] })
      } catch (error) {
        console.warn('LCP observer not supported')
      }

      // FID
      try {
        new PerformanceObserver((list) => {
          const entries = list.getEntries()
          if (entries.length > 0) {
            vitals.fid = (entries[0] as any).processingStart - entries[0].startTime
          }
        }).observe({ entryTypes: ['first-input'] })
      } catch (error) {
        console.warn('FID observer not supported')
      }

      // CLS
      try {
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!(entry as any).hadRecentInput) {
              vitals.cls += (entry as any).value
            }
          }
        }).observe({ entryTypes: ['layout-shift'] })
      } catch (error) {
        console.warn('CLS observer not supported')
      }
    }

    return vitals
  }

  let longTaskObserver: PerformanceObserver | null = null

  onMounted(() => {
    animationFrameId = requestAnimationFrame(calculateFPS)
    getNavigationTiming()
    longTaskObserver = observeLongTasks()
    
    // Update memory usage periodically
    const memoryInterval = setInterval(getMemoryUsage, 5000)
    
    onUnmounted(() => {
      clearInterval(memoryInterval)
    })
  })

  onUnmounted(() => {
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId)
    }
    if (longTaskObserver) {
      longTaskObserver.disconnect()
    }
  })

  return {
    metrics,
    measureRenderTime,
    mark,
    measure,
    getResourceTiming,
    getCoreWebVitals
  }
}

// Utility function to log performance data
export function logPerformanceData() {
  if ('getEntriesByType' in performance) {
    console.group('Performance Data')
    
    // Navigation timing
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
    if (navigation) {
      console.log('Page Load Time:', navigation.loadEventEnd - navigation.navigationStart, 'ms')
      console.log('DOM Content Loaded:', navigation.domContentLoadedEventEnd - navigation.navigationStart, 'ms')
      console.log('First Paint:', navigation.responseStart - navigation.navigationStart, 'ms')
    }
    
    // Resource timing
    const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[]
    const slowResources = resources.filter(r => r.duration > 1000)
    if (slowResources.length > 0) {
      console.warn('Slow Resources (>1s):', slowResources)
    }
    
    // Memory usage
    if ('memory' in performance) {
      const memory = (performance as any).memory
      console.log('Memory Usage:', {
        used: Math.round(memory.usedJSHeapSize / 1024 / 1024) + 'MB',
        total: Math.round(memory.totalJSHeapSize / 1024 / 1024) + 'MB',
        limit: Math.round(memory.jsHeapSizeLimit / 1024 / 1024) + 'MB'
      })
    }
    
    console.groupEnd()
  }
}