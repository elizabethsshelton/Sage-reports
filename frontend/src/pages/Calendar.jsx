import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Calendar as CalendarIcon, Plus, FileText, ChevronLeft, ChevronRight, Clock, X, Edit, Trash2, MoreVertical } from 'lucide-react'
import { getStudents, getReports, getCalendarSessions, createCalendarSession, updateCalendarSession, deleteCalendarSession, createStudent } from '../services/api'

function Calendar() {
  const navigate = useNavigate()
  const [students, setStudents] = useState([])
  const [reports, setReports] = useState([])
  const [calendarSessions, setCalendarSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [currentWeek, setCurrentWeek] = useState(0) // 0 = this week, 1 = next week, -1 = last week
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedSession, setSelectedSession] = useState(null)
  const [menuOpen, setMenuOpen] = useState(null) // Track which session menu is open
  const [showNewStudentFields, setShowNewStudentFields] = useState(false)

  useEffect(() => {
    loadData()
  }, [currentWeek])

  const loadData = async () => {
    try {
      const weekDates = getWeekDates()
      const startDate = weekDates[0].toISOString()
      const endDate = weekDates[6].toISOString()
      
      const [activeStudentsData, allStudentsData, reportsData, sessionsData] = await Promise.all([
        getStudents(true),  // Active students for recurring schedule
        getStudents(false), // All students for report matching
        getReports(),
        getCalendarSessions(startDate, endDate)
      ])
      setStudents(activeStudentsData)  // For recurring schedules
      setReports(reportsData)
      setCalendarSessions(sessionsData)
      
      // Store all students for report lookups
      window.allStudents = allStudentsData
    } catch (error) {
      console.error('Error loading calendar data:', error)
    } finally {
      setLoading(false)
    }
  }
  
  // Get dates for current week (moved up to be available in loadData)
  const getWeekDates = () => {
    const today = new Date()
    const currentDay = today.getDay()
    const diff = today.getDate() - currentDay + (currentWeek * 7)
    
    const sunday = new Date(today.setDate(diff))
    sunday.setHours(0, 0, 0, 0)
    
    return Array.from({ length: 7 }, (_, i) => {
      const date = new Date(sunday)
      date.setDate(sunday.getDate() + i)
      return date
    })
  }

  // Parse student schedules
  const parseSchedule = (schedule) => {
    if (!schedule) return []
    
    const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    const sessions = []
    
    // Parse formats like "Mondays 4pm, Thursdays 6pm" or "Mon/Wed 3pm"
    const parts = schedule.toLowerCase().split(',').map(s => s.trim())
    
    parts.forEach(part => {
      days.forEach((day, index) => {
        if (part.includes(day) || part.includes(day.substring(0, 3))) {
          // Extract time
          const timeMatch = part.match(/(\d{1,2})(?::(\d{2}))?\s*(am|pm)?/)
          if (timeMatch) {
            let hour = parseInt(timeMatch[1])
            const minute = timeMatch[2] || '00'
            const period = timeMatch[3] || (hour >= 8 && hour <= 11 ? 'am' : 'pm')
            
            if (period === 'pm' && hour < 12) hour += 12
            if (period === 'am' && hour === 12) hour = 0
            
            sessions.push({
              dayOfWeek: index,
              time: `${hour.toString().padStart(2, '0')}:${minute}`,
              displayTime: `${timeMatch[1]}:${minute} ${period.toUpperCase()}`
            })
          }
        }
      })
    })
    
    return sessions
  }

  const weekDates = getWeekDates()
  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  
  // Build calendar data - merge recurring schedule + calendar sessions
  const calendarData = weekDates.map((date, dayIndex) => {
    const sessionsForDay = []
    const dateStr = date.toISOString().split('T')[0]
    
    // Add recurring sessions from student schedules
    students.forEach(student => {
      const schedule = parseSchedule(student.recurring_schedule)
      schedule.forEach(session => {
        if (session.dayOfWeek === dayIndex) {
          // Check if there's a calendar override for this specific recurring session
          const override = calendarSessions.find(cs => 
            cs.student_id === student.id &&
            cs.session_date?.startsWith(dateStr) &&
            cs.is_one_time === false
          )
          
          // If deleted, skip (don't show on calendar)
          if (override && override.status === 'deleted') {
            return
          }
          
          // Check for report
          const hasReport = reports.some(r => 
            r.student_id === student.id && 
            r.session_date?.startsWith(dateStr)
          )
          const matchedReport = hasReport ? reports.find(r => r.student_id === student.id && r.session_date?.startsWith(dateStr)) : null
          
          // Add session with override status if present, or 'scheduled' as default
          sessionsForDay.push({
            student,
            time: session.displayTime,
            time24: session.time,
            hasReport,
            reportId: matchedReport?.id,
            date: new Date(date),
            type: 'recurring',
            status: override ? override.status : 'scheduled',
            calendarSessionId: override ? override.id : null,
            duration_hours: override?.duration_hours || matchedReport?.duration_hours || '1'
          })
        }
      })
    })
    
    // Add one-time sessions (exclude only deleted)
    const oneTimeSessions = calendarSessions.filter(cs => 
      cs.is_one_time && 
      cs.session_date?.startsWith(dateStr) &&
      cs.status !== 'deleted'
    )
    
    oneTimeSessions.forEach(cs => {
      const student = students.find(s => s.id === cs.student_id) || (window.allStudents && window.allStudents.find(s => s.id === cs.student_id))
      if (student) {
        const sessionTime = new Date(cs.session_date)
        const displayTime = sessionTime.toLocaleTimeString('en-US', { 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        })
        
        const hasReport = reports.some(r => 
          r.student_id === student.id && 
          r.session_date?.startsWith(dateStr)
        )
        const matchedReport = hasReport ? reports.find(r => r.student_id === student.id && r.session_date?.startsWith(dateStr)) : null
        
        sessionsForDay.push({
          student,
          time: displayTime,
          hasReport,
          reportId: matchedReport?.id,
          date: new Date(date),
          type: 'one-time',
          status: cs.status,
          sessionId: cs.id,
          calendarSessionId: cs.id,
          notes: cs.notes,
          duration_hours: cs.duration_hours
        })
      }
    })
    
    // Add reports from inactive students (past sessions with completed reports)
    const reportsForDay = reports.filter(r => r.session_date?.startsWith(dateStr))
    reportsForDay.forEach(report => {
      const student = (window.allStudents && window.allStudents.find(s => s.id === report.student_id)) || students.find(s => s.id === report.student_id)
      
      // Only add if not already in sessionsForDay
      const alreadyShown = sessionsForDay.some(s => s.student.id === report.student_id)
      
      if (student && !alreadyShown) {
        // Extract time from session_date
        const sessionTime = new Date(report.session_date)
        const displayTime = sessionTime.toLocaleTimeString('en-US', { 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        })
        const time24 = sessionTime.toTimeString().substring(0, 5)
        
        sessionsForDay.push({
          student,
          time: displayTime,
          time24: time24,
          hasReport: true,
          reportId: report.id,
          date: new Date(date),
          type: 'past-inactive',
          status: 'completed',
          duration_hours: report.duration_hours,
          calendarSessionId: null
        })
      }
    })
    
    return {
      date,
      dayName: dayNames[dayIndex],
      sessions: sessionsForDay.sort((a, b) => a.time.localeCompare(b.time))
    }
  })

  const handleCreateReport = (student, date) => {
    // Navigate to new report page with pre-filled student and date
    navigate('/reports/new', { 
      state: { 
        studentId: student.id,
        sessionDate: date.toISOString().split('T')[0]
      }
    })
  }

  const handleCancelSession = async (session, date) => {
    const dateTimeStr = `${date.toISOString().split('T')[0]}T${session.time24 || '12:00'}:00`
    
    try {
      if (session.calendarSessionId) {
        // Update existing calendar session
        await updateCalendarSession(session.calendarSessionId, { status: 'cancelled' })
      } else {
        // Create new override for recurring session
        await createCalendarSession({
          student_id: session.student.id,
          session_date: dateTimeStr,
          status: 'cancelled',
          is_one_time: false,
          notes: 'Cancelled session'
        })
      }
      setMenuOpen(null)
      await loadData()
    } catch (error) {
      console.error('Error cancelling session:', error)
      alert('Error cancelling session')
    }
  }

  const handleEditSession = (session, date) => {
    const dateTimeStr = `${date.toISOString().split('T')[0]}T${session.time24 || '12:00'}:00`
    
    // For past-inactive sessions (report-only), use the actual report time
    let editDate = date.toISOString().split('T')[0]
    let editTime = session.time24 || '12:00'
    
    if (session.type === 'past-inactive' && session.reportId) {
      const report = reports.find(r => r.id === session.reportId)
      if (report && report.session_date) {
        const reportDate = new Date(report.session_date)
        editDate = reportDate.toISOString().split('T')[0]
        editTime = reportDate.toTimeString().substring(0, 5)
      }
    }
    
    setSelectedSession({
      ...session,
      originalDate: date,
      originalDateTime: dateTimeStr,
      editDate: editDate,
      editTime: editTime,
      editDuration: session.duration_hours || '1',
      editNotes: session.notes || ''
    })
    setShowEditModal(true)
    setMenuOpen(null)
  }

  const handleAddOneTimeSession = (date) => {
    setSelectedSession({
      date: date,
      isNew: true
    })
    setShowAddModal(true)
  }

  const isToday = (date) => {
    const today = new Date()
    return date.toDateString() === today.toDateString()
  }

  const isPast = (date) => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    return date < today
  }

  if (loading) {
    return <div className="text-center py-12">Loading calendar...</div>
  }

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-sage-800">Session Calendar</h2>
          <p className="text-sage-600 mt-1">
            View your weekly schedule and track which sessions need reports
          </p>
        </div>
      </div>

      {/* Week Navigation */}
      <div className="flex items-center justify-between mb-6 bg-white rounded-lg shadow-sm border border-sage-200 p-4">
        <button
          onClick={() => setCurrentWeek(currentWeek - 1)}
          className="p-2 hover:bg-sage-50 rounded-lg transition-colors"
        >
          <ChevronLeft className="w-5 h-5 text-sage-700" />
        </button>
        
        <div className="text-center">
          <p className="text-lg font-semibold text-sage-900">
            {currentWeek === 0 ? 'This Week' : currentWeek === 1 ? 'Next Week' : currentWeek === -1 ? 'Last Week' : `Week of ${weekDates[0].toLocaleDateString()}`}
          </p>
          <p className="text-sm text-sage-600">
            {weekDates[0].toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - {weekDates[6].toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
          </p>
        </div>
        
        <button
          onClick={() => setCurrentWeek(currentWeek + 1)}
          className="p-2 hover:bg-sage-50 rounded-lg transition-colors"
        >
          <ChevronRight className="w-5 h-5 text-sage-700" />
        </button>
      </div>

      {currentWeek !== 0 && (
        <div className="mb-4">
          <button
            onClick={() => setCurrentWeek(0)}
            className="text-sm text-sage-600 hover:text-sage-700 font-medium"
          >
            ← Back to This Week
          </button>
        </div>
      )}

      {/* Calendar Grid - Day Blocks in Row */}
      <div className="grid grid-cols-7 gap-4">
        {calendarData.map((day, index) => (
          <div
            key={index}
            className={`
              bg-white rounded-lg shadow-sm border-2 p-4 min-h-[300px]
              ${isToday(day.date) ? 'border-sage-600' : 'border-sage-200'}
            `}
          >
            {/* Day Header */}
            <div className="mb-3 pb-2 border-b border-sage-200">
              <p className="font-semibold text-sage-900">
                {day.dayName}
              </p>
              <p className={`text-sm ${isToday(day.date) ? 'text-sage-700 font-medium' : 'text-sage-600'}`}>
                {day.date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                {isToday(day.date) && ' (Today)'}
              </p>
            </div>

            {/* Sessions */}
            <div className="space-y-2">
              {day.sessions.map((session, idx) => {
                const isCancelled = session.status === 'cancelled'
                const menuKey = `${day.dayName}-${idx}`
                
                return (
                  <div
                    key={idx}
                    className={`
                      p-3 rounded-lg border transition-all relative
                      ${isCancelled
                        ? 'bg-gray-50 border-gray-300 opacity-75'
                        : session.hasReport 
                          ? 'bg-green-50 border-green-200' 
                          : isPast(day.date)
                            ? 'bg-red-50 border-red-200'
                            : 'bg-yellow-50 border-yellow-200'
                      }
                    `}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <p className={`font-medium text-sage-900 text-sm ${isCancelled ? 'line-through' : ''}`}>
                          {session.student.name}
                        </p>
                        <p className={`text-xs text-sage-600 flex items-center mt-1 ${isCancelled ? 'line-through' : ''}`}>
                          <Clock className="w-3 h-3 mr-1" />
                          {session.time}
                          {session.duration_hours && session.duration_hours !== '1' && (
                            <span className="ml-2 text-sage-500">({session.duration_hours}h)</span>
                          )}
                        </p>
                        {session.student.subject && (
                          <p className="text-xs text-sage-600 mt-1">
                            {session.student.subject}
                          </p>
                        )}
                        {session.type === 'one-time' && (
                          <span className="inline-block mt-1 px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded">
                            One-time
                          </span>
                        )}
                        {isCancelled && (
                          <span className="inline-block mt-1 px-2 py-0.5 bg-gray-200 text-gray-700 text-xs rounded">
                            Cancelled
                          </span>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-1">
                        {/* Status indicator - just checkmark for completed */}
                        {session.hasReport && !isCancelled && (
                          <span className="text-green-700 font-medium" title="Report written">
                            ✓
                          </span>
                        )}
                        
                        {/* 3-dot menu */}
                        <div className="relative">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              setMenuOpen(menuOpen === menuKey ? null : menuKey)
                            }}
                            className="p-1 hover:bg-white/50 rounded transition-colors"
                          >
                            <MoreVertical className="w-4 h-4 text-sage-600" />
                          </button>
                          
                          {menuOpen === menuKey && (
                            <div className="absolute right-0 top-6 z-20 bg-white shadow-lg border border-sage-200 rounded-lg py-1 w-48">
                              {!isCancelled && session.hasReport && (
                                <button
                                  onClick={() => {
                                    navigate(`/reports/${session.reportId}/edit`)
                                    setMenuOpen(null)
                                  }}
                                  className="w-full text-left px-4 py-2 text-sm text-sage-700 hover:bg-sage-50 flex items-center"
                                >
                                  <FileText className="w-4 h-4 mr-2" />
                                  Edit Report
                                </button>
                              )}
                              {!isCancelled && (
                                <button
                                  onClick={() => handleEditSession(session, day.date)}
                                  className="w-full text-left px-4 py-2 text-sm text-sage-700 hover:bg-sage-50 flex items-center"
                                >
                                  <Edit className="w-4 h-4 mr-2" />
                                  Edit Session
                                </button>
                              )}
                              {!isCancelled ? (
                                <button
                                  onClick={() => handleCancelSession(session, day.date)}
                                  className="w-full text-left px-4 py-2 text-sm text-orange-600 hover:bg-orange-50 flex items-center"
                                >
                                  <X className="w-4 h-4 mr-2" />
                                  Cancel Session
                                </button>
                              ) : (
                                <button
                                  onClick={async () => {
                                    if (session.sessionId) {
                                      await deleteCalendarSession(session.sessionId)
                                      setMenuOpen(null)
                                      await loadData()
                                    }
                                  }}
                                  className="w-full text-left px-4 py-2 text-sm text-sage-700 hover:bg-sage-50 flex items-center"
                                >
                                  <Trash2 className="w-4 h-4 mr-2" />
                                  Uncancel Session
                                </button>
                              )}
                              
                              <button
                                onClick={async () => {
                                  try {
                                    if (session.calendarSessionId) {
                                      // Update existing calendar session to deleted
                                      await updateCalendarSession(session.calendarSessionId, { status: 'deleted' })
                                    } else {
                                      // Create calendar override marked as deleted
                                      const dateTimeStr = `${day.date.toISOString().split('T')[0]}T${session.time24 || '12:00'}:00`
                                      await createCalendarSession({
                                        student_id: session.student.id,
                                        session_date: dateTimeStr,
                                        status: 'deleted',
                                        is_one_time: false
                                      })
                                    }
                                    setMenuOpen(null)
                                    await loadData()
                                  } catch (error) {
                                    console.error('Error deleting session:', error)
                                    alert('Error deleting session')
                                  }
                                }}
                                className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center border-t border-sage-200"
                              >
                                <Trash2 className="w-4 h-4 mr-2" />
                                Delete Session
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    {!session.hasReport && !isCancelled && (
                      <button
                        onClick={() => handleCreateReport(session.student, day.date)}
                        className="w-full mt-2 px-2 py-1 bg-sage-600 text-white text-xs rounded hover:bg-sage-700 transition-colors flex items-center justify-center"
                      >
                        <Plus className="w-3 h-3 mr-1" />
                        Write Report
                      </button>
                    )}
                  </div>
                )
              })}
              
              {/* Add Session Button */}
              <button
                onClick={() => handleAddOneTimeSession(day.date)}
                className="w-full mt-2 px-2 py-2 border-2 border-dashed border-sage-300 text-sage-600 text-xs rounded hover:border-sage-400 hover:bg-sage-50 transition-colors flex items-center justify-center"
              >
                <Plus className="w-3 h-3 mr-1" />
                Add Session
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* No Schedule Warning */}
      {students.length > 0 && students.every(s => !s.recurring_schedule) && (
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm font-medium text-yellow-900 mb-2">⚠️ No Schedules Set</p>
          <p className="text-sm text-yellow-800 mb-3">
            Add recurring schedules to your students to see them on the calendar!
          </p>
          <Link
            to="/students"
            className="inline-flex items-center text-yellow-700 hover:text-yellow-800 font-medium text-sm"
          >
            Go to Students →
          </Link>
        </div>
      )}

      {/* Add Session Modal */}
      {showAddModal && selectedSession && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="flex items-center justify-between p-6 border-b border-sage-200">
              <h3 className="text-lg font-bold text-sage-800">Add One-Time Session</h3>
              <button onClick={() => setShowAddModal(false)} className="text-sage-400 hover:text-sage-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={async (e) => {
              e.preventDefault()
              const formData = new FormData(e.target)
              let studentId = formData.get('student_id')
              const time = formData.get('time')
              const duration = formData.get('duration')
              
              try {
                // If "new" was selected, create the student first
                if (studentId === 'new') {
                  const newStudentName = formData.get('new_student_name')
                  const newStudentSubject = formData.get('new_student_subject')
                  
                  const newStudent = await createStudent({
                    name: newStudentName,
                    subject: newStudentSubject,
                    active: true
                  })
                  studentId = newStudent.id
                }
                
                const dateTime = `${selectedSession.date.toISOString().split('T')[0]}T${time}:00`
                
                await createCalendarSession({
                  student_id: parseInt(studentId),
                  session_date: dateTime,
                  duration_hours: duration,
                  status: 'scheduled',
                  is_one_time: true
                })
                setShowAddModal(false)
                setShowNewStudentFields(false)
                await loadData()
              } catch (error) {
                console.error('Error adding session:', error)
                alert('Error adding session')
              }
            }} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">Student *</label>
                <select 
                  name="student_id" 
                  required 
                  onChange={(e) => setShowNewStudentFields(e.target.value === 'new')}
                  className="w-full px-3 py-2 border border-sage-300 rounded-lg"
                >
                  <option value="">Select student...</option>
                  {students.map(s => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                  <option value="new">+ New Student</option>
                </select>
              </div>
              
              {/* New Student Fields */}
              {showNewStudentFields && (
                <>
                  <div className="pl-4 border-l-2 border-sage-300 space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-sage-700 mb-2">Student Name *</label>
                      <input 
                        type="text" 
                        name="new_student_name" 
                        required={showNewStudentFields}
                        placeholder="e.g., John Smith"
                        className="w-full px-3 py-2 border border-sage-300 rounded-lg" 
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-sage-700 mb-2">Subject</label>
                      <input 
                        type="text" 
                        name="new_student_subject" 
                        placeholder="e.g., Geometry, SAT Math"
                        className="w-full px-3 py-2 border border-sage-300 rounded-lg" 
                      />
                    </div>
                  </div>
                </>
              )}
              
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">Time *</label>
                <input 
                  type="time" 
                  name="time" 
                  required 
                  defaultValue={selectedSession.suggestedTime || "12:00"} 
                  className="w-full px-3 py-2 border border-sage-300 rounded-lg" 
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">Duration</label>
                <select name="duration" defaultValue="1" className="w-full px-3 py-2 border border-sage-300 rounded-lg">
                  <option value="0.5">0.5 hours</option>
                  <option value="1">1 hour</option>
                  <option value="1.5">1.5 hours</option>
                  <option value="2">2 hours</option>
                  <option value="2.5">2.5 hours</option>
                  <option value="3">3 hours</option>
                </select>
              </div>
              
              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setShowAddModal(false)} className="flex-1 px-4 py-2 border border-sage-300 text-sage-700 rounded-lg hover:bg-sage-50">
                  Cancel
                </button>
                <button type="submit" className="flex-1 px-4 py-2 bg-sage-600 text-white rounded-lg hover:bg-sage-700">
                  Add Session
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Reschedule Modal */}
      {showEditModal && selectedSession && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="flex items-center justify-between p-6 border-b border-sage-200">
              <h3 className="text-lg font-bold text-sage-800">Edit Session</h3>
              <button onClick={() => setShowEditModal(false)} className="text-sage-400 hover:text-sage-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={async (e) => {
              e.preventDefault()
              const formData = new FormData(e.target)
              const newDate = formData.get('edit_date')
              const newTime = formData.get('edit_time')
              const newDuration = formData.get('edit_duration')
              const newNotes = formData.get('edit_notes')
              
              const newDateTime = `${newDate}T${newTime}:00`
              
              try {
                if (selectedSession.calendarSessionId) {
                  // Update existing calendar session
                  await updateCalendarSession(selectedSession.calendarSessionId, {
                    session_date: newDateTime,
                    duration_hours: newDuration,
                    notes: newNotes
                  })
                } else {
                  // Create calendar override for recurring session
                  // First, cancel the original
                  await createCalendarSession({
                    student_id: selectedSession.student.id,
                    session_date: selectedSession.originalDateTime,
                    status: 'cancelled',
                    is_one_time: false,
                    notes: 'Edited'
                  })
                  
                  // Then create new session
                  await createCalendarSession({
                    student_id: selectedSession.student.id,
                    session_date: newDateTime,
                    duration_hours: newDuration,
                    status: 'scheduled',
                    is_one_time: true,
                    notes: newNotes
                  })
                }
                
                setShowEditModal(false)
                await loadData()
              } catch (error) {
                console.error('Error updating session:', error)
                alert('Error updating session')
              }
            }} className="p-6 space-y-4">
              <div className="bg-sage-50 border border-sage-200 rounded-lg p-3 mb-4">
                <p className="text-sm text-sage-700">
                  <strong>{selectedSession.student?.name}</strong>
                </p>
                <p className="text-xs text-sage-600">
                  {selectedSession.student?.subject}
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">Date *</label>
                <input type="date" name="edit_date" required defaultValue={selectedSession.editDate} className="w-full px-3 py-2 border border-sage-300 rounded-lg" />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-sage-700 mb-2">Time *</label>
                  <input type="time" name="edit_time" required defaultValue={selectedSession.editTime} className="w-full px-3 py-2 border border-sage-300 rounded-lg" />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-sage-700 mb-2">Duration</label>
                  <select name="edit_duration" defaultValue={selectedSession.editDuration} className="w-full px-3 py-2 border border-sage-300 rounded-lg">
                    <option value="0.5">0.5 hours</option>
                    <option value="1">1 hour</option>
                    <option value="1.5">1.5 hours</option>
                    <option value="2">2 hours</option>
                    <option value="2.5">2.5 hours</option>
                    <option value="3">3 hours</option>
                  </select>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-2">Notes</label>
                <textarea 
                  name="edit_notes" 
                  defaultValue={selectedSession.editNotes}
                  rows={3}
                  className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500"
                  placeholder="Any special notes for this session..."
                />
              </div>
              
              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setShowEditModal(false)} className="flex-1 px-4 py-2 border border-sage-300 text-sage-700 rounded-lg hover:bg-sage-50">
                  Cancel
                </button>
                <button type="submit" className="flex-1 px-4 py-2 bg-sage-600 text-white rounded-lg hover:bg-sage-700">
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Calendar

