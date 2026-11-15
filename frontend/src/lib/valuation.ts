import type { Holding } from '../api/types'
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
