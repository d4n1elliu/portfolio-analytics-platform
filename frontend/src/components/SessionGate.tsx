import type { ReactNode } from 'react'

import { useAuth } from '../lib/auth'
import { MUTED_TEXT } from '../lib/styles'
import PageLayout from './PageLayout'

/** Holds every page back until the app knows whether somebody is signed in. */
function SessionGate({ children }: { children: ReactNode }) {
  const { state } = useAuth()

  if (state.status === 'loading') {
    return (
      <PageLayout>
        <p role="status" className={MUTED_TEXT}>
          Loading…
        </p>
      </PageLayout>
    )
  }
  return children
}

export default SessionGate
