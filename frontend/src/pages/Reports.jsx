import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Plus, Edit2, Trash2, Search, Calendar, GraduationCap } from 'lucide-react'
import { getReports, getStudents, deleteReport, toggleReportTraining } from '../services/api'

function Reports() {
  const [searchParams] = useSearchParams()
  const [reports, setReports] = useState([])
  const [allReports, setAllReports] = useState([])
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStudent, setFilterStudent] = useState(searchParams.get('student') || '')
  const [filterStatus, setFilterStatus] = useState('')
  const [showType, setShowType] = useState('all') // all, regular, samples (based on source)
  const [sortBy, setSortBy] = useState('date-desc')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [reportsData, studentsData] = await Promise.all([
        getReports(),
        getStudents(false)
      ])
      setReports(reportsData)
      setStudents(studentsData)
      
      // All reports are now in one table - just sort by date
      const sorted = reportsData
        .map(r => ({ ...r, sortDate: r.session_date }))
        .sort((a, b) => new Date(b.sortDate) - new Date(a.sortDate))
      
      setAllReports(sorted)
    } catch (error) {
      console.error('Error loading reports:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this report?')) {
      try {
        await deleteReport(id)
        loadData()
      } catch (error) {
        console.error('Error deleting report:', error)
        alert('Error deleting report. Please try again.')
      }
    }
  }

  const handleToggleTraining = async (id, e) => {
    e.preventDefault()
    e.stopPropagation()
    try {
      await toggleReportTraining(id)
      loadData()
    } catch (error) {
      console.error('Error toggling training status:', error)
      alert('Error updating training status. Please try again.')
    }
  }

  const filteredAndSortedReports = allReports
    .filter((report) => {
      // Type filter (based on source)
      if (showType === 'regular' && report.source !== 'created') return false
      if (showType === 'samples' && report.source !== 'uploaded') return false
      
      // Search filter
      const matchesSearch = !searchTerm || 
        report.student_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.topics_covered?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.subject?.toLowerCase().includes(searchTerm.toLowerCase())
      
      // Student filter
      const matchesStudent = !filterStudent || 
        report.student_id === parseInt(filterStudent)
      
      // Status filter
      const matchesStatus = !filterStatus || report.status === filterStatus

      return matchesSearch && matchesStudent && matchesStatus
    })
    .sort((a, b) => {
      // Sort logic
      switch (sortBy) {
        case 'date-desc':
          return new Date(b.sortDate) - new Date(a.sortDate)
        case 'date-asc':
          return new Date(a.sortDate) - new Date(b.sortDate)
        case 'student-asc':
          return (a.student_name || '').localeCompare(b.student_name || '')
        case 'student-desc':
          return (b.student_name || '').localeCompare(a.student_name || '')
        default:
          return new Date(b.sortDate) - new Date(a.sortDate)
      }
    })

  if (loading) {
    return <div className="text-center py-12">Loading reports...</div>
  }

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-sage-800">Reports</h2>
        <Link
          to="/reports/new"
          className="inline-flex items-center px-4 py-2 bg-sage-600 text-white rounded-lg hover:bg-sage-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Report
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-sage-200 p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-sage-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search reports..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
            />
          </div>

          <select
            value={filterStudent}
            onChange={(e) => setFilterStudent(e.target.value)}
            className="px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
          >
            <option value="">All Students</option>
            {students.map((student) => (
              <option key={student.id} value={student.id}>
                {student.name}
              </option>
            ))}
          </select>

          <select
            value={showType}
            onChange={(e) => setShowType(e.target.value)}
            className="px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
          >
            <option value="all">All Reports</option>
            <option value="regular">Created Reports</option>
            <option value="samples">Uploaded Reports</option>
          </select>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
          >
            <option value="">All Status</option>
            <option value="draft">Draft</option>
            <option value="sent">Sent</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
          >
            <option value="date-desc">Date (Newest First)</option>
            <option value="date-asc">Date (Oldest First)</option>
          </select>
        </div>
      </div>

      {/* Reports List */}
      {filteredAndSortedReports.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-sage-200 p-12 text-center">
          <p className="text-sage-600 mb-4">
            {allReports.length === 0 ? 'No reports yet' : 'No reports match your filters'}
          </p>
          <Link
            to="/reports/new"
            className="text-sage-600 hover:text-sage-700 font-medium"
          >
            Create a new report →
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-sage-200 divide-y divide-sage-200">
          {filteredAndSortedReports.map((report) => (
            <div
              key={report.id}
              className="p-6 hover:bg-sage-50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-2 flex-wrap gap-2">
                    <h3 className="text-lg font-semibold text-sage-900">
                      {report.student_name || 'Unknown Student'}
                    </h3>
                    
                    {/* Status Badge */}
                    <span className={`
                      px-3 py-1 rounded-full text-xs font-medium
                      ${report.status === 'draft' ? 'bg-yellow-100 text-yellow-800' : ''}
                      ${report.status === 'sent' ? 'bg-green-100 text-green-800' : ''}
                    `}>
                      {report.status}
                    </span>
                    
                    {/* Training indicator - only show if explicitly marked for training */}
                    {report.use_for_training && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                        🎓 Used for Training
                      </span>
                    )}
                    
                    {/* Source Badge for uploaded reports */}
                    {report.source === 'uploaded' && (
                      <span className="px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800">
                        📤 Uploaded
                      </span>
                    )}
                    
                  </div>

                  <div className="flex items-center text-sm text-sage-600 mb-3 flex-wrap gap-x-4">
                    <span className="flex items-center">
                      <Calendar className="w-4 h-4 mr-1" />
                      {report.session_date ? new Date(report.session_date).toLocaleDateString('en-US', {
                        weekday: 'short',
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      }) : new Date(report.uploaded_at).toLocaleDateString()}
                    </span>
                    
                    {report.subject && (
                      <span>
                        <strong>Subject:</strong> {report.subject}
                      </span>
                    )}
                    
                    {report.status && (
                      <span>
                        <strong>Status:</strong> {report.status}
                      </span>
                    )}
                  </div>

                  {(report.final_report || report.content) && (
                    <p className="text-sm text-sage-600 line-clamp-2">
                      {(report.final_report || report.content).substring(0, 200)}...
                    </p>
                  )}
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={(e) => handleToggleTraining(report.id, e)}
                    className={`p-2 rounded transition-colors ${
                      report.use_for_training 
                        ? 'text-blue-600 hover:text-blue-700 hover:bg-blue-50' 
                        : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'
                    }`}
                    title={report.use_for_training ? 'Remove from training' : 'Use for training'}
                  >
                    <GraduationCap className="w-5 h-5" />
                  </button>
                  <Link
                    to={`/reports/${report.id}/edit`}
                    className="p-2 text-sage-600 hover:text-sage-700 hover:bg-sage-100 rounded transition-colors"
                    title="Edit report"
                  >
                    <Edit2 className="w-5 h-5" />
                  </Link>
                  <button
                    onClick={() => handleDelete(report.id)}
                    className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded transition-colors"
                    title="Delete report"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Summary */}
      <div className="mt-6 text-sm text-sage-600">
        Showing {filteredAndSortedReports.length} of {allReports.length} reports
        ({allReports.filter(r => r.source === 'created').length} created, {allReports.filter(r => r.source === 'uploaded').length} uploaded)
      </div>
    </div>
  )
}

export default Reports

