import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import Home from '../components/Home.vue'

function createTestRouter() {
  return createRouter({
    history: createMemoryHistory('/'),
    routes: [
      { path: '/', component: Home },
      { path: '/upload', component: { template: '<div>Upload</div>' } },
      { path: '/chat', component: { template: '<div>Chat</div>' } },
      { path: '/survey', component: { template: '<div>Survey</div>' } },
      { path: '/format', component: { template: '<div>Format</div>' } },
    ],
  })
}

describe('Home', () => {
  it('renders the hero section with title', async () => {
    const router = createTestRouter()
    await router.push('/')
    const wrapper = mount(Home, {
      global: { plugins: [router] },
    })

    expect(wrapper.text()).toContain('PaperMate')
    expect(wrapper.text()).toContain('LLM + RAG')
    expect(wrapper.text()).toContain('智能学术写作辅助工具')
  })

  it('renders all 4 feature cards', async () => {
    const router = createTestRouter()
    await router.push('/')
    const wrapper = mount(Home, {
      global: { plugins: [router] },
    })

    const cards = wrapper.findAll('.card')
    expect(cards).toHaveLength(4)

    const expectedFeatures = ['文件上传与管理', 'RAG 智能问答', '文献综述生成', '排版 & 降重']
    for (const feature of expectedFeatures) {
      expect(wrapper.text()).toContain(feature)
    }
  })

  it('renders workflow steps', async () => {
    const router = createTestRouter()
    await router.push('/')
    const wrapper = mount(Home, {
      global: { plugins: [router] },
    })

    expect(wrapper.text()).toContain('使用流程')
    expect(wrapper.text()).toContain('上传文档')
    expect(wrapper.text()).toContain('AI 解析')
    expect(wrapper.text()).toContain('交互问答')
    expect(wrapper.text()).toContain('生成结果')
  })

  it('has links to all feature pages', async () => {
    const router = createTestRouter()
    await router.push('/')
    const wrapper = mount(Home, {
      global: { plugins: [router] },
    })

    const links = wrapper.findAll('a')
    const hrefs = links.map((l) => l.attributes('href'))
    expect(hrefs).toContain('/upload')
    expect(hrefs).toContain('/chat')
    expect(hrefs).toContain('/survey')
    expect(hrefs).toContain('/format')
  })
})
