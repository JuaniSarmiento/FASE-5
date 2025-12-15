from sqlalchemy import Column, String, Integer, Text, DateTime, Float, JSON
from sqlalchemy.sql import func
from backend.database.base import Base
import uuid

class Exercise(Base):
    __tablename__ = "exercises"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    difficulty_level = Column(Integer, nullable=False)  # 1-10
    starter_code = Column(Text, nullable=True)
    test_cases = Column(JSON, nullable=False)  # [{"input": ..., "expected_output": ...}]
    hints = Column(JSON, nullable=True)  # ["hint1", "hint2", ...]
    max_score = Column(Float, default=10.0)
    time_limit_seconds = Column(Integer, default=300)  # 5 minutos
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Exercise {self.title} (Level {self.difficulty_level})>"


class UserExerciseSubmission(Base):
    __tablename__ = "user_exercise_submissions"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    exercise_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=True, index=True)
    submitted_code = Column(Text, nullable=False)
    
    # Resultados de ejecución
    passed_tests = Column(Integer, default=0)
    total_tests = Column(Integer, default=0)
    execution_time_ms = Column(Integer, nullable=True)
    
    # Evaluación de IA
    ai_score = Column(Float, nullable=True)  # 0-10
    ai_feedback = Column(Text, nullable=True)
    code_quality_score = Column(Float, nullable=True)
    readability_score = Column(Float, nullable=True)
    efficiency_score = Column(Float, nullable=True)
    best_practices_score = Column(Float, nullable=True)
    
    # Metadata
    is_correct = Column(String, default="false")  # "true" si pasó todos los tests
    attempts = Column(Integer, default=1)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Submission {self.user_id[:8]} - Exercise {self.exercise_id[:8]}>"
