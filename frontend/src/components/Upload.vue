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
      <div v-else class="max-w-2xl mx-auto">
        <div class="text-2xl mb-3">
          {{ allDone ? '🎉' : '⏳' }}
        </div>
        <p class="font-medium text-gray-700 mb-1">
          {{ allDone ? `全部完成！成功 ${successCount} 个` : '正在逐文件上传并解析...' }}
        </p>
        <p class="text-sm text-gray-400 mb-4">
          {{ completedCount }} / {{ totalCount }} 个文件
          <span v-if="failedCount > 0" class="text-red-500 ml-2">{{ failedCount }} 个失败</span>
        </p>

        <!-- Overall progress bar -->
        <div class="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden mb-6">
          <div
            class="h-full rounded-full transition-all duration-500"
            :class="failedCount > 0 && !allDone ? 'bg-yellow-500' : 'bg-primary-600'"
            :style="{ width: overallProgress + '%' }"
          ></div>
        </div>

        <!-- Per-file list with stages -->
        <div class="text-left space-y-1.5 max-h-72 overflow-y-auto">
          <div
            v-for="(item, idx) in fileItems"
            :key="idx"
            class="flex items-center gap-2.5 text-sm p-2.5 rounded-lg"
            :class="item.status === 'error' ? 'bg-red-50' : item.status === 'done' ? 'bg-green-50' : 'bg-gray-50'"
          >
            <!-- Stage icon -->
            <span class="flex-shrink-0 w-6 text-center text-sm">
              {{ stageIcon(item.status) }}
            </span>

            <!-- File info -->
            <span class="flex-1 truncate text-gray-700 text-xs" :title="item.file.name">
              {{ item.file.name }}
            </span>

            <!-- Stage label -->
            <span class="flex-shrink-0 text-xs font-medium min-w-[60px] text-right"
              :class="{
                'text-gray-400': item.status === 'pending',
                'text-blue-500': item.status === 'uploading',
                'text-purple-500': item.status === 'parsing',
                'text-orange-500': item.status === 'indexing',
                'text-green-600': item.status === 'done',
                'text-red-500': item.status === 'error',
              }">
              {{ stageLabel(item.status) }}
            </span>

            <!-- Progress percentage or retry button -->
            <template v-if="item.status === 'error'">
              <button
                @click="retryFile(idx)"
                class="flex-shrink-0 text-xs px-2.5 py-1 rounded-lg bg-red-100 text-red-700 hover:bg-red-200 transition-colors font-medium"
                :disabled="retrying.has(idx)"
              >
                {{ retrying.has(idx) ? '⏳' : '🔄 重试' }}
              </button>
            </template>
            <template v-else>
              <span class="flex-shrink-0 text-xs text-gray-400 w-10 text-right">
                {{ item.status === 'done' ? '' : item.progress + '%' }}
              </span>
            </template>
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
          <button @click="goToDocuments" class="btn-secondary text-xs py-1.5 px-3">
            📚 查看全部
          </button>
        </div>
      </div>

      <!-- Failed results -->
      <div v-if="failedItems.length > 0 && results.length > 0" class="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
        <p class="text-sm font-medium text-yellow-800 mb-2">
          ⚠️ {{ failedItems.length }} 个文件处理失败
        </p>
        <ul class="text-xs text-yellow-700 space-y-1">
          <li v-for="(item, idx) in failedItems" :key="idx">
            {{ item.file.name }} — {{ item.error || '未知错误' }}
          </li>
        </ul>
      </div>

      <div class="text-center">
        <button @click="resetUpload" class="btn-secondary text-sm mt-2">
          📤 继续上传
        </button>
      </div>
    </div>

    <!-- All-failed state -->
    <div v-if="results.length === 0 && allDone && totalCount > 0 && failedCount > 0" class="mt-8 space-y-4">
      <div class="p-6 bg-red-50 border border-red-200 rounded-xl text-center">
        <span class="text-4xl block mb-3">❌</span>
        <h3 class="font-semibold text-red-800 mb-2">全部上传失败</h3>
        <p class="text-sm text-red-600 mb-4">{{ failedItems.length }} 个文件均未能成功处理</p>
        <div class="text-left max-w-md mx-auto space-y-2 mb-4">
          <div
            v-for="(item, idx) in failedItems"
            :key="idx"
            class="flex items-center justify-between text-sm p-2 bg-white rounded-lg"
          >
            <span class="truncate flex-1 text-gray-700 text-xs">{{ item.file.name }}</span>
            <button
              @click="retryFile(fileItems.indexOf(item))"
              class="flex-shrink-0 text-xs px-3 py-1 rounded-lg bg-red-100 text-red-700 hover:bg-red-200 transition-colors ml-2"
            >
              🔄 重试
            </button>
          </div>
        </div>
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
import { uploadFile } from '../api/index.js'

