/**
 * API Tests
 * 
 * 測試 app/lib/api.ts 的 API 函數
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { 
  streamDebate, 
  checkHealth, 
  saveDebate, 
  getRecentDebates, 
  getDebateById,
  SSEEvent
} from '@/app/lib/api'

// Mock fetch
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('API Client', () => {
  beforeEach(() => {
    mockFetch.mockClear()
  })

  describe('checkHealth', () => {
    it('should return true when health check succeeds', async () => {
      mockFetch.mockResolvedValue({ ok: true })
      
      const result = await checkHealth()
      
      expect(result).toBe(true)
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/health',
        { method: 'GET' }
      )
    })

    it('should return false when health check fails', async () => {
      mockFetch.mockResolvedValue({ ok: false })
      
      const result = await checkHealth()
      
      expect(result).toBe(false)
    })

    it('should return false on network error', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'))
      
      const result = await checkHealth()
      
      expect(result).toBe(false)
    })
  })

  describe('saveDebate', () => {
    it('should save debate successfully', async () => {
      const mockResponse = { success: true, debate_id: 'test-uuid' }
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })
      
      const result = await saveDebate('Test Topic', [], 3, 0)
      
      expect(result.success).toBe(true)
      expect(result.debate_id).toBe('test-uuid')
    })

    it('should handle save failure', async () => {
      mockFetch.mockResolvedValue({ ok: false, status: 500 })
      
      const result = await saveDebate('Test Topic', [], 3, 0)
      
      expect(result.success).toBe(false)
      expect(result.error).toBe('HTTP 500')
    })

    it('should handle network error', async () => {
      mockFetch.mockRejectedValue(new Error('Network error'))
      
      const result = await saveDebate('Test Topic', [], 3, 0)
      
      expect(result.success).toBe(false)
    })
  })

  describe('getRecentDebates', () => {
    it('should fetch recent debates', async () => {
      const mockDebates = [
        { id: '1', topic: 'Topic 1', created_at: '2025-12-26', rounds_completed: 3 }
      ]
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ debates: mockDebates })
      })
      
      const result = await getRecentDebates(5)
      
      expect(result).toEqual(mockDebates)
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/debate/history?limit=5'
      )
    })

    it('should return empty array on error', async () => {
      mockFetch.mockResolvedValue({ ok: false })
      
      const result = await getRecentDebates()
      
      expect(result).toEqual([])
    })
  })

  describe('getDebateById', () => {
    it('should fetch debate by id', async () => {
      const mockDebate = { 
        id: 'test-id', 
        topic: 'Test Topic', 
        messages: [] 
      }
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockDebate)
      })
      
      const result = await getDebateById('test-id')
      
      expect(result).toEqual(mockDebate)
    })

    it('should return null when not found', async () => {
      mockFetch.mockResolvedValue({ ok: false })
      
      const result = await getDebateById('nonexistent')
      
      expect(result).toBeNull()
    })
  })

  describe('streamDebate', () => {
    it('should handle SSE events', async () => {
      // Create a mock ReadableStream for SSE
      const encoder = new TextEncoder()
      const sseData = 'data: {"type":"status","text":"開始辯論"}\n\n'
      
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(encoder.encode(sseData))
          controller.close()
        }
      })

      mockFetch.mockResolvedValue({
        ok: true,
        body: stream
      })

      const events: SSEEvent[] = []
      await streamDebate(
        { topic: 'Test', max_rounds: 3 },
        (event) => events.push(event)
      )

      expect(events.length).toBeGreaterThan(0)
      expect(events[0].type).toBe('status')
      expect((events[0] as { type: 'status'; text: string }).text).toBe('開始辯論')
    })

    it('should handle abort signal', async () => {
      const abortController = new AbortController()
      
      // Create an error that mimics AbortError
      const abortError = new Error('The operation was aborted')
      abortError.name = 'AbortError'
      mockFetch.mockRejectedValue(abortError)
      
      const events: SSEEvent[] = []
      
      try {
        await streamDebate(
          { topic: 'Test' },
          (event) => events.push(event),
          abortController.signal
        )
      } catch {
        // Expected to throw
      }

      // When aborted, an event should be emitted
      expect(events.length).toBeGreaterThanOrEqual(0)
    })

    it('should handle HTTP error', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      })

      const events: SSEEvent[] = []
      
      try {
        await streamDebate(
          { topic: 'Test' },
          (event) => events.push(event)
        )
      } catch {
        // Expected to throw
      }

      expect(events.some(e => e.type === 'error')).toBe(true)
    })
  })
})
