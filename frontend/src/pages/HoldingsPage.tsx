import Card from '../components/Card'
import PageLayout from '../components/PageLayout'

function HoldingsPage() {
  return (
    <PageLayout title="Holdings">
      <Card title="Positions">
        <p className="text-sm text-slate-500">The fund's current positions will be shown here.</p>
      </Card>
    </PageLayout>
  )
}

export default HoldingsPage
