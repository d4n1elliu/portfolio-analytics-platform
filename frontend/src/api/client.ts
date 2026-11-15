// The only file that calls fetch. Everything else uses the typed functions
// in this folder.

import { API_URL } from '../config'

/** Thrown when the API cannot be reached or answers with an error status. */
export class ApiError extends Error {
  /** HTTP status code, or 0 if the request never reached the API. */
  readonly status: number
  /** The JSON body of the error response, if it had one. */
  readonly body: unknown

  constructor(message: string, status: number, body: unknown = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.body = body
  }
}

/** Send a request to the API and return the parsed JSON response. */
export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    // Sends the session cookie, which the browser leaves out by default when
    // the API is on a different address, as it is in development.
    response = await fetch(`${API_URL}${path}`, { credentials: 'include', ...init })
  } catch (error) {
    if (isAbortError(error)) throw error
    throw new ApiError('Could not reach the API. Check that the backend is running.', 0)
  }

  // An error response may have no JSON body.
  const body: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    throw new ApiError(errorMessage(body, response.status), response.status, body)
  }
  return body as T
}

/** Send a POST request with a JSON body. */
export function postJson<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body ?? {}),
  })
}

/** Upload one file as a form field named "file". */
export function uploadFile<T>(path: string, file: File): Promise<T> {
  const form = new FormData()
  form.append('file', file)
  return request<T>(path, { method: 'POST', body: form })
}

/** True for the error thrown when a request is cancelled. */
export function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError'
}

/** The message to show a user for any thrown error. */
export function messageFrom(error: unknown, fallback: string): string {
  return error instanceof Error ? error.message : fallback
}

/** Prefer the API's own "detail" text when it sent one. */
function errorMessage(body: unknown, status: number): string {
  if (typeof body === 'object' && body !== null && 'detail' in body) {
    if (typeof body.detail === 'string') return body.detail
  }
  return `The request failed (HTTP ${status}).`
}
