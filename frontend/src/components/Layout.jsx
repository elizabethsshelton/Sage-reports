import { Outlet, Link, useLocation } from 'react-router-dom'
import { Home, Users, FileText, Calendar, Settings, CheckCircle, XCircle } from 'lucide-react'

function Layout({ apiStatus }) {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/students', label: 'Students', icon: Users },
    { path: '/reports', label: 'Reports', icon: FileText },
    { path: '/settings', label: 'Settings', icon: Settings },
  ]

  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(path)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-sage-50 to-gray-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-sage-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-sage-800 tracking-tight">🎓 Sage Reports</h1>
            </div>
            
            <div className="flex items-center space-x-2">
              {apiStatus.connected ? (
                <div className="flex items-center text-green-700 text-sm font-medium px-3 py-1.5 bg-green-50 rounded-full border border-green-200">
                  <CheckCircle className="w-4 h-4 mr-1.5" />
                  <span>AI Connected</span>
                </div>
              ) : (
                <div className="flex items-center text-red-700 text-sm font-medium px-3 py-1.5 bg-red-50 rounded-full border border-red-200">
                  <XCircle className="w-4 h-4 mr-1.5" />
                  <span>AI Offline</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-sm border-b border-sage-200 sticky top-16 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {navItems.map((item) => {
              const Icon = item.icon
              const active = isActive(item.path)
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    flex items-center px-4 py-4 text-sm font-semibold border-b-3 transition-smooth
                    ${active 
                      ? 'border-sage-600 text-sage-800 bg-sage-50/50' 
                      : 'border-transparent text-sage-600 hover:text-sage-800 hover:bg-sage-50/30'
                    }
                  `}
                >
                  <Icon className={`w-4 h-4 mr-2 ${active ? 'text-sage-600' : ''}`} />
                  {item.label}
                </Link>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white/60 border-t border-sage-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-sage-600 font-medium">
            Sage Tutoring Report Assistant © 2025
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Layout
