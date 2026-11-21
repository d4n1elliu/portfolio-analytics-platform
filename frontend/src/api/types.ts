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

export interface SecurityPrice {
  /** Date only, as "YYYY-MM-DD". */
  date: string
  close: string
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
  // The fields below are null when the position is closed or has no stored price.
  last_price: string | null
  /** Date only, as "YYYY-MM-DD". */
  price_date: string | null
  market_value: string | null
  unrealised_pnl: string | null
  /** A fraction, such as "0.088552" for 8.86%. */
  unrealised_return: string | null
  /** Share of the total market value, as a fraction. */
  weight: string | null
}

/** The value of the open positions at the end of one date. */
export interface PortfolioHistoryPoint {
  /** Date only, as "YYYY-MM-DD". */
  date: string
  market_value: string
  cost_basis: string
  unrealised_pnl: string
}

export type PerformancePeriod = '1m' | '3m' | 'ytd' | '1y' | 'inception'

export interface PeriodReturn {
  period: PerformancePeriod
  /** A fraction, such as "0.088552" for 8.86%. Null when the history starts after the period. */
  portfolio_return: string | null
  /** The date the return is measured from. Null when there is no return. */
  start_date: string | null
  benchmark_return: string | null
}

export interface GrowthPoint {
  /** Date only, as "YYYY-MM-DD". */
  date: string
  /** What 1 invested at the start is worth at the end of this date. */
  portfolio: string
  benchmark: string | null
}

export interface PortfolioPerformance {
  /** The latest priced date, or null when there is no history. */
  as_of: string | null
  benchmark: string | null
  periods: PeriodReturn[]
  growth: GrowthPoint[]
}

export type Role = 'operations' | 'portfolio_manager' | 'analyst'

export type Permission = 'import_trades' | 'export_trades' | 'upload_research'

export interface User {
  email: string
  name: string
  role: Role
  permissions: Permission[]
  ai_enabled: boolean
}

export interface AiUsage {
  requests_used: number
  requests_limit: number
  tokens_used: number
  tokens_limit: number
}

export type ChatRole = 'user' | 'assistant'

export type ToolCallStatus = 'running' | 'done' | 'failed'

export interface ToolCall {
  id: string
  name: string
  input: string
  output: string | null
  status: ToolCallStatus
}

export interface ChatMessage {
  id: string
  role: ChatRole
  text: string
  toolCalls: ToolCall[]
}

export interface ChatTurn {
  role: ChatRole
  text: string
}

export type ChatEvent =
  | { type: 'text'; text: string }
  | { type: 'tool_call'; id: string; name: string; input: Record<string, unknown> }
  | { type: 'tool_result'; id: string; output: string; failed: boolean }
  | { type: 'done' }
  | { type: 'error'; message: string }

export type TradeSide = 'BUY' | 'SELL'

export type TradeSortKey = 'trade_date' | 'ticker' | 'side' | 'quantity' | 'price' | 'fees'

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

export interface ImportBatch {
  id: number
  file_name: string
  row_count: number
  imported_by: string
  created_at: string
}

export interface ResearchDocument {
  id: number
  title: string
  file_name: string
  ticker: string
  document_date: string
  chunk_count: number
  uploaded_by: string
  created_at: string
}

export interface ResearchChunk {
  id: number
  position: number
  text: string
}

export interface ResearchDocumentDetail extends ResearchDocument {
  chunks: ResearchChunk[]
}
