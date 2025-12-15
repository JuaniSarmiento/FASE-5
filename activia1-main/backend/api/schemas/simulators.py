"""
Pydantic schemas for professional simulators (Sprint 6)

Provides request/response models for:
- Technical Interview Simulator (IT-IA)
- Incident Response Simulator (IR-IA)
- Scrum Master Simulator (SM-IA)
- Client Experience Simulator (CX-IA)
- DevSecOps Auditor (DSO-IA)
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

from .common import validate_uuid_format


# ============================================================================
# INTERVIEW SIMULATOR (IT-IA) - HU-EST-011
# ============================================================================


class InterviewStartRequest(BaseModel):
    """Request to start a technical interview simulation"""

    session_id: str = Field(..., description="AI-Native session ID")
    student_id: str = Field(..., description="Student ID")
    activity_id: Optional[str] = Field(None, description="Optional activity ID")
    interview_type: str = Field(
        ...,
        description="Type of interview: CONCEPTUAL, ALGORITHMIC, DESIGN, BEHAVIORAL",
    )
    difficulty_level: str = Field(
        "MEDIUM", description="Difficulty: EASY, MEDIUM, HARD"
    )

    @field_validator("interview_type")
    @classmethod
    def validate_interview_type(cls, v: str) -> str:
        valid_types = ["CONCEPTUAL", "ALGORITHMIC", "DESIGN", "BEHAVIORAL"]
        if v not in valid_types:
            raise ValueError(f"interview_type must be one of {valid_types}")
        return v

    @field_validator("difficulty_level")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        valid_levels = ["EASY", "MEDIUM", "HARD"]
        if v not in valid_levels:
            raise ValueError(f"difficulty_level must be one of {valid_levels}")
        return v


class InterviewQuestion(BaseModel):
    """A question in the interview"""

    question: str = Field(..., description="Question text")
    type: str = Field(..., description="Question type")
    expected_key_points: List[str] = Field(
        default_factory=list, description="Expected key points in answer"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class InterviewResponseRequest(BaseModel):
    """Student's response to an interview question"""

    interview_id: str = Field(..., description="Interview session ID")
    response: str = Field(..., min_length=10, description="Student's answer")


class InterviewEvaluation(BaseModel):
    """Evaluation of a student's response"""

    clarity_score: float = Field(..., ge=0.0, le=1.0)
    technical_accuracy: float = Field(..., ge=0.0, le=1.0)
    thinking_aloud: bool = Field(..., description="Did student think aloud?")
    key_points_covered: List[str] = Field(default_factory=list)


class InterviewCompleteRequest(BaseModel):
    """Request to complete an interview"""

    interview_id: str = Field(..., description="Interview session ID")


class InterviewResponse(BaseModel):
    """Response with interview details"""

    interview_id: str
    session_id: str
    student_id: str
    interview_type: str
    difficulty_level: str
    questions_asked: List[Dict[str, Any]]
    responses: List[Dict[str, Any]]
    evaluation_score: Optional[float] = None
    evaluation_breakdown: Optional[Dict[str, float]] = None
    feedback: Optional[str] = None
    duration_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime


# ============================================================================
# INCIDENT SIMULATOR (IR-IA) - HU-EST-012
# ============================================================================


class IncidentStartRequest(BaseModel):
    """Request to start an incident response simulation"""

    session_id: str = Field(..., description="AI-Native session ID")
    student_id: str = Field(..., description="Student ID")
    activity_id: Optional[str] = Field(None, description="Optional activity ID")
    incident_type: str = Field(
        ...,
        description="Type: API_ERROR, PERFORMANCE, SECURITY, DATABASE, DEPLOYMENT",
    )
    severity: str = Field("HIGH", description="Severity: LOW, MEDIUM, HIGH, CRITICAL")

    @field_validator("incident_type")
    @classmethod
    def validate_incident_type(cls, v: str) -> str:
        valid_types = ["API_ERROR", "PERFORMANCE", "SECURITY", "DATABASE", "DEPLOYMENT"]
        if v not in valid_types:
            raise ValueError(f"incident_type must be one of {valid_types}")
        return v

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        valid_severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        if v not in valid_severities:
            raise ValueError(f"severity must be one of {valid_severities}")
        return v


class DiagnosisStepRequest(BaseModel):
    """Student's diagnosis step"""

    incident_id: str = Field(..., description="Incident simulation ID")
    action: str = Field(..., min_length=10, description="Action taken")
    finding: Optional[str] = Field(None, description="Finding from this action")


class IncidentSolutionRequest(BaseModel):
    """Student's proposed solution for the incident"""

    incident_id: str = Field(..., description="Incident simulation ID")
    solution_proposed: str = Field(..., min_length=50, description="Proposed solution")
    root_cause_identified: str = Field(
        ..., min_length=20, description="Identified root cause"
    )
    post_mortem: str = Field(
        ..., min_length=100, description="Post-mortem documentation"
    )


