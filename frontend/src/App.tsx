import { useEffect, useState } from 'react'

// Set VITE_API_URL in frontend/.env to point at a different backend.
const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

type ApiStatus = 'checking' | 'ok' | 'unreachable'

function App() {
  const [status, setStatus] = useState<ApiStatus>('checking')

  useEffect(() => {
    // Lets the cleanup function below cancel the request if this component
    // is removed from the page before the response arrives.
    const controller = new AbortController()

    fetch(`${API_URL}/health`, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        return response.json()
      })
      .then((data: { status: string }) => {
        setStatus(data.status === 'ok' ? 'ok' : 'unreachable')
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) return
        console.error('Health check failed:', error)
        setStatus('unreachable')
      })

    return () => controller.abort()
  }, [])

  return (
    <main className="min-h-screen bg-slate-50 p-8 text-slate-900">
      <h1 className="text-3xl font-semibold">Portfolio Analytics Platform</h1>
      <p className="mt-4">
        API status:{' '}
        <span
          className={
            status === 'ok'
              ? 'font-medium text-emerald-700'
              : status === 'unreachable'
                ? 'font-medium text-red-700'
                : 'text-slate-500'
          }
        >
          {status}
        </span>
      </p>
    </main>
  )
}

export default App
