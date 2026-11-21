// The page for the signed-in user: who they are, and a form to change their password.

import Card from '../components/Card'
import ChangePasswordForm from '../components/ChangePasswordForm'
import DetailsList from '../components/DetailsList'
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
        <DetailsList
          details={[
            { label: 'Name', value: user.name },
            { label: 'Email', value: user.email },
            { label: 'Role', value: ROLE_LABELS[user.role] },
            { label: 'Can', value: allowedActions(user) },
          ]}
        />
      </Card>
      <Card title="Change password">
        <ChangePasswordForm />
      </Card>
    </PageLayout>
  )
}

export default AccountPage
