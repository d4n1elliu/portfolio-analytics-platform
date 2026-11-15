import type { Role } from '../api/types'

/** The name of each role as shown to people. */
export const ROLE_LABELS: Record<Role, string> = {
  operations: 'Operations',
  portfolio_manager: 'Portfolio Manager',
  analyst: 'Analyst',
}
