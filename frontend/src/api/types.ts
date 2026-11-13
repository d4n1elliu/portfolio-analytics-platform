// Shapes of the JSON the API returns. They mirror backend/app/schemas, so
// change both together.

/** One page of a list. */
export interface Page<T> {
  items: T[]
  /** Number of items in the whole list, not just on this page. */
  total: number
  limit: number
  offset: number
}

export interface ImportResult {
  imported: number
}

/** One problem in an uploaded CSV. The header is row 1. */
export interface ImportRowError {
  row: number
  column: string
  message: string
}

export interface Security {
  id: number
  ticker: string
  name: string
  sector: string
  asset_class: string
  currency: string
}

/** The position in one security. Decimals arrive as text, like Trade. */
export interface Holding {
  ticker: string
  security_name: string
  sector: string
  asset_class: string
  currency: string
  quantity: string
  /** Null when nothing is held. */
  average_cost: string | null
  cost_basis: string
  realised_pnl: string
  /** Units sold that were never held. */
  oversold_quantity: string
}

export type TradeSide = 'BUY' | 'SELL'

export interface Trade {
  id: number
  /** Date only, as "YYYY-MM-DD". */
  trade_date: string
  ticker: string
  security_name: string
  currency: string
  side: TradeSide
  // Decimals arrive as text such as "45.250000" to keep their precision.
  quantity: string
  price: string
  fees: string
  created_at: string
}
