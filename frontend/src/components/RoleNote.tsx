// A card telling the user what their role can and cannot do on a page.

import type { Role } from '../api/types'
import { ROLE_LABELS } from '../lib/roles'
import { MUTED_TEXT } from '../lib/styles'
import Card from './Card'

interface RoleNoteProps {
  title: string
  role: Role
  can: string
  cannot: string
}

function RoleNote({ title, role, can, cannot }: RoleNoteProps) {
  return (
    <Card title={title}>
      <p className={MUTED_TEXT}>
        You are signed in as {ROLE_LABELS[role]}, which can {can} but not {cannot}.
      </p>
    </Card>
  )
}

export default RoleNote
