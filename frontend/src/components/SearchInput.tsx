import { FOCUS_OUTLINE } from '../lib/styles'

interface SearchInputProps {
  /** Describes the box for screen readers. */
  label: string
  value: string
  placeholder?: string
  onChange: (value: string) => void
}

function SearchInput({ label, value, placeholder, onChange }: SearchInputProps) {
  return (
    <input
      type="search"
      aria-label={label}
      value={value}
      placeholder={placeholder}
      onChange={(event) => onChange(event.target.value)}
      className={`h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm placeholder:text-slate-400 sm:w-64 ${FOCUS_OUTLINE}`}
    />
  )
}

export default SearchInput
