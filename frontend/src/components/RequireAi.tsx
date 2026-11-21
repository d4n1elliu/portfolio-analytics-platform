// Lets the AI pages through only when the AI features are on.

import { Navigate, Outlet } from 'react-router'

import { useAuth } from '../lib/auth'
import { HOME } from '../routes'

function RequireAi() {
  const { state } = useAuth()
  const aiEnabled = state.status === 'signedIn' && state.user.ai_enabled
  return aiEnabled ? <Outlet /> : <Navigate to={HOME} replace />
}

export default RequireAi
