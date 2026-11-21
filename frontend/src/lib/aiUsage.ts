// Describes how much of the AI allowance has been used.

import type { AiUsage } from '../api/types'
import type { Detail } from '../components/DetailsList'
import { formatQuantity } from './format'

export function aiUsageDetails(usage: AiUsage): Detail[] {
  return [
    {
      label: 'Requests in the last hour',
      value: usedOf(usage.requests_used, usage.requests_limit),
    },
    {
      label: 'Tokens in the last day',
      value: usedOf(usage.tokens_used, usage.tokens_limit),
    },
  ]
}

function usedOf(used: number, limit: number): string {
  return `${formatQuantity(used)} of ${formatQuantity(limit)}`
}
