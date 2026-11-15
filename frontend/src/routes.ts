// The address of each page, so links and routes use the same values.

export const ROUTES = {
  dashboard: '/dashboard',
  holdings: '/holdings',
  login: '/login',
  trades: '/trades',
} as const

/** The pages a signed-in user can open, in the order the nav bar lists them. */
export const PAGES = [
  { path: ROUTES.dashboard, label: 'Dashboard' },
  { path: ROUTES.holdings, label: 'Holdings' },
  { path: ROUTES.trades, label: 'Trades' },
]

/** What a page hands to the login page when it sends a signed-out visitor there. */
export interface LoginState {
  /** The address to return to after signing in. */
  from: string
}
