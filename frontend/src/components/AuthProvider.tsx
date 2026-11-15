import { useCallback, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

import { getCurrentUser, login, logout } from '../api/auth'
import { isAbortError, setSessionExpiredHandler } from '../api/client'
import { AuthContext } from '../lib/auth'
import type { AuthState } from '../lib/auth'

const SIGNED_OUT: AuthState = { status: 'signedOut' }

function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ status: 'loading' })

  useEffect(() => {
    const controller = new AbortController()

    getCurrentUser(controller.signal)
      .then((user) => setState(user ? { status: 'signedIn', user } : SIGNED_OUT))
      .catch((error: unknown) => {
        // If the API cannot be reached, the pages show their own errors.
        if (!isAbortError(error)) setState(SIGNED_OUT)
      })

    return () => controller.abort()
  }, [])

  useEffect(() => {
    setSessionExpiredHandler(() => setState({ status: 'signedOut', reason: 'expired' }))
    return () => setSessionExpiredHandler(null)
  }, [])

  const signIn = useCallback(async (email: string, password: string) => {
    const user = await login(email, password)
    setState({ status: 'signedIn', user })
  }, [])

  const signOut = useCallback(async () => {
    await logout()
    setState({ status: 'signedOut', reason: 'choseTo' })
  }, [])

  const auth = useMemo(() => ({ state, signIn, signOut }), [state, signIn, signOut])

  return <AuthContext value={auth}>{children}</AuthContext>
}

export default AuthProvider
