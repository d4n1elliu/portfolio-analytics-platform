import { useState } from 'react'

import { COLOUR_TRANSITION, FOCUS_OUTLINE } from '../lib/styles'
import EyeIcon from './EyeIcon'
import TextField from './TextField'

const EYE_BUTTON =
  `mr-1.5 rounded-md p-1.5 text-slate-400 hover:text-slate-700 ` +
  `${COLOUR_TRANSITION} ${FOCUS_OUTLINE}`

interface PasswordFieldProps {
  label: string
  value: string
  /** Tells the browser and password managers what the box holds. */
  autoComplete: string
  onChange: (value: string) => void
}

/** A password box with an eye button that shows or hides what was typed. */
function PasswordField({ label, value, autoComplete, onChange }: PasswordFieldProps) {
  const [visible, setVisible] = useState(false)

  return (
    <TextField
      label={label}
      type={visible ? 'text' : 'password'}
      value={value}
      autoComplete={autoComplete}
      onChange={onChange}
      trailing={
        <button
          // Not a submit button, so clicking it does not send the form.
          type="button"
          aria-label={visible ? 'Hide password' : 'Show password'}
          aria-pressed={visible}
          onClick={() => setVisible(!visible)}
          className={EYE_BUTTON}
        >
          <EyeIcon crossedOut={visible} />
        </button>
      }
    />
  )
}

export default PasswordField
