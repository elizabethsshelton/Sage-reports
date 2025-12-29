import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Health check
export const checkAPIHealth = async () => {
  try {
    const response = await api.get('/health')
    return {
      connected: true,
      ...response.data
    }
  } catch (error) {
    return {
      connected: false,
      error: error.message
    }
  }
}

// Students
export const getStudents = async (activeOnly = true) => {
  const response = await api.get('/students', { params: { active_only: activeOnly } })
  return response.data
}

export const getStudent = async (id) => {
  const response = await api.get(`/students/${id}`)
  return response.data
}

export const createStudent = async (studentData) => {
  const response = await api.post('/students', studentData)
  return response.data
}

export const updateStudent = async (id, studentData) => {
  const response = await api.put(`/students/${id}`, studentData)
  return response.data
}

export const deleteStudent = async (id) => {
  const response = await api.delete(`/students/${id}`)
  return response.data
}

// Reports
export const getReports = async (studentId = null) => {
  const params = studentId ? { student_id: studentId } : {}
  const response = await api.get('/reports', { params })
  return response.data
}

export const getReport = async (id) => {
  const response = await api.get(`/reports/${id}`)
  return response.data
}

export const generateReport = async (reportData) => {
  const response = await api.post('/reports/generate', reportData)
  return response.data
}

export const createReport = async (reportData) => {
  const response = await api.post('/reports', reportData)
  return response.data
}

export const updateReport = async (id, reportData) => {
  const response = await api.put(`/reports/${id}`, reportData)
  return response.data
}

export const deleteReport = async (id) => {
  const response = await api.delete(`/reports/${id}`)
  return response.data
}

export const toggleReportTraining = async (id) => {
  const response = await api.post(`/reports/${id}/toggle-training`)
  return response.data
}

export const getSessionReminders = async (studentId) => {
  const response = await api.get(`/reports/reminders/${studentId}`)
  return response.data
}

export const fixReportGrammar = async (reportId, reportText) => {
  const response = await api.post(`/reports/${reportId}/fix-grammar`, { report_text: reportText })
  return response.data
}

export const suggestSentences = async (reportId, reportText, cursorPosition = null) => {
  const response = await api.post(`/reports/${reportId}/suggest-sentences`, { 
    report_text: reportText,
    cursor_position: cursorPosition
  })
  return response.data
}

export const polishText = async (reportId, textToPolish, fullContext) => {
  const response = await api.post(`/reports/${reportId}/polish-text`, { 
    text_to_polish: textToPolish,
    full_context: fullContext
  })
  return response.data
}

export const addContactToReport = async (reportId) => {
  const response = await api.post(`/reports/${reportId}/add-contact`)
  return response.data
}

export const suggestOpeningClosing = async (reportId, sentenceType) => {
  const response = await api.post(`/reports/${reportId}/suggest-opening-closing`, { 
    type: sentenceType  // 'opening' or 'closing'
  })
  return response.data
}

export const suggestSynonyms = async (reportId, word, context = '') => {
  const response = await api.post(`/reports/${reportId}/suggest-synonyms`, { 
    word: word,
    context: context
  })
  return response.data
}

export const reviewReportPhrases = async (reportId, reportText) => {
  const response = await api.post(`/reports/${reportId}/review-phrases`, { 
    report_text: reportText
  })
  return response.data
}

// Sample Reports
export const getSampleReports = async () => {
  const response = await api.get('/sample-reports')
  return response.data
}

export const uploadSampleReport = async (filename, content, metadata = {}) => {
  const response = await api.post('/sample-reports', { 
    filename, 
    content,
    ...metadata
  })
  return response.data
}

export const deleteSampleReport = async (id) => {
  const response = await api.delete(`/sample-reports/${id}`)
  return response.data
}

// Statistics
export const getStats = async () => {
  const response = await api.get('/stats')
  return response.data
}

export const getTodaySessions = async () => {
  const response = await api.get('/today-sessions')
  return response.data
}

// User Settings
export const getUserSettings = async () => {
  const response = await api.get('/user-settings')
  return response.data
}

export const updateUserSettings = async (settingsData) => {
  const response = await api.put('/user-settings', settingsData)
  return response.data
}

// Calendar Sessions
export const getCalendarSessions = async (startDate = null, endDate = null) => {
  const params = {}
  if (startDate) params.start_date = startDate
  if (endDate) params.end_date = endDate
  const response = await api.get('/calendar-sessions', { params })
  return response.data
}

export const createCalendarSession = async (sessionData) => {
  const response = await api.post('/calendar-sessions', sessionData)
  return response.data
}

export const updateCalendarSession = async (id, sessionData) => {
  const response = await api.put(`/calendar-sessions/${id}`, sessionData)
  return response.data
}

export const deleteCalendarSession = async (id) => {
  const response = await api.delete(`/calendar-sessions/${id}`)
  return response.data
}

export const getDeletedSessions = async () => {
  const response = await api.get('/calendar-sessions/deleted')
  return response.data
}

export const getCalendarSessionForDate = async (studentId, sessionDate) => {
  const response = await api.get('/calendar-sessions/for-date', {
    params: { student_id: studentId, session_date: sessionDate }
  })
  return response.data
}

export const clearAllDeletedSessions = async () => {
  const response = await api.delete('/calendar-sessions/deleted/clear-all')
  return response.data
}

export const permanentlyDeleteSession = async (id) => {
  const response = await api.delete(`/calendar-sessions/${id}/permanent-delete`)
  return response.data
}

export default api
