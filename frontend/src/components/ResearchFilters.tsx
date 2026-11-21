// The filter bar of the research library: ticker and a date range.

import { NO_RESEARCH_FILTERS, hasResearchFilters } from '../lib/research'
import type { ResearchFilters as Filters } from '../lib/research'
import Button from './Button'
import DateRangeInputs from './DateRangeInputs'
import Select from './Select'

interface ResearchFiltersProps {
  filters: Filters
  tickers: string[]
  onChange: (filters: Filters) => void
}

function ResearchFilters({ filters, tickers, onChange }: ResearchFiltersProps) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <Select
        label="Ticker"
        allLabel="All tickers"
        options={tickers}
        value={filters.ticker}
        onChange={(ticker) => onChange({ ...filters, ticker })}
      />
      <DateRangeInputs
        from={filters.dateFrom}
        to={filters.dateTo}
        onFromChange={(dateFrom) => onChange({ ...filters, dateFrom })}
        onToChange={(dateTo) => onChange({ ...filters, dateTo })}
      />
      {hasResearchFilters(filters) && (
        <Button variant="secondary" onClick={() => onChange(NO_RESEARCH_FILTERS)}>
          Clear filters
        </Button>
      )}
    </div>
  )
}

export default ResearchFilters
