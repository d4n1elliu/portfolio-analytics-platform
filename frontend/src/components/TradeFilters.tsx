import type { TradeSide } from '../api/types'
import { NO_TRADE_FILTERS, TRADE_SIDES, hasTradeFilters } from '../lib/trades'
import type { TradeFilters as Filters } from '../lib/trades'
import Button from './Button'
import DateInput from './DateInput'
import Select from './Select'

interface TradeFiltersProps {
  filters: Filters
  tickers: string[]
  onChange: (filters: Filters) => void
}

function TradeFilters({ filters, tickers, onChange }: TradeFiltersProps) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <Select
        label="Ticker"
        allLabel="All tickers"
        options={tickers}
        value={filters.ticker}
        onChange={(ticker) => onChange({ ...filters, ticker })}
      />
      <Select
        label="Side"
        allLabel="Buys and sells"
        options={TRADE_SIDES}
        value={filters.side}
        // The list only holds the two sides and '' for both.
        onChange={(side) => onChange({ ...filters, side: side as TradeSide | '' })}
      />
      <DateInput
        label="From"
        value={filters.dateFrom}
        max={filters.dateTo || undefined}
        onChange={(dateFrom) => onChange({ ...filters, dateFrom })}
      />
      <DateInput
        label="To"
        value={filters.dateTo}
        min={filters.dateFrom || undefined}
        onChange={(dateTo) => onChange({ ...filters, dateTo })}
      />
      {hasTradeFilters(filters) && (
        <Button variant="secondary" onClick={() => onChange(NO_TRADE_FILTERS)}>
          Clear filters
        </Button>
      )}
    </div>
  )
}

export default TradeFilters
