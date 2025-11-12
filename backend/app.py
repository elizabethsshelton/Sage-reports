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

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database
# Use absolute path to project root database
DB_PATH = os.getenv('DATABASE_PATH', '/Users/ellizabethshelton/Desktop/Sage/Sage Reports/database/sage_reports.db')
init_db(DB_PATH)

# Initialize AI service
AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai')
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
        
        # Generate suggestions with cursor context
        suggestions = ai_service.suggest_sentences(
            report_text=report_text,
            student_name=student.name if student else 'the student',
            subject=student.subject if student else 'the subject',
            cursor_position=cursor_position
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
        
        # Get current report's opening/closing for reference
        current_text = report.final_report or report.ai_generated_report or ''
        current_sentence = ""
        if current_text:
            if sentence_type == 'opening':
                current_sentence = current_text.split('.')[0] + '.' if '.' in current_text else current_text[:100]
            else:
                sentences = current_text.strip().split('.')
                current_sentence = sentences[-2] + '.' if len(sentences) > 1 else sentences[-1]
        
        # Get previous report's sentence for reference
        previous_sentence = ""
        if previous_texts:
            prev_text = previous_texts[0]
            if sentence_type == 'opening':
                previous_sentence = prev_text.split('.')[0] + '.' if '.' in prev_text else prev_text[:100]
            else:
                sentences = prev_text.strip().split('.')
                previous_sentence = sentences[-2] + '.' if len(sentences) > 1 else sentences[-1]
        
        # Generate suggestions
        suggestions = ai_service.suggest_opening_closing(
            student_name=student.name,
            previous_reports=previous_texts,
            sentence_type=sentence_type
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
    session_db = get_session(DB_PATH)
    
    try:
        report = session_db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Get current report text
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
                'ai_extracted': [],
                'last_session_date': None
            })
        
        # Get manual next_session_notes
        manual_notes = last_report.next_session_notes
        
        # Extract AI action items from the report text
        ai_extracted = []
        report_text = last_report.final_report or last_report.ai_generated_report
        
        if report_text and ai_service.client:
            # Use AI to extract action items
            try:
                prompt = f"""Analyze this tutoring session report and extract ONLY forward-looking action items specifically mentioned for the NEXT session.

Report:
{report_text}

CRITICAL: Only extract items that explicitly refer to FUTURE sessions/plans, such as:
- "Has a test on [date]" → upcoming assessment
- "Next time we'll focus on..." → explicit next session plan
- "Student needs to practice X before next session" → homework/prep
- "Will continue working on Y" → ongoing topic
- "Bring Z next time" → specific material request

DO NOT extract:
- General struggles from THIS session (unless explicitly mentioned as needing follow-up)
- Past accomplishments
- Generic suggestions without future context
- Descriptions of what happened in this session

REQUIREMENTS:
- Maximum 3 items (if report doesn't mention specific next-session plans, return [])
- Be DIRECT and CONCISE
- Include brief context (WHAT + WHY)
- Skip fluff and platitudes

Good examples (forward-looking):
- "Geometry test Friday - review angle relationships"
- "Continue factoring next time; still struggling with GCF"
- "Bring completed homework packet to review together"

Bad examples (about THIS session, not NEXT):
- "Student worked on proofs today"
- "Struggled with complex diagrams in this session"
- "Showed improvement in algebra"

Return JSON array:
[
  {{"reminder": "concise forward-looking reminder", "source": "1-2 sentence excerpt mentioning next session"}},
]

Return 0-3 items. If nothing forward-looking mentioned, return []."""

                if ai_service.provider == 'openai':
                    response = ai_service.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3,
                        max_tokens=300
                    )
                    result = response.choices[0].message.content.strip()
                else:  # anthropic
                    response = ai_service.client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=300,
                        temperature=0.3,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    result = response.content[0].text.strip()
                
                # Parse JSON response
                import json
                import re
                
                # Clean up response - remove markdown code blocks if present
                result = result.strip()
                if result.startswith('```'):
                    result = re.sub(r'```(?:json)?\s*|\s*```', '', result).strip()
                
                print(f"Reminders extraction raw response: {result}")
                
                if not result or result == '[]':
                    ai_extracted = []
                else:
                    ai_extracted = json.loads(result)
                    if not isinstance(ai_extracted, list):
                        ai_extracted = []
                    # Validate format: should be list of objects with 'reminder' and 'source' keys
                    # But also support old string format for backwards compatibility
                    validated = []
                    for item in ai_extracted:
                        if isinstance(item, str):
                            validated.append({'reminder': item, 'source': None})
                        elif isinstance(item, dict) and 'reminder' in item:
                            validated.append(item)
                    ai_extracted = validated[:3]  # Limit to 3
                    print(f"Extracted reminders: {ai_extracted}")
                
            except Exception as e:
                print(f"Error extracting action items: {e}")
                ai_extracted = []
        
        return jsonify({
            'has_reminders': bool(manual_notes or ai_extracted),
            'manual_notes': manual_notes,
            'ai_extracted': ai_extracted,
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
            query = query.filter(CalendarSession.session_date >= datetime.fromisoformat(start_date))
        if end_date:
            query = query.filter(CalendarSession.session_date <= datetime.fromisoformat(end_date))
        
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
        calendar_session = CalendarSession(
            student_id=data.get('student_id'),
            session_date=datetime.fromisoformat(data.get('session_date')),
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
            calendar_session.session_date = datetime.fromisoformat(data['session_date'])
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
