import { ApiError } from './client'
import type { ImportRowError } from './types'

/** The row errors from a rejected CSV import, or an empty list for any other error. */
export function rowErrorsFrom(error: unknown): ImportRowError[] {
  if (!(error instanceof ApiError)) return []
  const body = error.body
  if (typeof body === 'object' && body !== null && 'errors' in body && Array.isArray(body.errors)) {
    return body.errors as ImportRowError[]
  }
  return []
}
