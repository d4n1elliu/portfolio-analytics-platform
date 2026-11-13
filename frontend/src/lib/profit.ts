/** Text colour for a profit or loss: green above zero, red below. */
export function profitColour(value: string | number): string {
  const amount = Number(value)
  if (amount > 0) return 'text-emerald-700'
  if (amount < 0) return 'text-red-700'
  return ''
}
