"""
Flask API for Sage Tutoring Report System
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime

from database import init_db, get_session, Student, Report, SampleReport, CalendarSession, UserSettings
from ai_service import AIService, test_ai_connection

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database
# Use dynamic path based on project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from project root
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai')

DB_PATH = os.getenv('DATABASE_PATH', os.path.join(PROJECT_ROOT, 'database', 'sage_reports.db'))
init_db(DB_PATH)

# Initialize AI service
ai_service = AIService(provider=AI_PROVIDER)


# ============================================
# HEALTH CHECK & STATUS
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if the API is running"""
    ai_status, ai_message = test_ai_connection()
    return jsonify({
        'status': 'ok',
        'ai_connected': ai_status,
        'ai_message': ai_message,
        'provider': AI_PROVIDER
    })


# ============================================
# STUDENT ENDPOINTS
# ============================================

@app.route('/api/students', methods=['GET'])
def get_students():
    """Get all students"""
    session = get_session(DB_PATH)
    try:
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        query = session.query(Student)
        if active_only:
            query = query.filter(Student.active == True)
        
        students = query.order_by(Student.name).all()
        return jsonify([s.to_dict() for s in students])
    finally:
        session.close()


@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Get a specific student"""
    session = get_session(DB_PATH)
    try:
        student = session.query(Student).filter(Student.id == student_id).first()
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        return jsonify(student.to_dict())
    finally:
        session.close()


@app.route('/api/students', methods=['POST'])
def create_student():
    """Create a new student"""
    data = request.json
    session = get_session(DB_PATH)
    
    try:
        student_name = data.get('name')
        
        # Check for duplicate name
        existing = session.query(Student).filter(Student.name == student_name).first()
        if existing:
            return jsonify({
                'error': 'duplicate',
                'message': f'A student named "{student_name}" already exists.',
                'existing_student': existing.to_dict()
            }), 409  # 409 Conflict status code
        
        student = Student(
            name=student_name,
            subject=data.get('subject'),
            grade_level=data.get('grade_level'),
            school=data.get('school'),
            teacher=data.get('teacher'),
            parent_name=data.get('parent_name'),
            notes=data.get('notes'),
            recurring_schedule=data.get('recurring_schedule'),
            active=data.get('active', True)
        )
        
        session.add(student)
        session.commit()
        
        return jsonify(student.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()


@app.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    """Update a student"""
    data = request.json
    session = get_session(DB_PATH)
    
    try:
        student = session.query(Student).filter(Student.id == student_id).first()
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Update fields
        if 'name' in data:
            student.name = data['name']
        if 'subject' in data:
            student.subject = data['subject']
        if 'grade_level' in data:
            student.grade_level = data['grade_level']
        if 'school' in data:
            student.school = data['school']
        if 'teacher' in data:
            student.teacher = data['teacher']
        if 'parent_name' in data:
            student.parent_name = data['parent_name']
        if 'notes' in data:
            student.notes = data['notes']
        if 'recurring_schedule' in data:
            student.recurring_schedule = data['recurring_schedule']
        if 'active' in data:
            student.active = data['active']
        
        session.commit()
        return jsonify(student.to_dict())
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()


@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student"""
    session = get_session(DB_PATH)
    
    try:
        student = session.query(Student).filter(Student.id == student_id).first()
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        session.delete(student)
        session.commit()
        return jsonify({'message': 'Student deleted successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()


# ============================================
# REPORT ENDPOINTS
# ============================================

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Get all reports (optionally filtered by student)"""
    session = get_session(DB_PATH)
    try:
        student_id = request.args.get('student_id', type=int)
        
        query = session.query(Report)
        if student_id:
            query = query.filter(Report.student_id == student_id)
        
        reports = query.order_by(Report.session_date.desc()).all()
        return jsonify([r.to_dict() for r in reports])
    finally:
        session.close()


@app.route('/api/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """Get a specific report"""
    session = get_session(DB_PATH)
    try:
        report = session.query(Report).filter(Report.id == report_id).first()
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        return jsonify(report.to_dict())
    finally:
        session.close()


@app.route('/api/reports', methods=['POST'])
def create_report():
    """Create a report without AI generation (save draft)"""
    data = request.json
    session = get_session(DB_PATH)
    
    try:
        report = Report(
            student_id=data.get('student_id'),
            session_date=datetime.fromisoformat(data.get('session_date', datetime.now().isoformat())),
            duration_hours=data.get('duration_hours', '1'),
            topics_covered=data.get('topics_covered'),
            activities=data.get('activities'),
            notes=data.get('notes'),
            next_session_notes=data.get('next_session_notes'),
            status='draft'
        )
        
        session.add(report)
        session.commit()
        
        return jsonify(report.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()


@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Generate a new report using AI"""
    data = request.json
    session = get_session(DB_PATH)
    
    try:
        # Get student info
        student_id = data.get('student_id')
        student = session.query(Student).filter(Student.id == student_id).first()
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get training data from reports table (only reports marked for training)
        # This includes both created reports and uploaded historical reports that have use_for_training=True
        import random
        
        all_training_reports = session.query(Report)\
            .filter(Report.use_for_training == True)\
            .all()
        
        # Separate by student
        student_reports = [r for r in all_training_reports if r.student_id == student_id and r.final_report]
        other_reports = [r for r in all_training_reports if r.student_id != student_id and r.final_report]
        
        # STUDENT-SPECIFIC SELECTION (10 total)
        student_texts = []
        
        # 1. Most recent 3 (for timeline/continuity)
        recent_student = sorted(student_reports, key=lambda r: r.session_date, reverse=True)[:3]
        student_texts.extend([r.final_report for r in recent_student])
        
        # 2. Longest 5 (for best quality examples)
        longest_student = sorted(student_reports, key=lambda r: len(r.final_report or ''), reverse=True)[:5]
        student_texts.extend([r.final_report for r in longest_student if r.final_report not in student_texts])
        
        # 3. Random 2 (for variety)
        remaining_student = [r for r in student_reports if r.final_report not in student_texts]
        if len(remaining_student) > 0:
            random_student = random.sample(remaining_student, min(2, len(remaining_student)))
            student_texts.extend([r.final_report for r in random_student])
        
        # GENERAL SELECTION (10 total)
        general_texts = []
        
        # 1. Longest report from each of 5 different students (diversity + quality)
        students_seen = set()
        longest_per_student = sorted(other_reports, key=lambda r: len(r.final_report or ''), reverse=True)
        for r in longest_per_student:
            if r.student_id not in students_seen:
                general_texts.append(r.final_report)
                students_seen.add(r.student_id)
            if len(students_seen) >= 5:
                break
        
        # 2. Random 5 from different students not yet included
        remaining_general = [r for r in other_reports if r.final_report not in general_texts]
        if len(remaining_general) > 0:
            random_general = random.sample(remaining_general, min(5, len(remaining_general)))
            general_texts.extend([r.final_report for r in random_general])
        
        sample_texts = student_texts + general_texts
        
        # Get previous reports for this student
        previous_reports = session.query(Report)\
            .filter(Report.student_id == student_id)\
            .order_by(Report.session_date.desc())\
            .limit(3)\
            .all()
        previous_report_dicts = [pr.to_dict() for pr in previous_reports]
        
        # Get user settings for signature
        user_settings = session.query(UserSettings).first()
        
        # Generate the report
        minimal_editing = data.get('minimal_editing', False)
        include_contact = data.get('include_contact', False)
        
        ai_report = ai_service.generate_report(
            student_name=student.name,
            subject=data.get('subject', student.subject),
            topics_covered=data.get('topics_covered', ''),
            activities=data.get('activities', ''),
            notes=data.get('notes', ''),
            sample_reports=sample_texts,
            previous_reports=previous_report_dicts,
            minimal_editing=minimal_editing,
            parent_name=student.parent_name,
            tutor_name=user_settings.tutor_name if user_settings else None,
            include_contact=include_contact,
            tutor_phone=user_settings.phone if user_settings else None,
            tutor_email=user_settings.email if user_settings else None
        )
        
        # Create and save the report
        report = Report(
            student_id=student_id,
            session_date=datetime.fromisoformat(data.get('session_date', datetime.now().isoformat())),
            duration_hours=data.get('duration_hours', '1'),
            topics_covered=data.get('topics_covered'),
            activities=data.get('activities'),
            notes=data.get('notes'),
            next_session_notes=data.get('next_session_notes'),
            ai_generated_report=ai_report,
            final_report=ai_report,  # Initially same as AI version
            status='draft'
        )
        
        session.add(report)
        session.commit()
        
        return jsonify(report.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()


@app.route('/api/reports/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    """Update a report"""
    data = request.json
    session = get_session(DB_PATH)
    
    try:
        report = session.query(Report).filter(Report.id == report_id).first()
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Update fields
        if 'final_report' in data:
            report.final_report = data['final_report']
        if 'status' in data:
            report.status = data['status']
        if 'student_id' in data:
            report.student_id = data['student_id']
        if 'session_date' in data:
            report.session_date = datetime.fromisoformat(data['session_date'].replace('Z', '+00:00'))
        if 'duration_hours' in data:
            report.duration_hours = data['duration_hours']
        if 'topics_covered' in data:
            report.topics_covered = data['topics_covered']
        if 'activities' in data:
            report.activities = data['activities']
        if 'notes' in data:
            report.notes = data['notes']
        if 'next_session_notes' in data:
            report.next_session_notes = data['next_session_notes']
        if 'use_for_training' in data:
            report.use_for_training = data['use_for_training']
        
        report.updated_at = datetime.utcnow()
        session.commit()
        return jsonify(report.to_dict())
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()


@app.route('/api/reports/<int:report_id>/toggle-training', methods=['POST'])
def toggle_report_training(report_id):
    """Toggle whether a report should be used for AI training"""
    session = get_session(DB_PATH)
    
    try:
        report = session.query(Report).filter(Report.id == report_id).first()
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Toggle the training status
        report.use_for_training = not report.use_for_training
        report.updated_at = datetime.utcnow()
        
        session.commit()
        return jsonify({
            'success': True,
            'use_for_training': report.use_for_training,
            'report': report.to_dict()
        })
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()


@app.route('/api/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """Delete a report"""
    session = get_session(DB_PATH)
    
    try:
        report = session.query(Report).filter(Report.id == report_id).first()
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        session.delete(report)
        session.commit()
        return jsonify({'message': 'Report deleted successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()


@app.route('/api/reports/<int:report_id>/fix-grammar', methods=['POST'])
def fix_report_grammar(report_id):
    """Fix grammar in a report while preserving content"""
    data = request.json
    
    try:
        report_text = data.get('report_text', '')
        if not report_text:
            return jsonify({'error': 'No report text provided'}), 400
        
        # Use AI to fix grammar only
        fixed_text = ai_service.fix_grammar(report_text)
        
        return jsonify({'fixed_report': fixed_text}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/reports/<int:report_id>/suggest-sentences', methods=['POST'])
def suggest_sentences_for_report(report_id):
    """Generate sentence suggestions for a report"""
    data = request.json
    session_db = get_session(DB_PATH)
    
    try:
        report = session_db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        report_text = data.get('report_text', '')
        cursor_position = data.get('cursor_position')
        student = session_db.query(Student).filter(Student.id == report.student_id).first()
        
        # Get previous reports for style reference (just a few for context)
        previous_reports = session_db.query(Report)\
            .filter(Report.student_id == report.student_id)\
            .filter(Report.id != report_id)\
            .filter(Report.use_for_training == True)\
            .order_by(Report.session_date.desc())\
            .limit(5)\
            .all()
        
        previous_texts = []
        for prev_report in previous_reports:
            text = prev_report.final_report or prev_report.ai_generated_report
            if text:
                previous_texts.append(text)
        
        # Generate suggestions with cursor context and style reference
        suggestions = ai_service.suggest_sentences(
            report_text=report_text,
            student_name=student.name if student else 'the student',
            subject=student.subject if student else 'the subject',
            cursor_position=cursor_position,
            previous_reports=previous_texts
        )
        
        return jsonify({'suggestions': suggestions}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        session_db.close()


@app.route('/api/reports/<int:report_id>/polish-text', methods=['POST'])
def polish_report_text(report_id):
    """Polish a selected portion of text"""
    data = request.json
    
    try:
        text_to_polish = data.get('text_to_polish', '')
        full_context = data.get('full_context', '')
        
        if not text_to_polish:
            return jsonify({'error': 'No text provided'}), 400
        
        # Polish the text
        polished = ai_service.polish_text(text_to_polish, full_context)
        
        return jsonify({'polished_text': polished}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/reports/<int:report_id>/polish-full-report', methods=['POST'])
def polish_full_report(report_id):
    """Polish entire report using GPT-4o with change tracking"""
    data = request.json
    
    try:
        report_text = data.get('report_text', '')
        
        if not report_text:
            return jsonify({'error': 'No report text provided'}), 400
        
        # Polish the full report
        result = ai_service.polish_full_report(report_text)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/reports/<int:report_id>/ask-ai', methods=['POST'])
def ask_ai_about_text(report_id):
    """Ask AI questions about selected text"""
    data = request.json
    session_db = get_session(DB_PATH)
    
    try:
        report = session_db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        selected_text = data.get('selected_text', '')
        question = data.get('question', '')
        full_report = data.get('full_report', '')
        conversation_history = data.get('conversation_history', [])
        
        if not selected_text or not question:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get student name for context
        student = session_db.query(Student).filter(Student.id == report.student_id).first()
        student_name = student.name if student else 'the student'
        
        # Ask AI
        answer = ai_service.ask_about_text(
            selected_text=selected_text,
            question=question,
            full_report=full_report,
            student_name=student_name,
            conversation_history=conversation_history
        )
        
        return jsonify({'answer': answer}), 200
    except Exception as e:
        print(f"Error in ask_ai_about_text: {str(e)}")
        return jsonify({'error': str(e)}), 400
    finally:
        session_db.close()


@app.route('/api/reports/<int:report_id>/get-synonyms', methods=['POST'])
def get_synonyms_endpoint(report_id):
    """Get synonyms for a word in context"""
    data = request.json
    
    try:
        word = data.get('word', '')
        context = data.get('context', '')
        
        if not word:
            return jsonify({'error': 'No word provided'}), 400
        
        # Get synonyms from AI
        synonyms = ai_service.get_synonyms(word, context)
        
        return jsonify({'synonyms': synonyms}), 200
    except Exception as e:
        print(f"Error getting synonyms: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/reports/<int:report_id>/review-phrases', methods=['POST'])
def review_phrases_endpoint(report_id):
    """Review report for improvements"""
    data = request.json
    session_db = get_session(DB_PATH)
    
    try:
        report = session_db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        report_text = data.get('report_text', '')
        
        if not report_text:
            return jsonify({'error': 'No report text provided'}), 400
        
        # Get student name for context
        student = session_db.query(Student).filter(Student.id == report.student_id).first()
        student_name = student.name if student else 'the student'
        
        # Review the report
        suggestions = ai_service.review_report(report_text, student_name)
        
        return jsonify({'suggestions': suggestions}), 200
    except Exception as e:
        print(f"Error reviewing report: {str(e)}")
        return jsonify({'error': str(e)}), 400
    finally:
        session_db.close()


@app.route('/api/reports/<int:report_id>/redo-paragraph', methods=['POST'])
def redo_paragraph(report_id):
    """Completely rewrite a paragraph in the user's style"""
    data = request.json
    session_db = get_session(DB_PATH)
    
    try:
        report = session_db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        paragraph = data.get('paragraph', '')
        full_report = data.get('full_report', '')
        
        if not paragraph:
            return jsonify({'error': 'No paragraph provided'}), 400
        
        # Get student info
        student = session_db.query(Student).filter(Student.id == report.student_id).first()
        student_name = student.name if student else 'the student'
        
        # Get previous reports for style reference
        previous_reports = session_db.query(Report)\
            .filter(Report.student_id == report.student_id)\
            .filter(Report.id != report_id)\
            .filter(Report.use_for_training == True)\
            .order_by(Report.session_date.desc())\
            .limit(5)\
            .all()
        
        previous_texts = []
        for prev_report in previous_reports:
            text = prev_report.final_report or prev_report.ai_generated_report
            if text:
                previous_texts.append(text)
        
        # Rewrite the paragraph
        rewritten = ai_service.redo_paragraph(
            paragraph=paragraph,
            full_report=full_report,
            student_name=student_name,
            previous_reports=previous_texts
        )
        
        return jsonify({'rewritten_paragraph': rewritten}), 200
    except Exception as e:
        print(f"Error redoing paragraph: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
    finally:
        session_db.close()


def _extract_sentence(text: str, sentence_type: str) -> str:
    """Extract opening or closing sentence properly handling ., !, and ?"""
    import re
    if not text:
        return ""
    
    text = text.strip()
    
    # Remove greeting lines like "Hi Name," at the start
    if sentence_type == 'opening':
        lines = text.split('\n')
        # Skip greeting line if it starts with "Hi"
        if lines and lines[0].strip().startswith('Hi '):
            text = '\n'.join(lines[1:]).strip()
    
    # Remove signature at the end (Best, Name)
    if sentence_type == 'closing':
        text = re.sub(r'\n*Best,\n[^\n]+(?:\n[^\n]+)*$', '', text).strip()
    
    # Split on sentence boundaries (., !, ?)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return text[:100] if len(text) > 100 else text
    
    if sentence_type == 'opening':
        # For opening, get ONLY the first sentence
        return sentences[0]
    else:  # closing
        # For closing, get ONLY the last sentence
        return sentences[-1]


@app.route('/api/reports/<int:report_id>/suggest-opening-closing', methods=['POST'])
def suggest_opening_closing_sentences(report_id):
    """Generate opening or closing sentence suggestions"""
    data = request.json
    session_db = get_session(DB_PATH)
    
    try:
        report = session_db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        student = session_db.query(Student).filter(Student.id == report.student_id).first()
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        sentence_type = data.get('type', 'opening')  # 'opening' or 'closing'
        
        # Get previous reports for this student
        previous_reports = session_db.query(Report)\
            .filter(Report.student_id == report.student_id)\
            .filter(Report.id != report_id)\
            .filter(Report.use_for_training == True)\
            .order_by(Report.session_date.desc())\
            .limit(15)\
            .all()
        
        # Extract the text from previous reports
        previous_texts = []
        for prev_report in previous_reports:
            text = prev_report.final_report or prev_report.ai_generated_report
            if text:
                previous_texts.append(text)
        
        # Get current report text from request body (most up-to-date version)
        current_text = data.get('report_text', '')
        if not current_text:
            # Fallback to database version
            current_text = report.final_report or report.ai_generated_report or ''
        
        # Extract current sentence using improved function
        current_sentence = _extract_sentence(current_text, sentence_type)
        
        # Get previous report's sentence for reference
        previous_sentence = ""
        if previous_texts:
            previous_sentence = _extract_sentence(previous_texts[0], sentence_type)
        
        # Generate suggestions with full context
        suggestions = ai_service.suggest_opening_closing(
            student_name=student.name,
            previous_reports=previous_texts,
            sentence_type=sentence_type,
            current_report_text=current_text
        )
        
        return jsonify({
            'suggestions': suggestions,
            'current_sentence': current_sentence.strip(),
            'previous_sentence': previous_sentence.strip()
        }), 200
    except Exception as e:
        print(f"Error in suggest_opening_closing_sentences: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400
    finally:
        session_db.close()


@app.route('/api/reports/<int:report_id>/add-contact', methods=['POST'])
def add_contact_to_report(report_id):
    """Add contact information to an existing report"""
    data = request.json
    session_db = get_session(DB_PATH)
    
    try:
        report = session_db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # CRITICAL: Get current report text from request body (the user's current edits)
        # NOT from the database (which would be the old saved version)
        current_report = data.get('report_text', '')
        if not current_report:
            # Fallback to database version only if no text provided
            current_report = report.final_report or report.ai_generated_report or ''
        
        # Get settings for contact info
        settings = session_db.query(UserSettings).first()
        if not settings:
            return jsonify({'error': 'Settings not configured'}), 400
        
        tutor_name = settings.tutor_name
        tutor_phone = settings.phone
        tutor_email = settings.email
        
        if not tutor_name:
            return jsonify({'error': 'Tutor name not configured in settings'}), 400
        
        # Build signature with contact info
        signature = f"Best,\n{tutor_name}"
        if tutor_phone:
            signature += f"\n{tutor_phone}"
        if tutor_email:
            signature += f"\n{tutor_email}"
        
        # Check if signature already exists
        if signature in current_report:
            return jsonify({'report_text': current_report, 'message': 'Contact info already present'}), 200
        
        # Remove any existing signature (Best, [name] pattern)
        import re
        # Match "Best," followed by optional whitespace and a name
        current_report = re.sub(r'\n*Best,\n[^\n]+(?:\n[^\n]+)*$', '', current_report).strip()
        
        # Add signature with contact info
        updated_report = current_report + "\n\n" + signature
        
        return jsonify({'report_text': updated_report}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        session_db.close()


@app.route('/api/reports/reminders/<int:student_id>', methods=['GET'])
def get_session_reminders(student_id):
    """Get reminders from the most recent report for a student"""
    session = get_session(DB_PATH)
    
    try:
        # Get the most recent report for this student
        last_report = session.query(Report)\
            .filter(Report.student_id == student_id)\
            .order_by(Report.session_date.desc())\
            .first()
        
        if not last_report:
            return jsonify({
                'has_reminders': False,
                'manual_notes': None,
                'last_session_date': None
            })
        
        # Get manual next_session_notes only
        manual_notes = last_report.next_session_notes
        
        return jsonify({
            'has_reminders': bool(manual_notes),
            'manual_notes': manual_notes,
            'last_session_date': last_report.session_date.isoformat() if last_report.session_date else None,
            'last_report_id': last_report.id
        })
        
    except Exception as e:
        print(f"Error getting reminders: {e}")
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()


# ============================================
# SAMPLE REPORTS ENDPOINTS
# ============================================

@app.route('/api/sample-reports', methods=['GET'])
def get_sample_reports():
    """Get all sample reports"""
    session = get_session(DB_PATH)
    try:
        samples = session.query(SampleReport).order_by(SampleReport.uploaded_at.desc()).all()
        return jsonify([s.to_dict() for s in samples])
    finally:
        session.close()


@app.route('/api/sample-reports', methods=['POST'])
def upload_sample_report():
    """Upload a historical report (now saves to reports table)"""
    data = request.json
    session = get_session(DB_PATH)
    
    try:
        # Get or create student
        student_id = data.get('student_id')
        student_name = data.get('student_name')
        
        if student_id:
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                return jsonify({'error': 'Student not found'}), 404
        elif student_name:
            # Try to find student by name
            student = session.query(Student).filter(Student.name == student_name).first()
            if not student:
                # Create new inactive student for historical data
                student = Student(
                    name=student_name,
                    subject=data.get('subject'),
                    active=False  # Historical students start as inactive
                )
                session.add(student)
                session.flush()  # Get the ID
            student_id = student.id
        else:
            return jsonify({'error': 'Student name or ID required'}), 400
        
        # Parse session_date
        session_date = None
        if data.get('session_date'):
            try:
                session_date = datetime.fromisoformat(data['session_date'].replace('Z', '+00:00'))
            except:
                session_date = datetime.now()
        else:
            session_date = datetime.now()
        
        # Create report
        report = Report(
            student_id=student_id,
            session_date=session_date,
            duration_hours=data.get('duration_hours', '1'),
            topics_covered=data.get('subject') or 'Historical session',
            final_report=data.get('content'),
            status='sent',  # Uploaded reports are automatically finalized
            source='uploaded'  # Mark as uploaded
        )
        
        session.add(report)
        session.commit()
        
        return jsonify(report.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()


@app.route('/api/sample-reports/<int:sample_id>', methods=['DELETE'])
def delete_sample_report(sample_id):
    """Delete a sample report"""
    session = get_session(DB_PATH)
    
    try:
        sample = session.query(SampleReport).filter(SampleReport.id == sample_id).first()
        if not sample:
            return jsonify({'error': 'Sample report not found'}), 404
        
        session.delete(sample)
        session.commit()
        return jsonify({'message': 'Sample report deleted successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()


# ============================================
# TODAY'S SESSIONS ENDPOINT
# ============================================

@app.route('/api/today-sessions', methods=['GET'])
def get_today_sessions():
    """Get today's scheduled sessions with prep notes"""
    from datetime import date
    session = get_session(DB_PATH)
    
    try:
        today = date.today()
        today_str = today.strftime('%A').lower()  # e.g., 'monday'
        
        # Get all active students with recurring schedules
        students = session.query(Student).filter(Student.active == True).all()
        
        today_sessions = []
        for student in students:
            if student.recurring_schedule:
                schedule_lower = student.recurring_schedule.lower()
                # Check if today is in their schedule
                if today_str[:3] in schedule_lower or today_str in schedule_lower:
                    # Check if there's ANY calendar session for today (any status)
                    cal_session = session.query(CalendarSession)\
                        .filter(
                            CalendarSession.student_id == student.id,
                            CalendarSession.session_date >= datetime.combine(today, datetime.min.time()),
                            CalendarSession.session_date < datetime.combine(today, datetime.max.time()),
                            CalendarSession.is_one_time == False
                        )\
                        .first()
                    
                    # Skip if cancelled or deleted
                    if cal_session and cal_session.status in ['cancelled', 'deleted']:
                        continue
                    
                    # Create calendar session if it doesn't exist
                    if not cal_session:
                        cal_session = CalendarSession(
                            student_id=student.id,
                            session_date=datetime.combine(today, datetime.min.time().replace(hour=12)),
                            status='scheduled',
                            is_one_time=False
                        )
                        session.add(cal_session)
                        session.flush()  # Get the ID
                    
                    # Get the most recent report for this student
                    last_report = session.query(Report)\
                        .filter(Report.student_id == student.id)\
                        .order_by(Report.session_date.desc())\
                        .first()
                    
                    session_info = {
                        'session_id': cal_session.id,
                        'student_id': student.id,
                        'student_name': student.name,
                        'subject': student.subject,
                        'schedule': student.recurring_schedule,
                        'notes': cal_session.notes,
                        'next_session_notes': last_report.next_session_notes if last_report else None,
                        'has_prep_notes': bool(last_report and last_report.next_session_notes),
                        'session_time': cal_session.session_date  # For sorting
                    }
                    today_sessions.append(session_info)
        
        session.commit()  # Commit any new calendar sessions created
        
        # Also check one-time calendar_sessions for today
        one_time_sessions = session.query(CalendarSession)\
            .filter(
                CalendarSession.session_date >= datetime.combine(today, datetime.min.time()),
                CalendarSession.session_date < datetime.combine(today, datetime.max.time()),
                CalendarSession.status.in_(['scheduled', 'rescheduled', 'completed']),
                CalendarSession.is_one_time == True
            )\
            .all()
        
        for cal_session in one_time_sessions:
            student = session.query(Student).filter(Student.id == cal_session.student_id).first()
            if student:
                last_report = session.query(Report)\
                    .filter(Report.student_id == student.id)\
                    .order_by(Report.session_date.desc())\
                    .first()
                
                session_info = {
                    'session_id': cal_session.id,
                    'student_id': student.id,
                    'student_name': student.name,
                    'subject': student.subject,
                    'schedule': cal_session.session_date.strftime('%I:%M %p'),
                    'notes': cal_session.notes,
                    'next_session_notes': last_report.next_session_notes if last_report else None,
                    'has_prep_notes': bool(last_report and last_report.next_session_notes),
                    'session_time': cal_session.session_date  # For sorting
                }
                today_sessions.append(session_info)
        
        # Sort all sessions by time
        today_sessions.sort(key=lambda s: s.get('session_time', datetime.combine(today, datetime.min.time())))
        
        return jsonify({
            'date': today.isoformat(),
            'sessions': today_sessions,
            'total_sessions': len(today_sessions)
        })
        
    except Exception as e:
        print(f"Error getting today's sessions: {e}")
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()


# ============================================
# STATISTICS ENDPOINTS
# ============================================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    session = get_session(DB_PATH)
    try:
        total_students = session.query(Student).filter(Student.active == True).count()
        total_reports = session.query(Report).count()
        draft_reports = session.query(Report).filter(Report.status == 'draft').count()
        total_samples = session.query(Report).filter(Report.source == 'uploaded').count()
        
        return jsonify({
            'total_students': total_students,
            'total_reports': total_reports,
            'draft_reports': draft_reports,
            'total_samples': total_samples
        })
    finally:
        session.close()


# ============================================
# CALENDAR SESSION ENDPOINTS
# ============================================

@app.route('/api/calendar-sessions/for-date', methods=['GET'])
def get_calendar_session_for_date():
    """Get calendar session for a specific student and date"""
    session = get_session(DB_PATH)
    student_id = request.args.get('student_id')
    session_date = request.args.get('session_date')
    
    if not student_id or not session_date:
        return jsonify({'error': 'student_id and session_date required'}), 400
    
    try:
        # Parse the date
        target_date = datetime.fromisoformat(session_date.replace('Z', '+00:00')).date()
        
        # Find calendar session for this student on this date
        cal_session = session.query(CalendarSession)\
            .filter(CalendarSession.student_id == int(student_id))\
            .filter(CalendarSession.session_date >= datetime.combine(target_date, datetime.min.time()))\
            .filter(CalendarSession.session_date < datetime.combine(target_date, datetime.max.time()))\
            .first()
        
        if cal_session:
            return jsonify(cal_session.to_dict())
        else:
            return jsonify({'notes': None})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()


@app.route('/api/calendar-sessions', methods=['GET'])
def get_calendar_sessions():
    """Get all calendar sessions (optionally filtered by date range)"""
    session = get_session(DB_PATH)
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = session.query(CalendarSession)
        
        # Don't filter here - let frontend handle display logic
        # This way deleted overrides can be detected to hide recurring sessions
        
        if start_date:
            # Handle ISO format with 'Z' suffix (replace Z with +00:00 for Python compatibility)
            start_date_parsed = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(CalendarSession.session_date >= start_date_parsed)
        if end_date:
            # Handle ISO format with 'Z' suffix
            end_date_parsed = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(CalendarSession.session_date <= end_date_parsed)
        
        sessions = query.order_by(CalendarSession.session_date).all()
        return jsonify([s.to_dict() for s in sessions])
    finally:
        session.close()


@app.route('/api/calendar-sessions', methods=['POST'])
def create_calendar_session():
    """Create a new calendar session"""
    data = request.json
    session = get_session(DB_PATH)
    
    try:
        session_date_str = data.get('session_date')
        # Handle ISO format with 'Z' suffix
        session_date = datetime.fromisoformat(session_date_str.replace('Z', '+00:00'))
        
        calendar_session = CalendarSession(
            student_id=data.get('student_id'),
            session_date=session_date,
            duration_hours=data.get('duration_hours', '1'),
            status=data.get('status', 'scheduled'),
            notes=data.get('notes'),
            is_one_time=data.get('is_one_time', False)
        )
        
        session.add(calendar_session)
        session.commit()
        
        return jsonify(calendar_session.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()


@app.route('/api/calendar-sessions/<int:session_id>', methods=['PUT'])
def update_calendar_session(session_id):
    """Update a calendar session (cancel, reschedule, etc.)"""
    data = request.json
    db_session = get_session(DB_PATH)
    
    try:
        calendar_session = db_session.query(CalendarSession).filter(CalendarSession.id == session_id).first()
        if not calendar_session:
            return jsonify({'error': 'Calendar session not found'}), 404
        
        # Update fields
        if 'session_date' in data:
            # Handle ISO format with 'Z' suffix
            calendar_session.session_date = datetime.fromisoformat(data['session_date'].replace('Z', '+00:00'))
        if 'duration_hours' in data:
            calendar_session.duration_hours = data['duration_hours']
        if 'status' in data:
            calendar_session.status = data['status']
        if 'notes' in data:
            calendar_session.notes = data['notes']
        
        calendar_session.updated_at = datetime.utcnow()
        db_session.commit()
        
        return jsonify(calendar_session.to_dict())
    except Exception as e:
        db_session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db_session.close()


@app.route('/api/calendar-sessions/<int:session_id>', methods=['DELETE'])
def delete_calendar_session(session_id):
    """Delete a calendar session (hard delete - removes from database)"""
    db_session = get_session(DB_PATH)
    
    try:
        calendar_session = db_session.query(CalendarSession).filter(CalendarSession.id == session_id).first()
        if not calendar_session:
            return jsonify({'error': 'Calendar session not found'}), 404
        
        db_session.delete(calendar_session)
        db_session.commit()
        return jsonify({'message': 'Calendar session deleted successfully'})
    except Exception as e:
        db_session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db_session.close()


@app.route('/api/calendar-sessions/deleted', methods=['GET'])
def get_deleted_sessions():
    """Get all deleted sessions for restore functionality"""
    db_session = get_session(DB_PATH)
    try:
        deleted_sessions = db_session.query(CalendarSession)\
            .filter(CalendarSession.status == 'deleted')\
            .order_by(CalendarSession.session_date.desc())\
            .all()
        return jsonify([s.to_dict() for s in deleted_sessions])
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        db_session.close()


@app.route('/api/calendar-sessions/deleted/clear-all', methods=['DELETE'])
def clear_all_deleted_sessions():
    """Permanently delete all sessions marked as deleted"""
    db_session = get_session(DB_PATH)
    try:
        deleted_sessions = db_session.query(CalendarSession)\
            .filter(CalendarSession.status == 'deleted')\
            .all()
        
        count = len(deleted_sessions)
        for session in deleted_sessions:
            db_session.delete(session)
        
        db_session.commit()
        return jsonify({'message': f'{count} deleted sessions permanently removed'})
    except Exception as e:
        db_session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db_session.close()


@app.route('/api/calendar-sessions/<int:session_id>/permanent-delete', methods=['DELETE'])
def permanently_delete_session(session_id):
    """Permanently delete a specific deleted session"""
    db_session = get_session(DB_PATH)
    try:
        session_obj = db_session.query(CalendarSession)\
            .filter(CalendarSession.id == session_id)\
            .first()
        
        if not session_obj:
            return jsonify({'error': 'Session not found'}), 404
        
        db_session.delete(session_obj)
        db_session.commit()
        return jsonify({'message': 'Session permanently deleted'})
    except Exception as e:
        db_session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        db_session.close()


@app.route('/api/reports-needed', methods=['GET'])
def get_reports_needed():
    """Get sessions that need reports written"""
    db_session = get_session(DB_PATH)
    from datetime import timedelta
    
    try:
        # Get past sessions from last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        past_sessions = db_session.query(CalendarSession)\
            .filter(CalendarSession.session_date >= thirty_days_ago)\
            .filter(CalendarSession.session_date < datetime.now())\
            .filter(CalendarSession.status.in_(['completed', 'scheduled']))\
            .order_by(CalendarSession.session_date.desc())\
            .all()
        
        # Get all reports
        all_reports = db_session.query(Report).all()
        
        needs_reports = []
        
        for session in past_sessions:
            # Check if there's a finalized report for this session
            has_finalized_report = any(
                r.student_id == session.student_id and
                r.session_date.date() == session.session_date.date() and
                r.status == 'sent'
                for r in all_reports
            )
            
            if not has_finalized_report:
                # Check if there's a draft
                draft_report = next((
                    r for r in all_reports
                    if r.student_id == session.student_id and
                    r.session_date.date() == session.session_date.date() and
                    r.status == 'draft'
                ), None)
                
                needs_reports.append({
                    'session_id': session.id,
                    'student_id': session.student_id,
                    'student_name': session.student.name if session.student else 'Unknown',
                    'subject': session.student.subject if session.student else None,
                    'session_date': session.session_date.isoformat(),
                    'has_draft': draft_report is not None,
                    'draft_id': draft_report.id if draft_report else None,
                    'session_notes': session.notes
                })
        
        return jsonify(needs_reports)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        db_session.close()


# ============================================
# USER SETTINGS ENDPOINTS
# ============================================

@app.route('/api/user-settings', methods=['GET'])
def get_user_settings():
    """Get user/tutor profile settings"""
    session = get_session(DB_PATH)
    
    try:
        # Get or create user settings (there should only be one row)
        settings = session.query(UserSettings).first()
        
        if not settings:
            # Create default settings if none exist
            settings = UserSettings(
                tutor_name='Elizabeth',
                phone=None,
                email=None,
                default_include_contact=False
            )
            session.add(settings)
            session.commit()
        
        return jsonify(settings.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()


@app.route('/api/user-settings', methods=['PUT'])
def update_user_settings():
    """Update user/tutor profile settings"""
    data = request.json
    session = get_session(DB_PATH)
    
    try:
        settings = session.query(UserSettings).first()
        
        if not settings:
            # Create if doesn't exist
            settings = UserSettings()
            session.add(settings)
        
        # Update fields
        if 'tutor_name' in data:
            settings.tutor_name = data['tutor_name']
        if 'phone' in data:
            settings.phone = data['phone']
        if 'email' in data:
            settings.email = data['email']
        if 'default_include_contact' in data:
            settings.default_include_contact = data['default_include_contact']
        
        session.commit()
        return jsonify(settings.to_dict())
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()


# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    
    print(f"\n🎓 Sage Tutoring Report System")
    print(f"📊 Server running at http://{host}:{port}")
    print(f"🤖 AI Provider: {AI_PROVIDER}")
    print(f"💾 Database: {os.path.abspath(DB_PATH)}")
    print(f"💾 Database exists: {os.path.exists(DB_PATH)}\n")
    
    app.run(host=host, port=port, debug=True)
