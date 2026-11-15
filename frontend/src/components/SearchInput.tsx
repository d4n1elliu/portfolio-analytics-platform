import { FOCUS_OUTLINE, TEXT_INPUT } from '../lib/styles'

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
      className={`${TEXT_INPUT} sm:w-64 ${FOCUS_OUTLINE}`}
    />
  )
}

export default SearchInput
