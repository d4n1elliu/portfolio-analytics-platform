import type { Holding } from '../api/types'

/** An open, priced holding for tests. Pass only the fields a test is about. */
export function makeHolding(fields: Partial<Holding> = {}): Holding {
  return {
    ticker: 'BHP',
    security_name: 'BHP Group Limited',
    sector: 'Materials',
    asset_class: 'Equity',
    currency: 'AUD',
    quantity: '100.000000',
    average_cost: '40.000000',
    cost_basis: '4000.00',
    realised_pnl: '0.00',
    oversold_quantity: '0.000000',
    last_price: '45.000000',
    price_date: '2026-11-13',
    market_value: '4500.00',
    unrealised_pnl: '500.00',
    unrealised_return: '0.125000',
    weight: '1.000000',
    ...fields,
  }
}

/** A holding with no stored price, so its valuation fields are empty. */
export function makeUnpricedHolding(fields: Partial<Holding> = {}): Holding {
  return makeHolding({
    last_price: null,
    price_date: null,
    market_value: null,
    unrealised_pnl: null,
    unrealised_return: null,
    weight: null,
    ...fields,
  })
}
