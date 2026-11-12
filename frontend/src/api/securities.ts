import { request } from './client'
import type { Security } from './types'

/** Fetch every security, ordered by ticker. */
export function listSecurities(signal?: AbortSignal): Promise<Security[]> {
  return request<Security[]>('/securities', { signal })
}
