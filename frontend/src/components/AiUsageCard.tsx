// A card showing how much of the AI allowance the signed-in user has used.

import { getAiUsage } from '../api/ai'
import { useApiQuery } from '../hooks/useApiQuery'
import { aiUsageDetails } from '../lib/aiUsage'
import Card from './Card'
import DetailsList from './DetailsList'
import LoadState from './LoadState'

function AiUsageCard() {
  const { state, reload } = useApiQuery(getAiUsage)

  return (
    <Card title="AI usage">
      <LoadState
        state={state}
        onRetry={reload}
        loadingText="Loading AI usage…"
        emptyText=""
        isEmpty={() => false}
      >
        {(usage) => <DetailsList details={aiUsageDetails(usage)} />}
      </LoadState>
    </Card>
  )
}

export default AiUsageCard
