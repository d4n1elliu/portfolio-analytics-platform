import { ApiError, postJson, request } from './client'
import type { User } from './types'

const NOT_SIGNED_IN = 401

/** Sign in. The API sets the session cookie. */
export function login(email: string, password: string): Promise<User> {
  return postJson<User>('/auth/login', { email, password })
}

/** Sign out. The API clears the session cookie. */
export async function logout(): Promise<void> {
  await postJson('/auth/logout')
}

/** Fetch the signed-in user, or null when nobody is signed in. */
export async function getCurrentUser(signal?: AbortSignal): Promise<User | null> {
  try {
    return await request<User>('/auth/me', { signal })
  } catch (error) {
    if (error instanceof ApiError && error.status === NOT_SIGNED_IN) return null
    throw error
  }
}
