import { describe, it, expect, beforeEach, vi } from 'vitest'
import { apiUrl, API_BASE } from '../api/index.js'

// The api module uses axios; we test the helper and module structure.

describe('API helpers', () => {
  describe('API_BASE', () => {
    it('is defined as a string', () => {
      expect(typeof API_BASE).toBe('string')
    })

    it('does not end with a trailing slash', () => {
      expect(API_BASE.endsWith('/')).toBe(false)
    })
  })

  describe('apiUrl', () => {
    it('prepends API_BASE to a path', () => {
      const url = apiUrl('/search')
      expect(url).toBe(`${API_BASE}/search`)
    })

    it('handles path without leading slash', () => {
      const url = apiUrl('search')
      expect(url).toBe(`${API_BASE}/search`)
    })

    it('handles empty path', () => {
      const url = apiUrl('')
      expect(url).toBe(`${API_BASE}/`)
    })
  })
})

describe('API module exports', () => {
  it('exports all expected functions', async () => {
    const api = await import('../api/index.js')

    const expectedExports = [
      'searchPapers',
      'generateSurvey',
      'uploadFile',
      'uploadFiles',
      'listDocuments',
      'deleteDocument',
      'askDocument',
      'askDocumentStream',
      'rewriteText',
      'formatDocument',
      'postEventStream',
      'apiUrl',
      'API_BASE',
    ]

    for (const name of expectedExports) {
      expect(api).toHaveProperty(name)
    }
  })
})
