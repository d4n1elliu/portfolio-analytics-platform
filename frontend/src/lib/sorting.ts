// What a list is sorted by, and how a click on a column changes it.

export type SortDirection = 'ascending' | 'descending'

export interface SortBy<Key> {
  key: Key
  direction: SortDirection
}

export function nextSort<Key>(current: SortBy<Key> | null, key: Key): SortBy<Key> {
  const reverse = current?.key === key && current.direction === 'ascending'
  return { key, direction: reverse ? 'descending' : 'ascending' }
}
