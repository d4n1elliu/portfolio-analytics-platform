import { BrowserRouter, Navigate, Route, Routes } from 'react-router'

import AuthProvider from './components/AuthProvider'
import DashboardPage from './pages/DashboardPage'
import HoldingsPage from './pages/HoldingsPage'
import TradesPage from './pages/TradesPage'
import { ROUTES } from './routes'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path={ROUTES.dashboard} element={<DashboardPage />} />
          <Route path={ROUTES.holdings} element={<HoldingsPage />} />
          <Route path={ROUTES.trades} element={<TradesPage />} />
          {/* Any other address, including the home page, goes to Holdings. */}
          <Route path="*" element={<Navigate to={ROUTES.holdings} replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
