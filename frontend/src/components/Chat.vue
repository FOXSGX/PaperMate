<template>
  <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 h-[calc(100vh-10rem)] flex gap-4">
    <!-- Session Sidebar -->
    <div
      v-if="showSidebar"
      class="w-64 shrink-0 bg-white border border-gray-200 rounded-xl flex flex-col overflow-hidden"
    >
      <div class="p-3 border-b border-gray-100 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-gray-700">📋 历史会话</h3>
        <button
          @click="newSession"
          class="text-xs px-2 py-1 rounded-lg bg-primary-50 text-primary-700 hover:bg-primary-100 transition-colors"
          :disabled="!effectiveDocId"
        >
          + 新建
        </button>
      </div>

      <!-- Session List -->
      <div class="flex-1 overflow-y-auto">
        <div v-if="sessions.length === 0" class="p-4 text-center text-xs text-gray-400">
          暂无历史会话
        </div>
        <div
          v-for="sess in sessions"
          :key="sess.id"
          class="flex items-center gap-2 px-3 py-2.5 cursor-pointer hover:bg-gray-50 transition-colors border-b border-gray-50"
          :class="currentSessionId === sess.id ? 'bg-primary-50 border-l-2 border-l-primary-500' : ''"
          @click="switchSession(sess.id)"
        >
          <div class="flex-1 min-w-0" :title="sess.label">
            <p class="text-xs font-medium text-gray-700 truncate">{{ sess.label || '空会话' }}</p>
            <p class="text-xs text-gray-400 mt-0.5">
              {{ sess.messages.length }} 条消息 · {{ formatSessionDate(sess.updatedAt) }}
            </p>
          </div>
          <button
            @click.stop="confirmDeleteSession(sess)"
            class="text-xs text-gray-300 hover:text-red-500 transition-colors p-1"
            title="删除会话"
          >
            🗑️
          </button>
        </div>
      </div>

      <!-- Sidebar Footer -->
      <div class="p-3 border-t border-gray-100">
        <button
          @click="clearAllSessions"
          class="text-xs text-gray-400 hover:text-red-500 transition-colors w-full text-center"
          :disabled="sessions.length === 0"
        >
          清除全部会话
        </button>
      </div>
    </div>

    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Header -->
      <div class="text-center mb-4 shrink-0">
        <span class="text-3xl mb-1 block">💬</span>
        <h1 class="text-xl font-bold text-gray-900">RAG 智能问答</h1>
        <p class="text-xs text-gray-500">基于上传文档的检索增强生成问答</p>
      </div>

      <!-- Document ID Input (if not from upload page) -->
      <div v-if="!docIdFromUpload" class="mb-3 shrink-0">
        <div class="flex gap-2 max-w-md mx-auto">
          <input v-model="documentId" type="text" placeholder="输入文档 ID（上传后可获取）"
            class="input-field text-sm flex-1" />
          <button
            @click="toggleSidebar"
            class="btn-secondary text-xs px-3 py-2 shrink-0"
            :title="showSidebar ? '收起侧栏' : '展开侧栏'"
          >
            {{ showSidebar ? '◀' : '📋' }}
          </button>
        </div>
      </div>
      <div v-else class="mb-3 shrink-0">
        <div class="flex items-center justify-center gap-2">
          <div class="flex items-center gap-2 text-sm text-gray-500 bg-blue-50 rounded-lg py-2 px-4">
            <span>📄</span>
            <span class="font-mono text-xs truncate max-w-[200px]">文档：{{ docIdFromUpload }}</span>
          </div>
          <button
            @click="toggleSidebar"
            class="btn-secondary text-xs px-3 py-2 shrink-0"
            :title="showSidebar ? '收起侧栏' : '展开侧栏'"
          >
            {{ showSidebar ? '◀' : '📋' }}
          </button>
        </div>
      </div>

      <!-- Messages -->
      <div ref="msgContainer" class="flex-1 overflow-y-auto space-y-4 mb-4 pr-2 scroll-smooth">
        <!-- Empty State -->
        <div v-if="messages.length === 0" class="flex items-center justify-center h-full">
          <div class="text-center text-gray-400">
            <span class="text-6xl block mb-4">🤖</span>
            <p class="text-lg font-medium mb-2">开始提问吧</p>
            <p class="text-sm">上传文档后，输入问题即可获得基于文档内容的智能回答</p>
          </div>
        </div>

        <!-- Message Bubbles -->
        <div v-for="(msg, idx) in messages" :key="idx" class="animate-slide-up">
          <!-- User -->
          <div v-if="msg.role === 'user'" class="flex justify-end mb-3">
            <div class="bg-primary-600 text-white rounded-2xl rounded-br-md px-4 py-3 max-w-[80%]">
              <p class="text-sm whitespace-pre-wrap">{{ msg.content }}</p>
            </div>
            <span class="text-2xl ml-2 shrink-0">👤</span>
          </div>

          <!-- Assistant -->
          <div v-else class="flex mb-3">
            <span class="text-2xl mr-2 shrink-0">🤖</span>
            <div class="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 max-w-[80%] shadow-sm">
              <p class="text-sm whitespace-pre-wrap">{{ msg.content }}
                <span v-if="msg.streaming" class="inline-block w-2 h-4 bg-primary-600 animate-pulse ml-0.5 align-text-bottom"></span>
              </p>

              <!-- Citations -->
              <div v-if="msg.citations && msg.citations.length > 0" class="mt-3 pt-3 border-t border-gray-100">
                <p class="text-xs font-medium text-gray-500 mb-2">📚 引用来源</p>
                <div v-for="(cite, ci) in msg.citations" :key="ci"
                  class="text-xs text-gray-500 bg-gray-50 rounded-lg p-2 mb-1.5">
                  <p class="text-primary-600 font-medium mb-0.5">片段 {{ cite.chunk_id }} · 相关度 {{ (cite.score * 100).toFixed(0) }}%</p>
                  <p class="leading-relaxed line-clamp-3">{{ cite.text }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="shrink-0">
        <div class="flex gap-3">
          <input v-model="question" type="text" placeholder="输入你的问题..."
            class="input-field flex-1" @keyup.enter="sendQuestion" :disabled="isStreaming || loading" />
          <button @click="sendQuestion" class="btn-primary shrink-0" :disabled="isStreaming || loading || !question.trim()">
            <span v-if="!loading">发送</span>
            <span v-else>...</span>
          </button>
        </div>
        <p class="text-xs text-gray-400 mt-2 text-center">
          按 Enter 发送 · 基于 RAG 的文档问答
          <span v-if="currentSessionId" class="ml-2">· 会话自动保存</span>
        </p>
      </div>
    </div>

    <!-- Delete Session Confirmation -->
    <div
      v-if="showDeleteConfirm"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
    >
      <div class="bg-white rounded-2xl p-6 max-w-sm w-full mx-4 shadow-xl animate-slide-up">
        <h3 class="text-lg font-semibold text-gray-900 mb-2">删除会话</h3>
        <p class="text-sm text-gray-500 mb-6">确定要删除这个会话吗？此操作不可撤销。</p>
        <div class="flex gap-3 justify-end">
          <button @click="showDeleteConfirm = false" class="btn-secondary text-sm px-4 py-2">取消</button>
          <button @click="doDeleteSession" class="bg-red-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-red-700 transition-colors">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { askDocumentStream } from '../api/index.js'
import {
  getSessions,
  getActiveSessionId,
  createSession,
  loadSession,
  saveSessionMessages,
  deleteSession,
  deleteDocumentSessions,
  setActiveSessionId,
} from '../utils/chatSessions.js'

const route = useRoute()
const docIdFromUpload = ref(route.query.docId || '')

const documentId = ref('')
const question = ref('')
const messages = ref([])
const msgContainer = ref(null)
const isStreaming = ref(false)
const loading = ref(false)
const showSidebar = ref(false)
const currentSessionId = ref(null)
const sessions = ref([])
const showDeleteConfirm = ref(false)
const deleteTarget = ref(null)

const effectiveDocId = computed(() => docIdFromUpload.value || documentId.value.trim())

// Watch document changes
watch(() => route.query.docId, (val) => {
  if (val) {
    docIdFromUpload.value = val
    refreshSessions()
    autoRestoreSession()
  }
})

watch(effectiveDocId, () => {
  refreshSessions()
})

onMounted(() => {
  refreshSessions()
  autoRestoreSession()
})

function refreshSessions() {
  sessions.value = getSessions(effectiveDocId.value)
}

function autoRestoreSession() {
  const activeId = getActiveSessionId()
  if (activeId) {
    const session = loadSession(activeId)
    if (session && (!effectiveDocId.value || session.documentId === effectiveDocId.value)) {
      currentSessionId.value = session.id
      messages.value = session.messages || []
      if (!effectiveDocId.value && session.documentId) {
        if (docIdFromUpload.value) {
          // Already has doc from upload
        } else {
          documentId.value = session.documentId
        }
      }
      return
    }
  }

  // Check if there are sessions for this doc
  if (sessions.value.length > 0) {
    const lastSession = sessions.value[0]
    currentSessionId.value = lastSession.id
    messages.value = lastSession.messages || []
    setActiveSessionId(lastSession.id)
    return
  }

  // No existing session — start fresh
  messages.value = []
  currentSessionId.value = null
}

function newSession() {
  const docId = effectiveDocId.value
  if (!docId) return

  // Save current session first if it has messages
  if (currentSessionId.value && messages.value.length > 0) {
    saveSessionMessages(currentSessionId.value, effectiveDocId.value, messages.value)
  }

  const session = createSession(docId)
  currentSessionId.value = session.id
  messages.value = []
  refreshSessions()
}

function switchSession(sessionId) {
  // Save current session
  if (currentSessionId.value && messages.value.length > 0) {
    saveSessionMessages(currentSessionId.value, effectiveDocId.value, messages.value)
  }

  const session = loadSession(sessionId)
  if (session) {
    currentSessionId.value = session.id
    messages.value = session.messages || []
    if (session.documentId && !effectiveDocId.value) {
      documentId.value = session.documentId
    }
    refreshSessions()
    scrollToBottom()
  }
}

function confirmDeleteSession(sess) {
  deleteTarget.value = sess
  showDeleteConfirm.value = true
}

function doDeleteSession() {
  if (!deleteTarget.value) return
  deleteSession(deleteTarget.value.id)
  if (currentSessionId.value === deleteTarget.value.id) {
    currentSessionId.value = null
    messages.value = []
  }
  showDeleteConfirm.value = false
  deleteTarget.value = null
  refreshSessions()
}

function clearAllSessions() {
  const docId = effectiveDocId.value
  if (docId) {
    deleteDocumentSessions(docId)
  }
  currentSessionId.value = null
  messages.value = []
  refreshSessions()
}

function toggleSidebar() {
  showSidebar.value = !showSidebar.value
}

function getDocId() {
  return effectiveDocId.value
}

function scrollToBottom() {
  nextTick(() => {
    if (msgContainer.value) {
      msgContainer.value.scrollTop = msgContainer.value.scrollHeight
    }
  })
}

function persistSession() {
  if (messages.value.length === 0) return
  const docId = effectiveDocId.value
  if (!currentSessionId.value && docId) {
    const session = createSession(docId)
    currentSessionId.value = session.id
  }
  if (currentSessionId.value) {
    saveSessionMessages(currentSessionId.value, docId, messages.value)
    refreshSessions()
  }
}

async function sendQuestion() {
  const q = question.value.trim()
  const docId = getDocId()
  if (!q || !docId) return

  messages.value.push({ role: 'user', content: q })
  question.value = ''
  loading.value = true
  isStreaming.value = true
  scrollToBottom()

  // Add placeholder for assistant response
  const assistantMsg = { role: 'assistant', content: '', citations: [], streaming: true }
  messages.value.push(assistantMsg)

  // Persist after user message
  persistSession()

  try {
    const response = await askDocumentStream(docId, q, 3)

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const jsonStr = line.slice(6)
        try {
          const data = JSON.parse(jsonStr)
          if (data.done) {
            assistantMsg.streaming = false
            if (data.citations) assistantMsg.citations = data.citations
          } else if (data.content) {
            assistantMsg.content += (assistantMsg.content ? '\n' : '') + data.content
          }
        } catch { /* skip invalid JSON */ }
      }
      scrollToBottom()
    }

    // Process remaining buffer
    if (buffer.startsWith('data: ')) {
      try {
        const data = JSON.parse(buffer.slice(6))
        if (data.done) {
          assistantMsg.streaming = false
          if (data.citations) assistantMsg.citations = data.citations
        }
      } catch { /* skip */ }
    }
  } catch {
    // Fallback to error message
    assistantMsg.content = '抱歉，请求失败，请检查网络连接后重试。'
    assistantMsg.streaming = false
  }

  // Persist after complete response
  persistSession()

  loading.value = false
  isStreaming.value = false
  scrollToBottom()
}

function formatSessionDate(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  const now = new Date()
  const diff = now - d
  const mins = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (mins < 1) return '刚刚'
  if (mins < 60) return `${mins}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return d.toLocaleDateString('zh-CN')
}
</script>
