import type { Holding } from '../api/types'
import { formatDate } from './format'
import { commonCurrency, sumMoney } from './holdings'

/** A holding that has a stored price, so its valuation fields are filled in. */
export interface ValuedHolding extends Holding {
  market_value: string
  unrealised_pnl: string
}

export interface ValuationSummary {
  marketValue: number
  unrealisedPnl: number
  /** Unrealised P&L as a fraction of the cost basis, or null when the cost is zero. */
  unrealisedReturn: number | null
  /** The currency of the totals, or null if the holdings use more than one. */
  currency: string | null
}

export interface ProfitSummary {
  /** Profit already made by selling, including on positions that are now closed. */
  realisedPnl: number
  /** Realised and unrealised profit together. */
  totalPnl: number
}

export interface SectorShare {
  sector: string
  marketValue: number
  /** Share of the total market value, as a fraction. */
  weight: number
}

export function valuedHoldings(holdings: Holding[]): ValuedHolding[] {
  return holdings.filter(
    (holding): holding is ValuedHolding =>
      holding.market_value !== null && holding.unrealised_pnl !== null,
  )
}

export function summariseValuation(holdings: ValuedHolding[]): ValuationSummary {
  const costBasis = sumMoney(holdings.map((holding) => holding.cost_basis))
  const unrealisedPnl = sumMoney(holdings.map((holding) => holding.unrealised_pnl))
  return {
    marketValue: sumMoney(holdings.map((holding) => holding.market_value)),
    unrealisedPnl,
    unrealisedReturn: costBasis === 0 ? null : unrealisedPnl / costBasis,
    currency: commonCurrency(holdings),
  }
}

/** Add up the profit of every holding, open or closed. A holding with no price adds no unrealised profit. */
export function summariseProfit(holdings: Holding[]): ProfitSummary {
  const realised = holdings.map((holding) => holding.realised_pnl)
  const unrealised = valuedHoldings(holdings).map((holding) => holding.unrealised_pnl)
  return { realisedPnl: sumMoney(realised), totalPnl: sumMoney([...realised, ...unrealised]) }
}

/** How many open positions have no stored price, so cannot be valued. */
export function countUnpriced(holdings: Holding[]): number {
  return holdings.filter((holding) => Number(holding.quantity) > 0 && holding.market_value === null)
    .length
}

/** "Prices as at 13 Nov 2026", or nothing when there is no price date. */
export function pricesAsAt(priceDate: string | null): string {
  return priceDate === null ? '' : `Prices as at ${formatDate(priceDate)}`
}

export function latestPriceDate(holdings: Holding[]): string | null {
  const dates = holdings.map((holding) => holding.price_date).filter((date) => date !== null)
  return dates.sort().at(-1) ?? null
}

/** Each sector's market value and share of the total, largest first. */
export function sectorAllocation(holdings: ValuedHolding[]): SectorShare[] {
  const valuesBySector = new Map<string, string[]>()
  for (const holding of holdings) {
    const values = valuesBySector.get(holding.sector) ?? []
    valuesBySector.set(holding.sector, [...values, holding.market_value])
  }

  const total = sumMoney(holdings.map((holding) => holding.market_value))
  return [...valuesBySector]
    .map(([sector, values]) => {
      const marketValue = sumMoney(values)
      return { sector, marketValue, weight: total === 0 ? 0 : marketValue / total }
    })
    .sort((a, b) => b.marketValue - a.marketValue)
}
