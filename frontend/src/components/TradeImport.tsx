import { listSecurities } from '../api/securities'
import { TRADE_CSV_COLUMNS, importTrades } from '../api/trades'
import { useApiQuery } from '../hooks/useApiQuery'
import Card from './Card'
import CsvImportForm from './CsvImportForm'

/** The card for uploading a CSV of trades, with the columns and tickers it accepts. */
function TradeImport({ onImported }: { onImported: () => void }) {
  const { state: securities } = useApiQuery(listSecurities)

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
          {securities.status === 'loaded' && (
            <p>Known tickers: {securities.data.map((security) => security.ticker).join(', ')}.</p>
          )}
        </div>
      </CsvImportForm>
    </Card>
  )
}

export default TradeImport
