import { createContext, useContext } from 'react'

import type { User } from '../api/types'

export type AuthState =
  // 'loading' while the app asks the API whether somebody is signed in.
  | { status: 'loading' }
  // 'reason' says how a signed-in user came to be signed out. A visitor who
  // was never signed in has none.
  | { status: 'signedOut'; reason?: 'expired' | 'choseTo' }
  | { status: 'signedIn'; user: User }

export interface Auth {
  state: AuthState
  /** Rejects with the API's message when the email or password is wrong. */
  signIn: (email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
}

export const AuthContext = createContext<Auth | null>(null)

/** Who is signed in, and how to sign in and out. Use inside AuthProvider. */
export function useAuth(): Auth {
  const auth = useContext(AuthContext)
  if (!auth) throw new Error('useAuth must be used inside AuthProvider.')
  return auth
}
