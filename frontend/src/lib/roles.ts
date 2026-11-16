import type { Role } from '../api/types'

export const ROLE_LABELS: Record<Role, string> = {
  operations: 'Operations',
  portfolio_manager: 'Portfolio Manager',
  analyst: 'Analyst',
}

/** Keep in step with POST /trades/import in the backend. */
export const IMPORT_ROLES: Role[] = ['operations']

export function canImportTrades(role: Role): boolean {
  return IMPORT_ROLES.includes(role)
}
