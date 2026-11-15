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

/** Where a signed-in user starts. */
export const HOME = ROUTES.dashboard

/** What a page hands to the login page when it sends a signed-out visitor there. */
export interface LoginState {
  /** The address to return to after signing in. */
  from: string
}

/**
 * The page a visitor was sent to the login page from, if any.
 *
 * Only a page of this app is accepted, so the value can never send someone
 * to another site.
 */
export function returnPage(state: unknown) {
  const from = (state as Partial<LoginState> | null)?.from
  return PAGES.find((page) => page.path === from)
}
