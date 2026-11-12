import Button from './Button'

interface PaginationProps {
  /** Number of rows skipped before the current page. */
  offset: number
  pageSize: number
  total: number
  /** Called with the offset of the page to show. */
  onChange: (offset: number) => void
}

/** Previous and Next buttons. Renders nothing when everything fits on one page. */
function Pagination({ offset, pageSize, total, onChange }: PaginationProps) {
  if (total <= pageSize) return null

  return (
    <div className="flex justify-end gap-2 border-t border-slate-100 px-6 py-3">
      <Button
        variant="secondary"
        disabled={offset === 0}
        onClick={() => onChange(Math.max(0, offset - pageSize))}
      >
        Previous
      </Button>
      <Button
        variant="secondary"
        disabled={offset + pageSize >= total}
        onClick={() => onChange(offset + pageSize)}
      >
        Next
      </Button>
    </div>
  )
}

export default Pagination
