"""
Services package for AI-Native MVP

SPRINT 5 Services:
- CourseReportGenerator: Generate institutional reports (cohort summaries, risk dashboards)
- InstitutionalRiskManager: Manage risk alerts and remediation plans
"""

from .course_report_generator import CourseReportGenerator
from .institutional_risk_manager import InstitutionalRiskManager

__all__ = [
    "CourseReportGenerator",
    "InstitutionalRiskManager",
]
