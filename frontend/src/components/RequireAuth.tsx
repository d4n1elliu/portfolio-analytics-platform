import { Navigate, Outlet, useLocation } from 'react-router'

import { useAuth } from '../lib/auth'
import { ROUTES } from '../routes'
import type { LoginState } from '../routes'

/** Shows the page inside it to a signed-in user. Anyone else is sent to the login page. */
function RequireAuth() {
  const { state } = useAuth()
  const { pathname } = useLocation()

  if (state.status === 'signedIn') return <Outlet />

  // A user who chose to sign out is not trying to open this page, so the
  // login page is told nothing about it.
  const choseToSignOut = state.status === 'signedOut' && state.reason === 'choseTo'
  const returnTo: LoginState | undefined = choseToSignOut ? undefined : { from: pathname }
  return <Navigate to={ROUTES.login} replace state={returnTo} />
}

export default RequireAuth
