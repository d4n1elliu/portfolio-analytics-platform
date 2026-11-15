import { useId } from 'react'
import type { ReactNode, Ref } from 'react'

import { FOCUS_OUTLINE, TEXT_INPUT } from '../lib/styles'

export interface TextFieldProps {
  label: string
  type: 'email' | 'password' | 'text'
  value: string
  /** Tells the browser and password managers what the box holds. */
  autoComplete: string
  onChange: (value: string) => void
  /** A small control shown inside the right end of the box, such as a button. */
  trailing?: ReactNode
  /** Puts the cursor in this box when the page opens. */
  autoFocus?: boolean
  /** Gives the page the box itself, for example to move the cursor to it. */
  inputRef?: Ref<HTMLInputElement>
}

/** A labelled text box that must be filled in. */
function TextField(props: TextFieldProps) {
  const { label, type, value, autoComplete, onChange, trailing, autoFocus, inputRef } = props
  const id = useId()

  return (
    <div className="space-y-1">
      <label htmlFor={id} className="block text-sm font-medium">
        {label}
      </label>
      <div className="relative">
        <input
          id={id}
          ref={inputRef}
          type={type}
          value={value}
          autoComplete={autoComplete}
          autoFocus={autoFocus}
          required
          onChange={(event) => onChange(event.target.value)}
          className={`${TEXT_INPUT} ${FOCUS_OUTLINE} ${trailing ? 'pr-10' : ''}`}
        />
        {trailing && <div className="absolute inset-y-0 right-0 flex items-center">{trailing}</div>}
      </div>
    </div>
  )
}

export default TextField
