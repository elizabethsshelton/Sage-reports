import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Save, Copy, Download, CheckCircle, Check, Trash2, Sparkles, RefreshCw, ChevronDown, ChevronUp, Wand2, Undo2, Contact, X, Send, AlertCircle } from 'lucide-react'
import { getReport, updateReport, deleteReport, getStudents, getReports, fixReportGrammar, suggestSentences, polishText, polishFullReport, generateReport, addContactToReport, askAIAboutText, getSynonyms, reviewPhrases } from '../services/api'

function EditReport() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [regenerating, setRegenerating] = useState(false)
  const [copied, setCopied] = useState(false)
  const [editedReport, setEditedReport] = useState('')
  const [status, setStatus] = useState('draft')
  const [students, setStudents] = useState([])
  const [selectedStudentId, setSelectedStudentId] = useState('')
  const [sessionDate, setSessionDate] = useState('')
  const [fixingGrammar, setFixingGrammar] = useState(false)
  const [suggestions, setSuggestions] = useState([])
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(true)
  const [selectedText, setSelectedText] = useState('')
  const [polishing, setPolishing] = useState(false)
  const [nextSessionNotes, setNextSessionNotes] = useState('')
  const [useForTraining, setUseForTraining] = useState(false)
  const [undoStack, setUndoStack] = useState([])
  const [showUndoButton, setShowUndoButton] = useState(false)
  const [addingContact, setAddingContact] = useState(false)
  // Previous report viewer
  const [showPreviousReport, setShowPreviousReport] = useState(false)
  const [previousReport, setPreviousReport] = useState(null)
  const [loadingPreviousReport, setLoadingPreviousReport] = useState(false)
  
  // Ask AI feature
  const [showAskAI, setShowAskAI] = useState(false)
  const [selectedTextForAI, setSelectedTextForAI] = useState('')
  const [aiChatHistory, setAiChatHistory] = useState([])
  const [currentAIQuestion, setCurrentAIQuestion] = useState('')
  const [loadingAIAnswer, setLoadingAIAnswer] = useState(false)
  
  // Regenerate with instructions
  const [showRegenerateModal, setShowRegenerateModal] = useState(false)
  const [regenerateInstructions, setRegenerateInstructions] = useState('')
  
  // Review Report feature
  const [reviewSuggestions, setReviewSuggestions] = useState([])
  const [loadingReview, setLoadingReview] = useState(false)
  const [activeSuggestion, setActiveSuggestion] = useState(null)
  
  // Synonym finder
  const [selectedWord, setSelectedWord] = useState('')
  const [synonyms, setSynonyms] = useState([])
  const [loadingSynonyms, setLoadingSynonyms] = useState(false)
  const [showSynonyms, setShowSynonyms] = useState(false)
  const [wordPosition, setWordPosition] = useState({ start: 0, end: 0 })
  
  // Polish Full Report
  const [loadingPolish, setLoadingPolish] = useState(false)
  const [polishChanges, setPolishChanges] = useState([])
  const [showPolishChanges, setShowPolishChanges] = useState(false)
  const [originalBeforePolish, setOriginalBeforePolish] = useState('')
  
  // Auto-save
  const [autoSaveStatus, setAutoSaveStatus] = useState('saved') // 'saving', 'saved', 'error'
  
  const textareaRef = useRef(null)
  const aiChatEndRef = useRef(null)

  useEffect(() => {
    loadReport()
    loadStudents()
  }, [id])

  useEffect(() => {
    // Load suggestions when report is loaded
    if (report && editedReport) {
      loadSuggestions()
    }
  }, [report])

  // Auto-save functionality - saves 2 seconds after user stops typing
  useEffect(() => {
    if (!report || !editedReport || editedReport === report.final_report) {
      return // Don't save if no changes
    }

    setAutoSaveStatus('saving')
    const saveTimer = setTimeout(async () => {
      try {
        await updateReport(id, {
          final_report: editedReport,
          status: status,
          use_for_training: useForTraining,
          student_id: selectedStudentId,
          session_date: sessionDate,
          next_session_notes: nextSessionNotes
        })
        setAutoSaveStatus('saved')
        console.log('✅ Auto-saved at', new Date().toLocaleTimeString())
        
        // Update report state to match saved version
        setReport(prev => ({ ...prev, final_report: editedReport }))
      } catch (error) {
        console.error('Auto-save error:', error)
        setAutoSaveStatus('error')
      }
    }, 2000) // Save 2 seconds after last keystroke

    return () => clearTimeout(saveTimer)
  }, [editedReport, id, status, useForTraining, selectedStudentId, sessionDate, nextSessionNotes])

  const loadStudents = async () => {
    try {
      const data = await getStudents(false) // Get all students
      setStudents(data)
    } catch (error) {
      console.error('Error loading students:', error)
    }
  }

  const loadReport = async () => {
    try {
      const data = await getReport(id)
      setReport(data)
      setEditedReport(data.final_report || data.ai_generated_report || '')
      setStatus(data.status || 'draft')
      setUseForTraining(data.use_for_training || false)
      setSelectedStudentId(data.student_id || '')
      setSessionDate(data.session_date ? data.session_date.split('T')[0] : '')
      setNextSessionNotes(data.next_session_notes || '')
      
      // Load previous report for this student
      if (data.student_id) {
        loadPreviousReport(data.student_id, data.session_date)
      }
    } catch (error) {
      console.error('Error loading report:', error)
      alert('Error loading report')
      navigate('/reports')
    } finally {
      setLoading(false)
    }
  }

  const loadPreviousReport = async (studentId, currentSessionDate) => {
    try {
      setLoadingPreviousReport(true)
      const reports = await getReports(studentId)
      
      // Find the most recent report before the current one
      const currentDate = new Date(currentSessionDate)
      const previousReports = reports
        .filter(r => r.id !== parseInt(id) && new Date(r.session_date) < currentDate)
        .sort((a, b) => new Date(b.session_date) - new Date(a.session_date))
      
      if (previousReports.length > 0) {
        setPreviousReport(previousReports[0])
      }
    } catch (error) {
      console.error('Error loading previous report:', error)
    } finally {
      setLoadingPreviousReport(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await updateReport(id, {
        final_report: editedReport,
        status: status,
        use_for_training: useForTraining,
        student_id: selectedStudentId,
        session_date: sessionDate,
        next_session_notes: nextSessionNotes
      })
      alert('Report saved successfully!')
      loadReport() // Reload to get updated student name
    } catch (error) {
      console.error('Error saving report:', error)
      alert('Error saving report. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const handleFinalize = async () => {
    setSaving(true)
    try {
      await updateReport(id, {
        final_report: editedReport,
        status: 'sent',  // Auto-approve
        use_for_training: true,  // Mark for training
        student_id: selectedStudentId,
        session_date: sessionDate,
        next_session_notes: nextSessionNotes
      })
      setStatus('sent')
      setUseForTraining(true)
      alert('✅ Report finalized and added to training data! This report will now help improve future AI generations.')
      setTimeout(() => navigate('/reports'), 1500)
    } catch (error) {
      console.error('Error finalizing report:', error)
      alert('Error finalizing report. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this report? This action cannot be undone.')) {
      return
    }
    
    try {
      await deleteReport(id)
      alert('Report deleted successfully')
      navigate('/reports')
    } catch (error) {
      console.error('Error deleting report:', error)
      alert('Error deleting report. Please try again.')
    }
  }

  const handleRegenerate = async (instructions = '') => {
    setShowRegenerateModal(false)
    setRegenerating(true)
    
    try {
      // Regenerate the report using the original data
      const regeneratedReport = await generateReport({
        student_id: report.student_id,
        session_date: report.session_date,
        duration_hours: report.duration_hours,
        topics_covered: report.topics_covered,
        activities: report.activities,
        notes: report.notes,
        ai_instructions: instructions,
        include_contact: false  // User can manually add this if needed
      })
      
      // Update the edited report with the new AI-generated content
      setEditedReport(regeneratedReport.ai_generated_report)
      setRegenerateInstructions('')
      alert('Report regenerated! Review the new version and save when ready.')
    } catch (error) {
      console.error('Error regenerating report:', error)
      alert('Error regenerating report. Please check your AI configuration and try again.')
    } finally {
      setRegenerating(false)
    }
  }

  const handlePolishFullReport = async () => {
    if (!editedReport) return
    
    setLoadingPolish(true)
    setOriginalBeforePolish(editedReport) // Save original for undo
    
    try {
      const result = await polishFullReport(id, editedReport)
      
      if (result.error) {
        alert(`Error polishing report: ${result.error}`)
        return
      }
      
      // Update the report with polished version
      setEditedReport(result.polished_text)
      setPolishChanges(result.changes || [])
      setShowPolishChanges(true)
      
      console.log('✨ Report polished successfully')
    } catch (error) {
      console.error('Error polishing report:', error)
      alert('Error polishing report. Please try again.')
    } finally {
      setLoadingPolish(false)
    }
  }

  const handleUndoPolish = () => {
    if (originalBeforePolish) {
      setEditedReport(originalBeforePolish)
      setShowPolishChanges(false)
      setPolishChanges([])
      setOriginalBeforePolish('')
      console.log('↩️ Undid polish')
    }
  }

  const handleAcceptPolish = () => {
    setShowPolishChanges(false)
    setPolishChanges([])
    setOriginalBeforePolish('') // Clear undo history after accepting
    console.log('✅ Accepted polished version')
  }

  const handleFixGrammar = async () => {
    setFixingGrammar(true)
    try {
      const result = await fixReportGrammar(id, editedReport)
      setEditedReport(result.fixed_report)
    } catch (error) {
      console.error('Error fixing grammar:', error)
      alert('Error fixing grammar. Please try again.')
    } finally {
      setFixingGrammar(false)
    }
  }

  const loadSuggestions = async () => {
    setLoadingSuggestions(true)
    try {
      // Get current cursor position from textarea
      const textarea = textareaRef.current
      const cursorPos = textarea ? textarea.selectionStart : null
      
      console.log('Cursor position:', cursorPos)
      console.log('Text at cursor:', editedReport.substring(Math.max(0, cursorPos - 50), cursorPos + 50))
      
      const result = await suggestSentences(id, editedReport, cursorPos)
      console.log('Suggestions API response:', result)
      console.log('Suggestions array:', result.suggestions)
      setSuggestions(result.suggestions || [])
    } catch (error) {
      console.error('Error loading suggestions:', error)
      setSuggestions([])
    } finally {
      setLoadingSuggestions(false)
    }
  }

  const insertSuggestion = (sentence) => {
    const textarea = textareaRef.current
    if (!textarea) return

    const cursorPos = textarea.selectionStart
    const textBefore = editedReport.substring(0, cursorPos)
    const textAfter = editedReport.substring(cursorPos)
    
    // Smart spacing - add space before/after if needed
    const spaceBefore = textBefore && !textBefore.endsWith(' ') && !textBefore.endsWith('\n') ? ' ' : ''
    const spaceAfter = textAfter && !textAfter.startsWith(' ') && !textAfter.startsWith('\n') ? ' ' : ''
    
    const newText = textBefore + spaceBefore + sentence + spaceAfter + textAfter
    setEditedReport(newText)
    
    // Set cursor position after inserted text
    setTimeout(() => {
      const newPos = cursorPos + spaceBefore.length + sentence.length + spaceAfter.length
      textarea.focus()
      textarea.setSelectionRange(newPos, newPos)
    }, 0)
  }

  const handlePolishSelection = async () => {
    const textarea = textareaRef.current
    if (!textarea) return

    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    
    if (start === end) {
      alert('Please select some text to polish')
      return
    }

    const selectedText = editedReport.substring(start, end)
    setSelectedText(selectedText)
    setPolishing(true)

    // Save current state to undo stack
    setUndoStack(prev => [...prev, editedReport])
    setShowUndoButton(true)

    // Save scroll position
    const scrollTop = textarea.scrollTop

    // Preserve leading/trailing whitespace
    const leadingSpace = selectedText.match(/^\s*/)[0]
    const trailingSpace = selectedText.match(/\s*$/)[0]
    const trimmedText = selectedText.trim()

    try {
      // Polish only the trimmed text
      const result = await polishText(id, trimmedText, editedReport)
      let polished = result.polished_text

      // Strip surrounding quotes if AI added them
      polished = polished.replace(/^["']|["']$/g, '')

      // Add back the original leading/trailing spaces
      const polishedWithSpaces = leadingSpace + polished + trailingSpace

      // Replace selected text with polished version
      const newText = editedReport.substring(0, start) + polishedWithSpaces + editedReport.substring(end)
      setEditedReport(newText)

      // Restore scroll position and cursor
      setTimeout(() => {
        textarea.scrollTop = scrollTop
        const newPos = start + polishedWithSpaces.length
        textarea.setSelectionRange(newPos, newPos)
      }, 0)
    } catch (error) {
      console.error('Error polishing text:', error)
      alert('Error polishing text. Please try again.')
    } finally {
      setPolishing(false)
      setSelectedText('')
    }
  }

  const handleUndo = () => {
    if (undoStack.length === 0) return
    
    // Get the last saved state
    const previousState = undoStack[undoStack.length - 1]
    
    // Remove it from the stack
    setUndoStack(prev => prev.slice(0, -1))
    
    // Restore the previous state
    setEditedReport(previousState)
    
    // Hide undo button if no more undo states
    if (undoStack.length === 1) {
      setShowUndoButton(false)
    }
  }

  const handleAddContact = async () => {
    setAddingContact(true)
    try {
      const result = await addContactToReport(id)
      setEditedReport(result.report_text)
      if (result.message) {
        alert(result.message)
      } else {
        alert('Contact information added to report!')
      }
    } catch (error) {
      console.error('Error adding contact info:', error)
      alert('Error adding contact information. Please check your settings to ensure tutor name is configured.')
    } finally {
      setAddingContact(false)
    }
  }




  const handleCopy = () => {
    navigator.clipboard.writeText(editedReport)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    const blob = new Blob([editedReport], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${report.student_name}_Report_${new Date(report.session_date).toLocaleDateString()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // Ask AI handler
  const handleAskAI = async () => {
    if (!currentAIQuestion.trim()) return
    
    const newQuestion = { question: currentAIQuestion, answer: null }
    setAiChatHistory([...aiChatHistory, newQuestion])
    setCurrentAIQuestion('')
    setLoadingAIAnswer(true)
    
    try {
      const response = await askAIAboutText(id, selectedTextForAI, currentAIQuestion, editedReport, aiChatHistory)
      setAiChatHistory(prev => {
        const updated = [...prev]
        updated[updated.length - 1].answer = response.answer
        return updated
      })
    } catch (error) {
      console.error('Error asking AI:', error)
      setAiChatHistory(prev => {
        const updated = [...prev]
        updated[updated.length - 1].answer = "Sorry, I couldn't process that question. Please try again."
        return updated
      })
    } finally {
      setLoadingAIAnswer(false)
    }
  }

  // Synonym handler
  const handleLoadSynonyms = async (word, context, position) => {
    setLoadingSynonyms(true)
    try {
      const response = await getSynonyms(id, word, context)
      setSynonyms(response.synonyms || [])
      setShowSynonyms(true)
    } catch (error) {
      console.error('Error loading synonyms:', error)
      setSynonyms([])
    } finally {
      setLoadingSynonyms(false)
    }
  }

  const handleReplaceSynonym = (synonym) => {
    const before = editedReport.substring(0, wordPosition.start)
    const after = editedReport.substring(wordPosition.end)
    const newReport = before + synonym + after
    setEditedReport(newReport)
    setShowSynonyms(false)
    setSynonyms([])
    setSelectedWord('')
  }

  if (loading) {
    return <div className="text-center py-12">Loading report...</div>
  }

  if (!report) {
    return <div className="text-center py-12">Report not found</div>
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/reports')}
          className="flex items-center text-sage-600 hover:text-sage-700 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Reports
        </button>
        <div>
          <h2 className="text-2xl font-bold text-sage-800">
            Edit Report: {report.student_name}
          </h2>
          <p className="text-sage-600 mt-1">
            Session: {new Date(report.session_date).toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </p>
        </div>
      </div>

      {/* Key Info Bar - Top */}
      <div className="bg-white rounded-lg shadow-sm border border-sage-200 p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          {/* Student */}
              <div>
            <label className="block text-sm font-medium text-sage-700 mb-1">
              Student
            </label>
            <select
              value={selectedStudentId}
              onChange={(e) => setSelectedStudentId(e.target.value)}
              className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
            >
              <option value="">Select a student...</option>
              {students.map((student) => (
                <option key={student.id} value={student.id}>
                  {student.name} {student.subject ? `- ${student.subject}` : ''}
                </option>
              ))}
            </select>
              </div>

          {/* Date */}
              <div>
            <label className="block text-sm font-medium text-sage-700 mb-1">
              Session Date
            </label>
            <input
              type="date"
              value={sessionDate}
              onChange={(e) => setSessionDate(e.target.value)}
              className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
            />
              </div>

          {/* Status */}
                <div>
            <label className="block text-sm font-medium text-sage-700 mb-1">
              Status
            </label>
            <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setStatus('draft')}
                className={`flex-1 px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                    status === 'draft'
                      ? 'bg-yellow-100 text-yellow-800 border-2 border-yellow-400'
                    : 'bg-sage-50 text-sage-700 border border-sage-300 hover:border-sage-400'
                  }`}
                >
                  📝 Draft
                </button>
                <button
                  type="button"
                  onClick={() => setStatus('sent')}
                className={`flex-1 px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                    status === 'sent'
                      ? 'bg-green-100 text-green-800 border-2 border-green-400'
                    : 'bg-sage-50 text-sage-700 border border-sage-300 hover:border-sage-400'
                  }`}
                >
                  ✅ Sent
                </button>
            </div>
          </div>

          {/* Use for Training Toggle */}
          <div className="flex items-center">
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={useForTraining}
                onChange={(e) => setUseForTraining(e.target.checked)}
                className="w-5 h-5 text-blue-600 border-sage-300 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm font-medium text-sage-700">
                🎓 Use for AI Training
              </span>
            </label>
              </div>
            </div>
        </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Report Editor - Left (Wider) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white rounded-lg shadow-sm border border-sage-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <h3 className="text-lg font-semibold text-sage-800">Final Report</h3>
                {/* Auto-save status indicator */}
                {autoSaveStatus === 'saving' && (
                  <span className="text-xs text-gray-500 italic">Saving...</span>
                )}
                {autoSaveStatus === 'saved' && (
                  <span className="text-xs text-green-600 italic">✓ Saved</span>
                )}
                {autoSaveStatus === 'error' && (
                  <span className="text-xs text-red-600 italic">⚠ Save failed</span>
                )}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={handleCopy}
                  className="p-2 text-sage-600 hover:bg-sage-50 rounded transition-colors"
                  title="Copy to clipboard"
                >
                  {copied ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : (
                    <Copy className="w-5 h-5" />
                  )}
                </button>
                <button
                  onClick={handleDownload}
                  className="p-2 text-sage-600 hover:bg-sage-50 rounded transition-colors"
                  title="Download as text file"
                >
                  <Download className="w-5 h-5" />
                </button>
              </div>
            </div>

            <textarea
              ref={textareaRef}
              value={editedReport}
              onChange={(e) => setEditedReport(e.target.value)}
              onSelect={(e) => {
                const start = e.target.selectionStart
                const end = e.target.selectionEnd
                const selected = editedReport.substring(start, end)
                
                if (start !== end) {
                  setSelectedText(selected)
                  setSelectedTextForAI(selected)
                  
                  // Check if it's a single word (for synonyms)
                  const wordPattern = /^[\w'-]+$/
                  const cleanSelected = selected.trim().replace(/^[^\w]+|[^\w]+$/g, '')
                  
                  if (cleanSelected && wordPattern.test(cleanSelected) && cleanSelected.length > 1) {
                    // Single word - show synonyms
                    setSelectedWord(cleanSelected)
                    setWordPosition({ start, end })
                    handleLoadSynonyms(cleanSelected, editedReport, start)
                  } else {
                    // Multiple words - hide synonyms
                    setSelectedWord('')
                    setSynonyms([])
                    setShowSynonyms(false)
                  }
                } else {
                  setSelectedText('')
                  setSelectedWord('')
                  setSynonyms([])
                  setShowSynonyms(false)
                }
              }}
              rows={25}
              className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500 font-mono text-sm"
              placeholder="Edit your report here..."
            />

            {/* Ask AI About This Button */}
            {selectedTextForAI && (
              <button
                onClick={() => setShowAskAI(true)}
                className="mt-3 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                Ask AI About This
              </button>
            )}

            {/* Synonym Popup */}
            {showSynonyms && synonyms.length > 0 && (
              <div className="mt-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-semibold text-blue-900">Synonyms for "{selectedWord}":</p>
                  <button
                    onClick={() => {
                      setShowSynonyms(false)
                      setSynonyms([])
                    }}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {synonyms.map((synonym, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleReplaceSynonym(synonym)}
                      className="px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-800 rounded-md text-sm transition-colors"
                    >
                      {synonym}
                    </button>
                  ))}
                </div>
              </div>
            )}
            <div className="mt-4 space-y-3">
              {selectedText && (
                <div className="flex justify-end gap-2 animate-fade-in">
                  <button
                    onClick={handlePolishSelection}
                    disabled={polishing}
                    className="px-5 py-2 bg-blue-50 text-blue-700 text-sm font-medium rounded-lg hover:bg-blue-100 transition-smooth hover-lift shadow-sm disabled:opacity-50 flex items-center border-2 border-blue-200"
                  >
                    <Wand2 className="w-4 h-4 mr-2" />
                    {polishing ? 'Polishing...' : 'Polish Selection'}
                  </button>
              </div>
              )}
              
              {showUndoButton && undoStack.length > 0 && (
                <div className="flex justify-end animate-fade-in">
                  <button
                    onClick={handleUndo}
                    disabled={polishing || saving}
                    className="px-5 py-2 bg-amber-50 text-amber-700 text-sm font-medium rounded-lg hover:bg-amber-100 transition-smooth hover-lift shadow-sm disabled:opacity-50 flex items-center border-2 border-amber-200"
                    title={`Undo last ${undoStack.length} polish${undoStack.length > 1 ? 'es' : ''}`}
                  >
                    <Undo2 className="w-4 h-4 mr-2" />
                    Undo Polish ({undoStack.length})
                  </button>
              </div>
              )}
              
              {/* AI Action Buttons */}
              <div className="grid grid-cols-3 gap-3">
                <button
                  onClick={handleFixGrammar}
                  disabled={fixingGrammar || saving || regenerating}
                  className="px-6 py-2.5 bg-purple-50 text-purple-700 font-medium rounded-xl hover:bg-purple-100 transition-smooth hover-lift shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center border-2 border-purple-200"
                  title="Fix grammar and spelling while keeping your exact wording"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  {fixingGrammar ? 'Fixing...' : 'Fix Grammar'}
                </button>

                <button
                  onClick={handlePolishFullReport}
                  disabled={loadingPolish || saving || regenerating}
                  className="px-6 py-2.5 bg-amber-50 text-amber-700 font-medium rounded-xl hover:bg-amber-100 transition-smooth hover-lift shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center border-2 border-amber-200"
                  title="Clean up and polish your report with GPT-4o (keeps your wording, improves clarity)"
                >
                  <Wand2 className="w-4 h-4 mr-2" />
                  {loadingPolish ? 'Polishing...' : 'Polish Report'}
                </button>
                
                <button
                  onClick={() => setShowRegenerateModal(true)}
                  disabled={regenerating || saving || fixingGrammar}
                  className="px-6 py-2.5 bg-blue-50 text-blue-700 font-medium rounded-xl hover:bg-blue-100 transition-smooth hover-lift shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center border-2 border-blue-200"
                  title="Generate a completely new report from scratch"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${regenerating ? 'animate-spin' : ''}`} />
                  {regenerating ? 'Regenerating...' : 'Regenerate Report'}
                </button>

                <button
                  onClick={handleAddContact}
                  disabled={addingContact || saving}
                  className="px-6 py-2.5 bg-teal-50 text-teal-700 font-medium rounded-xl hover:bg-teal-100 transition-smooth hover-lift shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center border-2 border-teal-200"
                  title="Add your contact information to the report"
                >
                  <Contact className="w-4 h-4 mr-2" />
                  {addingContact ? 'Adding...' : 'Add Contact Info'}
                </button>
              </div>
              
              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="flex-1 px-6 py-3 bg-sage-100 text-sage-700 font-semibold rounded-xl hover:bg-sage-200 transition-smooth hover-lift shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  onClick={handleFinalize}
                  disabled={saving}
                  className="flex-1 px-6 py-3 bg-green-600 text-white font-semibold rounded-xl hover:bg-green-700 transition-smooth hover-lift shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  title="Save and mark as approved - will be used for AI training"
                >
                  <Check className="w-4 h-4 mr-2" />
                  {saving ? 'Finalizing...' : 'Finalize & Use for Training'}
                </button>
              </div>

              {/* Delete Button */}
              <div className="pt-3 border-t border-sage-200">
                <button
                  onClick={handleDelete}
                  className="w-full px-6 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors flex items-center justify-center"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete Report
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Right Sidebar - AI Tools & Reference */}
        <div className="lg:col-span-1 space-y-4">
          {/* AI Suggestions */}
          <div className="bg-white rounded-lg shadow-sm border border-sage-200 p-4">
            <button
              onClick={() => setShowSuggestions(!showSuggestions)}
              className="w-full flex items-center justify-between mb-3 text-sage-800 font-semibold"
            >
              <span className="flex items-center">
                <Sparkles className="w-4 h-4 mr-2" />
                AI Suggestions
              </span>
              {showSuggestions ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showSuggestions && (
              <>
                <p className="text-xs text-sage-600 mb-3">
                  💡 Click any sentence to insert. Move cursor and refresh for context-specific suggestions.
                </p>

                {loadingSuggestions ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sage-600 mx-auto mb-2"></div>
                    <p className="text-xs text-sage-500">Generating suggestions...</p>
                  </div>
                ) : suggestions.length > 0 ? (
                  <div className="space-y-2 mb-3">
                    {suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => insertSuggestion(suggestion)}
                        className="w-full text-left p-3 bg-sage-50 hover:bg-sage-100 border border-sage-200 rounded-lg transition-colors text-sm text-sage-700"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-sage-500 italic py-4 text-center">
                    No suggestions yet
                  </p>
                )}

                <button
                  onClick={loadSuggestions}
                  disabled={loadingSuggestions}
                  className="w-full px-4 py-2 bg-sage-600 text-white text-sm rounded-lg hover:bg-sage-700 transition-colors disabled:opacity-50 flex items-center justify-center"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  {loadingSuggestions ? 'Generating...' : 'Generate for Cursor Position'}
                </button>

                <div className="mt-3 pt-3 border-t border-sage-200">
                  <p className="text-xs text-sage-500 mb-2">
                    💡 <strong>How it works:</strong> Place cursor where you want to add text, click "Generate" for 4 context-specific sentences. Move cursor to different spots for different suggestions.
                  </p>
                  <p className="text-xs text-sage-500">
                    ✨ <strong>Polish:</strong> Highlight any text and click "Polish Selection" to improve it.
                  </p>
                </div>
              </>
            )}
          </div>

          {/* Reminders for Next Session - Editable */}
          <div className="bg-white rounded-lg shadow-sm border border-sage-200 p-4">
            <h3 className="text-sm font-semibold text-sage-800 mb-3">Reminders for Next Session</h3>
            <textarea
              value={nextSessionNotes}
              onChange={(e) => {
                let newValue = e.target.value
                // Auto-convert "- " to "• "
                if (newValue.endsWith('- ')) {
                  newValue = newValue.slice(0, -2) + '• '
                }
                setNextSessionNotes(newValue)
              }}
              className="w-full px-3 py-2 text-xs border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
              rows={3}
              placeholder="e.g., Review for Friday's test, bring homework packet, focus on quadratic formula"
            />
            <button
              onClick={handleSave}
              disabled={saving}
              className="mt-3 px-4 py-1.5 bg-sage-600 text-white text-xs rounded-lg hover:bg-sage-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              <Save className="w-3 h-3 mr-1.5" />
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>


          {/* Previous Report Viewer */}
          {previousReport && (
            <div className="bg-white rounded-lg shadow-sm border border-sage-200 p-4">
              <button
                onClick={() => setShowPreviousReport(!showPreviousReport)}
                className="w-full flex items-center justify-between mb-3 text-sage-800 font-semibold hover:text-sage-900"
              >
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Previous Report ({new Date(previousReport.session_date).toLocaleDateString()})
                </span>
                {showPreviousReport ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>

              {showPreviousReport && (
                <div className="mt-3 max-h-96 overflow-y-auto">
                  <div className="text-xs text-sage-700 bg-sage-50 p-3 rounded border border-sage-200 whitespace-pre-wrap leading-relaxed">
                    {previousReport.final_report || previousReport.ai_generated_report}
                  </div>
                  <p className="mt-2 text-[10px] text-gray-500">
                    Compare with your previous report to maintain consistency
                  </p>
                </div>
              )}
              
              {loadingPreviousReport && (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-sage-600 mx-auto"></div>
                  <p className="text-xs text-sage-500 mt-2">Loading previous report...</p>
                </div>
              )}
            </div>
          )}

          {/* Session Notes */}
          <div className="bg-white rounded-lg shadow-sm border border-sage-200 p-4">
            <h3 className="text-sm font-semibold text-sage-800 mb-3">Session Notes</h3>
            
            <div className="space-y-2">
              {report.topics_covered && (
                <div>
                  <p className="text-xs font-medium text-sage-700 mb-1">Topics Covered</p>
                  <p className="text-xs text-sage-600 bg-sage-50 p-2 rounded border border-sage-200">
                    {report.topics_covered}
                  </p>
                </div>
              )}

              {report.activities && (
                <div>
                  <p className="text-xs font-medium text-sage-700 mb-1">Activities</p>
                  <p className="text-xs text-sage-600 bg-sage-50 p-2 rounded border border-sage-200 whitespace-pre-wrap">
                    {report.activities}
                  </p>
                </div>
              )}

              {report.notes && (
                <div>
                  <p className="text-xs font-medium text-sage-700 mb-1">Notes</p>
                  <p className="text-xs text-sage-600 bg-sage-50 p-2 rounded border border-sage-200 whitespace-pre-wrap">
                    {report.notes}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* AI Generated Version */}
          {report.ai_generated_report && report.ai_generated_report !== editedReport && (
            <div className="bg-white rounded-lg shadow-sm border border-sage-200 p-4">
              <h3 className="text-sm font-semibold text-sage-800 mb-3">
                Original AI Version
              </h3>
              <div className="text-xs text-sage-700 bg-sage-50 p-3 rounded border border-sage-200 max-h-64 overflow-y-auto whitespace-pre-wrap">
                {report.ai_generated_report}
              </div>
              <button
                onClick={() => setEditedReport(report.ai_generated_report)}
                className="mt-2 text-xs text-sage-600 hover:text-sage-700 font-medium"
              >
                Restore AI version
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Regenerate Report Modal */}
      {showRegenerateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" onClick={() => setShowRegenerateModal(false)}>
          <div 
            className="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-sage-800 mb-2 flex items-center gap-2">
                <RefreshCw className="w-5 h-5 text-blue-600" />
                Regenerate Report
              </h3>
              <p className="text-sm text-gray-600">
                This will generate a completely new report from scratch. Your current edits will be replaced.
              </p>
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-purple-700 mb-2">
                AI Writing Instructions (Optional)
              </label>
              <textarea
                value={regenerateInstructions}
                onChange={(e) => setRegenerateInstructions(e.target.value)}
                className="w-full px-3 py-2 border border-purple-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                rows={3}
                placeholder="e.g., 'Make it more concise', 'Focus on her problem-solving skills'"
              />
              <p className="text-xs text-purple-500 mt-1">
                Tell the AI how you'd like the new report to be written.
              </p>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={() => setShowRegenerateModal(false)}
                className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                onClick={() => handleRegenerate(regenerateInstructions)}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Regenerate
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Polish Changes Sidebar */}
      {showPolishChanges && (
        <div className="fixed top-0 right-0 h-full w-96 bg-white shadow-2xl z-40 flex flex-col border-l border-gray-200">
          {/* Header */}
          <div className="bg-gradient-to-r from-amber-500 to-orange-500 text-white p-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Wand2 className="w-5 h-5" />
              <h3 className="font-semibold">Polish Changes</h3>
            </div>
            <button
              onClick={() => setShowPolishChanges(false)}
              className="text-white hover:text-amber-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Undo/Accept Buttons */}
          <div className="p-4 bg-amber-50 border-b border-amber-200 flex gap-2">
            <button
              onClick={handleUndoPolish}
              disabled={!originalBeforePolish}
              className="flex-1 px-4 py-2 bg-white text-amber-700 font-medium rounded-lg hover:bg-amber-100 transition-colors border-2 border-amber-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              <Undo2 className="w-4 h-4" />
              Undo Polish
            </button>
            <button
              onClick={handleAcceptPolish}
              className="flex-1 px-4 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
            >
              <Check className="w-4 h-4" />
              Accept
            </button>
          </div>

          {/* Changes List */}
          <div className="flex-1 overflow-y-auto p-4">
            <div className="mb-3">
              <p className="text-sm font-semibold text-amber-800">
                {polishChanges.length} {polishChanges.length === 1 ? 'change' : 'changes'} made
              </p>
              <p className="text-xs text-gray-600 mt-1">
                Your report has been polished with GPT-4o. Review the changes and accept or undo.
              </p>
            </div>

            <div className="space-y-3">
              {polishChanges.map((change, idx) => (
                <div key={idx} className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                  <div className="flex items-start gap-2">
                    <div className="flex-shrink-0 w-6 h-6 bg-amber-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                      {idx + 1}
                    </div>
                    <div className="flex-1 text-sm text-gray-700">
                      {change.description}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {polishChanges.length === 0 && (
              <div className="text-center text-gray-500 text-sm mt-8">
                <Wand2 className="w-12 h-12 mx-auto mb-3 text-amber-300" />
                <p>No specific changes listed</p>
                <p className="text-xs mt-2">The report was polished successfully</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Ask AI Sidebar - ChatGPT Style */}
      {showAskAI && (
        <div className="fixed right-0 top-0 h-full w-[440px] bg-white shadow-2xl border-l border-gray-200 z-50 flex flex-col">
          {/* Header - Clean like ChatGPT */}
          <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-gray-700" />
                <h3 className="font-semibold text-gray-900">Chat</h3>
              </div>
              <span className="px-2 py-0.5 bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-[10px] font-semibold rounded-full">
                GPT-4
              </span>
            </div>
            <div className="flex items-center gap-2">
              {aiChatHistory.length > 0 && (
                <button
                  onClick={() => setAiChatHistory([])}
                  className="text-xs text-gray-500 hover:text-gray-700 font-medium"
                >
                  New chat
                </button>
              )}
              <button
                onClick={() => setShowAskAI(false)}
                className="text-gray-500 hover:text-gray-700 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Chat Messages - ChatGPT Style */}
          <div className="flex-1 overflow-y-auto">
            {aiChatHistory.length === 0 && !loadingAIAnswer && (
              <div className="flex flex-col items-center justify-center h-full px-8 text-center">
                <div className="w-14 h-14 rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 flex items-center justify-center mb-4">
                  <Sparkles className="w-7 h-7 text-white" />
                </div>
                <p className="text-lg font-medium text-gray-900 mb-2">Ask me about your report</p>
                <p className="text-sm text-gray-500 max-w-sm">
                  I can help you improve your writing, check grammar, suggest rewording, or answer any questions.
                </p>
                <div className="mt-6 space-y-2 w-full max-w-sm">
                  <button
                    onClick={() => setCurrentAIQuestion("Does this sound professional?")}
                    className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm text-gray-700 border border-gray-200 transition-colors"
                  >
                    Does this sound professional?
                  </button>
                  <button
                    onClick={() => setCurrentAIQuestion("How can I make this clearer?")}
                    className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm text-gray-700 border border-gray-200 transition-colors"
                  >
                    How can I make this clearer?
                  </button>
                  <button
                    onClick={() => setCurrentAIQuestion("Is the tone appropriate for parents?")}
                    className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm text-gray-700 border border-gray-200 transition-colors"
                  >
                    Is the tone appropriate for parents?
                  </button>
                </div>
              </div>
            )}
            
            {/* Message Thread */}
            {aiChatHistory.length > 0 && (
              <div className="py-6">
                {aiChatHistory.map((chat, idx) => (
                  <div key={idx}>
                    {/* User Message */}
                    <div className="px-6 py-6 bg-white">
                      <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-full bg-gray-900 flex items-center justify-center flex-shrink-0 text-white text-xs font-semibold">
                          E
                        </div>
                        <div className="flex-1 pt-1">
                          <p className="text-[15px] text-gray-900 leading-relaxed">{chat.question}</p>
                        </div>
                      </div>
                    </div>
                    
                    {/* AI Response */}
                    {chat.answer && (
                      <div className="px-6 py-6 bg-gray-50">
                        <div className="flex gap-3">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 flex items-center justify-center flex-shrink-0">
                            <Sparkles className="w-4 h-4 text-white" />
                          </div>
                          <div className="flex-1 pt-1">
                            <p className="text-[15px] text-gray-900 leading-relaxed whitespace-pre-wrap">{chat.answer}</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                
                {/* Loading State */}
                {loadingAIAnswer && aiChatHistory[aiChatHistory.length - 1]?.answer === null && (
                  <div className="px-6 py-6 bg-gray-50">
                    <div className="flex gap-3">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 flex items-center justify-center flex-shrink-0">
                        <Sparkles className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex-1 pt-1">
                        <div className="flex items-center gap-2">
                          <div className="flex gap-1">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
            
            <div ref={aiChatEndRef} />
          </div>

          {/* Input Area - ChatGPT Style */}
          <div className="p-4 bg-white border-t border-gray-200">
            <div className="relative">
              <input
                type="text"
                value={currentAIQuestion}
                onChange={(e) => setCurrentAIQuestion(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleAskAI()}
                placeholder="Message ChatGPT..."
                className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl focus:ring-2 focus:ring-gray-900 focus:border-transparent text-[15px] shadow-sm resize-none"
                style={{ minHeight: '48px' }}
              />
              <button
                onClick={handleAskAI}
                disabled={!currentAIQuestion.trim() || loadingAIAnswer}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-gray-900"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
            <p className="mt-2 text-[11px] text-center text-gray-400">
              Powered by GPT-4 • Full conversation context
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default EditReport

