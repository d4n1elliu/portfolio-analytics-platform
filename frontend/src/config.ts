// App-wide settings. Change a value here and it applies everywhere.

/** Backend address. Override it with VITE_API_URL in frontend/.env. */
export const API_URL: string = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export const APP_NAME = 'Portfolio Analytics Platform'
export const APP_TAGLINE = 'A fictional fund. No real client data.'

/** Controls how dates and numbers are written, for example 16 Mar 2026. */
export const LOCALE = 'en-AU'
export const DEFAULT_CURRENCY = 'AUD'

/** Rows shown per page in tables. */
export const PAGE_SIZE = 25

export const IMPORT_HISTORY_SIZE = 10

export const SECURITY_TRADES_LIMIT = 500

export const MIN_PASSWORD_LENGTH = 12