class IncidentResponse(BaseModel):
    """Response with incident details"""

    incident_id: str
    session_id: str
    student_id: str
    incident_type: str
    severity: str
    incident_description: str
    simulated_logs: Optional[str] = None
    simulated_metrics: Optional[Dict[str, Any]] = None
    diagnosis_process: List[Dict[str, Any]]
    solution_proposed: Optional[str] = None
    root_cause_identified: Optional[str] = None
    time_to_diagnose_minutes: Optional[int] = None
    time_to_resolve_minutes: Optional[int] = None
    post_mortem: Optional[str] = None
    evaluation: Optional[Dict[str, float]] = None
    created_at: datetime
    updated_at: datetime


# ============================================================================
# SCRUM MASTER SIMULATOR (SM-IA) - HU-EST-010
# ============================================================================


class DailyStandupRequest(BaseModel):
    """Request to participate in daily standup"""

    session_id: str = Field(..., description="AI-Native session ID")
    student_id: str = Field(..., description="Student ID")
    activity_id: Optional[str] = Field(None, description="Sprint activity ID")
    what_did_yesterday: str = Field(..., min_length=10, description="Yesterday's work")
    what_will_do_today: str = Field(..., min_length=10, description="Today's plan")
    impediments: Optional[str] = Field(None, description="Any impediments")


class DailyStandupResponse(BaseModel):
    """Scrum Master's response to daily standup"""

    feedback: str = Field(..., description="SM-IA feedback")
    questions: List[str] = Field(
        default_factory=list, description="Follow-up questions"
    )
    detected_issues: List[str] = Field(
        default_factory=list, description="Detected issues"
    )
    suggestions: List[str] = Field(default_factory=list, description="Suggestions")


# ============================================================================
# CLIENT SIMULATOR (CX-IA) - HU-EST-013
# ============================================================================


class ClientRequirementRequest(BaseModel):
    """Request to get client requirements"""

    session_id: str = Field(..., description="AI-Native session ID")
    student_id: str = Field(..., description="Student ID")
    activity_id: Optional[str] = Field(None, description="Project activity ID")
    project_type: str = Field(
        "WEB_APP", description="Project type: WEB_APP, MOBILE_APP, API, DESKTOP"
    )


class ClientClarificationRequest(BaseModel):
    """Student's clarification question to client"""

    session_id: str = Field(..., description="Session ID")
    question: str = Field(..., min_length=10, description="Clarification question")


class ClientResponse(BaseModel):
    """Client's response"""

    response: str = Field(..., description="Client's answer")
    additional_requirements: Optional[List[str]] = Field(
        None, description="New requirements revealed"
    )
    evaluation: Dict[str, float] = Field(
        ..., description="Soft skills evaluation (empathy, clarity, professionalism)"
    )


# ============================================================================
# DEVSECOPS AUDITOR (DSO-IA) - HU-EST-014
# ============================================================================


class SecurityAuditRequest(BaseModel):
    """Request for security audit"""

    session_id: str = Field(..., description="AI-Native session ID")
    student_id: str = Field(..., description="Student ID")
    activity_id: Optional[str] = Field(None, description="Activity ID")
    code: str = Field(..., min_length=50, description="Code to audit")
    language: str = Field(
        "python", description="Programming language: python, javascript, java, etc."
    )


class SecurityVulnerability(BaseModel):
    """A detected security vulnerability"""

    severity: str = Field(
        ..., description="Severity: CRITICAL, HIGH, MEDIUM, LOW, INFO"
    )
    vulnerability_type: str = Field(
        ..., description="Type: SQL_INJECTION, XSS, CSRF, SECRETS, etc."
    )
    line_number: Optional[int] = Field(None, description="Line number in code")
    description: str = Field(..., description="Vulnerability description")
    recommendation: str = Field(..., description="How to fix")
    cwe_id: Optional[str] = Field(None, description="CWE ID (e.g., CWE-89)")
    owasp_category: Optional[str] = Field(None, description="OWASP Top 10 category")


class SecurityAuditResponse(BaseModel):
    """Security audit results"""

    audit_id: str = Field(..., description="Audit session ID")
    total_vulnerabilities: int = Field(..., description="Total found")
    critical_count: int = Field(default=0)
    high_count: int = Field(default=0)
    medium_count: int = Field(default=0)
    low_count: int = Field(default=0)
    vulnerabilities: List[SecurityVulnerability] = Field(
        default_factory=list, description="List of vulnerabilities"
    )
    overall_security_score: float = Field(
        ..., ge=0.0, le=10.0, description="Security score (0-10)"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="General recommendations"
    )
    compliant_with_owasp: bool = Field(
        ..., description="Compliant with OWASP Top 10"
    )