import { Navigate, Outlet, useLocation } from 'react-router'

import { useAuth } from '../lib/auth'
import { MUTED_TEXT } from '../lib/styles'
import { ROUTES } from '../routes'
import type { LoginState } from '../routes'
import PageLayout from './PageLayout'

/** Shows the page inside it to a signed-in user. Anyone else is sent to the login page. */
function RequireAuth() {
  const { state } = useAuth()
  const { pathname } = useLocation()

  if (state.status === 'loading') {
    return (
      <PageLayout>
        <p className={MUTED_TEXT}>Loading…</p>
      </PageLayout>
    )
  }
  if (state.status === 'signedOut') {
    const returnTo: LoginState = { from: pathname }
    return <Navigate to={ROUTES.login} replace state={returnTo} />
  }
  return <Outlet />
}

export default RequireAuth
