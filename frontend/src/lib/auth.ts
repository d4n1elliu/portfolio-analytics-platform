import { createContext, useContext } from 'react'

import type { User } from '../api/types'

export type AuthState =
  | { status: 'loading' }
  // A visitor who was never signed in has no reason.
  | { status: 'signedOut'; reason?: 'expired' | 'choseTo' }
  | { status: 'signedIn'; user: User }

export interface Auth {
  state: AuthState
  /** Rejects with the API's message when the email or password is wrong. */
  signIn: (email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
}

export const AuthContext = createContext<Auth | null>(null)

export function useAuth(): Auth {
  const auth = useContext(AuthContext)
  if (!auth) throw new Error('useAuth must be used inside AuthProvider.')
  return auth
}
