import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import Format from '../components/Format.vue'

function createTestRouter() {
  return createRouter({
    history: createMemoryHistory('/'),
    routes: [
      { path: '/format', component: Format },
    ],
  })
}

describe('Format', () => {
  it('renders the format & rewrite page', async () => {
    const router = createTestRouter()
    await router.push('/format')
    const wrapper = mount(Format, {
      global: { plugins: [router] },
    })

    expect(wrapper.text()).toContain('排版')
    expect(wrapper.text()).toContain('降重')
  })

  it('has tab switcher with format and rewrite tabs', async () => {
    const router = createTestRouter()
    await router.push('/format')
    const wrapper = mount(Format, {
      global: { plugins: [router] },
    })

    expect(wrapper.text()).toContain('格式排版')
    expect(wrapper.text()).toContain('降重改写')
  })

  it('shows format tab content by default', async () => {
    const router = createTestRouter()
    await router.push('/format')
    const wrapper = mount(Format, {
      global: { plugins: [router] },
    })

    // Format tab content should be visible
    expect(wrapper.text()).toContain('文档 ID')
    expect(wrapper.text()).toContain('排版模板')
  })

  it('shows template options', async () => {
    const router = createTestRouter()
    await router.push('/format')
    const wrapper = mount(Format, {
      global: { plugins: [router] },
    })

    expect(wrapper.text()).toContain('GB/T 7713')
    expect(wrapper.text()).toContain('期刊模板')
  })

  it('has rewrite style options', async () => {
    const router = createTestRouter()
    await router.push('/format')
    const wrapper = mount(Format, {
      global: { plugins: [router] },
    })

    // Switch to rewrite tab
    const rewriteBtn = wrapper.findAll('button').find((b) => b.text().includes('降重改写'))
    if (rewriteBtn) {
      await rewriteBtn.trigger('click')
      expect(wrapper.text()).toContain('学术')
      expect(wrapper.text()).toContain('简洁')
      expect(wrapper.text()).toContain('润色')
    }
  })

  it('has text input for rewrite', async () => {
    const router = createTestRouter()
    await router.push('/format')
    const wrapper = mount(Format, {
      global: { plugins: [router] },
    })

    // Switch to rewrite tab
    const rewriteBtn = wrapper.findAll('button').find((b) => b.text().includes('降重改写'))
    if (rewriteBtn) {
      await rewriteBtn.trigger('click')
      const textarea = wrapper.find('textarea')
      expect(textarea.exists()).toBe(true)
    }
  })
})
