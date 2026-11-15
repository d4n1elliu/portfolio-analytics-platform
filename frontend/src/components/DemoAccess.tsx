import { listDemoAccess } from '../api/auth'
import type { DemoAccess as Access } from '../api/types'
import { useApiQuery } from '../hooks/useApiQuery'
import { ROLE_LABELS, ROLE_SUMMARIES } from '../lib/roles'
import { MUTED_TEXT } from '../lib/styles'
import Card from './Card'
import CopyButton from './CopyButton'

/** Lists the demo roles, with the sign-in details of the ones that are public. */
function DemoAccess() {
  const { state } = useApiQuery(listDemoAccess)

  // The box is a convenience, so nothing is shown if the list cannot be loaded.
  if (state.status !== 'loaded') return null

  return (
    <Card title="Demo access">
      <ul className="space-y-4">
        {state.data.map((access) => (
          <li key={access.role} className="space-y-2">
            <div>
              <p className="text-sm font-medium">{ROLE_LABELS[access.role]}</p>
              <p className={MUTED_TEXT}>{ROLE_SUMMARIES[access.role]}</p>
            </div>
            <SignInDetails access={access} />
          </li>
        ))}
      </ul>
    </Card>
  )
}

function SignInDetails({ access }: { access: Access }) {
  if (access.email === null || access.password === null) {
    return <p className="text-sm">Available on request.</p>
  }
  const role = ROLE_LABELS[access.role]

  return (
    <dl className="space-y-1 text-sm">
      <Detail name="Email" value={access.email} copyLabel={`${role} email`} />
      <Detail name="Password" value={access.password} copyLabel={`${role} password`} />
    </dl>
  )
}

function Detail({ name, value, copyLabel }: { name: string; value: string; copyLabel: string }) {
  return (
    <div className="flex items-center gap-2">
      <dt className="w-20 text-slate-500">{name}</dt>
      <dd className="min-w-0 flex-1 truncate font-mono text-xs">{value}</dd>
      <CopyButton text={value} label={copyLabel} />
    </div>
  )
}

export default DemoAccess
