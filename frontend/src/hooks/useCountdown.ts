import { useCallback, useEffect, useState } from 'react'

const ONE_SECOND = 1000

/** Returns the whole seconds left, 0 when not counting, and a function that starts a countdown. */
export function useCountdown(): [number, (seconds: number) => void] {
  const [endsAt, setEndsAt] = useState<number | null>(null)
  const [secondsLeft, setSecondsLeft] = useState(0)

  useEffect(() => {
    if (endsAt === null) return

    const timer = setInterval(() => {
      const left = Math.max(0, Math.ceil((endsAt - Date.now()) / ONE_SECOND))
      setSecondsLeft(left)
      if (left === 0) setEndsAt(null)
    }, ONE_SECOND)

    return () => clearInterval(timer)
  }, [endsAt])

  const start = useCallback((seconds: number) => {
    setEndsAt(Date.now() + seconds * ONE_SECOND)
    setSecondsLeft(seconds)
  }, [])

  return [secondsLeft, start]
}
