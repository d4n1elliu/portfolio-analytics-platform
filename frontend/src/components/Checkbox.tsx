interface CheckboxProps {
  label: string
  checked: boolean
  onChange: (checked: boolean) => void
}

/** A tick box with its label. */
function Checkbox({ label, checked, onChange }: CheckboxProps) {
  return (
    <label className="inline-flex items-center gap-2 text-sm text-slate-700">
      <input
        type="checkbox"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
        className="size-4 rounded border-slate-300"
      />
      {label}
    </label>
  )
}

export default Checkbox
