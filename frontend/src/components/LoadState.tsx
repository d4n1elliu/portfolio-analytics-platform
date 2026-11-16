import type { ReactNode } from 'react'

import type { QueryState } from '../hooks/useApiQuery'
import { MUTED_TEXT } from '../lib/styles'
import LoadError from './LoadError'

interface LoadStateProps<T> {
  state: QueryState<T>
  onRetry: () => void
  loadingText: string
  /** Shown in place of the content when the data has nothing in it. */
  emptyText: string
  isEmpty: (data: T) => boolean
  children: (data: T) => ReactNode
}

/** Shows a loading line, an error with a retry button, an empty line, or the loaded content. */
function LoadState<T>(props: LoadStateProps<T>) {
  const { state, onRetry, loadingText, emptyText, isEmpty, children } = props

  if (state.status === 'loading') return <p className={MUTED_TEXT}>{loadingText}</p>
  if (state.status === 'error') return <LoadError message={state.message} onRetry={onRetry} />
  if (isEmpty(state.data)) return <p className={MUTED_TEXT}>{emptyText}</p>
  return children(state.data)
}

export default LoadState
