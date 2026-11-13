import { FOCUS_OUTLINE } from '../lib/styles'

interface CheckboxProps {
  label: string
  checked: boolean
  onChange: (checked: boolean) => void
  disabled?: boolean
  title?: string
}

/** A tick box with its label. */
function Checkbox({ label, checked, onChange, disabled = false, title }: CheckboxProps) {
  return (
    <label
      title={title}
      className={`inline-flex h-10 items-center gap-2 px-3 text-sm select-none ${disabled ? 'cursor-not-allowed text-slate-400' : 'text-slate-700'}`}
    >
      <input
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={(event) => onChange(event.target.checked)}
        className={`size-4 rounded border-slate-300 ${FOCUS_OUTLINE}`}
      />
      {label}
    </label>
  )
}

export default Checkbox
