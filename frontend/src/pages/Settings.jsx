import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Upload, Trash2, CheckCircle, XCircle, FileText, X, Users, TrendingUp } from 'lucide-react'
import { getReports, uploadSampleReport, checkAPIHealth, getStudents, getUserSettings, updateUserSettings, getDeletedSessions, updateCalendarSession, clearAllDeletedSessions, permanentlyDeleteSession, getStats } from '../services/api'

function Settings() {
  const [sampleReports, setSampleReports] = useState([])
  const [apiStatus, setApiStatus] = useState(null)
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [students, setStudents] = useState([])
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [uploadMetadata, setUploadMetadata] = useState({
    student_id: '',
    session_date: '',
    subject: '',
    duration_hours: '1',
    content: '',
    student_name_hint: ''
  })
  const [userSettings, setUserSettings] = useState({
    tutor_name: '',
    phone: '',
    email: '',
    default_include_contact: false
  })
  const [savingProfile, setSavingProfile] = useState(false)
  const [deletedSessions, setDeletedSessions] = useState([])

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [allReports, health, studentsList, settings, deleted, statsData] = await Promise.all([
        getReports(),
        checkAPIHealth(),
        getStudents(),
        getUserSettings(),
        getDeletedSessions(),
        getStats()
      ])
      // Filter to only uploaded reports for count display
      const uploadedReports = allReports.filter(r => r.source === 'uploaded')
      setSampleReports(uploadedReports)
      setApiStatus(health)
      setStudents(studentsList)
      setUserSettings(settings)
      setDeletedSessions(deleted)
      setStats(statsData)
    } catch (error) {
      console.error('Error loading settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files)
    if (files.length === 0) return

    const file = files[0] // For now, handle one file at a time
        const text = await file.text()
    
    // Open modal with file content pre-filled
    setUploadMetadata({
      ...uploadMetadata,
      content: text
    })
    setShowUploadModal(true)
      e.target.value = '' // Reset file input
  }

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this sample report?')) {
      try {
        await deleteSampleReport(id)
        loadData()
      } catch (error) {
        console.error('Error deleting sample:', error)
        alert('Error deleting sample report. Please try again.')
      }
    }
  }

  const handleSaveProfile = async () => {
    setSavingProfile(true)
    try {
      await updateUserSettings(userSettings)
      alert('Profile saved successfully!')
    } catch (error) {
      console.error('Error saving profile:', error)
      alert('Error saving profile. Please try again.')
    } finally {
      setSavingProfile(false)
    }
  }

  const handleOpenUploadModal = () => {
    setUploadMetadata({
      student_id: '',
      session_date: '',
      subject: '',
      duration_hours: '1',
      content: ''
    })
    setShowUploadModal(true)
  }

  const parseLearnSpeedFormat = (text) => {
    // Parse LearnSpeed format and extract key fields
    const lines = text.split('\n')
    const parsed = {
      duration: '1',
      date: '',
      studentName: '',
      subject: '',
      content: ''
    }

    let inClientNote = false
    let clientNoteLines = []
    
    // Fields that mark the end of Client Note content
    const endMarkers = ['Group Note:', 'Created Date:', 'Created by:', 'Posted Date:', 'Modified Date:']

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]
      
      // Check if we've reached Client Note
      if (line.startsWith('Client Note:')) {
        inClientNote = true
        // Get content after "Client Note:" on same line
        const contentOnSameLine = line.replace('Client Note:', '').trim()
        if (contentOnSameLine) {
          clientNoteLines.push(contentOnSameLine)
        }
        continue
      }
      
      // Check if we've hit an end marker (stop collecting content)
      if (inClientNote && endMarkers.some(marker => line.startsWith(marker))) {
        inClientNote = false
        break // Stop collecting content
      }
      
      // If in client note section, collect lines
      if (inClientNote) {
        clientNoteLines.push(line)
        continue
      }

      // Parse key-value pairs (before Client Note)
      if (line.includes(':')) {
        const colonIndex = line.indexOf(':')
        const key = line.substring(0, colonIndex).trim()
        const value = line.substring(colonIndex + 1).trim()
        
        if (key === 'Hours') {
          parsed.duration = value || '1'
        } else if (key === 'Session Date') {
          // Parse date like "08/27/25 5:00 pm PDT"
          try {
            const dateMatch = value.match(/(\d{2})\/(\d{2})\/(\d{2})/)
            if (dateMatch) {
              const [_, month, day, year] = dateMatch
              parsed.date = `20${year}-${month}-${day}`
            }
          } catch (e) {
            console.error('Error parsing date:', e)
          }
        } else if (key === 'Student') {
          // Parse "Mueller, Rose" or "Last, First" or "Rice, Tallula"
          const nameParts = value.split(',').map(s => s.trim())
          if (nameParts.length === 2) {
            parsed.studentName = `${nameParts[1]} ${nameParts[0]}` // "Rose Mueller" or "Tallula Rice"
          } else {
            parsed.studentName = value
          }
        } else if (key === 'Subject') {
          parsed.subject = value
        }
      }
    }

    // Join all client note lines and clean up
    parsed.content = clientNoteLines.join('\n').trim()

    return parsed
  }

  const handleSmartPaste = (pastedText) => {
    // Check if it looks like LearnSpeed format
    if (pastedText.includes('Client Note:') && pastedText.includes('Session Date:')) {
      const parsed = parseLearnSpeedFormat(pastedText)
      
      // Find student by name
      const matchedStudent = students.find(s => 
        s.name.toLowerCase() === parsed.studentName.toLowerCase()
      )

      setUploadMetadata({
        student_id: matchedStudent?.id || '',
        session_date: parsed.date,
        subject: parsed.subject,
        duration_hours: parsed.duration,
        content: parsed.content,
        student_name_hint: matchedStudent ? '' : parsed.studentName // For creating new student
      })
      
      return true // Parsed successfully
    }
    return false // Not LearnSpeed format
  }

  const handleMetadataUpload = async () => {
    if (!uploadMetadata.content.trim()) {
      alert('Please enter report content')
      return
    }

    setUploading(true)
    try {
      // Find student name from student_id
      const student = students.find(s => s.id === parseInt(uploadMetadata.student_id))
      const studentName = student ? student.name : ''
      
      // Create filename
      const dateStr = uploadMetadata.session_date 
        ? new Date(uploadMetadata.session_date).toLocaleDateString().replace(/\//g, '-')
        : 'no-date'
      const filename = studentName 
        ? `${studentName} - ${dateStr}${uploadMetadata.subject ? ' - ' + uploadMetadata.subject : ''}.txt`
        : 'Manual Entry.txt'

      // Upload with metadata
      await uploadSampleReport(filename, uploadMetadata.content, {
        student_name: studentName,
        session_date: uploadMetadata.session_date,
        subject: uploadMetadata.subject,
        duration_hours: uploadMetadata.duration_hours,
        source: 'manual'
      })

      loadData()
      setShowUploadModal(false)
      alert('Sample report added successfully!')
    } catch (error) {
      console.error('Error uploading report:', error)
      alert('Error adding sample report. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading settings...</div>
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold text-sage-800 mb-6">Settings</h2>

      {/* AI Status */}
      <div className="bg-white rounded-lg shadow-sm border border-sage-200 p-6 mb-6">
        <h3 className="text-lg font-semibold text-sage-800 mb-4">AI Connection Status</h3>
        
        <div className="flex items-center justify-between p-4 bg-sage-50 rounded-lg border border-sage-200">
          <div className="flex items-center">
            {apiStatus?.ai_connected ? (
              <CheckCircle className="w-6 h-6 text-green-600 mr-3" />
            ) : (
              <XCircle className="w-6 h-6 text-red-600 mr-3" />
            )}
            <div>
              <p className="font-medium text-sage-900">
                {apiStatus?.ai_connected ? 'AI Connected' : 'AI Not Connected'}
              </p>
              <p className="text-sm text-sage-600">
                {apiStatus?.ai_message || 'Check your API key configuration'}
              </p>
            </div>
          </div>
          <div className="text-sm text-sage-600">
            Provider: <span className="font-medium">{apiStatus?.provider || 'Unknown'}</span>
          </div>
        </div>

        {!apiStatus?.ai_connected && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm font-medium text-yellow-900 mb-2">Setup Required</p>
            <ol className="text-sm text-yellow-800 space-y-1 list-decimal list-inside">
              <li>Copy the <code className="bg-yellow-100 px-1 rounded">.env.example</code> file to <code className="bg-yellow-100 px-1 rounded">.env</code></li>
              <li>Add your OpenAI or Anthropic API key to the <code className="bg-yellow-100 px-1 rounded">.env</code> file</li>
              <li>Restart the backend server</li>
            </ol>
          </div>
        )}
      </div>

      {/* My Profile */}
      <div className="bg-white rounded-lg shadow-sm border border-sage-200 p-6 mb-6">
        <h3 className="text-lg font-semibold text-sage-800 mb-4">👤 My Profile</h3>
        
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-sage-700 mb-1">
                Your Name
              </label>
              <input
                type="text"
                value={userSettings.tutor_name}
                onChange={(e) => setUserSettings({ ...userSettings, tutor_name: e.target.value })}
                className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
                placeholder="e.g., Elizabeth"
              />
              <p className="text-xs text-sage-500 mt-1">Reports will end with "Best, [Your Name]"</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-1">
                Phone Number
              </label>
              <input
                type="tel"
                value={userSettings.phone || ''}
                onChange={(e) => setUserSettings({ ...userSettings, phone: e.target.value })}
                className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
                placeholder="e.g., (415) 747-4657"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-sage-700 mb-1">
              Email Address
            </label>
            <input
              type="email"
              value={userSettings.email || ''}
              onChange={(e) => setUserSettings({ ...userSettings, email: e.target.value })}
              className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
              placeholder="e.g., elizabeth@sageeducators.com"
            />
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-sage-200">
            <div className="text-sm text-sage-600">
              <p className="mb-1">📧 When creating reports, you can optionally include contact info in the signature.</p>
              <p className="text-xs text-sage-500">Phone and email will only appear if you check the box when generating.</p>
            </div>
            <button
              onClick={handleSaveProfile}
              disabled={savingProfile}
              className="px-6 py-2 bg-sage-600 text-white rounded-lg hover:bg-sage-700 transition-colors disabled:opacity-50"
            >
              {savingProfile ? 'Saving...' : 'Save Profile'}
            </button>
          </div>
        </div>
      </div>

      {/* Upload Historical Reports */}
      <div className="bg-white rounded-lg shadow-sm border border-sage-200 p-6">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-sage-800 flex items-center">
            📤 Upload Historical Reports
          </h3>
          <p className="text-sm text-sage-600 mt-2">
            Upload past session reports to train the AI and show complete calendar history.
          </p>
        </div>

        {/* Upload Buttons */}
        <div className="flex space-x-3 mb-6">
          <label className="flex-1 cursor-pointer">
            <div className="flex items-center justify-center px-4 py-3 bg-sage-600 text-white rounded-lg hover:bg-sage-700 transition-colors">
              <Upload className="w-5 h-5 mr-2" />
              {uploading ? 'Uploading...' : 'Upload File'}
            </div>
            <input
              type="file"
              accept=".txt,.doc,.docx"
              onChange={handleFileUpload}
              className="hidden"
              disabled={uploading}
            />
          </label>
          
          <button
            onClick={handleOpenUploadModal}
            className="flex-1 flex items-center justify-center px-4 py-3 bg-sage-100 text-sage-700 rounded-lg hover:bg-sage-200 transition-colors"
          >
            <FileText className="w-5 h-5 mr-2" />
            Add with Details
          </button>
        </div>

        {/* Upload Status */}
        <div className="bg-gradient-to-br from-green-50 to-blue-50 border border-green-200 rounded-lg p-6 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-full border-2 border-green-400 mb-3">
            <span className="text-2xl font-bold text-green-700">{sampleReports.length}</span>
          </div>
          <p className="text-lg font-semibold text-sage-900 mb-1">
            ✅ {sampleReports.length} Historical Report{sampleReports.length !== 1 ? 's' : ''} Uploaded
          </p>
          <p className="text-sm text-sage-600 mb-4">
            {sampleReports.length === 0 
              ? 'Upload past reports to train the AI and populate your calendar history'
              : 'These reports are training the AI and visible in your timeline'}
          </p>
          <Link
            to="/reports"
            className="inline-flex items-center text-sm text-sage-700 hover:text-sage-900 font-medium"
          >
            View full timeline in Reports page →
          </Link>
        </div>
      </div>

      {/* Deleted Sessions */}
      <div className="mt-6 bg-white rounded-lg shadow-sm border border-sage-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-sage-800">🗑️ Deleted Sessions</h3>
            <p className="text-sm text-sage-600 mt-1">
              Sessions you've removed from your calendar. You can restore them if needed.
            </p>
          </div>
          {deletedSessions.length > 0 && (
            <button
              onClick={async () => {
                if (!window.confirm(`Are you sure you want to permanently delete all ${deletedSessions.length} deleted sessions? This cannot be undone.`)) {
                  return
                }
                try {
                  await clearAllDeletedSessions()
                  loadData()
                } catch (error) {
                  console.error('Error clearing deleted sessions:', error)
                  alert('Error clearing deleted sessions')
                }
              }}
              className="px-4 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
            >
              <Trash2 className="w-4 h-4" />
              Clear All
            </button>
          )}
        </div>
        
        {deletedSessions.length === 0 ? (
          <div className="text-center py-8 border-2 border-dashed border-sage-300 rounded-lg">
            <p className="text-sage-600">No deleted sessions</p>
            <p className="text-xs text-sage-500 mt-1">
              Deleted sessions will appear here and can be restored
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {deletedSessions.map((session) => (
              <div
                key={session.id}
                className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg"
              >
                <div className="flex-1">
                  <p className="font-medium text-sage-900">{session.student_name}</p>
                  <p className="text-sm text-sage-600">
                    {new Date(session.session_date).toLocaleDateString('en-US', {
                      weekday: 'short',
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric'
                    })} at {new Date(session.session_date).toLocaleTimeString('en-US', {
                      hour: 'numeric',
                      minute: '2-digit',
                      hour12: true
                    })}
                    {session.duration_hours && session.duration_hours !== '1' && ` (${session.duration_hours}h)`}
                  </p>
                  {session.notes && (
                    <p className="text-xs text-sage-500 mt-1">{session.notes}</p>
                  )}
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={async () => {
                      try {
                        await updateCalendarSession(session.id, { status: 'scheduled' })
                        loadData()
                      } catch (error) {
                        console.error('Error restoring session:', error)
                        alert('Error restoring session')
                      }
                    }}
                    className="px-4 py-2 bg-sage-600 text-white text-sm rounded-lg hover:bg-sage-700 transition-colors"
                  >
                    Restore
                  </button>
                  <button
                    onClick={async () => {
                      if (!window.confirm('Permanently delete this session? This cannot be undone.')) {
                        return
                      }
                      try {
                        await permanentlyDeleteSession(session.id)
                        loadData()
                      } catch (error) {
                        console.error('Error deleting session:', error)
                        alert('Error deleting session')
                      }
                    }}
                    className="px-3 py-2 bg-red-100 text-red-700 text-sm rounded-lg hover:bg-red-200 transition-colors"
                    title="Delete permanently"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* System Stats */}
      <div className="mt-6 bg-white rounded-lg shadow-sm border border-sage-200 p-6">
        <h3 className="text-lg font-semibold text-sage-800 mb-4">📊 System Statistics</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-blue-900 mb-1">Active Students</p>
                <p className="text-2xl font-bold text-blue-700">{stats?.total_students || 0}</p>
              </div>
              <Users className="w-8 h-8 text-blue-600 opacity-50" />
            </div>
          </div>

          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-green-900 mb-1">Total Reports</p>
                <p className="text-2xl font-bold text-green-700">{stats?.total_reports || 0}</p>
              </div>
              <FileText className="w-8 h-8 text-green-600 opacity-50" />
            </div>
          </div>

          <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-yellow-900 mb-1">Draft Reports</p>
                <p className="text-2xl font-bold text-yellow-700">{stats?.draft_reports || 0}</p>
              </div>
              <FileText className="w-8 h-8 text-yellow-600 opacity-50" />
            </div>
          </div>

          <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-purple-900 mb-1">Training Samples</p>
                <p className="text-2xl font-bold text-purple-700">{stats?.total_samples || 0}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-purple-600 opacity-50" />
            </div>
          </div>
        </div>
      </div>

      {/* About */}
      <div className="mt-6 bg-white rounded-lg shadow-sm border border-sage-200 p-6">
        <h3 className="text-lg font-semibold text-sage-800 mb-3">About Sage Reports</h3>
        <p className="text-sm text-sage-600 mb-2">
          Version 1.0.0
        </p>
        <p className="text-sm text-sage-600">
          An AI-powered tutoring report assistant to help you write professional, 
          personalized session reports for parents.
        </p>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-sage-200">
              <h3 className="text-xl font-bold text-sage-800">Upload Historical Report</h3>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-sage-400 hover:text-sage-600 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-4">
              {/* Smart Paste Info */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p className="text-xs font-medium text-blue-900 mb-1">💡 Smart Paste Detected!</p>
                <p className="text-xs text-blue-800">
                  Paste your LearnSpeed report export and the system will automatically extract the student, date, subject, and report content for you!
                </p>
              </div>

              {/* Student Selection */}
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">
                  Student <span className="text-sage-500 font-normal">(optional but recommended)</span>
                </label>
                <select
                  value={uploadMetadata.student_id}
                  onChange={(e) => setUploadMetadata({ ...uploadMetadata, student_id: e.target.value })}
                  className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sage-500"
                >
                  <option value="">Select a student...</option>
                  {students.map(student => (
                    <option key={student.id} value={student.id}>
                      {student.name}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-sage-500 mt-1">
                  Linking to a student allows the AI to reference this report when generating future reports for them
                </p>
              </div>

              {/* Session Date */}
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">
                  Session Date <span className="text-sage-500 font-normal">(optional)</span>
                </label>
                <input
                  type="date"
                  value={uploadMetadata.session_date}
                  onChange={(e) => setUploadMetadata({ ...uploadMetadata, session_date: e.target.value })}
                  className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sage-500"
                />
              </div>

              {/* Subject */}
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">
                  Subject <span className="text-sage-500 font-normal">(optional)</span>
                </label>
                <input
                  type="text"
                  value={uploadMetadata.subject}
                  onChange={(e) => setUploadMetadata({ ...uploadMetadata, subject: e.target.value })}
                  placeholder="e.g., Geometry, SAT Math, Multi. Subject"
                  className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sage-500"
                />
              </div>

              {/* Duration */}
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">
                  Session Duration (hours) <span className="text-sage-500 font-normal">(optional)</span>
                </label>
                <input
                  type="text"
                  value={uploadMetadata.duration_hours}
                  onChange={(e) => setUploadMetadata({ ...uploadMetadata, duration_hours: e.target.value })}
                  placeholder="e.g., 1, 0.5, 1.5"
                  className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sage-500"
                />
              </div>

              {/* Report Content */}
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">
                  Report Content <span className="text-red-600">*</span>
                </label>
                <textarea
                  value={uploadMetadata.content}
                  onChange={(e) => setUploadMetadata({ ...uploadMetadata, content: e.target.value })}
                  onPaste={(e) => {
                    const pastedText = e.clipboardData.getData('text')
                    if (handleSmartPaste(pastedText)) {
                      e.preventDefault() // Prevent default paste since we're handling it
                    }
                  }}
                  placeholder="Paste your report here - LearnSpeed format will be auto-detected!"
                  rows={10}
                  className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sage-500 font-mono text-sm"
                />
                <p className="text-xs text-sage-500 mt-1">
                  {uploadMetadata.content.length} characters
                  {uploadMetadata.student_name_hint && (
                    <span className="ml-2 text-blue-600">
                      • ✨ Auto-detected: {uploadMetadata.student_name_hint}
                    </span>
                  )}
                </p>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-end gap-3 p-6 border-t border-sage-200 bg-sage-50">
              <button
                onClick={() => setShowUploadModal(false)}
                className="px-4 py-2 text-sage-700 hover:bg-sage-100 rounded-lg transition-colors"
                disabled={uploading}
              >
                Cancel
              </button>
              <button
                onClick={handleMetadataUpload}
                disabled={uploading || !uploadMetadata.content.trim()}
                className="px-6 py-2 bg-sage-600 text-white rounded-lg hover:bg-sage-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {uploading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    Add Sample Report
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Settings

