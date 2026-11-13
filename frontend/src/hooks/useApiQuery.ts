import { useCallback, useEffect, useState } from 'react'

import { isAbortError, messageFrom } from '../api/client'

export type QueryState<T> =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'loaded'; data: T }

type Outcome<T> = Exclude<QueryState<T>, { status: 'loading' }>

interface QueryOptions {
  /** Keep showing the last data while newer data loads, instead of 'loading'. */
  keepPreviousData?: boolean
}

/**
 * Load data from the API and track whether it is loading, loaded or failed.
 *
 * Wrap `load` in useCallback. The data is fetched again whenever `load`
 * changes or `reload` is called.
 */
export function useApiQuery<T>(
  load: (signal: AbortSignal) => Promise<T>,
  { keepPreviousData = false }: QueryOptions = {},
) {
  const [reloadCount, setReloadCount] = useState(0)
  // The latest outcome, kept with the request that produced it.
  const [result, setResult] = useState<{
    load: typeof load
    reloadCount: number
    outcome: Outcome<T>
  } | null>(null)

  useEffect(() => {
    // Cancels the request if a newer one starts or the component is removed.
    const controller = new AbortController()

    load(controller.signal)
      .then((data) => setResult({ load, reloadCount, outcome: { status: 'loaded', data } }))
      .catch((error: unknown) => {
        if (isAbortError(error)) return
        const message = messageFrom(error, 'Could not load the data.')
        setResult({ load, reloadCount, outcome: { status: 'error', message } })
      })

    return () => controller.abort()
  }, [load, reloadCount])

  const reload = useCallback(() => setReloadCount((count) => count + 1), [])

  // An outcome from an earlier request means the current one is still loading.
  const isCurrent = result !== null && result.load === load && result.reloadCount === reloadCount
  const canKeep = keepPreviousData && result?.outcome.status === 'loaded'
  const state: QueryState<T> = isCurrent || canKeep ? result.outcome : { status: 'loading' }

  /** True while newer data loads behind the data on screen. */
  const isRefreshing = !isCurrent && canKeep

  return { state, reload, isRefreshing }
}
