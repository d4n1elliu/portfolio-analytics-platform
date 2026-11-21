import { useState } from 'react'

import { messageFrom } from '../api/client'
import { saveFile } from '../lib/download'
import Button from './Button'

interface DownloadButtonProps {
  label: string
  fileName: string
  /** Fetches the file from the API, for example exportTrades. */
  download: () => Promise<Blob>
}

/** A button that fetches a file and saves it, and says so if that fails. */
function DownloadButton({ label, fileName, download }: DownloadButtonProps) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleClick() {
    setBusy(true)
    setError(null)
    try {
      saveFile(await download(), fileName)
    } catch (thrown) {
      setError(messageFrom(thrown, 'The download failed.'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex items-center gap-3">
      {error && (
        <p role="alert" className="text-sm text-red-700">
          {error}
        </p>
      )}
      <Button variant="secondary" disabled={busy} onClick={handleClick}>
        {busy ? 'Preparing…' : label}
      </Button>
    </div>
  )
}

export default DownloadButton
