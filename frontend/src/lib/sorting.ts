export type SortDirection = 'ascending' | 'descending'

/** What a list is sorted by: a column, and which way. */
export interface SortBy<Key> {
  key: Key
  direction: SortDirection
}

/** Sort by a key. Choosing the same key again reverses the order. */
export function nextSort<Key>(current: SortBy<Key> | null, key: Key): SortBy<Key> {
  const reverse = current?.key === key && current.direction === 'ascending'
  return { key, direction: reverse ? 'descending' : 'ascending' }
}
