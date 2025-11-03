"""
Database models for the Sage Tutoring Report System
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()


class UserSettings(Base):
    """User/Tutor profile settings"""
    __tablename__ = 'user_settings'
    
    id = Column(Integer, primary_key=True)
    tutor_name = Column(String(100), default='Elizabeth')
    phone = Column(String(20))
    email = Column(String(100))
    default_include_contact = Column(Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tutor_name': self.tutor_name,
            'phone': self.phone,
            'email': self.email,
            'default_include_contact': self.default_include_contact
        }

class Student(Base):
    """Student information and preferences"""
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    subject = Column(String(100))  # Main subject (e.g., "SAT Math", "AP Biology")
    grade_level = Column(String(50))
    school = Column(String(100))  # Student's school
    teacher = Column(String(100))  # Student's teacher at school
    parent_name = Column(String(100))  # Parent/guardian name for report greeting
    notes = Column(Text)  # Important information to remember
    recurring_schedule = Column(String(200))  # e.g., "Mondays 4pm, Thursdays 6pm"
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    reports = relationship("Report", back_populates="student", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'grade_level': self.grade_level,
            'school': self.school,
            'teacher': self.teacher,
            'parent_name': self.parent_name,
            'notes': self.notes,
            'recurring_schedule': self.recurring_schedule,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'total_reports': len(self.reports) if self.reports else 0
        }


class Report(Base):
    """Session reports for students"""
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    session_date = Column(DateTime, nullable=False)
    duration_hours = Column(String(20), default='1')  # Session length (e.g., "1", "0.5", "1.5")
    topics_covered = Column(Text)  # User input: what topics were covered
    activities = Column(Text)  # User input: what we did during session
    notes = Column(Text)  # User input: additional notes or gaps to fill
    next_session_notes = Column(Text)  # User input: things to remember for next session
    ai_generated_report = Column(Text)  # Full AI-generated report
    final_report = Column(Text)  # User's edited final version
    status = Column(String(20), default='draft')  # draft, sent
    use_for_training = Column(Boolean, default=False)  # whether to use this report for AI training
    source = Column(String(20), default='created')  # created, uploaded, imported
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="reports")
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'subject': self.student.subject if self.student else None,
            'session_date': self.session_date.isoformat() if self.session_date else None,
            'duration_hours': self.duration_hours,
            'topics_covered': self.topics_covered,
            'activities': self.activities,
            'notes': self.notes,
            'next_session_notes': self.next_session_notes,
            'ai_generated_report': self.ai_generated_report,
            'final_report': self.final_report,
            'status': self.status,
            'use_for_training': self.use_for_training,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SampleReport(Base):
    """Sample reports to train the AI on writing style"""
    __tablename__ = 'sample_reports'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(200))
    content = Column(Text, nullable=False)
    
    # Metadata from LearnSpeed or manual entry
    student_name = Column(String(100))  # Student name from the session
    session_date = Column(DateTime)  # When the tutoring session occurred
    subject = Column(String(100))  # Subject taught (e.g., "Geometry", "Multi. Subject")
    session_type = Column(String(100))  # e.g., "One-on-one Tutoring 2025"
    duration_hours = Column(String(20))  # e.g., "1", "0.5"
    attendance_status = Column(String(50))  # e.g., "Attended", "Courtesy Cancel"
    
    # Import tracking
    source = Column(String(50), default='manual')  # 'manual', 'learnspeed', 'file_upload'
    learnspeed_session_id = Column(String(100))  # Unique identifier to avoid duplicates
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'content': self.content,
            'student_name': self.student_name,
            'session_date': self.session_date.isoformat() if self.session_date else None,
            'subject': self.subject,
            'session_type': self.session_type,
            'duration_hours': self.duration_hours,
            'attendance_status': self.attendance_status,
            'source': self.source,
            'learnspeed_session_id': self.learnspeed_session_id,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }


class CalendarSession(Base):
    """Actual calendar sessions - overrides/supplements recurring schedule"""
    __tablename__ = 'calendar_sessions'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    session_date = Column(DateTime, nullable=False)  # Specific date/time of session
    duration_hours = Column(String(20), default='1')
    status = Column(String(20), default='scheduled')  # scheduled, cancelled, rescheduled
    notes = Column(Text)  # Special notes for this session
    is_one_time = Column(Boolean, default=False)  # True if not part of recurring schedule
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student")
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'session_date': self.session_date.isoformat() if self.session_date else None,
            'duration_hours': self.duration_hours,
            'status': self.status,
            'notes': self.notes,
            'is_one_time': self.is_one_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# Database initialization
def init_db(db_path='database/sage_reports.db'):
    """Initialize the database"""
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Create engine
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    Session = sessionmaker(bind=engine)
    
    return engine, Session


def get_session(db_path='database/sage_reports.db'):
    """Get a database session"""
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    return Session()