const router = useRouter()
const fileInput = ref(null)
const folderInput = ref(null)
const isDragging = ref(false)
const uploading = ref(false)
const totalCount = ref(0)
const fileItems = ref([])
const results = ref([])
const errorMsg = ref('')
const retrying = ref(new Set())

const completedCount = computed(() => fileItems.value.filter((i) => i.status === 'done').length)
const failedCount = computed(() => fileItems.value.filter((i) => i.status === 'error').length)
const successCount = computed(() => results.value.length)
const allDone = computed(() => {
  if (totalCount.value === 0) return false
  return fileItems.value.every((i) => i.status === 'done' || i.status === 'error')
})
const failedItems = computed(() => fileItems.value.filter((i) => i.status === 'error'))
const overallProgress = computed(() => {
  if (totalCount.value === 0) return 0
  const total = fileItems.value.reduce((sum, item) => sum + item.progress, 0)
  return Math.round(total / totalCount.value)
})

function stageIcon(status) {
  const icons = {
    pending: '⏸️',
    uploading: '⬆️',
    parsing: '🔍',
    indexing: '📇',
    done: '✅',
    error: '❌',
  }
  return icons[status] || '⏸️'
}

function stageLabel(status) {
  const labels = {
    pending: '等待中',
    uploading: '上传中',
    parsing: '解析中',
    indexing: '索引中',
    done: '已完成',
    error: '失败',
  }
  return labels[status] || status
}

function triggerFileInput() {
  if (uploading.value && !allDone.value) return
  fileInput.value?.click()
}

function triggerFolderInput() {
  if (uploading.value && !allDone.value) return
  folderInput.value?.click()
}

function handleDrop(e) {
  isDragging.value = false
  const files = Array.from(e.dataTransfer?.files || [])
  if (files.length > 0) {
    const valid = files.filter((f) => {
      const ext = f.name.split('.').pop()?.toLowerCase()
      return ['pdf', 'docx', 'doc', 'txt', 'md'].includes(ext)
    })
    if (valid.length > 0) startUpload(valid)
  }
}

function handleFileSelect(e) {
  const files = Array.from(e.target.files || [])
  if (files.length > 0) startUpload(files)
  e.target.value = ''
}

async function startUpload(files) {
  errorMsg.value = ''
  results.value = []
  totalCount.value = files.length

  fileItems.value = files.map((file) => ({
    file,
    status: 'pending',
    progress: 0,
    error: '',
  }))

  uploading.value = true

  // Upload files sequentially for accurate per-file progress
  for (let i = 0; i < files.length; i++) {
    await uploadSingleFile(i)
  }
}

async function uploadSingleFile(index) {
  const item = fileItems.value[index]
  if (!item) return

  const formData = new FormData()
  formData.append('file', item.file)

  // Stage 1: Uploading
  item.status = 'uploading'
  item.progress = 0

  try {
    const res = await uploadFile(formData, (e) => {
      if (e.total) {
        // Upload progress: 0-70%
        item.progress = Math.round((e.loaded / e.total) * 70)
      }
    })

    // Stage 2: Parsing & Indexing (simulated progress: 70-100%)
    item.status = 'parsing'
    item.progress = 75
    await sleep(150)

    item.status = 'indexing'
    item.progress = 85
    await sleep(150)

    // Done
    item.status = 'done'
    item.progress = 100
    item.error = ''
    results.value.push(res.data)
  } catch (err) {
    item.status = 'error'
    item.progress = 0
    const detail = err.response?.data?.detail
    item.error = typeof detail === 'string' ? detail : (err.message || '上传失败')
  }
}

async function retryFile(index) {
  retrying.value.add(index)
  errorMsg.value = ''
  const item = fileItems.value[index]
  if (!item) return

  try {
    await uploadSingleFile(index)
  } finally {
    retrying.value.delete(index)
  }
}

function goToChat(docId) {
  router.push({ path: '/chat', query: { docId } })
}

function goToDocuments() {
  router.push('/documents')
}

function resetUpload() {
  results.value = []
  fileItems.value = []
  totalCount.value = 0
  errorMsg.value = ''
  uploading.value = false
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}
</script>
