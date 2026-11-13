import type { ReactNode } from 'react'

const VARIANTS = {
  success: 'border-emerald-200 bg-emerald-50 text-emerald-800',
  warning: 'border-amber-200 bg-amber-50 text-amber-900',
  error: 'border-red-200 bg-red-50 text-red-800',
}

interface AlertProps {
  variant: keyof typeof VARIANTS
  children: ReactNode
}

/** A coloured message box. Screen readers announce it when it appears. */
function Alert({ variant, children }: AlertProps) {
  return (
    <div
      role={variant === 'error' ? 'alert' : 'status'}
      className={`rounded-md border px-4 py-3 text-sm ${VARIANTS[variant]}`}
    >
      {children}
    </div>
  )
}

export default Alert
