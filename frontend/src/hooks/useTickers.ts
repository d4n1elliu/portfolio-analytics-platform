// Loads the ticker of every security. Empty until they have loaded.

import { useMemo } from 'react'

import { listSecurities } from '../api/securities'
import { useApiQuery } from './useApiQuery'

export function useTickers(): string[] {
  const { state } = useApiQuery(listSecurities)
  return useMemo(
    () => (state.status === 'loaded' ? state.data.map((security) => security.ticker) : []),
    [state],
  )
}
