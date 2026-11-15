import { Navigate } from 'react-router'

import { useAuth } from '../lib/auth'
import { HOME, ROUTES } from '../routes'

/** Sends an address that is not a page to where the visitor should start. */
function HomeRedirect() {
  const { state } = useAuth()
  return <Navigate to={state.status === 'signedIn' ? HOME : ROUTES.login} replace />
}

export default HomeRedirect
