// The API calls for the AI features.

import { request } from './client'
import type { AiUsage } from './types'

export function getAiUsage(signal?: AbortSignal): Promise<AiUsage> {
  return request<AiUsage>('/ai/usage', { signal })
}
