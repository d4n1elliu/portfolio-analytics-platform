import { Navigate, Outlet, useLocation } from 'react-router'

import { useAuth } from '../lib/auth'
import { ROUTES } from '../routes'
import type { LoginState } from '../routes'

/** Shows the page inside it to a signed-in user. Anyone else is sent to the login page. */
function RequireAuth() {
  const { state } = useAuth()
  const { pathname } = useLocation()

  if (state.status === 'signedOut') {
    const returnTo: LoginState = { from: pathname }
    return <Navigate to={ROUTES.login} replace state={returnTo} />
  }
  return <Outlet />
}

export default RequireAuth
