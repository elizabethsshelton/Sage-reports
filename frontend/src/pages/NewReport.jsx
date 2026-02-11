import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Sparkles, ArrowLeft, Loader } from 'lucide-react'
import { getStudents, generateReport, getStats, createStudent, createReport, getSessionReminders, getCalendarSessionForDate } from '../services/api'

function NewReport() {
  const navigate = useNavigate()
  const location = useLocation()
  const [students, setStudents] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showNewStudentFields, setShowNewStudentFields] = useState(false)
  const [formData, setFormData] = useState({
    student_id: location.state?.studentId || '',
    session_date: location.state?.sessionDate || new Date().toISOString().split('T')[0],
    duration_hours: '1',
    topics_covered: '',
    activities: '',
    notes: '',
    ai_instructions: ''
  })
  const [newStudentData, setNewStudentData] = useState({
    name: '',
    subject: ''
  })
  const [savingDraft, setSavingDraft] = useState(false)
  const [reminders, setReminders] = useState(null)
  const [loadingReminders, setLoadingReminders] = useState(false)

  useEffect(() => {
    loadStudents()
    loadStats()
    loadCalendarSessionNotes()
  }, [])

  useEffect(() => {
    if (formData.student_id && formData.student_id !== 'new') {
      loadReminders(formData.student_id)
    } else {
      setReminders(null)
    }
  }, [formData.student_id])

  const loadCalendarSessionNotes = async () => {
    // If coming from dashboard, load the calendar session notes
    if (location.state?.studentId && location.state?.sessionDate) {
      try {
        const calSession = await getCalendarSessionForDate(
          location.state.studentId,
          location.state.sessionDate
        )
        if (calSession && calSession.notes) {
          setFormData(prev => ({ ...prev, notes: calSession.notes }))
        }
      } catch (error) {
        console.error('Error loading calendar session notes:', error)
      }
    }
  }

  const loadStudents = async () => {
    try {
      const data = await getStudents(true)
      setStudents(data)
      // Only set default student if not pre-filled from calendar
      if (data.length > 0 && !location.state?.studentId) {
        setFormData(prev => ({ ...prev, student_id: data[0].id }))
      }
    } catch (error) {
      console.error('Error loading students:', error)
    }
  }

  const loadStats = async () => {
    try {
      const data = await getStats()
      setStats(data)
    } catch (error) {
      console.error('Error loading stats:', error)
    }
  }

  const loadReminders = async (studentId) => {
    setLoadingReminders(true)
    try {
      const data = await getSessionReminders(studentId)
      setReminders(data)
    } catch (error) {
      console.error('Error loading reminders:', error)
      setReminders(null)
    } finally {
      setLoadingReminders(false)
    }
  }

  const addReminderToNotes = (reminderText) => {
    const currentNotes = formData.notes
    const newNote = currentNotes ? `${currentNotes}\n• ${reminderText}` : `• ${reminderText}`
    setFormData({ ...formData, notes: newNote })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    let studentId = formData.student_id
    
    // If "new" was selected, create the student first
    if (studentId === 'new') {
      if (!newStudentData.name) {
        alert('Please enter student name')
        return
      }
      
      setLoading(true)
      try {
        const newStudent = await createStudent({
          name: newStudentData.name,
          subject: newStudentData.subject,
          active: true
        })
        studentId = newStudent.id
        
        // Reload students list
        await loadStudents()
      } catch (error) {
        console.error('Error creating student:', error)
        
        // Check if it's a duplicate error
        if (error.response?.status === 409 || error.response?.data?.error === 'duplicate') {
          const existing = error.response?.data?.existing_student
          if (existing) {
            alert(`⚠️ A student named "${newStudentData.name}" already exists!\n\nSchedule: ${existing.recurring_schedule || 'Not set'}\nSubject: ${existing.subject || 'Not set'}\n\nPlease select them from the dropdown instead.`)
          } else {
            alert(`⚠️ A student named "${newStudentData.name}" already exists. Please select them from the dropdown.`)
          }
        } else {
          alert('Error creating student. Please try again.')
        }
        
        setLoading(false)
        return
      }
    }
    
    if (!studentId) {
      alert('Please select a student')
      return
    }

    setLoading(true)
    try {
      const report = await generateReport({ 
        ...formData, 
        student_id: studentId
      })
      navigate(`/reports/${report.id}/edit`)
    } catch (error) {
      console.error('Error generating report:', error)
      alert('Error generating report. Please check your AI configuration and try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveDraft = async () => {
    let studentId = formData.student_id
    
    // If "new" was selected, create the student first
    if (studentId === 'new') {
      if (!newStudentData.name) {
        alert('Please enter student name')
        return
      }
      
      setSavingDraft(true)
      try {
        const newStudent = await createStudent({
          name: newStudentData.name,
          subject: newStudentData.subject,
          active: true
        })
        studentId = newStudent.id
        await loadStudents()
      } catch (error) {
        console.error('Error creating student:', error)
        
        // Check if it's a duplicate error
        if (error.response?.status === 409 || error.response?.data?.error === 'duplicate') {
          const existing = error.response?.data?.existing_student
          if (existing) {
            alert(`⚠️ A student named "${newStudentData.name}" already exists!\n\nSchedule: ${existing.recurring_schedule || 'Not set'}\nSubject: ${existing.subject || 'Not set'}\n\nPlease select them from the dropdown instead.`)
          } else {
            alert(`⚠️ A student named "${newStudentData.name}" already exists. Please select them from the dropdown.`)
          }
        } else {
          alert('Error creating student. Please try again.')
        }
        
        setSavingDraft(false)
        return
      }
    }
    
    if (!studentId) {
      alert('Please select a student')
      return
    }

    setSavingDraft(true)
    try {
      const report = await createReport({
        ...formData,
        student_id: studentId
      })
      alert('Draft saved! You can continue editing it later from the Reports page.')
      navigate('/reports')
    } catch (error) {
      console.error('Error saving draft:', error)
      alert('Error saving draft. Please try again.')
    } finally {
      setSavingDraft(false)
    }
  }

  const selectedStudent = students.find(s => s.id === parseInt(formData.student_id))

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center text-sage-600 hover:text-sage-700 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </button>
        <h2 className="text-2xl font-bold text-sage-800">Write New Report</h2>
        <p className="text-sage-600 mt-1">
          Fill in the session details and let AI generate a professional report
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Form - Left Side (3 columns) */}
        <form onSubmit={handleSubmit} className="lg:col-span-3 space-y-6">
        {/* Student Selection */}
        <div className="bg-white rounded-lg shadow-sm border border-sage-200 p-6">
          <h3 className="text-lg font-semibold text-sage-800 mb-4">Student Information</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-sage-700 mb-1">
                Student *
              </label>
              <select
                required
                value={formData.student_id}
                onChange={(e) => {
                  setFormData({ ...formData, student_id: e.target.value })
                  setShowNewStudentFields(e.target.value === 'new')
                }}
                className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
              >
                <option value="">Select a student...</option>
                {students.map((student) => (
                  <option key={student.id} value={student.id}>
                    {student.name} {student.subject ? `- ${student.subject}` : ''}
                  </option>
                ))}
                <option value="new">+ New Student</option>
              </select>
            </div>
            
            {/* New Student Fields */}
            {showNewStudentFields && (
              <div className="col-span-3 pl-4 border-l-2 border-sage-300 space-y-3 bg-blue-50 p-4 rounded-lg">
                <p className="text-sm font-medium text-blue-900 mb-2">Create New Student</p>
                <div>
                  <label className="block text-xs font-medium text-sage-700 mb-1">
                    Student Name *
                  </label>
                  <input
                    type="text"
                    value={newStudentData.name}
                    onChange={(e) => setNewStudentData({ ...newStudentData, name: e.target.value })}
                    placeholder="e.g., John Smith"
                    className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
                    required={showNewStudentFields}
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-sage-700 mb-1">
                    Subject
                  </label>
                  <input
                    type="text"
                    value={newStudentData.subject}
                    onChange={(e) => setNewStudentData({ ...newStudentData, subject: e.target.value })}
                    placeholder="e.g., Geometry, SAT Math"
                    className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-1">
                Session Date *
              </label>
              <input
                type="date"
                required
                value={formData.session_date}
                onChange={(e) => setFormData({ ...formData, session_date: e.target.value })}
                className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-700 mb-1">
                Duration (hours)
              </label>
              <select
                value={formData.duration_hours}
                onChange={(e) => setFormData({ ...formData, duration_hours: e.target.value })}
                className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
              >
                <option value="0.5">0.5 hours</option>
                <option value="1">1 hour</option>
                <option value="1.5">1.5 hours</option>
                <option value="2">2 hours</option>
                <option value="2.5">2.5 hours</option>
                <option value="3">3 hours</option>
              </select>
            </div>
          </div>

          {selectedStudent && selectedStudent.notes && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm font-medium text-blue-900 mb-1">Student Notes:</p>
              <p className="text-sm text-blue-800">{selectedStudent.notes}</p>
            </div>
          )}
        </div>


        {/* Session Details */}
        <div className="bg-white rounded-lg shadow-sm border border-sage-200 p-6">
          <h3 className="text-lg font-semibold text-sage-800 mb-4">Session Details</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-sage-700 mb-1">
                Session Notes *
              </label>
              <textarea
                required
                value={formData.notes}
                onChange={(e) => {
                  let newValue = e.target.value
                  // Auto-convert "- " to "• "
                  if (newValue.endsWith('- ')) {
                    newValue = newValue.slice(0, -2) + '• '
                  }
                  setFormData({ ...formData, notes: newValue })
                }}
                onFocus={(e) => {
                  // Auto-start with bullet if empty
                  if (!formData.notes) {
                    setFormData({ ...formData, notes: '• ' })
                    setTimeout(() => {
                      e.target.selectionStart = e.target.selectionEnd = 2
                    }, 0)
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    const textarea = e.target
                    const cursorPos = textarea.selectionStart
                    const textBefore = formData.notes.substring(0, cursorPos)
                    const textAfter = formData.notes.substring(cursorPos)
                    
                    // Add new line with bullet
                    const newText = textBefore + '\n• ' + textAfter
                    setFormData({ ...formData, notes: newText })
                    
                    // Set cursor position after the bullet
                    setTimeout(() => {
                      textarea.selectionStart = textarea.selectionEnd = cursorPos + 3
                    }, 0)
                  }
                }}
                rows={8}
                className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
                placeholder="• Worked on quadratic equations&#10;• Student understood factoring well&#10;• Struggled with word problems&#10;• Very engaged today&#10;• Has geometry test on Friday"
              />
              <p className="text-xs text-sage-500 mt-1">
                Press Enter for new bullet • Type "- " (dash-space) to create bullet
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-purple-700 mb-1">
                AI Writing Instructions (Optional)
              </label>
              <textarea
                value={formData.ai_instructions}
                onChange={(e) => setFormData({ ...formData, ai_instructions: e.target.value })}
                className="w-full px-3 py-2 border border-purple-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                rows={3}
                placeholder="e.g., 'Keep it brief and focus on his enthusiasm', 'Highlight her progress in algebra'"
              />
              <p className="text-xs text-purple-500 mt-1">
                Tell the AI how you'd like this specific report to be written.
              </p>
            </div>

          </div>
        </div>

        {/* Submit Buttons */}
        <div className="flex justify-between items-center">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="px-6 py-3 text-sage-700 hover:bg-sage-50 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={handleSaveDraft}
              disabled={savingDraft || loading}
              className="px-6 py-3 border-2 border-sage-300 text-sage-700 font-medium rounded-xl hover:bg-sage-50 transition-smooth shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {savingDraft ? 'Saving...' : 'Save Draft'}
            </button>
            <button
              type="submit"
              disabled={loading || savingDraft}
              className="px-8 py-3 bg-sage-600 text-white font-semibold rounded-xl hover:bg-sage-700 transition-smooth hover-lift shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 mr-2 animate-spin" />
                  Generating Report...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5 mr-2" />
                  Generate Report with AI
                </>
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Reminders Sidebar - Right Side (1 column) */}
      <div className="lg:col-span-1">
        {reminders && reminders.has_reminders ? (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 sticky top-6">
            <p className="text-xs font-medium text-gray-600 mb-2">
              Reminders from last session
            </p>
            <p className="text-xs text-gray-400 mb-3">
              ({reminders.last_session_date ? new Date(reminders.last_session_date).toLocaleDateString() : ''})
            </p>

            {reminders.ai_extracted && reminders.ai_extracted.length > 0 ? (
              <div>
                <div className="space-y-2">
                  {reminders.ai_extracted.map((item, index) => {
                    const reminderText = typeof item === 'string' ? item : item.reminder
                    const sourceText = typeof item === 'object' && item.source ? item.source : null
                    
                    return (
                      <div key={index} className="relative group">
                        <button
                          type="button"
                          onClick={() => addReminderToNotes(reminderText)}
                          className="block text-left text-xs text-gray-600 hover:text-sage-700 hover:underline w-full"
                        >
                          • {reminderText}
                        </button>
                        {sourceText && (
                          <div className="hidden group-hover:block absolute z-10 left-0 top-full mt-1 p-3 bg-gray-800 text-white text-xs rounded-lg shadow-lg max-w-md">
                            <p className="font-semibold mb-1">From previous report:</p>
                            <p className="italic">"{sourceText}"</p>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
                <p className="text-xs text-gray-400 mt-3 italic">Click to add to notes</p>
              </div>
            ) : (
              <p className="text-xs text-gray-500 italic">No action items found in last report</p>
            )}
          </div>
        ) : loadingReminders ? (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center sticky top-6">
            <p className="text-xs text-gray-500">Loading reminders...</p>
          </div>
        ) : null}
      </div>
      </div>
    </div>
  )
}

export default NewReport

