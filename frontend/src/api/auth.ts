import { ApiError, NOT_SIGNED_IN, postJson, request } from './client'
import type { DemoAccess, User } from './types'

export function login(email: string, password: string): Promise<User> {
  return postJson<User>('/auth/login', { email, password })
}

export async function logout(): Promise<void> {
  await postJson('/auth/logout')
}

export async function getCurrentUser(signal?: AbortSignal): Promise<User | null> {
  try {
    return await request<User>('/auth/me', { signal })
  } catch (error) {
    if (error instanceof ApiError && error.status === NOT_SIGNED_IN) return null
    throw error
  }
}

export function listDemoAccess(signal?: AbortSignal): Promise<DemoAccess[]> {
  return request<DemoAccess[]>('/auth/demo-accounts', { signal })
}
