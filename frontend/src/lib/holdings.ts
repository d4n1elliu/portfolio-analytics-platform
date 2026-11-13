import type { Holding } from '../api/types'

export interface HoldingFilters {
  /** Text to look for in the ticker or name. */
  search: string
  /** A sector to show, or '' for all. */
  sector: string
  /** An asset class to show, or '' for all. */
  assetClass: string
}

export const NO_FILTERS: HoldingFilters = { search: '', sector: '', assetClass: '' }

export interface HoldingsSummary {
  positions: number
  costBasis: number
  realisedPnl: number
  /** The currency of the totals, or null if the holdings use more than one. */
  currency: string | null
}

/** Holdings where more units were sold than were ever bought. */
export function findOversold(holdings: Holding[]): Holding[] {
  return holdings.filter((holding) => Number(holding.oversold_quantity) > 0)
}

/** The holdings to list: open positions, plus closed ones when asked for. */
export function selectByStatus(holdings: Holding[], showClosed: boolean): Holding[] {
  if (showClosed) return holdings
  // An oversold position is always listed, because it means the trades are wrong.
  return holdings.filter(
    (holding) => Number(holding.quantity) > 0 || Number(holding.oversold_quantity) > 0,
  )
}

/** How many positions are hidden until closed ones are asked for. */
export function countClosed(holdings: Holding[]): number {
  return holdings.length - selectByStatus(holdings, false).length
}

export function filterHoldings(holdings: Holding[], filters: HoldingFilters): Holding[] {
  const search = filters.search.trim().toLowerCase()
  return holdings.filter(
    (holding) =>
      (search === '' ||
        holding.ticker.toLowerCase().includes(search) ||
        holding.security_name.toLowerCase().includes(search)) &&
      (filters.sector === '' || holding.sector === filters.sector) &&
      (filters.assetClass === '' || holding.asset_class === filters.assetClass),
  )
}

export function hasFilters(filters: HoldingFilters): boolean {
  return filters.search.trim() !== '' || filters.sector !== '' || filters.assetClass !== ''
}

export function sectorsOf(holdings: Holding[]): string[] {
  return uniqueSorted(holdings.map((holding) => holding.sector))
}

export function assetClassesOf(holdings: Holding[]): string[] {
  return uniqueSorted(holdings.map((holding) => holding.asset_class))
}

export function summariseHoldings(holdings: Holding[]): HoldingsSummary {
  const currencies = new Set(holdings.map((holding) => holding.currency))
  return {
    positions: holdings.length,
    costBasis: sumMoney(holdings.map((holding) => holding.cost_basis)),
    realisedPnl: sumMoney(holdings.map((holding) => holding.realised_pnl)),
    currency: currencies.size === 1 ? [...currencies][0] : null,
  }
}

function uniqueSorted(values: string[]): string[] {
  return [...new Set(values)].sort((a, b) => a.localeCompare(b))
}

/** Add amounts in whole cents to avoid rounding errors. */
function sumMoney(amounts: string[]): number {
  const cents = amounts.reduce((total, amount) => total + Math.round(Number(amount) * 100), 0)
  return cents / 100
}
