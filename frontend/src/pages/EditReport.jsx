import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Save, Copy, Download, CheckCircle, Check, Trash2, Sparkles, RefreshCw, ChevronDown, ChevronUp, Wand2, Undo2, Contact } from 'lucide-react'
import { getReport, updateReport, deleteReport, getStudents, fixReportGrammar, suggestSentences, polishText, generateReport, addContactToReport, suggestOpeningClosing, suggestSynonyms, reviewReportPhrases } from '../services/api'

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
  const [showOpeningTool, setShowOpeningTool] = useState(false)
  const [showClosingTool, setShowClosingTool] = useState(false)
  const [openingSuggestions, setOpeningSuggestions] = useState([])
  const [closingSuggestions, setClosingSuggestions] = useState([])
  const [loadingOpeningSuggestions, setLoadingOpeningSuggestions] = useState(false)
  const [loadingClosingSuggestions, setLoadingClosingSuggestions] = useState(false)
  const [currentOpening, setCurrentOpening] = useState('')
  const [currentClosing, setCurrentClosing] = useState('')
  const [previousOpening, setPreviousOpening] = useState('')
  const [previousClosing, setPreviousClosing] = useState('')
  const [originalOpening, setOriginalOpening] = useState('')
  const [originalClosing, setOriginalClosing] = useState('')
  const [hasChangedOpening, setHasChangedOpening] = useState(false)
  const [hasChangedClosing, setHasChangedClosing] = useState(false)
  const [lastSavedContent, setLastSavedContent] = useState('')
  const [autoSaveStatus, setAutoSaveStatus] = useState('') // 'saving', 'saved', 'error'
  const [selectedWord, setSelectedWord] = useState('')
  const [synonyms, setSynonyms] = useState([])
  const [loadingSynonyms, setLoadingSynonyms] = useState(false)
  const [showSynonyms, setShowSynonyms] = useState(false)
  const [wordPosition, setWordPosition] = useState({ start: 0, end: 0 })
  const [reviewSuggestions, setReviewSuggestions] = useState([])
  const [reviewing, setReviewing] = useState(false)
  const [activeSuggestion, setActiveSuggestion] = useState(null)
  const [editedSuggestion, setEditedSuggestion] = useState('') // For editing suggestions in popup
  const [textareaHeight, setTextareaHeight] = useState(0) // Height of textarea for indicator positioning
  const textareaRef = useRef(null)
  const indicatorBarRef = useRef(null)
  const autoSaveTimeoutRef = useRef(null)
  const isInitialLoadRef = useRef(true)

  useEffect(() => {
    loadReport()
    loadStudents()
    
    // Load from localStorage if available (backup)
    const savedContent = localStorage.getItem(`report_${id}_backup`)
    if (savedContent) {
      try {
        const parsed = JSON.parse(savedContent)
        // Only use if it's newer than 1 hour old
        if (Date.now() - parsed.timestamp < 3600000) {
          setEditedReport(parsed.content)
          console.log('Restored from localStorage backup')
        }
      } catch (e) {
        console.error('Error parsing localStorage backup:', e)
      }
    }
    
    // Cleanup on unmount
    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current)
      }
      // Save to localStorage as backup before leaving
      if (editedReport && editedReport !== lastSavedContent) {
        localStorage.setItem(`report_${id}_backup`, JSON.stringify({
          content: editedReport,
          timestamp: Date.now()
        }))
      }
    }
  }, [id])

  useEffect(() => {
    // Load suggestions when report is loaded
    if (report && editedReport) {
      loadSuggestions()
    }
  }, [report])

  // Auto-save effect - debounced
  useEffect(() => {
    // Skip auto-save on initial load
    if (isInitialLoadRef.current) {
      isInitialLoadRef.current = false
      setLastSavedContent(editedReport)
      return
    }

    // Skip if content hasn't changed
    if (editedReport === lastSavedContent) {
      return
    }

    // Clear existing timeout
    if (autoSaveTimeoutRef.current) {
      clearTimeout(autoSaveTimeoutRef.current)
    }

    // Save to localStorage immediately as backup
    localStorage.setItem(`report_${id}_backup`, JSON.stringify({
      content: editedReport,
      timestamp: Date.now()
    }))

    // Set debounced auto-save (2 seconds after user stops typing)
    autoSaveTimeoutRef.current = setTimeout(async () => {
      if (!report || editedReport === lastSavedContent) {
        return
      }

      setAutoSaveStatus('saving')
      try {
        await updateReport(id, {
          final_report: editedReport,
          status: status,
          use_for_training: useForTraining,
          student_id: selectedStudentId,
          session_date: sessionDate,
          next_session_notes: nextSessionNotes
        })
        setLastSavedContent(editedReport)
        setAutoSaveStatus('saved')
        
        // Clear localStorage backup after successful save
        localStorage.removeItem(`report_${id}_backup`)
        
        // Clear status message after 3 seconds
        setTimeout(() => setAutoSaveStatus(''), 3000)
      } catch (error) {
        console.error('Error auto-saving report:', error)
        setAutoSaveStatus('error')
        setTimeout(() => setAutoSaveStatus(''), 5000)
      }
    }, 2000)

    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current)
      }
    }
  }, [editedReport, id, report, status, useForTraining, selectedStudentId, sessionDate, nextSessionNotes, lastSavedContent])

  // Warn before leaving with unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (editedReport !== lastSavedContent && editedReport.trim() !== '') {
        e.preventDefault()
        e.returnValue = 'You have unsaved changes. Are you sure you want to leave?'
        return e.returnValue
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
    }
  }, [editedReport, lastSavedContent])

  // Update textarea height when content changes
  useEffect(() => {
    if (textareaRef.current) {
      setTextareaHeight(textareaRef.current.scrollHeight)
    }
  }, [editedReport, reviewSuggestions.length])


  // Helper function to get exact pixel position of text in textarea
  const getTextPosition = (textarea, charIndex) => {
    if (!textarea || charIndex < 0) return { top: 0, left: 0 }
    
    // Create a mirror div with same styling to measure exact position
    const mirror = document.createElement('div')
    const computedStyle = window.getComputedStyle(textarea)
    
    // Copy all relevant styles from textarea
    const stylesToCopy = [
      'fontFamily', 'fontSize', 'fontWeight', 'lineHeight',
      'paddingTop', 'paddingBottom', 'paddingLeft', 'paddingRight',
      'borderTopWidth', 'borderBottomWidth', 'borderLeftWidth', 'borderRightWidth',
      'boxSizing', 'whiteSpace', 'wordWrap', 'wordBreak', 'letterSpacing'
    ]
    
    stylesToCopy.forEach(prop => {
      mirror.style[prop] = computedStyle[prop]
    })
    
    // Set up mirror for measurement
    mirror.style.position = 'absolute'
    mirror.style.visibility = 'hidden'
    mirror.style.top = '-9999px'
    mirror.style.left = '-9999px'
    mirror.style.width = `${textarea.clientWidth}px`
    mirror.style.whiteSpace = 'pre-wrap'
    mirror.style.wordWrap = 'break-word'
    mirror.style.overflow = 'hidden'
    
    // Set text content up to the character index
    const textBefore = editedReport.substring(0, charIndex)
    mirror.textContent = textBefore
    
    document.body.appendChild(mirror)
    
    // Get the height of the text before the character
    const height = mirror.offsetHeight
    const lineHeight = parseFloat(computedStyle.lineHeight) || 20
    const paddingTop = parseFloat(computedStyle.paddingTop) || 8
    
    // Calculate position at center of the line
    // The height gives us the total pixel height, so we divide by line height to get line number
    const lineNumber = Math.floor((height - paddingTop) / lineHeight)
    const topPosition = paddingTop + (lineNumber * lineHeight) + (lineHeight / 2)
    
    document.body.removeChild(mirror)
    
    return {
      top: topPosition,
      left: 0
    }
  }

  // Sync indicator bar scroll with textarea
  useEffect(() => {
    const textarea = textareaRef.current
    const indicatorBar = indicatorBarRef.current
    
    if (!textarea || !indicatorBar) return
    
    const syncScroll = () => {
      indicatorBar.scrollTop = textarea.scrollTop
    }
    
    // Initial sync
    syncScroll()
    
    textarea.addEventListener('scroll', syncScroll)
    return () => {
      textarea.removeEventListener('scroll', syncScroll)
    }
  }, [reviewSuggestions.length, textareaHeight])

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
      
      // Always prioritize final_report if it exists (user's edits)
      // Only fall back to ai_generated_report if final_report is empty
      const contentToLoad = data.final_report || data.ai_generated_report || ''
      setEditedReport(contentToLoad)
      setLastSavedContent(contentToLoad)
      
      setStatus(data.status || 'draft')
      setUseForTraining(data.use_for_training || false)
      setSelectedStudentId(data.student_id || '')
      setSessionDate(data.session_date ? data.session_date.split('T')[0] : '')
      setNextSessionNotes(data.next_session_notes || '')
      
      // Clear localStorage backup after successful load
      localStorage.removeItem(`report_${id}_backup`)
    } catch (error) {
      console.error('Error loading report:', error)
      alert('Error loading report')
      navigate('/reports')
    } finally {
      setLoading(false)
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
      setLastSavedContent(editedReport)
      setAutoSaveStatus('saved')
      
      // Clear localStorage backup after successful save
      localStorage.removeItem(`report_${id}_backup`)
      
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
      setLastSavedContent(editedReport)
      setStatus('sent')
      setUseForTraining(true)
      
      // Clear localStorage backup after successful finalize
      localStorage.removeItem(`report_${id}_backup`)
      
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

  const handleRegenerate = async () => {
    if (!window.confirm('This will generate a completely new report from scratch. Your current edits will be replaced. Continue?')) {
      return
    }
    
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
        include_contact: false  // User can manually add this if needed
      })
      
      // Update the edited report with the new AI-generated content
      const newContent = regeneratedReport.ai_generated_report
      setEditedReport(newContent)
      // Note: Don't update lastSavedContent here - let auto-save handle it
      alert('Report regenerated! Review the new version and save when ready.')
    } catch (error) {
      console.error('Error regenerating report:', error)
      alert('Error regenerating report. Please check your AI configuration and try again.')
    } finally {
      setRegenerating(false)
    }
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

  const handleLoadSynonyms = async (word, fullText, cursorPosition) => {
    if (!word || word.length < 2) {
      setSynonyms([])
      setShowSynonyms(false)
      return
    }
    
    setLoadingSynonyms(true)
    setShowSynonyms(true)
    
    try {
      // Get context around the word (100 chars before and after)
      const contextStart = Math.max(0, cursorPosition - 100)
      const contextEnd = Math.min(fullText.length, cursorPosition + word.length + 100)
      const context = fullText.substring(contextStart, contextEnd)
      
      const result = await suggestSynonyms(id, word, context)
      setSynonyms(result.synonyms || [])
    } catch (error) {
      console.error('Error loading synonyms:', error)
      setSynonyms([])
    } finally {
      setLoadingSynonyms(false)
    }
  }

  const handleReplaceWord = (synonym) => {
    const textarea = textareaRef.current
    if (!textarea || !selectedWord) return
    
    const { start, end } = wordPosition
    const textBefore = editedReport.substring(0, start)
    const textAfter = editedReport.substring(end)
    
    // Preserve any punctuation that was part of the selection
    const selectedWithPunct = editedReport.substring(start, end)
    const leadingPunct = selectedWithPunct.match(/^[^\w]+/)?.[0] || ''
    const trailingPunct = selectedWithPunct.match(/[^\w]+$/)?.[0] || ''
    
    const newText = textBefore + leadingPunct + synonym + trailingPunct + textAfter
    setEditedReport(newText)
    
    // Clear selection and synonyms
    setSelectedWord('')
    setSynonyms([])
    setShowSynonyms(false)
    setSelectedText('')
    
    // Set cursor after the replaced word
    setTimeout(() => {
      const newPos = start + leadingPunct.length + synonym.length + trailingPunct.length
      textarea.focus()
      textarea.setSelectionRange(newPos, newPos)
    }, 0)
  }

  const handleReviewReport = async () => {
    setReviewing(true)
    setReviewSuggestions([])
    setActiveSuggestion(null)
    
    try {
      const result = await reviewReportPhrases(id, editedReport)
      const suggestions = result.suggestions || []
      
      // Validate and log suggestions for debugging
      console.log('=== REVIEW SUGGESTIONS DEBUG ===')
      console.log('Report length:', editedReport.length)
      console.log('Number of suggestions:', suggestions.length)
      
      const validated = suggestions.map((s, idx) => {
        const textAtIndices = editedReport.substring(s.start_index, s.end_index)
        const originalLower = s.original.toLowerCase().trim()
        const textAtIndicesLower = textAtIndices.toLowerCase().trim()
        const matches = textAtIndicesLower.includes(originalLower.slice(0, Math.min(30, originalLower.length))) || 
                       originalLower.includes(textAtIndicesLower.slice(0, Math.min(30, textAtIndicesLower.length)))
        
        console.log(`Suggestion ${idx}:`, {
          original: s.original.substring(0, 50),
          start: s.start_index,
          end: s.end_index,
          textAtIndices: textAtIndices.substring(0, 50),
          matches: matches,
          length: textAtIndices.length
        })
        
        // Show context around the indices
        const contextStart = Math.max(0, s.start_index - 20)
        const contextEnd = Math.min(editedReport.length, s.end_index + 20)
        const context = editedReport.substring(contextStart, contextEnd)
        console.log(`  Context: "...${context}..."`)
        
        return s
      }).filter(s => {
        // Only keep suggestions where the text at indices makes sense
        const textAtIndices = editedReport.substring(s.start_index, s.end_index)
        const isValid = textAtIndices.length > 0 && s.start_index >= 0 && s.end_index <= editedReport.length
        if (!isValid) {
          console.warn(`  ❌ Invalid suggestion ${s.start_index}-${s.end_index}`)
        }
        return isValid
      })
      
      console.log(`Validated: ${validated.length} out of ${suggestions.length} suggestions`)
      console.log('=== END DEBUG ===')
      
      setReviewSuggestions(validated)
    } catch (error) {
      console.error('Error reviewing report:', error)
      alert('Error reviewing report. Please try again.')
    } finally {
      setReviewing(false)
    }
  }

  const handleApplySuggestion = (suggestion, chosenAlternative) => {
    const { start_index, end_index } = suggestion
    
    // Use the chosen alternative (which is the text from the textarea)
    const textToApply = chosenAlternative.trim()
    
    // Validate indices are within bounds
    if (start_index < 0 || end_index > editedReport.length || start_index >= end_index) {
      console.error('Invalid indices for suggestion:', { start_index, end_index, reportLength: editedReport.length })
      alert('Error: Could not apply suggestion. The text may have changed. Please try reviewing the report again.')
      return
    }
    
    // Get the actual text at these indices to verify
    const actualText = editedReport.substring(start_index, end_index)
    console.log('Applying suggestion:', {
      start_index,
      end_index,
      original: suggestion.original,
      actualText,
      textToApply
    })
    
    const textBefore = editedReport.substring(0, start_index)
    const textAfter = editedReport.substring(end_index)
    
    const newText = textBefore + textToApply + textAfter
    setEditedReport(newText)
    
    // Remove this suggestion from the list
    setReviewSuggestions(prev => prev.filter(s => s !== suggestion))
    setActiveSuggestion(null)
    setEditedSuggestion('')
    
    // Update indices for remaining suggestions
    const offset = textToApply.length - (end_index - start_index)
    setReviewSuggestions(prev => prev.map(s => {
      if (s.start_index > end_index) {
        return { ...s, start_index: s.start_index + offset, end_index: s.end_index + offset }
      }
      return s
    }))
  }

  const handleDismissSuggestion = (suggestion) => {
    setReviewSuggestions(prev => prev.filter(s => s !== suggestion))
    setActiveSuggestion(null)
  }

  const handleAddContact = async () => {
    setAddingContact(true)
    try {
      const result = await addContactToReport(id)
      setEditedReport(result.report_text)
      // Auto-save will handle saving this change
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

  const handleLoadOpeningClosingSuggestions = async (type) => {
    const isOpening = type === 'opening'
    const setLoading = isOpening ? setLoadingOpeningSuggestions : setLoadingClosingSuggestions
    const setSuggestions = isOpening ? setOpeningSuggestions : setClosingSuggestions
    
    setLoading(true)
    try {
      const result = await suggestOpeningClosing(id, type)
      setSuggestions(result.suggestions || [])
      if (isOpening) {
        setCurrentOpening(result.current_sentence || '')
        setPreviousOpening(result.previous_sentence || '')
      } else {
        setCurrentClosing(result.current_sentence || '')
        setPreviousClosing(result.previous_sentence || '')
      }
    } catch (error) {
      console.error(`Error loading ${type} suggestions:`, error)
      alert(`Error loading suggestions. Please try again.`)
    } finally {
      setLoading(false)
    }
  }

  const handleApplyOpeningClosing = (newSentence, type) => {
    const isOpening = type === 'opening'
    
    // Save original if this is the first change
    if (isOpening && !hasChangedOpening) {
      const firstPeriodIndex = editedReport.indexOf('.')
      if (firstPeriodIndex !== -1) {
        const original = editedReport.substring(0, firstPeriodIndex + 1).trim()
        setOriginalOpening(original)
        setHasChangedOpening(true)
      }
    } else if (!isOpening && !hasChangedClosing) {
      const sentences = editedReport.trim().split('.')
      if (sentences.length > 1) {
        const original = sentences[sentences.length - 2].trim() + '.'
        setOriginalClosing(original)
        setHasChangedClosing(true)
      }
    }
    
    // Find and replace the first or last sentence
    if (isOpening) {
      // Replace opening sentence
      const firstPeriodIndex = editedReport.indexOf('.')
      if (firstPeriodIndex !== -1) {
        const newReport = newSentence + editedReport.substring(firstPeriodIndex + 1)
        setEditedReport(newReport)
        setCurrentOpening(newSentence)
      }
    } else {
      // Replace closing sentence
      const sentences = editedReport.trim().split('.')
      if (sentences.length > 1) {
        sentences[sentences.length - 2] = ' ' + newSentence.replace(/\.$/, '')
        const newReport = sentences.join('.')
        setEditedReport(newReport)
        setCurrentClosing(newSentence)
      }
    }
  }

  const handleUndoOpeningClosing = (type) => {
    const isOpening = type === 'opening'
    
    if (isOpening && originalOpening) {
      // Restore original opening
      const firstPeriodIndex = editedReport.indexOf('.')
      if (firstPeriodIndex !== -1) {
        const newReport = originalOpening + editedReport.substring(firstPeriodIndex + 1)
        setEditedReport(newReport)
        setCurrentOpening(originalOpening)
        setHasChangedOpening(false)
        setOriginalOpening('')
      }
    } else if (!isOpening && originalClosing) {
      // Restore original closing
      const sentences = editedReport.trim().split('.')
      if (sentences.length > 1) {
        sentences[sentences.length - 2] = ' ' + originalClosing.replace(/\.$/, '')
        const newReport = sentences.join('.')
        setEditedReport(newReport)
        setCurrentClosing(originalClosing)
        setHasChangedClosing(false)
        setOriginalClosing('')
      }
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
                {autoSaveStatus === 'saving' && (
                  <span className="text-xs text-sage-600 flex items-center gap-1">
                    <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-sage-600"></div>
                    Auto-saving...
                  </span>
                )}
                {autoSaveStatus === 'saved' && (
                  <span className="text-xs text-green-600 flex items-center gap-1">
                    <CheckCircle className="w-3 h-3" />
                    Auto-saved
                  </span>
                )}
                {autoSaveStatus === 'error' && (
                  <span className="text-xs text-red-600 flex items-center gap-1">
                    Auto-save failed - click Save manually
                  </span>
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

            {/* Opening Sentence Tool */}
            <div className="mb-4 border border-indigo-200 rounded-lg bg-indigo-50">
              <button
                onClick={() => {
                  setShowOpeningTool(!showOpeningTool)
                  if (!showOpeningTool && openingSuggestions.length === 0) {
                    handleLoadOpeningClosingSuggestions('opening')
                  }
                }}
                className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-indigo-100 transition-colors rounded-lg"
              >
                <span className="text-sm font-semibold text-indigo-900">✨ Change Opening Sentence</span>
                {showOpeningTool ? <ChevronUp className="w-4 h-4 text-indigo-700" /> : <ChevronDown className="w-4 h-4 text-indigo-700" />}
              </button>
              
              {showOpeningTool && (
                <div className="px-4 pb-4 space-y-3">
                  {currentOpening && (
                    <div className="bg-white border border-indigo-200 rounded-lg p-3">
                      <p className="text-xs font-semibold text-indigo-700 mb-1">Current Opening:</p>
                      <p className="text-sm text-sage-800">{currentOpening}</p>
                    </div>
                  )}
                  
                  {previousOpening && (
                    <div className="bg-white border border-gray-200 rounded-lg p-3">
                      <p className="text-xs font-semibold text-gray-600 mb-1">Previous Report Used:</p>
                      <p className="text-sm text-gray-700">{previousOpening}</p>
                    </div>
                  )}
                  
                  {loadingOpeningSuggestions ? (
                    <div className="text-center py-4">
                      <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
                      <p className="text-sm text-indigo-600 mt-2">Generating suggestions...</p>
                    </div>
                  ) : openingSuggestions.length > 0 ? (
                    <div className="space-y-2">
                      <p className="text-xs font-semibold text-indigo-700">Try These:</p>
                      {openingSuggestions.map((suggestion, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleApplyOpeningClosing(suggestion, 'opening')}
                          className="w-full text-left px-3 py-2 bg-white border border-indigo-200 rounded-lg hover:bg-indigo-50 hover:border-indigo-300 transition-colors text-sm"
                        >
                          {suggestion}
                        </button>
                      ))}
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleLoadOpeningClosingSuggestions('opening')}
                          className="flex-1 text-center px-3 py-2 bg-indigo-100 border border-indigo-300 rounded-lg hover:bg-indigo-200 transition-colors text-sm font-medium text-indigo-700"
                        >
                          🔄 Generate New Options
                        </button>
                        {hasChangedOpening && (
                          <button
                            onClick={() => handleUndoOpeningClosing('opening')}
                            className="px-4 py-2 bg-amber-50 border border-amber-300 rounded-lg hover:bg-amber-100 transition-colors text-sm font-medium text-amber-700"
                            title="Restore original opening sentence"
                          >
                            ↩️ Undo
                          </button>
                        )}
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleLoadOpeningClosingSuggestions('opening')}
                      className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
                    >
                      Generate Suggestions
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Textarea with highlight overlay and side indicators */}
            <div className="relative flex gap-2">
              {/* Side indicator bar for suggestions - positioned to scroll with textarea */}
              {reviewSuggestions.length > 0 && (
                <div 
                  className="relative" 
                  style={{ minWidth: '24px', width: '24px' }}
                >
                  {/* Container that matches textarea height and scrolls with it */}
                  <div 
                    ref={indicatorBarRef}
                    className="absolute inset-0 overflow-y-auto overflow-x-hidden pointer-events-none"
                    style={{
                      scrollbarWidth: 'none',
                      msOverflowStyle: 'none',
                      paddingTop: '8px'
                    }}
                  >
                    <style>{`
                      .indicator-scroll::-webkit-scrollbar {
                        display: none;
                      }
                    `}</style>
                    <div className="relative" style={{ 
                      minHeight: textareaHeight > 0 ? `${textareaHeight}px` : '100%',
                      height: textareaHeight > 0 ? `${textareaHeight}px` : 'auto'
                    }}>
                      {reviewSuggestions.map((suggestion, idx) => {
                        // Use the helper function to get exact pixel position
                        const textarea = textareaRef.current
                        const position = getTextPosition(textarea, suggestion.start_index)
                        const topPosition = position.top
                        
                        // Different colors for each suggestion
                        const colorClasses = [
                          'bg-blue-400 hover:bg-blue-500 border-blue-500',
                          'bg-purple-400 hover:bg-purple-500 border-purple-500',
                          'bg-pink-400 hover:bg-pink-500 border-pink-500',
                          'bg-indigo-400 hover:bg-indigo-500 border-indigo-500',
                          'bg-teal-400 hover:bg-teal-500 border-teal-500',
                          'bg-orange-400 hover:bg-orange-500 border-orange-500',
                          'bg-cyan-400 hover:bg-cyan-500 border-cyan-500',
                          'bg-rose-400 hover:bg-rose-500 border-rose-500',
                        ]
                        const colorClass = colorClasses[idx % colorClasses.length]
                        
                        return (
                          <div
                            key={idx}
                            className="group relative pointer-events-auto"
                            style={{
                              position: 'absolute',
                              top: `${topPosition}px`,
                              left: '0',
                              transform: 'translateY(-50%)'
                            }}
                          >
                            <button
                              onClick={() => {
                                setActiveSuggestion(suggestion)
                                setEditedSuggestion(suggestion.original) // Pre-fill with current text
                                // Scroll to the text in textarea
                                if (textareaRef.current) {
                                  textareaRef.current.focus()
                                  textareaRef.current.setSelectionRange(suggestion.start_index, suggestion.end_index)
                                  // Scroll to show the suggestion
                                  const textarea = textareaRef.current
                                  const computedStyle = window.getComputedStyle(textarea)
                                  const lineHeight = parseFloat(computedStyle.lineHeight) || 20
                                  const textBefore = editedReport.substring(0, suggestion.start_index)
                                  const linesBefore = textBefore.split('\n').length
                                  textarea.scrollTop = Math.max(0, (linesBefore - 5) * lineHeight)
                                }
                              }}
                              className={`w-4 h-4 rounded-full ${colorClass} transition-all cursor-pointer border-2 shadow-sm hover:scale-125`}
                              title={suggestion.issue}
                            />
                            {/* Tooltip on hover - shows the reasoning */}
                            <div className="absolute left-7 top-1/2 -translate-y-1/2 bg-sage-800 text-white text-xs rounded-lg px-3 py-2 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 shadow-lg">
                              {suggestion.issue}
                              <div className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-full">
                                <div className="border-4 border-transparent border-r-sage-800"></div>
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                </div>
              )}
              
              <div className="relative flex-1">
            <textarea
              ref={textareaRef}
              value={editedReport}
                onChange={(e) => {
                  setEditedReport(e.target.value)
                  // Update indices for suggestions when text changes
                  // We'll keep suggestions but they may need to be re-validated
                }}
              onSelect={(e) => {
                const start = e.target.selectionStart
                const end = e.target.selectionEnd
                  const selected = editedReport.substring(start, end)
                  
                if (start !== end) {
                    setSelectedText(selected)
                    
                    // Check if it's a single word (no spaces, punctuation only at edges)
                    const wordPattern = /^[\w'-]+$/
                    const cleanSelected = selected.trim().replace(/^[^\w]+|[^\w]+$/g, '')
                    
                    if (cleanSelected && wordPattern.test(cleanSelected) && cleanSelected.length > 1) {
                      // It's a single word - show synonyms
                      setSelectedWord(cleanSelected)
                      setWordPosition({ start, end })
                      handleLoadSynonyms(cleanSelected, editedReport, start)
                    } else {
                      // It's multiple words or not a word - hide synonyms
                      setSelectedWord('')
                      setSynonyms([])
                      setShowSynonyms(false)
                    }
                } else {
                  setSelectedText('')
                    setSelectedWord('')
                    setSynonyms([])
                    setShowSynonyms(false)
                    setActiveSuggestion(null)
                }
              }}
              rows={25}
                className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500 font-mono text-sm relative z-10 bg-transparent"
              placeholder="Edit your report here..."
                style={{ caretColor: 'rgb(55, 65, 81)' }}
              />
              
              </div>
            </div>
            
            {/* Review Controls */}
            {reviewSuggestions.length > 0 && (
              <div className="mt-4 flex items-center justify-between p-3 bg-sage-50 rounded-lg border border-sage-200">
                <div className="flex items-center gap-3">
                  <Sparkles className="w-4 h-4 text-violet-600" />
                  <span className="text-sm font-medium text-sage-700">
                    {reviewSuggestions.length} Suggestion{reviewSuggestions.length !== 1 ? 's' : ''} Found
                  </span>
                </div>
                <button
                  onClick={() => {
                    setReviewSuggestions([])
                    setActiveSuggestion(null)
                  }}
                  className="text-sm text-sage-600 hover:text-sage-700 px-3 py-1 rounded hover:bg-sage-100"
                >
                  Clear All
                </button>
              </div>
            )}
            
            {/* Suggestion Popup */}
            {activeSuggestion && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30" onClick={() => {
                setActiveSuggestion(null)
                setEditedSuggestion('')
              }}>
                <div 
                  className="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 p-6 transform transition-all"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-sage-800 mb-1">Improve This Phrase</h3>
                      <p className="text-sm text-sage-600">{activeSuggestion.issue}</p>
                    </div>
                    <button
                      onClick={() => {
                        setActiveSuggestion(null)
                        setEditedSuggestion('')
                      }}
                      className="text-sage-400 hover:text-sage-600 transition-colors"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-xs font-medium text-sage-600 mb-2">Edit the text below, or click a suggestion to use it:</p>
                    <textarea
                      ref={(el) => {
                        // Store ref to textarea for reading value
                        if (el && !el.dataset.suggestionRef) {
                          el.dataset.suggestionRef = 'true'
                        }
                      }}
                      value={editedSuggestion !== '' ? editedSuggestion : activeSuggestion.original}
                      onChange={(e) => setEditedSuggestion(e.target.value)}
                      className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500 text-sm mb-3 min-h-[80px] font-mono"
                    />
                    <div className="space-y-2">
                      {activeSuggestion.suggestions.map((suggestion, idx) => (
                        <button
                          key={idx}
                          onClick={() => {
                            setEditedSuggestion(suggestion)
                          }}
                          className="w-full text-left px-4 py-3 bg-gradient-to-r from-violet-50 to-purple-50 hover:from-violet-100 hover:to-purple-100 border-2 border-violet-200 hover:border-violet-300 rounded-lg transition-all text-sm text-violet-800 font-medium"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        handleDismissSuggestion(activeSuggestion)
                        setActiveSuggestion(null)
                        setEditedSuggestion('')
                      }}
                      className="flex-1 px-4 py-2 bg-red-50 text-red-700 border-2 border-red-200 rounded-lg hover:bg-red-100 hover:border-red-300 transition-colors text-sm font-medium flex items-center justify-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                      Remove Suggestion
                    </button>
                    <button
                      onClick={() => {
                        setActiveSuggestion(null)
                        setEditedSuggestion('')
                      }}
                      className="flex-1 px-4 py-2 bg-sage-200 text-sage-700 rounded-lg hover:bg-sage-300 transition-colors text-sm font-medium"
                    >
                      Close (Keep for Later)
                    </button>
                    <button
                      onClick={() => {
                        // Get the current value from the textarea
                        // If editedSuggestion is empty string, use original; otherwise use editedSuggestion
                        const currentValue = editedSuggestion !== '' ? editedSuggestion : activeSuggestion.original
                        const textToApply = currentValue.trim()
                        if (!textToApply) {
                          alert('Please enter some text or select a suggestion.')
                          return
                        }
                        handleApplySuggestion(activeSuggestion, textToApply)
                      }}
                      className="flex-1 px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 transition-colors text-sm font-medium"
                    >
                      Apply to Report
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Closing Sentence Tool */}
            <div className="mt-4 border border-rose-200 rounded-lg bg-rose-50">
              <button
                onClick={() => {
                  setShowClosingTool(!showClosingTool)
                  if (!showClosingTool && closingSuggestions.length === 0) {
                    handleLoadOpeningClosingSuggestions('closing')
                  }
                }}
                className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-rose-100 transition-colors rounded-lg"
              >
                <span className="text-sm font-semibold text-rose-900">✨ Change Closing Sentence</span>
                {showClosingTool ? <ChevronUp className="w-4 h-4 text-rose-700" /> : <ChevronDown className="w-4 h-4 text-rose-700" />}
              </button>
              
              {showClosingTool && (
                <div className="px-4 pb-4 space-y-3">
                  {currentClosing && (
                    <div className="bg-white border border-rose-200 rounded-lg p-3">
                      <p className="text-xs font-semibold text-rose-700 mb-1">Current Closing:</p>
                      <p className="text-sm text-sage-800">{currentClosing}</p>
                    </div>
                  )}
                  
                  {previousClosing && (
                    <div className="bg-white border border-gray-200 rounded-lg p-3">
                      <p className="text-xs font-semibold text-gray-600 mb-1">Previous Report Used:</p>
                      <p className="text-sm text-gray-700">{previousClosing}</p>
                    </div>
                  )}
                  
                  {loadingClosingSuggestions ? (
                    <div className="text-center py-4">
                      <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-rose-600"></div>
                      <p className="text-sm text-rose-600 mt-2">Generating suggestions...</p>
                    </div>
                  ) : closingSuggestions.length > 0 ? (
                    <div className="space-y-2">
                      <p className="text-xs font-semibold text-rose-700">Try These:</p>
                      {closingSuggestions.map((suggestion, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleApplyOpeningClosing(suggestion, 'closing')}
                          className="w-full text-left px-3 py-2 bg-white border border-rose-200 rounded-lg hover:bg-rose-50 hover:border-rose-300 transition-colors text-sm"
                        >
                          {suggestion}
                        </button>
                      ))}
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleLoadOpeningClosingSuggestions('closing')}
                          className="flex-1 text-center px-3 py-2 bg-rose-100 border border-rose-300 rounded-lg hover:bg-rose-200 transition-colors text-sm font-medium text-rose-700"
                        >
                          🔄 Generate New Options
                        </button>
                        {hasChangedClosing && (
                          <button
                            onClick={() => handleUndoOpeningClosing('closing')}
                            className="px-4 py-2 bg-amber-50 border border-amber-300 rounded-lg hover:bg-amber-100 transition-colors text-sm font-medium text-amber-700"
                            title="Restore original closing sentence"
                          >
                            ↩️ Undo
                          </button>
                        )}
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleLoadOpeningClosingSuggestions('closing')}
                      className="w-full px-4 py-2 bg-rose-600 text-white rounded-lg hover:bg-rose-700 transition-colors text-sm font-medium"
                    >
                      Generate Suggestions
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Synonym Suggestions - shown when single word is selected */}
            {showSynonyms && selectedWord && (
              <div className="mt-4 mb-4 border border-emerald-200 rounded-lg bg-emerald-50 p-4 animate-fade-in">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-emerald-900">💡 Synonyms for "{selectedWord}":</span>
                    {loadingSynonyms && (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-emerald-600"></div>
                    )}
                  </div>
                  <button
                    onClick={() => {
                      setShowSynonyms(false)
                      setSynonyms([])
                      setSelectedWord('')
                    }}
                    className="text-emerald-600 hover:text-emerald-700 text-sm"
                  >
                    ✕
                  </button>
                </div>
                
                {loadingSynonyms ? (
                  <p className="text-sm text-emerald-600">Finding synonyms...</p>
                ) : synonyms.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {synonyms.map((synonym, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleReplaceWord(synonym)}
                        className="px-3 py-1.5 bg-white border border-emerald-200 rounded-lg hover:bg-emerald-100 hover:border-emerald-300 transition-colors text-sm text-emerald-800"
                      >
                        {synonym}
                      </button>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-emerald-600 italic">No synonyms found</p>
                )}
              </div>
            )}

            <div className="mt-4 space-y-3">
              {selectedText && !selectedWord && (
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
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <button
                  onClick={handleReviewReport}
                  disabled={reviewing || saving || regenerating}
                  className="px-6 py-2.5 bg-gradient-to-r from-violet-50 to-purple-50 text-violet-700 font-medium rounded-xl hover:from-violet-100 hover:to-purple-100 transition-all hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center border-2 border-violet-200"
                  title="Review report for improvements (wordiness, tone, clarity, etc.)"
                >
                  <Sparkles className={`w-4 h-4 mr-2 ${reviewing ? 'animate-pulse' : ''}`} />
                  {reviewing ? 'Reviewing...' : 'Review Report'}
                </button>
                
                <button
                  onClick={handleFixGrammar}
                  disabled={fixingGrammar || saving || regenerating || reviewing}
                  className="px-6 py-2.5 bg-purple-50 text-purple-700 font-medium rounded-xl hover:bg-purple-100 transition-smooth hover-lift shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center border-2 border-purple-200"
                  title="Fix grammar and spelling while keeping your exact wording"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  {fixingGrammar ? 'Fixing...' : 'Fix Grammar'}
                </button>
                
                <button
                  onClick={handleRegenerate}
                  disabled={regenerating || saving || fixingGrammar || reviewing}
                  className="px-6 py-2.5 bg-blue-50 text-blue-700 font-medium rounded-xl hover:bg-blue-100 transition-smooth hover-lift shadow-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center border-2 border-blue-200"
                  title="Generate a completely new report from scratch"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${regenerating ? 'animate-spin' : ''}`} />
                  {regenerating ? 'Regenerating...' : 'Regenerate Report'}
                </button>

                <button
                  onClick={handleAddContact}
                  disabled={addingContact || saving || reviewing}
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
    </div>
  )
}

export default EditReport

