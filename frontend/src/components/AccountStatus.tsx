import { useAuth } from '../lib/auth'
import { ROLE_LABELS } from '../lib/roles'
import Button from './Button'

function AccountStatus() {
  const { state, signOut } = useAuth()

  if (state.status !== 'signedIn') return null

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
