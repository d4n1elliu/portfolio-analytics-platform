// The address of each page, so links and routes use the same values.

export const ROUTES = {
  dashboard: '/dashboard',
  holdings: '/holdings',
  login: '/login',
  trades: '/trades',
} as const

/** What a page hands to the login page when it sends a signed-out visitor there. */
export interface LoginState {
  /** The address to return to after signing in. */
  from: string
}
