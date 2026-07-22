import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  getSessions,
  getActiveSessionId,
  setActiveSessionId,
  createSession,
  loadSession,
  saveSessionMessages,
  deleteSession,
  deleteDocumentSessions,
} from '../utils/chatSessions.js'

// Mock localStorage
const localStorageMock = (() => {
  let store = {}
  return {
    getItem: vi.fn((key) => store[key] || null),
    setItem: vi.fn((key, value) => { store[key] = value }),
    removeItem: vi.fn((key) => { delete store[key] }),
    clear: vi.fn(() => { store = {} }),
  }
})()

Object.defineProperty(global, 'localStorage', { value: localStorageMock })

beforeEach(() => {
  localStorageMock.clear()
  vi.clearAllMocks()
})

describe('chatSessions', () => {
  describe('createSession', () => {
    it('creates a new session with an ID and label', () => {
      const session = createSession('doc123', '测试会话')

      expect(session).toHaveProperty('id')
      expect(session.id).toMatch(/^sess_/)
      expect(session.documentId).toBe('doc123')
      expect(session.label).toBe('测试会话')
      expect(session.messages).toEqual([])
      expect(session.createdAt).toBeGreaterThan(0)
      expect(session.updatedAt).toBeGreaterThan(0)
    })

    it('sets the session as active', () => {
      createSession('doc123', 'test')
      expect(getActiveSessionId()).toBeTruthy()
    })

    it('auto-generates a label if none provided', () => {
      const session = createSession('doc456')
      expect(session.label).toContain('会话')
    })
  })

  describe('getSessions', () => {
    it('returns sessions filtered by documentId', () => {
      createSession('doc1', 'Session 1')
      createSession('doc1', 'Session 2')
      createSession('doc2', 'Session 3')

      const doc1Sessions = getSessions('doc1')
      expect(doc1Sessions).toHaveLength(2)
      expect(doc1Sessions.every((s) => s.documentId === 'doc1')).toBe(true)
    })

    it('returns all sessions when no documentId provided', () => {
      createSession('doc1', 'Session 1')
      createSession('doc2', 'Session 2')

      const all = getSessions()
      expect(all).toHaveLength(2)
    })

    it('returns empty array when no sessions exist', () => {
      expect(getSessions('nonexistent')).toEqual([])
    })
  })

  describe('saveSessionMessages', () => {
    it('saves messages to an existing session', () => {
      const session = createSession('doc1', 'Test')
      const messages = [
        { role: 'user', content: 'Hello' },
        { role: 'assistant', content: 'Hi there' },
      ]

      const updated = saveSessionMessages(session.id, 'doc1', messages)
      expect(updated.messages).toEqual(messages)
      expect(updated.updatedAt).toBeGreaterThanOrEqual(session.createdAt)
    })

    it('auto-sets label from first user message when no label exists', () => {
      // Create a session directly via saveSessionMessages without a prior createSession call,
      // so there's no existing label
      const sessionId = 'sess_test_123'
      const messages = [
        { role: 'user', content: 'What is the main finding?' },
        { role: 'assistant', content: 'The main finding is...' },
      ]

      const saved = saveSessionMessages(sessionId, 'doc1', messages)
      expect(saved.label).toContain('What is the main finding')
    })
  })

  describe('loadSession', () => {
    it('loads a session by ID', () => {
      const created = createSession('doc1', 'Test')
      createSession('doc2', 'Other')

      const loaded = loadSession(created.id)
      expect(loaded).toBeTruthy()
      expect(loaded.id).toBe(created.id)
      expect(loaded.label).toBe('Test')
    })

    it('sets loaded session as active', () => {
      const created = createSession('doc1', 'Test')
      createSession('doc2', 'Other')

      loadSession(created.id)
      expect(getActiveSessionId()).toBe(created.id)
    })

    it('returns null for non-existent session', () => {
      const result = loadSession('nonexistent_id')
      expect(result).toBeNull()
    })
  })

  describe('deleteSession', () => {
    it('deletes a session by ID', () => {
      const s1 = createSession('doc1', 'Session 1')
      const s2 = createSession('doc1', 'Session 2')

      deleteSession(s1.id)
      const remaining = getSessions('doc1')
      expect(remaining).toHaveLength(1)
      expect(remaining[0].id).toBe(s2.id)
    })

    it('clears active session if deleted session was active', () => {
      const session = createSession('doc1', 'Test')
      deleteSession(session.id)
      expect(getActiveSessionId()).toBeNull()
    })

    it('does not clear active session if a different session is deleted', () => {
      const s1 = createSession('doc1', 'Session 1')
      const s2 = createSession('doc1', 'Session 2')

      // s2 is now active
      expect(getActiveSessionId()).toBe(s2.id)

      deleteSession(s1.id)
      expect(getActiveSessionId()).toBe(s2.id)
    })
  })

  describe('deleteDocumentSessions', () => {
    it('deletes all sessions for a document', () => {
      createSession('doc1', 'S1')
      createSession('doc1', 'S2')
      createSession('doc2', 'S3')

      deleteDocumentSessions('doc1')
      expect(getSessions('doc1')).toHaveLength(0)
      expect(getSessions('doc2')).toHaveLength(1)
    })
  })

  describe('activeSessionId', () => {
    it('returns null when no active session', () => {
      expect(getActiveSessionId()).toBeNull()
    })

    it('can set and clear active session id', () => {
      setActiveSessionId('test-123')
      expect(getActiveSessionId()).toBe('test-123')

      setActiveSessionId(null)
      expect(getActiveSessionId()).toBeNull()
    })
  })
})
