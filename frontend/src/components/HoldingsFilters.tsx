import type { HoldingFilters as Filters } from '../lib/holdings'
import Checkbox from './Checkbox'
import DateInput from './DateInput'
import SearchInput from './SearchInput'
import Select from './Select'

interface HoldingsFiltersProps {
  filters: Filters
  sectors: string[]
  assetClasses: string[]
  showClosed: boolean
  /** The tick box is disabled when this is 0. */
  closedCount: number
  /** The date the positions are shown for, as "YYYY-MM-DD", or '' for today. */
  asOf: string
  /** The latest date that can be picked. */
  today: string
  onAsOfChange: (asOf: string) => void
  onFiltersChange: (filters: Filters) => void
  onShowClosedChange: (showClosed: boolean) => void
}

function HoldingsFilters({
  filters,
  sectors,
  assetClasses,
  showClosed,
  closedCount,
  asOf,
  today,
  onAsOfChange,
  onFiltersChange,
  onShowClosedChange,
}: HoldingsFiltersProps) {
  return (
    <div className="flex flex-wrap items-center gap-3 px-6 pb-4">
      <SearchInput
        label="Search by ticker or name"
        placeholder="Search ticker or name"
        value={filters.search}
        onChange={(search) => onFiltersChange({ ...filters, search })}
      />
      <Select
        label="Sector"
        allLabel="All sectors"
        options={sectors}
        value={filters.sector}
        onChange={(sector) => onFiltersChange({ ...filters, sector })}
      />
      <Select
        label="Asset class"
        allLabel="All asset classes"
        options={assetClasses}
        value={filters.assetClass}
        onChange={(assetClass) => onFiltersChange({ ...filters, assetClass })}
      />
      <Checkbox
        label={`Show closed positions (${closedCount})`}
        checked={showClosed}
        onChange={onShowClosedChange}
        disabled={closedCount === 0}
        title={closedCount === 0 ? 'No closed positions yet' : undefined}
      />
      <DateInput label="As at" value={asOf} max={today} onChange={onAsOfChange} />
    </div>
  )
}

export default HoldingsFilters
