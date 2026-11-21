import type { Permission, Role, User } from '../api/types'

export const ROLE_LABELS: Record<Role, string> = {
  operations: 'Operations',
  portfolio_manager: 'Portfolio Manager',
  analyst: 'Analyst',
}

export const PERMISSION_LABELS: Record<Permission, string> = {
  import_trades: 'Import trades',
  export_trades: 'Export trades',
  upload_research: 'Upload research',
}

export function can(user: User | null, permission: Permission): boolean {
  return user !== null && user.permissions.includes(permission)
}

export function allowedActions(user: User): string {
  const actions = ['View everything', ...user.permissions.map((held) => PERMISSION_LABELS[held])]
  return actions.join(', ')
}
