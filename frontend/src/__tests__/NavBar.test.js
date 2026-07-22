import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import NavBar from '../components/NavBar.vue'

function createTestRouter(initialRoute = '/') {
  return createRouter({
    history: createMemoryHistory(initialRoute),
    routes: [
      { path: '/', component: { template: '<div>Home</div>' } },
      { path: '/upload', component: { template: '<div>Upload</div>' } },
      { path: '/documents', component: { template: '<div>Documents</div>' } },
      { path: '/chat', component: { template: '<div>Chat</div>' } },
      { path: '/survey', component: { template: '<div>Survey</div>' } },
      { path: '/format', component: { template: '<div>Format</div>' } },
    ],
  })
}

describe('NavBar', () => {
  it('renders all navigation links', async () => {
    const router = createTestRouter()
    await router.push('/')
    const wrapper = mount(NavBar, {
      global: { plugins: [router] },
    })

    const links = wrapper.findAll('a')
    // The router-link component renders as an anchor

    const expectedLabels = ['首页', '文件上传', '文档管理', '智能问答', '综述生成', '排版降重']
    for (const label of expectedLabels) {
      expect(wrapper.text()).toContain(label)
    }
  })

  it('highlights the active route', async () => {
    const router = createTestRouter()
    await router.push('/upload')
    const wrapper = mount(NavBar, {
      global: { plugins: [router] },
    })

    // The upload link should have the active class
    const uploadLink = wrapper.findAll('a').find((el) => el.text().includes('文件上传'))
    expect(uploadLink).toBeTruthy()
    expect(uploadLink.classes()).toContain('text-primary-700')
  })

  it('has a logo linking to home', async () => {
    const router = createTestRouter()
    await router.push('/')
    const wrapper = mount(NavBar, {
      global: { plugins: [router] },
    })

    const logo = wrapper.find('a[href="/"]')
    expect(logo.exists()).toBe(true)
    expect(logo.text()).toContain('PaperMate')
  })

  it('has mobile menu toggle', async () => {
    const router = createTestRouter()
    await router.push('/')
    const wrapper = mount(NavBar, {
      global: { plugins: [router] },
    })

    // The mobile toggle button exists
    const toggleBtn = wrapper.find('button.md\\:hidden')
    expect(toggleBtn.exists()).toBe(true)
  })

  it('home route is active only for exact match', async () => {
    const router = createTestRouter()
    await router.push('/chat')
    const wrapper = mount(NavBar, {
      global: { plugins: [router] },
    })

    // Home link should NOT be active when on /chat
    const homeLink = wrapper.findAll('a').find((el) => el.text().includes('首页'))
    expect(homeLink).toBeTruthy()
    // Should have inactive class, not active
    expect(homeLink.classes()).not.toContain('text-primary-700')
  })
})
