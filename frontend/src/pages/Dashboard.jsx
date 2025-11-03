import { useState, useEffect, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Plus, Users, FileText, BookOpen, TrendingUp, Calendar, Clock, Edit } from 'lucide-react'
import { getStats, getTodaySessions, updateCalendarSession, getSessionReminders, createCalendarSession, getStudents, getCalendarSessions, createStudent } from '../services/api'

function Dashboard() {
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [todaySessions, setTodaySessions] = useState(null)
  const [sessionNotes, setSessionNotes] = useState({}) // session_id -> notes text
  const [sessionReminders, setSessionReminders] = useState({}) // session_id -> reminders
  const [loading, setLoading] = useState(true)
  const [savingNotes, setSavingNotes] = useState({}) // session_id -> boolean
  const [showImpromptu, setShowImpromptu] = useState(false)
  const [students, setStudents] = useState([])
  const [weekSubjects, setWeekSubjects] = useState([])
  const [impromptuStudent, setImpromptuStudent] = useState('')
  const [impromptuTime, setImpromptuTime] = useState('12:00')
  const [newStudentName, setNewStudentName] = useState('')
  const [newStudentSubject, setNewStudentSubject] = useState('')

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [statsData, sessionsData, studentsList] = await Promise.all([
        getStats(),
        getTodaySessions(),
        getStudents(true) // Active students only
      ])
      setStats(statsData)
      setTodaySessions(sessionsData)
      setStudents(studentsList)
      
      // Initialize notes from sessions
      const notesObj = {}
      if (sessionsData && sessionsData.sessions) {
        for (const session of sessionsData.sessions) {
          notesObj[session.session_id] = session.notes || ''
          // Load reminders for each student
          if (session.student_id) {
            loadReminders(session.student_id, session.session_id)
          }
        }
      }
      setSessionNotes(notesObj)
      
      // Load week subjects
      loadWeekSubjects(studentsList)
    } catch (error) {
      console.error('Error loading dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadWeekSubjects = async (studentsList) => {
    try {
      // Get dates for the current week (Sunday to Saturday)
      const today = new Date()
      const currentDay = today.getDay()
      const sunday = new Date(today)
      sunday.setDate(today.getDate() - currentDay)
      sunday.setHours(0, 0, 0, 0)
      
      const saturday = new Date(sunday)
      saturday.setDate(sunday.getDate() + 6)
      saturday.setHours(23, 59, 59, 999)
      
      // Fetch calendar sessions for this week
      const calendarSessions = await getCalendarSessions(sunday.toISOString(), saturday.toISOString())
      
      // Build week structure
      const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
      const weekData = []
      
      for (let i = 0; i < 7; i++) {
        const date = new Date(sunday)
        date.setDate(sunday.getDate() + i)
        const dateStr = date.toISOString().split('T')[0]
        
        const daySubjectsMap = new Map() // Use Map to track normalized -> display name
        
        // Check recurring sessions for this day
        studentsList.forEach(student => {
          if (student.recurring_schedule && student.subject) {
            const schedule = student.recurring_schedule.toLowerCase()
            const dayName = dayNames[i].toLowerCase()
            
            if (schedule.includes(dayName.substring(0, 3)) || schedule.includes(dayName)) {
              // Check if this session is cancelled or deleted
              const override = calendarSessions.find(cs =>
                cs.student_id === student.id &&
                cs.session_date?.startsWith(dateStr) &&
                cs.is_one_time === false
              )
              
              // Only add if not cancelled/deleted
              if (!override || (override.status !== 'cancelled' && override.status !== 'deleted')) {
                const normalized = student.subject.trim().toLowerCase()
                if (!daySubjectsMap.has(normalized)) {
                  daySubjectsMap.set(normalized, student.subject.trim())
                }
              }
            }
          }
        })
        
        // Add one-time sessions for this day (exclude cancelled/deleted)
        calendarSessions.forEach(cs => {
          if (cs.is_one_time && cs.session_date?.startsWith(dateStr)) {
            if (cs.status !== 'cancelled' && cs.status !== 'deleted') {
              const student = studentsList.find(s => s.id === cs.student_id)
              if (student && student.subject) {
                const normalized = student.subject.trim().toLowerCase()
                if (!daySubjectsMap.has(normalized)) {
                  daySubjectsMap.set(normalized, student.subject.trim())
                }
              }
            }
          }
        })
        
        if (daySubjectsMap.size > 0) {
          weekData.push({
            dayName: dayNames[i],
            date: date,
            subjects: Array.from(daySubjectsMap.values()).sort()
          })
        }
      }
      
      setWeekSubjects(weekData)
    } catch (error) {
      console.error('Error loading week subjects:', error)
    }
  }

  const loadReminders = async (studentId, sessionId) => {
    try {
      const data = await getSessionReminders(studentId)
      if (data.has_reminders) {
        setSessionReminders(prev => ({
          ...prev,
          [sessionId]: data.ai_extracted || []
        }))
      }
    } catch (error) {
      console.error('Error loading reminders:', error)
    }
  }

  // Auto-save notes with debounce
  const saveNotes = useCallback(async (sessionId, notes) => {
    setSavingNotes(prev => ({ ...prev, [sessionId]: true }))
    try {
      await updateCalendarSession(sessionId, { notes })
    } catch (error) {
      console.error('Error saving notes:', error)
    } finally {
      setSavingNotes(prev => ({ ...prev, [sessionId]: false }))
    }
  }, [])

  // Debounced save (wait 1 second after typing stops)
  useEffect(() => {
    const timeouts = {}
    Object.keys(sessionNotes).forEach(sessionId => {
      if (timeouts[sessionId]) clearTimeout(timeouts[sessionId])
      timeouts[sessionId] = setTimeout(() => {
        const session = todaySessions?.sessions?.find(s => s.session_id === parseInt(sessionId))
        if (session && sessionNotes[sessionId] !== session.notes) {
          saveNotes(parseInt(sessionId), sessionNotes[sessionId])
        }
      }, 1000)
    })
    return () => Object.values(timeouts).forEach(clearTimeout)
  }, [sessionNotes, todaySessions, saveNotes])

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  return (
    <div className="relative">
      {/* This Week's Subjects - Sticky Note Style */}
      {weekSubjects.length > 0 && (
        <div className="absolute top-0 right-0 w-80 bg-gray-50 rounded-lg shadow-sm border border-gray-300 p-3 max-h-48 overflow-y-auto">
          <h3 className="text-xs font-semibold text-gray-700 mb-2 sticky top-0 bg-gray-50 pb-1">
            This Week's Subjects
          </h3>
          <div className="grid grid-cols-2 gap-2">
            {weekSubjects.map((day, idx) => {
              const isToday = new Date().toDateString() === day.date.toDateString()
              const isPast = day.date < new Date(new Date().setHours(0, 0, 0, 0))
              
              // Skip past days to keep it compact
              if (isPast) return null
              
              return (
                <div key={idx} className="text-xs">
                  <p className={`font-semibold ${isToday ? 'text-sage-900' : 'text-gray-700'}`}>
                    {isToday ? '→ ' : ''}{day.dayName.substring(0, 3)}
                  </p>
                  <div className="space-y-0.5 text-gray-600">
                    {day.subjects.map((subject, subIdx) => (
                      <p key={subIdx}>• {subject}</p>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Welcome Section */}
      <div className="mb-10 animate-fade-in">
        <h2 className="text-4xl font-bold text-sage-900 mb-3 tracking-tight">
          Welcome to Sage Reports
        </h2>
        <p className="text-lg text-sage-600">
          Your AI-powered tutoring report assistant
        </p>
      </div>

      {/* Quick Actions */}
      <div className="mb-10 flex gap-4">
        <Link
          to="/reports/new"
          className="inline-flex items-center px-8 py-3.5 bg-sage-600 text-white font-semibold rounded-xl hover:bg-sage-700 transition-smooth hover-lift shadow-md hover:shadow-lg"
        >
          <Plus className="w-5 h-5 mr-2.5" />
          Write New Report
        </Link>
        <Link
          to="/calendar"
          className="inline-flex items-center px-8 py-3.5 bg-white border-2 border-sage-600 text-sage-700 font-semibold rounded-xl hover:bg-sage-50 transition-smooth hover-lift shadow-sm"
        >
          <Calendar className="w-5 h-5 mr-2.5" />
          View Calendar
        </Link>
      </div>

      {/* Today's Sessions */}
      <div className="mb-8">
        <div className="px-2 py-3 mb-4">
            <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold text-sage-800 flex items-center">
                <Clock className="w-5 h-5 mr-2" />
                Today's Sessions
              </h3>
              <span className="text-sm text-sage-500">
              {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
              </span>
            </div>
          </div>

        {todaySessions && todaySessions.total_sessions > 0 ? (
          <div className="space-y-4">
            {todaySessions.sessions.map((session, index) => {
              // Cycle through soft pastel colors for visual separation
              const colors = [
                'border-blue-100 bg-blue-50/40',
                'border-green-100 bg-green-50/40',
                'border-purple-100 bg-purple-50/40',
                'border-rose-100 bg-rose-50/40',
                'border-amber-100 bg-amber-50/40',
                'border-cyan-100 bg-cyan-50/40'
              ]
              const colorClass = colors[index % colors.length]
              
              return (
                <div
                  key={session.session_id}
                  className={`border-2 rounded-xl shadow-md hover:shadow-lg transition-smooth p-5 animate-slide-up ${colorClass}`}
                >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-semibold text-sage-900">{session.student_name}</h4>
                    <p className="text-sm text-sage-600">{session.subject} • {session.schedule}</p>
                  </div>
                  <Link
                    to="/reports/new"
                    state={{ studentId: session.student_id, sessionDate: todaySessions.date }}
                    className="px-5 py-2.5 bg-sage-600 text-white text-sm font-semibold rounded-lg hover:bg-sage-700 transition-smooth hover-lift shadow-md hover:shadow-lg flex items-center"
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Write Report
                  </Link>
                </div>

                {/* Reminders */}
                {(session.next_session_notes || (sessionReminders[session.session_id] && sessionReminders[session.session_id].length > 0)) && (
                  <div className="mb-3 space-y-2">
                    {/* Manual Notes from Last Report */}
                    {session.next_session_notes && (
                      <div className="p-3.5 bg-amber-50 border-l-4 border-amber-400 rounded-lg shadow-sm">
                        <p className="text-xs font-semibold text-amber-900 mb-2">📝 Notes from last session:</p>
                        <p className="text-xs text-amber-800 whitespace-pre-wrap leading-relaxed">{session.next_session_notes}</p>
                      </div>
                    )}
                    
                    {/* AI Extracted Reminders */}
                    {sessionReminders[session.session_id] && sessionReminders[session.session_id].length > 0 && (
                      <div className="p-3.5 bg-blue-50 border-l-4 border-blue-400 rounded-lg shadow-sm">
                        <p className="text-xs font-semibold text-blue-900 mb-2">⏰ AI reminders:</p>
                        <ul className="text-xs text-blue-800 space-y-1">
                          {sessionReminders[session.session_id].map((item, idx) => {
                            const reminderText = typeof item === 'string' ? item : item.reminder
                            const sourceText = typeof item === 'object' && item.source ? item.source : null
                            
                            return (
                              <li key={idx} className="relative group">
                                <span className="cursor-help">• {reminderText}</span>
                                {sourceText && (
                                  <div className="hidden group-hover:block absolute z-10 left-0 top-full mt-1 p-3 bg-gray-800 text-white text-xs rounded-lg shadow-lg max-w-md">
                                    <p className="font-semibold mb-1">From previous report:</p>
                                    <p className="italic">"{sourceText}"</p>
        </div>
                                )}
                              </li>
                            )
                          })}
                        </ul>
            </div>
                    )}
                  </div>
                )}

                {/* Quick Notes Box */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium text-sage-700">
                      Quick Notes {savingNotes[session.session_id] && <span className="text-xs text-sage-500 ml-2">(saving...)</span>}
                    </label>
                  </div>
                  <textarea
                    value={sessionNotes[session.session_id] || ''}
                    onChange={(e) => {
                      let newValue = e.target.value
                      // Auto-convert "- " to "• "
                      if (newValue.endsWith('- ')) {
                        newValue = newValue.slice(0, -2) + '• '
                      }
                      setSessionNotes(prev => ({ ...prev, [session.session_id]: newValue }))
                    }}
                    onFocus={(e) => {
                      // Auto-start with bullet if empty
                      if (!sessionNotes[session.session_id]) {
                        setSessionNotes(prev => ({ ...prev, [session.session_id]: '• ' }))
                      }
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        const textarea = e.target
                        const cursorPos = textarea.selectionStart
                        const currentNotes = sessionNotes[session.session_id] || ''
                        const textBefore = currentNotes.substring(0, cursorPos)
                        const textAfter = currentNotes.substring(cursorPos)
                        const newText = textBefore + '\n• ' + textAfter
                        setSessionNotes(prev => ({ ...prev, [session.session_id]: newText }))
                        setTimeout(() => {
                          textarea.selectionStart = textarea.selectionEnd = cursorPos + 3
                        }, 0)
                      }
                    }}
                    rows={4}
                    className="w-full px-4 py-3 border-2 border-sage-300 rounded-xl focus:ring-2 focus:ring-sage-500 focus:border-sage-500 text-sm transition-smooth shadow-sm focus:shadow-md"
                    placeholder="• Type notes here - auto-saves as you type&#10;• Press Enter for new bullet"
                  />
                  <p className="text-xs text-sage-500 mt-1">
                    💾 Auto-saves as you type
                  </p>
                </div>
              </div>
            )})}
          </div>
        ) : (
          <div className="bg-white border-2 border-dashed border-sage-300 rounded-lg p-8 text-center">
            <Clock className="w-12 h-12 mx-auto mb-3 text-sage-400" />
            <p className="text-sage-600 mb-2">No sessions scheduled for today</p>
            <p className="text-sm text-sage-500">Add an impromptu session below or check your calendar</p>
          </div>
        )}

        {/* Add Impromptu Session */}
        {!showImpromptu ? (
          <div className="mt-6">
            <button
              onClick={() => {
                // Set default time to current time when opening form
                const now = new Date()
                const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
                setImpromptuTime(currentTime)
                setShowImpromptu(true)
              }}
              className="w-full px-5 py-4 border-2 border-dashed border-sage-400 text-sage-700 font-medium rounded-xl hover:border-sage-500 hover:bg-sage-50 transition-smooth flex items-center justify-center group"
            >
              <Plus className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" />
              Add Impromptu Session
            </button>
          </div>
        ) : (
          <div className="mt-6 bg-white border-2 border-sage-500 rounded-xl shadow-lg p-5 animate-scale-in">
            <p className="text-sm font-medium text-sage-800 mb-3">Quick Add Impromptu Session</p>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <select
                  value={impromptuStudent}
                  onChange={(e) => setImpromptuStudent(e.target.value)}
                  className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500"
                >
                  <option value="">Select student...</option>
                  {students.map(student => (
                    <option key={student.id} value={student.id}>
                      {student.name} - {student.subject}
                    </option>
                  ))}
                  <option value="new">+ New Student</option>
                </select>

                <input
                  type="time"
                  value={impromptuTime}
                  onChange={(e) => setImpromptuTime(e.target.value)}
                  className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500"
                />
              </div>

              {impromptuStudent === 'new' && (
                <div className="space-y-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <input
                    type="text"
                    value={newStudentName}
                    onChange={(e) => setNewStudentName(e.target.value)}
                    placeholder="Student Name *"
                    className="w-full px-3 py-2 border border-sage-300 rounded-lg text-sm"
                  />
                  <input
                    type="text"
                    value={newStudentSubject}
                    onChange={(e) => setNewStudentSubject(e.target.value)}
                    placeholder="Subject (optional)"
                    className="w-full px-3 py-2 border border-sage-300 rounded-lg text-sm"
                  />
                </div>
              )}

              <div className="flex gap-2">
                <button
                  onClick={async () => {
                    let studentId = impromptuStudent
                    
                    if (!studentId) {
                      alert('Please select a student')
                      return
                    }

                    try {
                      // Create new student if needed
                      if (studentId === 'new') {
                        if (!newStudentName.trim()) {
                          alert('Please enter student name')
                          return
                        }
                        try {
                          const newStudent = await createStudent({
                            name: newStudentName,
                            subject: newStudentSubject,
                            active: true
                          })
                          studentId = newStudent.id
                        } catch (createError) {
                          // Check if it's a duplicate error
                          if (createError.response?.status === 409 || createError.response?.data?.error === 'duplicate') {
                            const existing = createError.response?.data?.existing_student
                            if (existing) {
                              alert(`⚠️ A student named "${newStudentName}" already exists!\n\nSchedule: ${existing.recurring_schedule || 'Not set'}\nSubject: ${existing.subject || 'Not set'}\n\nPlease select them from the dropdown instead.`)
                            } else {
                              alert(`⚠️ A student named "${newStudentName}" already exists. Please select them from the dropdown.`)
                            }
                          } else {
                            alert('Error creating student. Please try again.')
                          }
                          return
                        }
                      }

                      // Create session date with selected time
                      const today = new Date().toISOString().split('T')[0]
                      const sessionDateTime = `${today}T${impromptuTime}:00`

                      await createCalendarSession({
                        student_id: parseInt(studentId),
                        session_date: sessionDateTime,
                        is_one_time: true,
                        status: 'scheduled'
                      })
                      setShowImpromptu(false)
                      setImpromptuStudent('')
                      setImpromptuTime('12:00')
                      setNewStudentName('')
                      setNewStudentSubject('')
                      loadDashboardData()
                    } catch (error) {
                      console.error('Error creating session:', error)
                      alert('Error creating session')
                    }
                  }}
                  className="flex-1 px-5 py-2.5 bg-sage-600 text-white text-sm font-semibold rounded-lg hover:bg-sage-700 transition-smooth hover-lift shadow-md"
                >
                  Add Session
                </button>
                <button
                  onClick={() => {
                    setShowImpromptu(false)
                    setImpromptuStudent('')
                    setImpromptuTime('12:00')
                    setNewStudentName('')
                    setNewStudentSubject('')
                  }}
                  className="px-5 py-2.5 bg-sage-100 text-sage-700 text-sm font-medium rounded-lg hover:bg-sage-200 transition-smooth"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Getting Started Guide */}
      {stats?.total_samples === 0 && (
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            👋 Getting Started
          </h3>
          <p className="text-blue-800 mb-4">
            Upload your past session reports in Settings to train the AI on your writing style. 
            The more samples you upload (10-20+ recommended), the more accurate the AI will be!
          </p>
          <Link
            to="/settings"
            className="inline-flex items-center text-blue-700 hover:text-blue-800 font-medium"
          >
            Go to Settings →
          </Link>
        </div>
      )}
      
      {stats?.total_samples > 0 && stats?.total_samples < 10 && (
        <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-yellow-900 mb-2">
            📈 Improve AI Accuracy
          </h3>
          <p className="text-yellow-800 mb-4">
            You have {stats.total_samples} sample report{stats.total_samples !== 1 ? 's' : ''} uploaded. 
            Upload 10-20+ samples for the best results!
          </p>
          <Link
            to="/settings"
            className="inline-flex items-center text-yellow-700 hover:text-yellow-800 font-medium"
          >
            Upload More Samples →
          </Link>
        </div>
      )}
    </div>
  )
}

export default Dashboard
