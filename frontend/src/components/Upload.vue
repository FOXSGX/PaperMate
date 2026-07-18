<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <!-- Header -->
    <div class="text-center mb-10">
      <span class="text-5xl mb-4 block">📤</span>
      <h1 class="text-3xl font-bold text-gray-900 mb-2">文件上传</h1>
      <p class="text-gray-500">上传 PDF / DOCX / TXT / MD 文件，系统自动解析并建立索引</p>
    </div>

    <!-- Drag & Drop Zone -->
    <div
      class="border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300"
      :class="isDragging
        ? 'border-primary-500 bg-primary-50 scale-[1.02]'
        : 'border-gray-300 bg-white hover:border-primary-300 hover:bg-gray-50'"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
    >
      <!-- Hidden inputs -->
      <input
        ref="fileInput"
        type="file"
        accept=".pdf,.docx,.txt,.md"
        multiple
        class="hidden"
        @change="handleFileSelect"
      />
      <input
        ref="folderInput"
        type="file"
        accept=".pdf,.docx,.txt,.md"
        webkitdirectory
        directory
        class="hidden"
        @change="handleFileSelect"
      />

      <div v-if="!uploading">
        <div class="text-6xl mb-4">📁</div>
        <p class="text-lg font-medium text-gray-700 mb-2">点击下方按钮或拖拽文件/文件夹到此处</p>
        <p class="text-sm text-gray-400 mb-6">支持 PDF、DOCX、TXT、MD 格式，最大 30MB / 文件</p>

        <div class="flex justify-center gap-4">
          <button @click.stop="triggerFileInput" class="btn-primary text-sm px-6 py-2.5">
            📄 选择文件
          </button>
          <button @click.stop="triggerFolderInput" class="btn-secondary text-sm px-6 py-2.5">
            📁 选择文件夹
          </button>
        </div>
      </div>

      <!-- Uploading Progress -->
      <div v-else class="max-w-lg mx-auto">
        <div class="text-2xl mb-3">⏳</div>
        <p class="font-medium text-gray-700 mb-1">正在上传并解析...</p>
        <p class="text-sm text-gray-400 mb-4">
          {{ completedCount }} / {{ totalCount }} 个文件
        </p>
        <!-- Overall progress bar -->
        <div class="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden mb-6">
          <div
            class="bg-primary-600 h-full rounded-full transition-all duration-500"
            :style="{ width: overallProgress + '%' }"
          ></div>
        </div>

        <!-- Per-file list -->
        <div class="text-left space-y-2 max-h-60 overflow-y-auto">
          <div
            v-for="(item, idx) in fileItems"
            :key="idx"
            class="flex items-center gap-3 text-sm p-2 rounded-lg"
            :class="item.status === 'error' ? 'bg-red-50' : item.status === 'done' ? 'bg-green-50' : 'bg-gray-50'"
          >
            <span class="flex-shrink-0 w-5 text-center">
              {{ item.status === 'uploading' ? '⏳' : item.status === 'done' ? '✅' : '❌' }}
            </span>
            <span class="flex-1 truncate text-gray-700" :title="item.file.name">{{ item.file.name }}</span>
            <span class="flex-shrink-0 text-xs text-gray-400 w-12 text-right">
              {{ item.status === 'done' ? '' : item.status === 'error' ? '失败' : item.progress + '%' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Batch Results -->
    <div v-if="results.length > 0" class="mt-8 space-y-4">
      <div class="flex items-center gap-2 mb-2">
        <span class="text-xl">📋</span>
        <h3 class="font-semibold text-gray-900">
          上传结果（{{ results.length }} / {{ totalCount }} 成功）
        </h3>
      </div>

      <div
        v-for="(r, idx) in results"
        :key="idx"
        class="card animate-slide-up"
      >
        <div class="flex items-center gap-3 mb-3">
          <span class="text-2xl">✅</span>
          <div>
            <h3 class="font-semibold text-gray-900 text-sm">{{ r.filename }}</h3>
            <p class="text-xs text-gray-400 font-mono">{{ r.document_id?.slice(0, 16) }}...</p>
          </div>
        </div>
        <div class="grid grid-cols-3 gap-3 text-center">
          <div class="bg-gray-50 rounded-lg p-2">
            <p class="text-xs text-gray-500">格式</p>
            <p class="text-sm font-medium text-gray-700">{{ r.content_type }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-2">
            <p class="text-xs text-gray-500">切片数</p>
            <p class="text-sm font-medium text-gray-700">{{ r.chunks }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-2">
            <p class="text-xs text-gray-500">状态</p>
            <p class="text-sm font-medium text-green-600">索引完成</p>
          </div>
        </div>
        <div class="mt-3 flex gap-2">
          <button @click="goToChat(r.document_id)" class="btn-primary text-xs flex-1 py-1.5">
            💬 智能问答
          </button>
        </div>
      </div>

      <div class="text-center">
        <button @click="resetUpload" class="btn-secondary text-sm mt-2">
          继续上传
        </button>
      </div>
    </div>

    <!-- Error -->
    <div v-if="errorMsg" class="mt-8 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm animate-fade-in">
      ⚠️ {{ errorMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { uploadFiles } from '../api/index.js'

const router = useRouter()
const fileInput = ref(null)
const folderInput = ref(null)
const isDragging = ref(false)
const uploading = ref(false)
const totalCount = ref(0)
const completedCount = ref(0)
const fileItems = ref([])
const results = ref([])
const errorMsg = ref('')

const overallProgress = computed(() => {
  if (totalCount.value === 0) return 0
  const total = fileItems.value.reduce((sum, item) => sum + item.progress, 0)
  return Math.round(total / totalCount.value)
})

function triggerFileInput() {
  if (uploading.value) return
  fileInput.value?.click()
}

function triggerFolderInput() {
  if (uploading.value) return
  folderInput.value?.click()
}

function handleDrop(e) {
  isDragging.value = false
  const files = Array.from(e.dataTransfer?.files || [])
  if (files.length > 0) startUpload(files)
}

function handleFileSelect(e) {
  const files = Array.from(e.target.files || [])
  if (files.length > 0) startUpload(files)
  // Reset input so the same folder/file can be re-selected
  e.target.value = ''
}

async function startUpload(files) {
  errorMsg.value = ''
  results.value = []
  totalCount.value = files.length
  completedCount.value = 0

  fileItems.value = files.map((file) => ({
    file,
    status: 'pending',
    progress: 0,
  }))

  uploading.value = true

  try {
    const res = await uploadFiles(files, (e) => {
      if (e.total) {
        // Distribute progress across all files
        const overall = Math.round((e.loaded / e.total) * 100)
        const doneCount = Math.floor((overall / 100) * files.length)
        completedCount.value = Math.min(doneCount, files.length)

        fileItems.value.forEach((item, idx) => {
          if (idx < doneCount) {
            item.status = 'done'
            item.progress = 100
          } else if (idx === doneCount) {
            item.status = 'uploading'
            // Fractional progress for the current file
            const frac = (overall / 100) * files.length - doneCount
            item.progress = Math.round(frac * 100)
          } else {
            item.status = 'pending'
            item.progress = 0
          }
        })
      }
    })

    results.value = res.data || []
    completedCount.value = files.length
    fileItems.value.forEach((item) => {
      item.status = 'done'
      item.progress = 100
    })
  } catch (err) {
    const detail = err.response?.data?.detail
    if (typeof detail === 'object' && detail.errors) {
      errorMsg.value = detail.errors.map((e) => `${e.filename}: ${e.error}`).join('; ')
    } else {
      errorMsg.value = typeof detail === 'string' ? detail : (err.message || '上传失败，请重试')
    }
    // Mark failed items
    fileItems.value.forEach((item) => {
      if (item.status !== 'done') item.status = 'error'
    })
  } finally {
    uploading.value = false
  }
}

function goToChat(docId) {
  router.push({ path: '/chat', query: { docId } })
}

function resetUpload() {
  results.value = []
  fileItems.value = []
  totalCount.value = 0
  completedCount.value = 0
  errorMsg.value = ''
}
</script>
