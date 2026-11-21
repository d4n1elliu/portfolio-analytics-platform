// Tests for describing the AI allowance.

import { describe, expect, it } from 'vitest'

import { aiUsageDetails } from './aiUsage'

describe('aiUsageDetails', () => {
  it('shows what was used out of each limit, with thousands separated', () => {
    const details = aiUsageDetails({
      requests_used: 3,
      requests_limit: 20,
      tokens_used: 12400,
      tokens_limit: 200000,
    })

    expect(details).toEqual([
      { label: 'Requests in the last hour', value: '3 of 20' },
      { label: 'Tokens in the last day', value: '12,400 of 200,000' },
    ])
  })
})
