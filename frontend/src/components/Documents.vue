<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <!-- Header -->
    <div class="text-center mb-10">
      <span class="text-5xl mb-4 block">📚</span>
      <h1 class="text-3xl font-bold text-gray-900 mb-2">文档管理</h1>
      <p class="text-gray-500">管理已上传的文档，查看索引状态，快速进入问答</p>
    </div>

    <!-- Action Bar -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <button @click="refreshList" class="btn-secondary text-sm px-4 py-2" :disabled="loading">
          <span v-if="!loading">🔄 刷新</span>
          <span v-else>⏳ 加载中...</span>
        </button>
        <span v-if="docs.length > 0" class="text-sm text-gray-400">
          共 {{ docs.length }} 个文档
        </span>
      </div>
      <router-link to="/upload" class="btn-primary text-sm px-4 py-2">
        📤 上传新文档
      </router-link>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && docs.length === 0" class="card text-center py-16">
      <span class="text-6xl block mb-4">📭</span>
      <h3 class="text-lg font-semibold text-gray-700 mb-2">暂无文档</h3>
      <p class="text-gray-500 mb-6">还没有上传任何文档，点击下方按钮开始上传</p>
      <router-link to="/upload" class="btn-primary inline-block text-sm">
        📤 去上传文档
      </router-link>
    </div>

    <!-- Loading Skeleton -->
    <div v-if="loading" class="space-y-4">
      <div v-for="n in 3" :key="n" class="card animate-pulse">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-gray-200 rounded-lg"></div>
          <div class="flex-1 space-y-2">
            <div class="h-4 bg-gray-200 rounded w-1/3"></div>
            <div class="h-3 bg-gray-100 rounded w-1/4"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Document List -->
    <div v-if="!loading && docs.length > 0" class="space-y-4">
      <div
        v-for="doc in docs"
        :key="doc.document_id"
        class="card animate-slide-up hover:border-primary-200 transition-all duration-300"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-start gap-4 flex-1 min-w-0">
            <!-- File Type Icon -->
            <span class="text-3xl p-2.5 rounded-xl bg-gray-50 shrink-0">
              {{ getFileIcon(doc.filename) }}
            </span>

            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-gray-900 mb-1 truncate" :title="doc.filename">
                {{ doc.filename || '未知文件' }}
              </h3>
              <div class="flex flex-wrap items-center gap-3 text-xs text-gray-500">
                <span class="font-mono bg-gray-100 px-2 py-0.5 rounded" :title="doc.document_id">
                  ID: {{ doc.document_id?.slice(0, 12) }}...
                </span>
                <span>📊 {{ doc.chunks }} 个切片</span>
                <span>📅 {{ formatDate(doc.indexed_at) }}</span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2 shrink-0">
            <button
              @click="goToChat(doc.document_id)"
              class="btn-primary text-xs px-4 py-2"
            >
              💬 问答
            </button>
            <button
              @click="confirmDelete(doc)"
              class="text-xs px-3 py-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              :disabled="deleting === doc.document_id"
            >
              {{ deleting === doc.document_id ? '⏳' : '🗑️' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
    >
      <div class="bg-white rounded-2xl p-6 max-w-sm w-full mx-4 shadow-xl animate-slide-up">
        <h3 class="text-lg font-semibold text-gray-900 mb-2">确认删除</h3>
        <p class="text-sm text-gray-500 mb-1">
          确定要删除文档 <span class="font-mono text-primary-700">{{ deleteTarget?.document_id?.slice(0, 16) }}...</span> 吗？
        </p>
        <p class="text-xs text-red-500 mb-6">此操作不可撤销，文档索引和上传文件将被永久删除。</p>
        <div class="flex gap-3 justify-end">
          <button @click="showDeleteModal = false" class="btn-secondary text-sm px-4 py-2">
            取消
          </button>
          <button @click="doDelete" class="bg-red-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-red-700 transition-colors">
            确认删除
          </button>
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-if="errorMsg" class="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm animate-fade-in">
      ⚠️ {{ errorMsg }}
    </div>

    <!-- Success Toast -->
    <div
      v-if="toastMsg"
      class="fixed bottom-6 right-6 bg-green-600 text-white px-5 py-3 rounded-xl shadow-lg animate-slide-up text-sm z-50"
    >
      ✅ {{ toastMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listDocuments, deleteDocument } from '../api/index.js'

const router = useRouter()
const docs = ref([])
const loading = ref(false)
const errorMsg = ref('')
const toastMsg = ref('')
const deleting = ref(null)
const showDeleteModal = ref(false)
const deleteTarget = ref(null)

onMounted(() => {
  refreshList()
})

async function refreshList() {
  errorMsg.value = ''
  loading.value = true
  try {
    const res = await listDocuments()
    docs.value = res.data || []
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || err.message || '获取文档列表失败'
  } finally {
    loading.value = false
  }
}

function confirmDelete(doc) {
  deleteTarget.value = doc
  showDeleteModal.value = true
}

async function doDelete() {
  if (!deleteTarget.value) return
  const docId = deleteTarget.value.document_id
  showDeleteModal.value = false
  deleting.value = docId
  errorMsg.value = ''

  try {
    await deleteDocument(docId)
    docs.value = docs.value.filter((d) => d.document_id !== docId)
    toastMsg.value = '文档已删除'
    setTimeout(() => (toastMsg.value = ''), 2500)
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || err.message || '删除失败'
  } finally {
    deleting.value = null
    deleteTarget.value = null
  }
}

function goToChat(docId) {
  router.push({ path: '/chat', query: { docId } })
}

function getFileIcon(filename) {
  if (!filename) return '📄'
  const ext = filename.split('.').pop()?.toLowerCase()
  const icons = { pdf: '📕', docx: '📘', doc: '📘', txt: '📃', md: '📝' }
  return icons[ext] || '📄'
}

function formatDate(ts) {
  if (!ts) return 'N/A'
  const d = new Date(ts * 1000)
  const now = new Date()
  const diff = now - d
  const mins = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (mins < 1) return '刚刚'
  if (mins < 60) return `${mins} 分钟前`
  if (hours < 24) return `${hours} 小时前`
  if (days < 7) return `${days} 天前`
  return d.toLocaleDateString('zh-CN')
}
</script>
