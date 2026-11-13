import { BrowserRouter, Navigate, Route, Routes } from 'react-router'

import HoldingsPage from './pages/HoldingsPage'
import TradesPage from './pages/TradesPage'
import { ROUTES } from './routes'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path={ROUTES.holdings} element={<HoldingsPage />} />
        <Route path={ROUTES.trades} element={<TradesPage />} />
        {/* Any other address, including the home page, goes to Holdings. */}
        <Route path="*" element={<Navigate to={ROUTES.holdings} replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
