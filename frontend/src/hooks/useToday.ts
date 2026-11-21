// Today's date as "YYYY-MM-DD", read once so it does not change while a page is open.

import { useState } from 'react'

import { toIsoDate } from '../lib/dates'

export function useToday(): string {
  const [today] = useState(() => toIsoDate(new Date()))
  return today
}
