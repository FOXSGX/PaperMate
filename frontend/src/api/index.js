import axios from 'axios'

/**
 * 前后端接口基址约定：
 * - 开发：Vite 将 /api、/outputs 代理到 http://127.0.0.1:8000
 * - 可通过 VITE_API_BASE 覆盖（例如直连 http://127.0.0.1:8000/api）
 */
const API_BASE = (import.meta.env.VITE_API_BASE || '/api').replace(/\/$/, '')

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

function apiUrl(path) {
  const normalized = path.startsWith('/') ? path : `/${path}`
  return `${API_BASE}${normalized}`
}

/** SSE / 流式 POST（与 axios 共用同一 API 基址） */
export async function postEventStream(path, body) {
  const response = await fetch(apiUrl(path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const data = await response.json()
      detail = data.detail || detail
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }
  return response
}

// ---- Literature ----
export function searchPapers(keyword, maxResults = 5) {
  return api.post('/search', { keyword, max_results: maxResults })
}

export function generateSurvey(topic, maxPapers = 5) {
  return postEventStream('/survey', { topic, max_papers: maxPapers })
}

// ---- Files ----
export function uploadFile(formData, onProgress) {
  return api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress,
  })
}

export function uploadFiles(files, onProgress) {
  const formData = new FormData()
  for (const file of files) {
    formData.append('files', file)
  }
  return api.post('/upload/batch', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress,
  })
}

// ---- RAG QA ----
export function askDocument(documentId, question, topK = 3) {
  return api.post('/qa', { document_id: documentId, question, top_k: topK })
}

export function askDocumentStream(documentId, question, topK = 3) {
  return postEventStream('/qa/stream', {
    document_id: documentId,
    question,
    top_k: topK,
  })
}

// ---- Writing ----
export function rewriteText(text, style = 'academic') {
  return api.post('/rewrite', { text, style })
}

export function formatDocument(documentId, template = 'gb7713') {
  return api.post('/format', { document_id: documentId, template })
}

export { API_BASE, apiUrl }
export default api
