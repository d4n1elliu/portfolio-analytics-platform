import type { Role } from '../api/types'
import { ROLE_LABELS } from '../lib/roles'
import { MUTED_TEXT } from '../lib/styles'
import Card from './Card'

function TradeImportNotAllowed({ role }: { role: Role }) {
  return (
    <Card title="Import trades">
      <p className={MUTED_TEXT}>
        You are signed in as {ROLE_LABELS[role]}, which can view trades but not import them.
      </p>
    </Card>
  )
}

export default TradeImportNotAllowed
