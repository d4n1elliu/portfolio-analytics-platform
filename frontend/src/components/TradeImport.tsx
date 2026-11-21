import { TRADE_CSV_COLUMNS, importTrades } from '../api/trades'
import Card from './Card'
import CsvImportForm from './CsvImportForm'

interface TradeImportProps {
  /** The tickers a file may use. Empty until they have loaded. */
  tickers: string[]
  onImported: () => void
}

function TradeImport({ tickers, onImported }: TradeImportProps) {
  return (
    <Card title="Import trades">
      <CsvImportForm upload={importTrades} singular="trade" plural="trades" onImported={onImported}>
        <div className="space-y-1 text-sm text-slate-600">
          <p>
            Upload a CSV file with the columns{' '}
            <code className="rounded bg-slate-100 px-1 py-0.5 text-xs">
              {TRADE_CSV_COLUMNS.join(', ')}
            </code>
            .
          </p>
          {tickers.length > 0 && <p>Known tickers: {tickers.join(', ')}.</p>}
        </div>
      </CsvImportForm>
    </Card>
  )
}

export default TradeImport
