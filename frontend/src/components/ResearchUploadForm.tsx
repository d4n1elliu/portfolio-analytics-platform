// A form that uploads one research document with its title, ticker and date.

import { useState } from 'react'
import type { FormEvent } from 'react'

import { messageFrom } from '../api/client'
import { RESEARCH_FILE_TYPES } from '../config'
import { uploadProblem } from '../lib/research'
import type { ResearchUpload } from '../lib/research'
import { FILE_INPUT } from '../lib/styles'
import Alert from './Alert'
import Button from './Button'
import DateInput from './DateInput'
import Select from './Select'
import TextField from './TextField'

const EMPTY_UPLOAD: ResearchUpload = { file: null, title: '', ticker: '', documentDate: '' }

type FormState =
  | { status: 'idle' }
  | { status: 'uploading' }
  | { status: 'uploaded'; title: string }
  | { status: 'error'; message: string }

interface ResearchUploadFormProps {
  tickers: string[]
  today: string
  upload: (upload: ResearchUpload) => Promise<void>
}

function ResearchUploadForm({ tickers, today, upload }: ResearchUploadFormProps) {
  const [fields, setFields] = useState(EMPTY_UPLOAD)
  const [formKey, setFormKey] = useState(0)
  const [state, setState] = useState<FormState>({ status: 'idle' })

  function change(changed: Partial<ResearchUpload>) {
    setFields((current) => ({ ...current, ...changed }))
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const problem = uploadProblem(fields, today)
    if (problem !== null) {
      setState({ status: 'error', message: problem })
      return
    }

    setState({ status: 'uploading' })
    try {
      await upload(fields)
      setState({ status: 'uploaded', title: fields.title })
      setFields(EMPTY_UPLOAD)
      setFormKey((key) => key + 1)
    } catch (error) {
      setState({ status: 'error', message: messageFrom(error, 'The upload failed.') })
    }
  }

  return (
    <form key={formKey} onSubmit={handleSubmit} noValidate className="space-y-4">
      {state.status === 'uploaded' && <Alert variant="success">Uploaded {state.title}.</Alert>}
      {state.status === 'error' && <Alert variant="error">{state.message}</Alert>}
      <input
        type="file"
        accept={RESEARCH_FILE_TYPES.join(',')}
        aria-label="Research file"
        onChange={(event) => change({ file: event.target.files?.[0] ?? null })}
        className={FILE_INPUT}
      />
      <div className="max-w-md">
        <TextField
          label="Title"
          type="text"
          value={fields.title}
          autoComplete="off"
          onChange={(title) => change({ title })}
        />
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <Select
          label="Ticker"
          allLabel="Choose a ticker"
          options={tickers}
          value={fields.ticker}
          onChange={(ticker) => change({ ticker })}
        />
        <DateInput
          label="Document date"
          value={fields.documentDate}
          max={today}
          onChange={(documentDate) => change({ documentDate })}
        />
        <Button type="submit" disabled={state.status === 'uploading'}>
          {state.status === 'uploading' ? 'Uploading…' : 'Upload'}
        </Button>
      </div>
    </form>
  )
}

export default ResearchUploadForm
