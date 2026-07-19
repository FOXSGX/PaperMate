<template>
  <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 h-[calc(100vh-10rem)] flex flex-col">
    <!-- Header -->
    <div class="text-center mb-6 shrink-0">
      <span class="text-4xl mb-2 block">💬</span>
      <h1 class="text-2xl font-bold text-gray-900">RAG 智能问答</h1>
      <p class="text-sm text-gray-500">基于上传文档的检索增强生成问答</p>
    </div>

    <!-- Document ID Input (if not from upload page) -->
    <div v-if="!docIdFromUpload" class="mb-4 shrink-0">
      <div class="flex gap-3 max-w-md mx-auto">
        <input v-model="documentId" type="text" placeholder="输入文档 ID（上传后可获取）"
          class="input-field text-sm flex-1" />
      </div>
    </div>
    <div v-else class="mb-4 shrink-0">
      <div class="flex items-center justify-center gap-2 text-sm text-gray-500 bg-blue-50 rounded-lg py-2 px-4 max-w-md mx-auto">
        <span>📄</span>
        <span class="font-mono text-xs truncate">文档：{{ docIdFromUpload }}</span>
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

      <!-- Loading indicator -->
      <div v-if="isStreaming" class="flex mb-3">
        <span class="text-2xl mr-2 shrink-0">🤖</span>
        <div class="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
          <div class="flex gap-1.5">
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
            <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
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
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { askDocumentStream } from '../api/index.js'

const route = useRoute()
const docIdFromUpload = ref(route.query.docId || '')

const documentId = ref('')
const question = ref('')
const messages = ref([])
const msgContainer = ref(null)
const isStreaming = ref(false)
const loading = ref(false)

// Pre-fill document ID from upload page
watch(() => route.query.docId, (val) => {
  if (val) docIdFromUpload.value = val
})

function getDocId() {
  return docIdFromUpload.value || documentId.value.trim()
}

function scrollToBottom() {
  nextTick(() => {
    if (msgContainer.value) {
      msgContainer.value.scrollTop = msgContainer.value.scrollHeight
    }
  })
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

  try {
    // 与 api/index.js 同一基址（开发经 Vite 代理到 :8000）
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
    // Fallback to non-streaming
    assistantMsg.content = '抱歉，请求失败，请检查网络连接后重试。'
    assistantMsg.streaming = false
  }

  loading.value = false
  isStreaming.value = false
  scrollToBottom()
}
</script>
