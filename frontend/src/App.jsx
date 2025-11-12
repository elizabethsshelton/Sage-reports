import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Layout from './components/Layout'
import Students from './pages/Students'
import Reports from './pages/Reports'
import Calendar from './pages/Calendar'
import NewReport from './pages/NewReport'
import EditReport from './pages/EditReport'
import Settings from './pages/Settings'
import { checkAPIHealth } from './services/api'

function App() {
  const [apiStatus, setApiStatus] = useState({ connected: false, loading: true })

  useEffect(() => {
    checkAPIHealth()
      .then(status => {
        setApiStatus({ ...status, loading: false })
      })
      .catch(err => {
        setApiStatus({ connected: false, loading: false, error: err.message })
      })
  }, [])

  if (apiStatus.loading) {
    return (
      <div className="min-h-screen bg-sage-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sage-600 mx-auto mb-4"></div>
          <p className="text-sage-700">Loading Sage Reports...</p>
        </div>
      </div>
    )
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout apiStatus={apiStatus} />}>
          <Route index element={<Calendar />} />
          <Route path="students" element={<Students />} />
          <Route path="reports" element={<Reports />} />
          <Route path="reports/new" element={<NewReport />} />
          <Route path="reports/:id/edit" element={<EditReport />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
