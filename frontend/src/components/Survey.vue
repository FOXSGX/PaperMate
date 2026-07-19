<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <!-- Header -->
    <div class="text-center mb-10">
      <span class="text-5xl mb-4 block">📝</span>
      <h1 class="text-3xl font-bold text-gray-900 mb-2">文献综述生成</h1>
      <p class="text-gray-500">输入研究主题，自动检索 arXiv 并生成结构化综述</p>
    </div>

    <!-- Search Area -->
    <div class="card mb-8">
      <!-- Topic Input -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">研究主题</label>
        <input v-model="topic" type="text" placeholder="例如：Vision Transformer 在医学图像分割中的应用"
          class="input-field" @keyup.enter="startGeneration" :disabled="generating" />
      </div>

      <!-- Settings Row -->
      <div class="flex flex-wrap items-end gap-4 mb-4">
        <div class="w-40">
          <label class="block text-sm font-medium text-gray-700 mb-2">检索论文数</label>
          <select v-model="maxPapers" class="input-field" :disabled="generating">
            <option :value="3">3 篇</option>
            <option :value="5">5 篇</option>
            <option :value="8">8 篇</option>
            <option :value="10">10 篇</option>
          </select>
        </div>

        <div class="w-40">
          <label class="block text-sm font-medium text-gray-700 mb-2">综述大纲</label>
          <select v-model="outlineStyle" class="input-field" :disabled="generating">
            <option value="standard">标准结构</option>
            <option value="method">方法导向</option>
            <option value="timeline">时间线</option>
          </select>
        </div>

        <button @click="startGeneration" class="btn-primary h-[46px]" :disabled="generating || !topic.trim()">
          <span v-if="!generating">🚀 开始生成</span>
          <span v-else class="flex items-center gap-2">
            <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            生成中...
          </span>
        </button>
      </div>
    </div>

    <!-- Paper List -->
    <div v-if="papers.length > 0" class="mb-8">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">
        📚 检索文献 <span class="text-sm font-normal text-gray-400 ml-2">共 {{ papers.length }} 篇</span>
      </h3>
      <div class="space-y-3">
        <div v-for="(paper, idx) in papers" :key="idx" class="card animate-slide-up"
          :style="{ animationDelay: idx * 80 + 'ms' }">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <h4 class="font-semibold text-gray-900 mb-1">{{ paper.title }}</h4>
              <p class="text-sm text-gray-500 mb-2">
                {{ paper.authors?.join(', ') }} · {{ paper.published }}
              </p>
              <p class="text-sm text-gray-600 line-clamp-3">{{ paper.summary }}</p>
              <div class="flex gap-2 mt-3 flex-wrap">
                <span v-for="cat in paper.categories" :key="cat"
                  class="text-xs bg-primary-50 text-primary-700 px-2 py-0.5 rounded-full">
                  {{ cat }}
                </span>
              </div>
            </div>
            <a v-if="paper.url" :href="paper.url" target="_blank" rel="noopener"
              class="shrink-0 text-sm text-primary-600 hover:text-primary-800 hover:underline">
              查看 →
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Survey Output -->
    <div v-if="surveyContent" class="card animate-slide-up">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-900">📄 综述初稿</h3>
        <button @click="copyContent" class="text-sm text-primary-600 hover:text-primary-800 transition-colors">
          {{ copied ? '✅ 已复制' : '📋 复制全文' }}
        </button>
      </div>
      <div class="prose prose-sm max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap"
        v-html="renderedContent"></div>
    </div>

    <!-- Error -->
    <div v-if="errorMsg" class="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm animate-fade-in">
      ⚠️ {{ errorMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { searchPapers, generateSurvey } from '../api/index.js'

const topic = ref('')
const maxPapers = ref(5)
const outlineStyle = ref('standard')
const generating = ref(false)
const papers = ref([])
const surveyContent = ref('')
const errorMsg = ref('')
const copied = ref(false)

const renderedContent = computed(() => {
  if (!surveyContent.value) return ''
  return surveyContent.value
    .replace(/^# (.+)$/gm, '<h3 class="text-lg font-bold mt-4 mb-2">$1</h3>')
    .replace(/^## (.+)$/gm, '<h4 class="text-base font-semibold mt-3 mb-1">$1</h4>')
    .replace(/^- (.+)$/gm, '<li class="ml-4">$1</li>')
    .replace(/\n\n/g, '<br/><br/>')
})

async function startGeneration() {
  if (!topic.value.trim()) return
  errorMsg.value = ''
  papers.value = []
  surveyContent.value = ''
  generating.value = true

  try {
    // Step 1: Search papers
    const res = await searchPapers(topic.value.trim(), maxPapers.value)
    papers.value = res.data.papers || []

    // Step 2: Generate survey via SSE（与 api 基址/代理一致）
    const response = await generateSurvey(topic.value.trim(), maxPapers.value)

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
        try {
          const data = JSON.parse(line.slice(6))
          if (data.done) break
          if (data.content) {
            surveyContent.value += (surveyContent.value ? '\n\n' : '') + data.content
          }
        } catch { /* skip */ }
      }
    }
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || err.message || '生成失败，请重试'
  } finally {
    generating.value = false
  }
}

async function copyContent() {
  if (surveyContent.value) {
    try {
      await navigator.clipboard.writeText(surveyContent.value)
      copied.value = true
      setTimeout(() => copied.value = false, 2000)
    } catch {
      // fallback
    }
  }
}
</script>
