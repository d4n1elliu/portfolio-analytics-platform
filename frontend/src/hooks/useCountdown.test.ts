// @vitest-environment jsdom
// Tests for useCountdown.

import { act, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { useCountdown } from './useCountdown'

beforeEach(() => vi.useFakeTimers())
afterEach(() => vi.useRealTimers())

describe('useCountdown', () => {
  it('counts down each second and stops at zero', () => {
    const { result } = renderHook(() => useCountdown())
    expect(result.current[0]).toBe(0)

    act(() => result.current[1](3))
    expect(result.current[0]).toBe(3)

    act(() => vi.advanceTimersByTime(1000))
    expect(result.current[0]).toBe(2)

    act(() => vi.advanceTimersByTime(5000))
    expect(result.current[0]).toBe(0)
    expect(vi.getTimerCount()).toBe(0)
  })
})
