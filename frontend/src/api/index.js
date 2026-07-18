import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

// ---- Literature ----
export function searchPapers(keyword, maxResults = 5) {
  return api.post('/search', { keyword, max_results: maxResults })
}

export function generateSurvey(topic, maxPapers = 5) {
  return api.post('/survey', { topic, max_papers: maxPapers }, { responseType: 'stream' })
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
  return api.post('/qa/stream', { document_id: documentId, question, top_k: topK }, { responseType: 'stream' })
}

// ---- Writing ----
export function rewriteText(text, style = 'academic') {
  return api.post('/rewrite', { text, style })
}

export function formatDocument(documentId, template = 'gb7713') {
  return api.post('/format', { document_id: documentId, template })
}

export default api
