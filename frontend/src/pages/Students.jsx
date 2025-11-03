import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Edit2, Trash2, FileText, X, Search } from 'lucide-react'
import { getStudents, createStudent, updateStudent, deleteStudent } from '../services/api'

function Students() {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingStudent, setEditingStudent] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [formData, setFormData] = useState({
    name: '',
    subject: '',
    grade_level: '',
    school: '',
    teacher: '',
    parent_name: '',
    notes: '',
    recurring_schedule: '',
    active: true
  })

  useEffect(() => {
    loadStudents()
  }, [])

  const loadStudents = async () => {
    try {
      const data = await getStudents(false) // Get all students
      setStudents(data)
    } catch (error) {
      console.error('Error loading students:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingStudent) {
        await updateStudent(editingStudent.id, formData)
      } else {
        await createStudent(formData)
      }
      setShowModal(false)
      setEditingStudent(null)
      resetForm()
      loadStudents()
    } catch (error) {
      console.error('Error saving student:', error)
      
      // Check if it's a duplicate error
      if (error.response?.status === 409 || error.response?.data?.error === 'duplicate') {
        const existingStudent = error.response?.data?.existing_student
        if (existingStudent) {
          alert(`⚠️ A student named "${formData.name}" already exists!\n\nSchedule: ${existingStudent.recurring_schedule || 'Not set'}\nSubject: ${existingStudent.subject || 'Not set'}\n\nPlease use a different name or edit the existing student.`)
        } else {
          alert(`⚠️ A student named "${formData.name}" already exists. Please use a different name.`)
        }
      } else {
        alert('Error saving student. Please try again.')
      }
    }
  }

  const handleEdit = (student) => {
    setEditingStudent(student)
    setFormData({
      name: student.name || '',
      subject: student.subject || '',
      grade_level: student.grade_level || '',
      school: student.school || '',
      teacher: student.teacher || '',
      parent_name: student.parent_name || '',
      notes: student.notes || '',
      recurring_schedule: student.recurring_schedule || '',
      active: student.active !== undefined ? student.active : true
    })
    setShowModal(true)
  }

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this student? All their reports will also be deleted.')) {
      try {
        await deleteStudent(id)
        loadStudents()
      } catch (error) {
        console.error('Error deleting student:', error)
        alert('Error deleting student. Please try again.')
      }
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      subject: '',
      grade_level: '',
      school: '',
      teacher: '',
      parent_name: '',
      notes: '',
      recurring_schedule: '',
      active: true
    })
  }

  const openNewModal = () => {
    setEditingStudent(null)
    resetForm()
    setShowModal(true)
  }

  // Filter students based on search term
  const filteredStudents = students.filter(student => {
    if (!searchTerm) return true
    const search = searchTerm.toLowerCase()
    return (
      student.name?.toLowerCase().includes(search) ||
      student.subject?.toLowerCase().includes(search) ||
      student.grade_level?.toLowerCase().includes(search) ||
      student.school?.toLowerCase().includes(search) ||
      student.teacher?.toLowerCase().includes(search) ||
      student.parent_name?.toLowerCase().includes(search) ||
      student.notes?.toLowerCase().includes(search)
    )
  })

  if (loading) {
    return <div className="text-center py-12">Loading students...</div>
  }

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-sage-800">Students</h2>
        <button
          onClick={openNewModal}
          className="inline-flex items-center px-4 py-2 bg-sage-600 text-white rounded-lg hover:bg-sage-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Student
        </button>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-lg shadow-sm border border-sage-200 p-4 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-sage-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search students by name, subject, school, teacher..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
          />
        </div>
      </div>

      {/* Students Grid */}
      {filteredStudents.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-sage-200 p-12 text-center">
          <p className="text-sage-600 mb-4">
            {students.length === 0 ? 'No students yet' : 'No students match your search'}
          </p>
          {students.length === 0 && (
            <button
              onClick={openNewModal}
              className="text-sage-600 hover:text-sage-700 font-medium"
            >
              Add your first student →
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredStudents.map((student) => (
            <div
              key={student.id}
              className="bg-white rounded-xl shadow-md border border-sage-200 p-6 hover:shadow-lg transition-smooth hover:-translate-y-1 card-elevated"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-sage-900">
                    {student.name}
                  </h3>
                  {student.subject && (
                    <p className="text-sm text-sage-600 mt-1">{student.subject}</p>
                  )}
                </div>
                <span className={`
                  px-2 py-1 rounded-full text-xs font-medium
                  ${student.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}
                `}>
                  {student.active ? 'Active' : 'Inactive'}
                </span>
              </div>

              <div className="space-y-1 mb-3">
                {student.grade_level && (
                  <p className="text-sm text-sage-600">
                    Grade: {student.grade_level}
                  </p>
                )}

                {student.school && (
                  <p className="text-sm text-sage-600">
                    🏫 {student.school}
                  </p>
                )}

                {student.teacher && (
                  <p className="text-sm text-sage-600">
                    👨‍🏫 Teacher: {student.teacher}
                  </p>
                )}

                {student.parent_name && (
                  <p className="text-sm text-sage-600">
                    👤 Parent: {student.parent_name}
                  </p>
                )}

                {student.recurring_schedule && (
                  <p className="text-sm text-sage-600">
                    📅 {student.recurring_schedule}
                  </p>
                )}
              </div>

              {student.notes && (
                <p className="text-sm text-sage-600 mb-4 italic">
                  {student.notes.substring(0, 100)}
                  {student.notes.length > 100 ? '...' : ''}
                </p>
              )}

              <div className="flex items-center justify-between pt-4 border-t border-sage-200">
                <Link
                  to={`/reports?student=${student.id}`}
                  className="text-sm text-sage-600 hover:text-sage-700 flex items-center"
                >
                  <FileText className="w-4 h-4 mr-1" />
                  {student.total_reports || 0} reports
                </Link>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEdit(student)}
                    className="p-2.5 text-sage-600 hover:text-sage-700 hover:bg-sage-50 rounded-lg transition-smooth hover:scale-110"
                    title="Edit student"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(student.id)}
                    className="p-2.5 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-smooth hover:scale-110"
                    title="Delete student"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b border-sage-200">
              <h3 className="text-xl font-semibold text-sage-900">
                {editingStudent ? 'Edit Student' : 'Add New Student'}
              </h3>
              <button
                onClick={() => {
                  setShowModal(false)
                  setEditingStudent(null)
                  resetForm()
                }}
                className="text-sage-500 hover:text-sage-700"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-sage-700 mb-1">
                  Student Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
                  placeholder="e.g., John Smith"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-sage-700 mb-1">
                    Subject/Class
                  </label>
                  <input
                    type="text"
                    value={formData.subject}
                    onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                    className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
                    placeholder="e.g., SAT Math"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-sage-700 mb-1">
                    Grade Level
                  </label>
                  <input
                    type="text"
                    value={formData.grade_level}
                    onChange={(e) => setFormData({ ...formData, grade_level: e.target.value })}
                    className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
                    placeholder="e.g., 11th Grade"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-sage-700 mb-1">
                    School
                  </label>
                  <input
                    type="text"
                    value={formData.school}
                    onChange={(e) => setFormData({ ...formData, school: e.target.value })}
                    className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
                    placeholder="e.g., Lincoln High School"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-sage-700 mb-1">
                    Teacher
                  </label>
                  <input
                    type="text"
                    value={formData.teacher}
                    onChange={(e) => setFormData({ ...formData, teacher: e.target.value })}
                    className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
                    placeholder="e.g., Mr. Johnson"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-sage-700 mb-1">
                  Parent Name
                </label>
                <input
                  type="text"
                  value={formData.parent_name}
                  onChange={(e) => setFormData({ ...formData, parent_name: e.target.value })}
                  className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
                  placeholder="e.g., Sarah Smith"
                />
                <p className="text-xs text-sage-500 mt-1">Reports will start with "Hi [first name],"</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-sage-700 mb-1">
                  Recurring Schedule
                </label>
                <input
                  type="text"
                  value={formData.recurring_schedule}
                  onChange={(e) => setFormData({ ...formData, recurring_schedule: e.target.value })}
                  className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
                  placeholder="e.g., Mondays 4pm, Thursdays 6pm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-sage-700 mb-1">
                  Notes
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-sage-300 rounded-lg focus:ring-2 focus:ring-sage-500 focus:border-sage-500"
                  placeholder="Important information to remember about this student..."
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="active"
                  checked={formData.active}
                  onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                  className="w-4 h-4 text-sage-600 border-sage-300 rounded focus:ring-sage-500"
                />
                <label htmlFor="active" className="ml-2 text-sm text-sage-700">
                  Active student
                </label>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false)
                    setEditingStudent(null)
                    resetForm()
                  }}
                  className="px-4 py-2 text-sage-700 hover:bg-sage-50 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-sage-600 text-white rounded-lg hover:bg-sage-700 transition-colors"
                >
                  {editingStudent ? 'Save Changes' : 'Add Student'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Students

