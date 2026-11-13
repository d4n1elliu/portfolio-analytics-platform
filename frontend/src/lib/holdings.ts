// Questions the app asks about a list of holdings.

import type { Holding } from '../api/types'

/** Holdings where more units were sold than were ever bought. */
export function findOversold(holdings: Holding[]): Holding[] {
  return holdings.filter((holding) => Number(holding.oversold_quantity) > 0)
}
