import type { Role } from '../api/types'
import { IMPORT_ROLES, ROLE_LABELS } from '../lib/roles'
import { MUTED_TEXT } from '../lib/styles'
import Card from './Card'

function TradeImportNotAllowed({ role }: { role: Role }) {
  const allowed = IMPORT_ROLES.map((allowedRole) => ROLE_LABELS[allowedRole]).join(' or ')

  return (
    <Card title="Import trades">
      <p className={MUTED_TEXT}>
        Only the {allowed} role can import trades. You are signed in as {ROLE_LABELS[role]}, which
        can view trades but not add them.
      </p>
    </Card>
  )
}

export default TradeImportNotAllowed
