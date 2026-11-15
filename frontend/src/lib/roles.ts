import type { Role } from '../api/types'

export const ROLE_LABELS: Record<Role, string> = {
  operations: 'Operations',
  portfolio_manager: 'Portfolio Manager',
  analyst: 'Analyst',
}

export const ROLE_SUMMARIES: Record<Role, string> = {
  operations: 'Views everything and imports trades.',
  portfolio_manager: 'Views the dashboard, holdings and trades. Cannot import.',
  analyst: 'Views the dashboard, holdings and trades. Cannot import.',
}

/** Keep in step with POST /trades/import in the backend. */
export const IMPORT_ROLES: Role[] = ['operations']

export function canImportTrades(role: Role): boolean {
  return IMPORT_ROLES.includes(role)
}
