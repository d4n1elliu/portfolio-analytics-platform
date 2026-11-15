import { useEffect, useState } from 'react'

import { COLOUR_TRANSITION, FOCUS_OUTLINE } from '../lib/styles'

const SHOW_RESULT_FOR = 2000
const LABELS = { idle: 'Copy', copied: 'Copied', failed: 'Not copied' }
const STYLE =
  `rounded-md border border-slate-300 bg-white px-2 py-1 text-xs font-medium ` +
  `hover:bg-slate-50 ${COLOUR_TRANSITION} ${FOCUS_OUTLINE}`

interface CopyButtonProps {
  text: string
  /** What is being copied, for screen readers, such as "Analyst email". */
  label: string
}

function CopyButton({ text, label }: CopyButtonProps) {
  const [result, setResult] = useState<keyof typeof LABELS>('idle')

  useEffect(() => {
    if (result === 'idle') return
    const timer = setTimeout(() => setResult('idle'), SHOW_RESULT_FOR)
    return () => clearTimeout(timer)
  }, [result])

  async function copy() {
    try {
      await navigator.clipboard.writeText(text)
      setResult('copied')
    } catch {
      // The browser can refuse, for example when the page is not in focus.
      setResult('failed')
    }
  }

  return (
    <button
      type="button"
      onClick={copy}
      aria-label={`Copy ${label}`}
      className={STYLE}
    >
      {/* Screen readers announce the result when the text changes. */}
      <span aria-live="polite">{LABELS[result]}</span>
    </button>
  )
}

export default CopyButton
