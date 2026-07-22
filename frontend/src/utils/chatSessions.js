/**
 * Chat session history management using localStorage.
 * Sessions are grouped by document_id, with multiple conversations per document.
 */

const STORAGE_KEY = 'papermate_chat_sessions'
const ACTIVE_SESSION_KEY = 'papermate_active_session'

/**
 * @typedef {Object} ChatMessage
 * @property {'user'|'assistant'} role
 * @property {string} content
 * @property {Object[]} [citations]
 * @property {boolean} [streaming]
 * @property {number} timestamp
 */

/**
 * @typedef {Object} ChatSession
 * @property {string} id - unique session id
 * @property {string} documentId - associated document ID
 * @property {string} label - display name (first question or date)
 * @property {ChatMessage[]} messages
 * @property {number} createdAt
 * @property {number} updatedAt
 */

function loadSessions() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveSessions(sessions) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions))
  } catch {
    // localStorage full — silently fail, sessions just won't persist
  }
}

export function getSessions(documentId) {
  const all = loadSessions()
  if (documentId) {
    return all
      .filter((s) => s.documentId === documentId)
      .sort((a, b) => b.updatedAt - a.updatedAt)
  }
  return all.sort((a, b) => b.updatedAt - a.updatedAt)
}

export function getActiveSessionId() {
  try {
    return localStorage.getItem(ACTIVE_SESSION_KEY) || null
  } catch {
    return null
  }
}

export function setActiveSessionId(id) {
  try {
    if (id) {
      localStorage.setItem(ACTIVE_SESSION_KEY, id)
    } else {
      localStorage.removeItem(ACTIVE_SESSION_KEY)
    }
  } catch {
    // ignore
  }
}

export function createSession(documentId, label) {
  const all = loadSessions()
  const id = `sess_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
  const session = {
    id,
    documentId,
    label: label || `会话 ${new Date().toLocaleString('zh-CN')}`,
    messages: [],
    createdAt: Date.now(),
    updatedAt: Date.now(),
  }
  all.push(session)
  saveSessions(all)
  setActiveSessionId(id)
  return session
}

export function loadSession(sessionId) {
  const all = loadSessions()
  const session = all.find((s) => s.id === sessionId)
  if (session) {
    setActiveSessionId(sessionId)
  }
  return session || null
}

export function saveSessionMessages(sessionId, documentId, messages, label) {
  const all = loadSessions()
  const idx = all.findIndex((s) => s.id === sessionId)
  const session = idx >= 0
    ? { ...all[idx], messages, documentId, updatedAt: Date.now() }
    : { id: sessionId, documentId, label: label || '', messages, createdAt: Date.now(), updatedAt: Date.now() }

  if (!session.label && messages.length > 0) {
    const firstUser = messages.find((m) => m.role === 'user')
    if (firstUser) {
      session.label = firstUser.content.slice(0, 40) + (firstUser.content.length > 40 ? '...' : '')
    }
  }

  if (idx >= 0) {
    all[idx] = session
  } else {
    all.push(session)
  }

  saveSessions(all)
  setActiveSessionId(sessionId)
  return session
}

export function deleteSession(sessionId) {
  const all = loadSessions()
  const filtered = all.filter((s) => s.id !== sessionId)
  saveSessions(filtered)
  if (getActiveSessionId() === sessionId) {
    setActiveSessionId(null)
  }
}

export function deleteDocumentSessions(documentId) {
  const all = loadSessions()
  const filtered = all.filter((s) => s.documentId !== documentId)
  saveSessions(filtered)
}
