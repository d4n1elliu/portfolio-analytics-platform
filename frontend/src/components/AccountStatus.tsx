import { useAuth } from '../lib/auth'
import { ROLE_LABELS } from '../lib/roles'
import { ROUTES } from '../routes'
import Button from './Button'
import HeaderLink from './HeaderLink'

/** The signed-in user's name and role with a sign out button, or a link to sign in. */
function AccountStatus() {
  const { state, signOut } = useAuth()

  if (state.status === 'loading') return null

  if (state.status === 'signedOut') {
    return <HeaderLink to={ROUTES.login}>Sign in</HeaderLink>
  }

  return (
    <div className="flex items-center gap-3">
      <div className="text-right text-sm leading-tight">
        <p className="font-medium">{state.user.name}</p>
        <p className="text-xs text-slate-500">{ROLE_LABELS[state.user.role]}</p>
      </div>
      <Button variant="secondary" onClick={signOut}>
        Sign out
      </Button>
    </div>
  )
}

export default AccountStatus
