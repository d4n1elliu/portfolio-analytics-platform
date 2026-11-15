import { BrowserRouter, Navigate, Route, Routes } from 'react-router'

import AuthProvider from './components/AuthProvider'
import RequireAuth from './components/RequireAuth'
import SessionGate from './components/SessionGate'
import DashboardPage from './pages/DashboardPage'
import HoldingsPage from './pages/HoldingsPage'
import LoginPage from './pages/LoginPage'
import TradesPage from './pages/TradesPage'
import { ROUTES } from './routes'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <SessionGate>
          <Routes>
            <Route path={ROUTES.login} element={<LoginPage />} />
            <Route element={<RequireAuth />}>
              <Route path={ROUTES.dashboard} element={<DashboardPage />} />
              <Route path={ROUTES.holdings} element={<HoldingsPage />} />
              <Route path={ROUTES.trades} element={<TradesPage />} />
            </Route>
            {/* Any other address, including the home page, goes to Holdings. */}
            <Route path="*" element={<Navigate to={ROUTES.holdings} replace />} />
          </Routes>
        </SessionGate>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
