import { Navigate } from 'react-router'

import { useAuth } from '../lib/auth'
import { HOME, ROUTES } from '../routes'

function HomeRedirect() {
  const { state } = useAuth()
  return <Navigate to={state.status === 'signedIn' ? HOME : ROUTES.login} replace />
}

export default HomeRedirect
