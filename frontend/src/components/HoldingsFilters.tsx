import type { HoldingFilters as Filters } from '../lib/holdings'
import Checkbox from './Checkbox'
import SearchInput from './SearchInput'
import Select from './Select'

interface HoldingsFiltersProps {
  filters: Filters
  sectors: string[]
  assetClasses: string[]
  showClosed: boolean
  onFiltersChange: (filters: Filters) => void
  onShowClosedChange: (showClosed: boolean) => void
}

/** The controls above the holdings table: search, two dropdowns and a tick box. */
function HoldingsFilters({
  filters,
  sectors,
  assetClasses,
  showClosed,
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
      <Checkbox label="Show closed positions" checked={showClosed} onChange={onShowClosedChange} />
    </div>
  )
}

export default HoldingsFilters
