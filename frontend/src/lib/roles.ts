import type { Role } from '../api/types'

/** The name of each role as shown to people. */
export const ROLE_LABELS: Record<Role, string> = {
  operations: 'Operations',
  portfolio_manager: 'Portfolio Manager',
  analyst: 'Analyst',
}

/** The roles that may import trades. Keep in step with POST /trades/import in the backend. */
export const IMPORT_ROLES: Role[] = ['operations']

export function canImportTrades(role: Role): boolean {
  return IMPORT_ROLES.includes(role)
}
