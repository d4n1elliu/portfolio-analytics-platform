import { BrowserRouter, Route, Routes } from 'react-router'

import AuthProvider from './components/AuthProvider'
import HomeRedirect from './components/HomeRedirect'
import RequireAi from './components/RequireAi'
import RequireAuth from './components/RequireAuth'
import SessionGate from './components/SessionGate'
import AccountPage from './pages/AccountPage'
import AssistantPage from './pages/AssistantPage'
import DashboardPage from './pages/DashboardPage'
import HoldingsPage from './pages/HoldingsPage'
import LoginPage from './pages/LoginPage'
import SecurityPage from './pages/SecurityPage'
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
              <Route path={ROUTES.security} element={<SecurityPage />} />
              <Route path={ROUTES.account} element={<AccountPage />} />
              <Route element={<RequireAi />}>
                <Route path={ROUTES.assistant} element={<AssistantPage />} />
              </Route>
            </Route>
            <Route path="*" element={<HomeRedirect />} />
          </Routes>
        </SessionGate>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
