import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

import Home from './components/Home.vue'
import Upload from './components/Upload.vue'
import Documents from './components/Documents.vue'
import Chat from './components/Chat.vue'
import Survey from './components/Survey.vue'
import Format from './components/Format.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/upload', name: 'Upload', component: Upload },
  { path: '/documents', name: 'Documents', component: Documents },
  { path: '/chat', name: 'Chat', component: Chat },
  { path: '/survey', name: 'Survey', component: Survey },
  { path: '/format', name: 'Format', component: Format },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const app = createApp(App)
app.use(router)
app.mount('#app')
