<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <!-- Header -->
    <div class="text-center mb-10">
      <span class="text-5xl mb-4 block">✨</span>
      <h1 class="text-3xl font-bold text-gray-900 mb-2">排版 & 降重</h1>
      <p class="text-gray-500">格式一键排版 + 智能同义改写</p>
    </div>

    <!-- Tab Switcher -->
    <div class="flex gap-1 bg-gray-100 rounded-xl p-1 mb-8 max-w-xs mx-auto">
      <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
        class="flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all duration-200"
        :class="activeTab === tab.key
          ? 'bg-white text-gray-900 shadow-sm'
          : 'text-gray-500 hover:text-gray-700'">
        <span class="mr-1.5">{{ tab.icon }}</span>{{ tab.label }}
      </button>
    </div>

    <!-- ==================== FORMAT TAB ==================== -->
    <div v-if="activeTab === 'format'" class="animate-fade-in">
      <div class="card">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">📐 格式排版</h3>

        <!-- Document ID -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">文档 ID</label>
          <input v-model="formatDocId" type="text" placeholder="输入已上传的 DOCX 文档 ID"
            class="input-field" />
          <p class="text-xs text-gray-400 mt-1">先在「文件上传」页面上传 DOCX 文件，将文档 ID 粘贴到这里</p>
        </div>

        <!-- Template Select -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">排版模板</label>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <label v-for="tpl in templates" :key="tpl.value"
              class="flex items-center gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all duration-200"
              :class="formatTemplate === tpl.value
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'">
              <input type="radio" :value="tpl.value" v-model="formatTemplate" class="hidden" />
              <span class="text-2xl">{{ tpl.icon }}</span>
              <div>
                <p class="font-medium text-gray-900 text-sm">{{ tpl.label }}</p>
                <p class="text-xs text-gray-500">{{ tpl.desc }}</p>
              </div>
            </label>
          </div>
        </div>

        <!-- Format Button -->
        <button @click="doFormat" class="btn-primary w-full" :disabled="formatLoading || !formatDocId.trim()">
          <span v-if="!formatLoading">🔧 一键排版</span>
          <span v-else class="flex items-center justify-center gap-2">
            <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            排版处理中...
          </span>
        </button>

        <!-- Format Result -->
        <div v-if="formatResult" class="mt-6 p-4 bg-green-50 border border-green-200 rounded-xl animate-slide-up">
          <div class="flex items-center gap-3">
            <span class="text-2xl">✅</span>
            <div>
              <p class="font-medium text-green-800">{{ formatResult.message }}</p>
              <p class="text-sm text-green-600">模板：{{ formatResult.template }}</p>
            </div>
          </div>
          <a :href="formatResult.output_url" target="_blank"
            class="btn-primary inline-block mt-3 text-sm">
            📥 下载排版文件
          </a>
        </div>

        <!-- Format Error -->
        <div v-if="formatError" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          ⚠️ {{ formatError }}
        </div>
      </div>
    </div>

    <!-- ==================== REWRITE TAB ==================== -->
    <div v-if="activeTab === 'rewrite'" class="animate-fade-in">
      <div class="card">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">✏️ 降重 / 去 AI 化改写</h3>

        <!-- Style Select -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">改写风格</label>
          <div class="flex gap-3 flex-wrap">
            <button v-for="style in styles" :key="style.value" @click="rewriteStyle = style.value"
              class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
              :class="rewriteStyle === style.value
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
              {{ style.icon }} {{ style.label }}
            </button>
          </div>
        </div>

        <!-- Original Text -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">原文</label>
          <textarea v-model="originalText" rows="6" placeholder="输入需要改写 / 降重的学术文本..."
            class="input-field resize-none"></textarea>
          <p class="text-xs text-gray-400 mt-1">{{ originalText.length }} 字 · 最少 5 个字符</p>
        </div>

        <!-- Rewrite Button -->
        <button @click="doRewrite" class="btn-primary w-full"
          :disabled="rewriteLoading || originalText.trim().length < 5">
          <span v-if="!rewriteLoading">🔄 开始改写</span>
          <span v-else class="flex items-center justify-center gap-2">
            <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            改写中...
          </span>
        </button>

        <!-- Rewrite Result -->
        <div v-if="rewriteResult" class="mt-6 animate-slide-up">
          <div class="flex items-center gap-3 mb-4">
            <span class="text-2xl">✅</span>
            <p class="font-medium text-gray-900">改写完成 · 风格：{{ rewriteResult.style }}</p>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div class="bg-gray-50 rounded-xl p-4">
              <p class="text-xs font-medium text-gray-500 mb-2">📄 原文</p>
              <p class="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{{ rewriteResult.original }}</p>
            </div>
            <div class="bg-green-50 rounded-xl p-4 border border-green-100">
              <p class="text-xs font-medium text-green-600 mb-2">✨ 改写后</p>
              <p class="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{{ rewriteResult.rewritten }}</p>
            </div>
          </div>
          <button @click="copyRewritten" class="btn-secondary text-sm mt-3">
            {{ rewriteCopied ? '✅ 已复制' : '📋 复制改写结果' }}
          </button>
        </div>

        <!-- Rewrite Error -->
        <div v-if="rewriteError" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          ⚠️ {{ rewriteError }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { formatDocument, rewriteText } from '../api/index.js'

const activeTab = ref('format')

const tabs = [
  { key: 'format', label: '格式排版', icon: '📐' },
  { key: 'rewrite', label: '降重改写', icon: '✏️' },
]

// ---- Format State ----
const formatDocId = ref('')
const formatTemplate = ref('gb7713')
const formatLoading = ref(false)
const formatResult = ref(null)
const formatError = ref('')

const templates = [
  { value: 'gb7713', label: 'GB/T 7713', desc: '学位论文标准格式', icon: '🎓' },
  { value: 'journal', label: '期刊模板', desc: '通用期刊投稿格式', icon: '📰' },
]

// ---- Rewrite State ----
const rewriteStyle = ref('academic')
const originalText = ref('')
const rewriteLoading = ref(false)
const rewriteResult = ref(null)
const rewriteError = ref('')
const rewriteCopied = ref(false)

const styles = [
  { value: 'academic', label: '学术', icon: '📖' },
  { value: 'concise', label: '简洁', icon: '✂️' },
  { value: 'polished', label: '润色', icon: '💎' },
]

// ---- Format Handler ----
async function doFormat() {
  formatError.value = ''
  formatResult.value = null
  formatLoading.value = true

  try {
    const res = await formatDocument(formatDocId.value.trim(), formatTemplate.value)
    formatResult.value = res.data
  } catch (err) {
    formatError.value = err.response?.data?.detail || err.message || '排版失败，请确认文档 ID 是否正确'
  } finally {
    formatLoading.value = false
  }
}

// ---- Rewrite Handler ----
async function doRewrite() {
  rewriteError.value = ''
  rewriteResult.value = null
  rewriteLoading.value = true

  try {
    const res = await rewriteText(originalText.value.trim(), rewriteStyle.value)
    rewriteResult.value = res.data
  } catch (err) {
    rewriteError.value = err.response?.data?.detail || err.message || '改写失败，请重试'
  } finally {
    rewriteLoading.value = false
  }
}

async function copyRewritten() {
  if (rewriteResult.value?.rewritten) {
    try {
      await navigator.clipboard.writeText(rewriteResult.value.rewritten)
      rewriteCopied.value = true
      setTimeout(() => rewriteCopied.value = false, 2000)
    } catch { /* fallback */ }
  }
}
</script>
