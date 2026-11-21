// The page for the signed-in user: who they are, and a form to change their password.

import Card from '../components/Card'
import ChangePasswordForm from '../components/ChangePasswordForm'
import PageLayout from '../components/PageLayout'
import { useAuth } from '../lib/auth'
import { ROLE_LABELS, allowedActions } from '../lib/roles'

function AccountPage() {
  const { state } = useAuth()
  if (state.status !== 'signedIn') return null
  const { user } = state

  return (
    <PageLayout title="Account">
      <Card title="Your details">
        <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 text-sm">
          <dt className="text-slate-500">Name</dt>
          <dd>{user.name}</dd>
          <dt className="text-slate-500">Email</dt>
          <dd>{user.email}</dd>
          <dt className="text-slate-500">Role</dt>
          <dd>{ROLE_LABELS[user.role]}</dd>
          <dt className="text-slate-500">Can</dt>
          <dd>{allowedActions(user)}</dd>
        </dl>
      </Card>
      <Card title="Change password">
        <ChangePasswordForm />
      </Card>
    </PageLayout>
  )
}

export default AccountPage
