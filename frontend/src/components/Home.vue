<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <!-- Hero -->
    <section class="text-center mb-16 animate-fade-in">
      <h1 class="text-5xl font-extrabold text-gray-900 mb-4 tracking-tight">
        📄 PaperMate
      </h1>
      <p class="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
        基于 <span class="font-semibold text-primary-700">LLM + RAG</span> 的智能学术写作辅助工具
      </p>
      <p class="text-gray-500 mt-3">
        文献调研从数天缩短到分钟，格式排版一键完成
      </p>
    </section>

    <!-- Feature Cards -->
    <section class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
      <router-link to="/upload"
        class="card group cursor-pointer hover:border-primary-200 hover:shadow-lg transform hover:-translate-y-1 transition-all duration-300">
        <div class="flex items-start gap-4">
          <span class="text-4xl p-3 rounded-xl bg-blue-50 group-hover:bg-blue-100 transition-colors">📤</span>
          <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-1">文件上传与管理</h3>
            <p class="text-gray-500 text-sm leading-relaxed">
              支持 PDF、DOCX、TXT、MD 格式上传，自动解析文档内容并建立文本索引，为智能问答做好准备。
            </p>
          </div>
        </div>
      </router-link>

      <router-link to="/chat"
        class="card group cursor-pointer hover:border-primary-200 hover:shadow-lg transform hover:-translate-y-1 transition-all duration-300">
        <div class="flex items-start gap-4">
          <span class="text-4xl p-3 rounded-xl bg-green-50 group-hover:bg-green-100 transition-colors">💬</span>
          <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-1">RAG 智能问答</h3>
            <p class="text-gray-500 text-sm leading-relaxed">
              上传论文后用自然语言提问，系统检索最相关片段并结合 LLM 生成精准回答，每条回答附带引用来源。
            </p>
          </div>
        </div>
      </router-link>

      <router-link to="/survey"
        class="card group cursor-pointer hover:border-primary-200 hover:shadow-lg transform hover:-translate-y-1 transition-all duration-300">
        <div class="flex items-start gap-4">
          <span class="text-4xl p-3 rounded-xl bg-purple-50 group-hover:bg-purple-100 transition-colors">📝</span>
          <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-1">文献综述生成</h3>
            <p class="text-gray-500 text-sm leading-relaxed">
              输入研究主题，自动检索 arXiv 获取相关论文，按大纲组织并生成结构化综述初稿。
            </p>
          </div>
        </div>
      </router-link>

      <router-link to="/format"
        class="card group cursor-pointer hover:border-primary-200 hover:shadow-lg transform hover:-translate-y-1 transition-all duration-300">
        <div class="flex items-start gap-4">
          <span class="text-4xl p-3 rounded-xl bg-orange-50 group-hover:bg-orange-100 transition-colors">✨</span>
          <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-1">排版 & 降重</h3>
            <p class="text-gray-500 text-sm leading-relaxed">
              一键格式排版（GB/T 7713、期刊模板）和智能同义改写，降低重复率与 AIGC 检测率。
            </p>
          </div>
        </div>
      </router-link>
    </section>

    <!-- Workflow -->
    <section class="text-center bg-gradient-to-br from-primary-50 to-blue-50 rounded-2xl p-10">
      <h2 class="text-2xl font-bold text-gray-900 mb-8">🚀 使用流程</h2>
      <div class="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-6">
        <div v-for="(step, idx) in steps" :key="idx"
          class="flex items-center gap-3 bg-white rounded-xl px-6 py-4 shadow-sm">
          <span class="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center text-sm font-bold shrink-0">{{ idx + 1 }}</span>
          <div class="text-left">
            <div class="font-semibold text-gray-900">{{ step.title }}</div>
            <div class="text-xs text-gray-500">{{ step.desc }}</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
const steps = [
  { title: '上传文档', desc: 'PDF / DOCX / TXT' },
  { title: 'AI 解析', desc: '自动切片与索引' },
  { title: '交互问答', desc: '多轮 RAG 对话' },
  { title: '生成结果', desc: '综述 / 排版 / 降重' },
]
</script>
