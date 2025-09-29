<template>
  <div
    ref="containerRef"
    class="virtual-scroll-container"
    :style="{ height: containerHeight + 'px' }"
    @scroll="handleScroll"
  >
    <div
      class="virtual-scroll-spacer"
      :style="{ height: totalHeight + 'px' }"
    >
      <div
        class="virtual-scroll-content"
        :style="{ transform: `translateY(${offsetY}px)` }"
      >
        <div
          v-for="(item, index) in visibleItems"
          :key="getItemKey(item, startIndex + index)"
          class="virtual-scroll-item"
          :style="{ height: itemHeight + 'px' }"
        >
          <slot :item="item" :index="startIndex + index" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'

interface Props {
  items: any[]
  itemHeight: number
  containerHeight: number
  overscan?: number
  getItemKey?: (item: any, index: number) => string | number
}

const props = withDefaults(defineProps<Props>(), {
  overscan: 5,
  getItemKey: (item: any, index: number) => index
})

// Reactive state
const containerRef = ref<HTMLElement>()
const scrollTop = ref(0)

// Computed properties
const totalHeight = computed(() => props.items.length * props.itemHeight)

const startIndex = computed(() => {
  const index = Math.floor(scrollTop.value / props.itemHeight)
  return Math.max(0, index - props.overscan)
})

const endIndex = computed(() => {
  const visibleCount = Math.ceil(props.containerHeight / props.itemHeight)
  const index = startIndex.value + visibleCount + props.overscan * 2
  return Math.min(props.items.length - 1, index)
})

const visibleItems = computed(() => {
  return props.items.slice(startIndex.value, endIndex.value + 1)
})

const offsetY = computed(() => startIndex.value * props.itemHeight)

// Methods
const handleScroll = () => {
  if (containerRef.value) {
    scrollTop.value = containerRef.value.scrollTop
  }
}

const scrollToIndex = (index: number) => {
  if (containerRef.value) {
    const targetScrollTop = index * props.itemHeight
    containerRef.value.scrollTop = targetScrollTop
  }
}

const scrollToTop = () => {
  scrollToIndex(0)
}

const scrollToBottom = () => {
  scrollToIndex(props.items.length - 1)
}

// Watch for items changes to reset scroll if needed
watch(
  () => props.items.length,
  (newLength, oldLength) => {
    if (newLength !== oldLength && newLength === 0) {
      scrollTop.value = 0
    }
  }
)

// Lifecycle
onMounted(() => {
  nextTick(() => {
    if (containerRef.value) {
      containerRef.value.addEventListener('scroll', handleScroll, { passive: true })
    }
  })
})

onUnmounted(() => {
  if (containerRef.value) {
    containerRef.value.removeEventListener('scroll', handleScroll)
  }
})

// Expose methods
defineExpose({
  scrollToIndex,
  scrollToTop,
  scrollToBottom
})
</script>

<style scoped>
.virtual-scroll-container {
  overflow-y: auto;
  position: relative;
}

.virtual-scroll-spacer {
  position: relative;
}

.virtual-scroll-content {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
}

.virtual-scroll-item {
  display: flex;
  align-items: center;
  box-sizing: border-box;
}
</style>