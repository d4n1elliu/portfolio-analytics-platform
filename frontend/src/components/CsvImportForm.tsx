import { useRef, useState } from 'react'
import type { FormEvent, ReactNode } from 'react'

import { messageFrom } from '../api/client'
import { rowErrorsFrom } from '../api/imports'
import type { ImportResult, ImportRowError } from '../api/types'
import { formatCount } from '../lib/format'
import Alert from './Alert'
import Button from './Button'

type ImportState =
  | { status: 'idle' }
  | { status: 'uploading' }
  | { status: 'success'; imported: number; fileName: string }
  | { status: 'error'; message: string; rowErrors: ImportRowError[] }

interface CsvImportFormProps {
  /** Sends the file to the API, for example importTrades. */
  upload: (file: File) => Promise<ImportResult>
  /** What one imported row is called, for the success message. */
  singular: string
  plural: string
  /** Called after rows have been saved. */
  onImported: () => void
  /** Help text shown above the file picker. */
  children?: ReactNode
}

/** A CSV file picker and upload button that shows the result or the row errors. */
function CsvImportForm({ upload, singular, plural, onImported, children }: CsvImportFormProps) {
  const [file, setFile] = useState<File | null>(null)
  const [state, setState] = useState<ImportState>({ status: 'idle' })
  const fileInput = useRef<HTMLInputElement>(null)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault() // Stop the browser reloading the page.
    if (!file) return

    setState({ status: 'uploading' })
    try {
      const result = await upload(file)
      setState({ status: 'success', imported: result.imported, fileName: file.name })
      // Clear the picker so the same file is not uploaded twice by accident.
      setFile(null)
      if (fileInput.current) fileInput.current.value = ''
      onImported()
    } catch (error) {
      setState({
        status: 'error',
        message: messageFrom(error, 'The upload failed.'),
        rowErrors: rowErrorsFrom(error),
      })
    }
  }

  const uploading = state.status === 'uploading'

  return (
    <div className="space-y-4">
      {children}

      <form onSubmit={handleSubmit} className="flex flex-wrap items-center gap-3">
        <input
          ref={fileInput}
          type="file"
          accept=".csv,text/csv"
          aria-label="CSV file"
          disabled={uploading}
          onChange={(event) => {
            setFile(event.target.files?.[0] ?? null)
            setState({ status: 'idle' })
          }}
          className="block text-sm text-slate-700 file:mr-3 file:cursor-pointer file:rounded-md file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:text-sm file:font-medium file:text-slate-800 hover:file:bg-slate-200"
        />
        <Button type="submit" disabled={!file || uploading}>
          {uploading ? 'Uploading…' : 'Upload'}
        </Button>
      </form>

      {state.status === 'success' && (
        <Alert variant="success">
          Imported {formatCount(state.imported, singular, plural)} from {state.fileName}.
        </Alert>
      )}

      {state.status === 'error' && (
        <Alert variant="error">
          <p className="font-medium">{state.message}</p>
          {state.rowErrors.length > 0 && (
            <ul className="mt-2 space-y-1">
              {state.rowErrors.map((rowError, index) => (
                <li key={index}>
                  <span className="font-medium">
                    Row {rowError.row}, {rowError.column}:
                  </span>{' '}
                  {rowError.message}
                </li>
              ))}
            </ul>
          )}
        </Alert>
      )}
    </div>
  )
}

export default CsvImportForm
