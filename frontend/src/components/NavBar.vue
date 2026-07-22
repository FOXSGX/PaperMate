<template>
  <nav class="bg-white border-b border-gray-100 sticky top-0 z-50 backdrop-blur-sm bg-white/95">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <span class="text-2xl">📄</span>
          <span class="text-xl font-bold text-gray-900">PaperMate</span>
        </router-link>

        <!-- Desktop Nav -->
        <div class="hidden md:flex items-center gap-1">
          <router-link v-for="item in navItems" :key="item.path" :to="item.path"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200"
            :class="isActive(item.path)
              ? 'bg-primary-50 text-primary-700'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'">
            <span class="mr-1.5">{{ item.icon }}</span>
            {{ item.label }}
          </router-link>
        </div>

        <!-- Mobile Menu Toggle -->
        <button @click="mobileOpen = !mobileOpen" class="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors">
          <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="!mobileOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Mobile Nav -->
      <div v-show="mobileOpen" class="md:hidden border-t border-gray-100 py-2 pb-4">
        <router-link v-for="item in navItems" :key="item.path" :to="item.path" @click="mobileOpen = false"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors duration-200"
          :class="isActive(item.path)
            ? 'bg-primary-50 text-primary-700'
            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'">
          <span>{{ item.icon }}</span>
          {{ item.label }}
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const mobileOpen = ref(false)

const navItems = [
  { path: '/', label: '首页', icon: '🏠' },
  { path: '/upload', label: '文件上传', icon: '📤' },
  { path: '/documents', label: '文档管理', icon: '📚' },
  { path: '/chat', label: '智能问答', icon: '💬' },
  { path: '/survey', label: '综述生成', icon: '📝' },
  { path: '/format', label: '排版降重', icon: '✨' },
]

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>
