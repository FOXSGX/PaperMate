import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import Survey from '../components/Survey.vue'

function createTestRouter() {
  return createRouter({
    history: createMemoryHistory('/'),
    routes: [
      { path: '/survey', component: Survey },
    ],
  })
}

describe('Survey', () => {
  it('renders the survey generation page', async () => {
    const router = createTestRouter()
    await router.push('/survey')
    const wrapper = mount(Survey, {
      global: { plugins: [router] },
    })

    expect(wrapper.text()).toContain('文献综述生成')
    expect(wrapper.text()).toContain('研究主题')
  })

  it('has topic input field', async () => {
    const router = createTestRouter()
    await router.push('/survey')
    const wrapper = mount(Survey, {
      global: { plugins: [router] },
    })

    const input = wrapper.find('input[type="text"]')
    expect(input.exists()).toBe(true)
    expect(input.attributes('placeholder')).toContain('Vision Transformer')
  })

  it('has outline style selector with 3 options', async () => {
    const router = createTestRouter()
    await router.push('/survey')
    const wrapper = mount(Survey, {
      global: { plugins: [router] },
    })

    // Two select elements: first is maxPapers, second is outlineStyle
    const selects = wrapper.findAll('select')
    expect(selects.length).toBeGreaterThanOrEqual(2)

    const outlineSelect = selects[1]
    expect(outlineSelect.exists()).toBe(true)
    const options = outlineSelect.findAll('option')
    const labels = options.map((o) => o.text())
    expect(labels).toContain('标准结构')
    expect(labels).toContain('方法导向')
    expect(labels).toContain('时间线')
  })

  it('has max papers selector', async () => {
    const router = createTestRouter()
    await router.push('/survey')
    const wrapper = mount(Survey, {
      global: { plugins: [router] },
    })

    // Find all select elements (max_papers and outline_style)
    const selects = wrapper.findAll('select')
    expect(selects.length).toBeGreaterThanOrEqual(1)
  })

  it('has a generate button', async () => {
    const router = createTestRouter()
    await router.push('/survey')
    const wrapper = mount(Survey, {
      global: { plugins: [router] },
    })

    const button = wrapper.find('button')
    expect(button.exists()).toBe(true)
    expect(button.text()).toContain('开始生成')
  })

  it('disables generate button when topic is empty', async () => {
    const router = createTestRouter()
    await router.push('/survey')
    const wrapper = mount(Survey, {
      global: { plugins: [router] },
    })

    const button = wrapper.find('button')
    // Button should be disabled when topic is empty
    expect(button.attributes('disabled')).toBeDefined()
  })
})
