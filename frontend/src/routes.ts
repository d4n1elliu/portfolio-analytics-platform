// The address of each page, so links and routes use the same values.

export const ROUTES = {
  dashboard: '/dashboard',
  holdings: '/holdings',
  login: '/login',
  trades: '/trades',
} as const

export const PAGES = [
  { path: ROUTES.dashboard, label: 'Dashboard' },
  { path: ROUTES.holdings, label: 'Holdings' },
  { path: ROUTES.trades, label: 'Trades' },
]

export const HOME = ROUTES.dashboard

export interface LoginState {
  from: string
}

/** Only a page of this app is accepted, so the value can never send someone to another site. */
export function returnPage(state: unknown) {
  const from = (state as Partial<LoginState> | null)?.from
  return PAGES.find((page) => page.path === from)
}
