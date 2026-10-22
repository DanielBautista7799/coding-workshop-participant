import {
  Navigate,
  Route,
  Routes,
} from 'react-router-dom'

import { useAuth } from './context/useAuth'

import AppLayout from './components/AppLayout'

import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import IncidentsPage from './pages/IncidentsPage'
import IncidentDetailPage from './pages/IncidentDetailPage'
import FacilitiesPage from './pages/FacilitiesPage'
import EngineersPage from './pages/EngineersPage'


function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
      />
    )
  }

  return children
}


function AdminRoute({ children }) {
  const { user } = useAuth()

  if (user.role !== 'FACILITY_ADMIN') {
    return (
      <Navigate
        to="/"
        replace
      />
    )
  }

  return children
}


function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={<LoginPage />}
      />

      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route
          path="/"
          element={<DashboardPage />}
        />

        <Route
          path="/incidents"
          element={<IncidentsPage />}
        />

        <Route
          path="/incidents/:id"
          element={<IncidentDetailPage />}
        />

        <Route
          path="/facilities"
          element={
            <AdminRoute>
              <FacilitiesPage />
            </AdminRoute>
          }
        />

        <Route
          path="/engineers"
          element={
            <AdminRoute>
              <EngineersPage />
            </AdminRoute>
          }
        />
      </Route>

      <Route
        path="*"
        element={
          <Navigate
            to="/"
            replace
          />
        }
      />
    </Routes>
  )
}


export default App