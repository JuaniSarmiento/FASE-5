"""
CourseReportGenerator - SPRINT 5 HU-DOC-009

Servicio para generar reportes institucionales a nivel de curso/cohorte.

Funcionalidades:
- Agregar datos de múltiples estudiantes en un período
- Generar reportes de:
  - Resumen de cohorte (estadísticas generales)
  - Dashboard de riesgos (distribución y estudiantes en riesgo)
  - Distribución de competencias
- Exportar a múltiples formatos (JSON, PDF, XLSX)
- Recomendaciones institucionales automáticas

Audiencia: Docentes, coordinadores, administradores educativos
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any
from uuid import uuid4
import json

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..database.models import (
    SessionDB,
    CognitiveTraceDB,
    RiskDB,
    EvaluationDB,
    StudentProfileDB,
)
from ..database.repositories import CourseReportRepository
from ..models.risk import RiskLevel, RiskDimension

logger = logging.getLogger(__name__)


class CourseReportGenerator:
    """
    Generador de reportes institucionales a nivel curso/cohorte

    Agrega datos de múltiples estudiantes y genera insights para docentes
    y administradores educativos.
    """

    def __init__(
        self,
        db_session: Session,
        report_repository: Optional[CourseReportRepository] = None,
    ):
        """
        Initialize CourseReportGenerator

        Args:
            db_session: SQLAlchemy database session
            report_repository: Repository for persisting reports (optional)
        """
        self.db = db_session
        self.report_repo = report_repository or CourseReportRepository(db_session)

    def generate_cohort_summary(
        self,
        course_id: str,
        teacher_id: str,
        student_ids: List[str],
        period_start: datetime,
        period_end: datetime,
        export_format: str = "json",
    ) -> Dict[str, Any]:
        """
        Generate cohort summary report

        Args:
            course_id: Course identifier (e.g., "PROG2_2025_1C")
            teacher_id: Teacher generating the report
            student_ids: List of student IDs in the cohort
            period_start: Start of reporting period
            period_end: End of reporting period
            export_format: Format for export (json, pdf, xlsx)

        Returns:
            Report data dict with:
            - summary_stats: Aggregate statistics
            - competency_distribution: Competency level counts
            - risk_distribution: Risk level counts
            - student_summaries: Individual student data
            - recommendations: Institutional recommendations
        """
        logger.info(
            "Generating cohort summary report",
            extra={
                "course_id": course_id,
                "teacher_id": teacher_id,
                "student_count": len(student_ids),
                "period": f"{period_start.date()} to {period_end.date()}",
            },
        )

        # Aggregate summary statistics
        summary_stats = self._aggregate_summary_stats(
            student_ids, period_start, period_end
        )

        # Competency distribution
        competency_distribution = self._aggregate_competency_distribution(
            student_ids, period_start, period_end
        )

        # Risk distribution
        risk_distribution = self._aggregate_risk_distribution(
            student_ids, period_start, period_end
        )

        # Top risks
        top_risks = self._get_top_risks(student_ids, period_start, period_end, limit=5)

        # Student-level summaries
        student_summaries = self._generate_student_summaries(
            student_ids, period_start, period_end
        )

        # Institutional recommendations
        recommendations = self._generate_institutional_recommendations(
            summary_stats, competency_distribution, risk_distribution, top_risks
        )

        # Students requiring intervention
        at_risk_students = self._identify_at_risk_students(student_summaries)

        # Persist report to database
        report = self.report_repo.create(
            course_id=course_id,
            teacher_id=teacher_id,
            report_type="cohort_summary",
            period_start=period_start,
            period_end=period_end,
            summary_stats=summary_stats,
            competency_distribution=competency_distribution,
            risk_distribution=risk_distribution,
            top_risks=top_risks,
            student_summaries=student_summaries,
            institutional_recommendations=recommendations,
            at_risk_students=at_risk_students,
            format=export_format,
        )

        logger.info(
            "Cohort summary report generated",
            extra={
                "report_id": report.id,
                "total_students": len(student_ids),
                "at_risk_count": len(at_risk_students),
            },
        )

        return {
            "report_id": report.id,
            "course_id": course_id,
            "teacher_id": teacher_id,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "summary_stats": summary_stats,
            "competency_distribution": competency_distribution,
            "risk_distribution": risk_distribution,
            "top_risks": top_risks,
            "student_summaries": student_summaries,
            "institutional_recommendations": recommendations,
            "at_risk_students": at_risk_students,
        }

    def generate_risk_dashboard(
        self,
        course_id: str,
        teacher_id: str,
        student_ids: List[str],
        period_start: datetime,
        period_end: datetime,
    ) -> Dict[str, Any]:
        """
        Generate risk-focused dashboard

        Provides detailed risk analysis for proactive intervention.

        Args:
            course_id: Course identifier
            teacher_id: Teacher generating the report
            student_ids: List of student IDs
            period_start: Start of period
            period_end: End of period

        Returns:
            Risk dashboard data
        """
        logger.info(
            "Generating risk dashboard",
            extra={"course_id": course_id, "student_count": len(student_ids)},
        )

        # Risk distribution by level
        risk_distribution = self._aggregate_risk_distribution(
            student_ids, period_start, period_end
        )

        # Risk distribution by dimension
        dimension_distribution = self._aggregate_risk_by_dimension(
            student_ids, period_start, period_end
        )

        # Top risks with details
        top_risks = self._get_top_risks(
            student_ids, period_start, period_end, limit=10
        )

        # Students by risk level
        students_by_risk_level = self._categorize_students_by_risk(
            student_ids, period_start, period_end
        )

        # Risk trends over time
        risk_trends = self._analyze_risk_trends(
            student_ids, period_start, period_end
        )

        # Critical students (high/critical risks) - keys are lowercase
        critical_students = [
            s
            for s in students_by_risk_level.get("critical", [])
            + students_by_risk_level.get("high", [])
        ]

        # Generate recommendations
        summary_stats = self._aggregate_summary_stats(
            student_ids, period_start, period_end
        )
        competency_dist = self._aggregate_competency_distribution(
            student_ids, period_start, period_end
        )
        recommendations = self._generate_institutional_recommendations(
            summary_stats, competency_dist, risk_distribution, top_risks
        )

        # Persist report
        report = self.report_repo.create(
            course_id=course_id,
            teacher_id=teacher_id,
            report_type="risk_dashboard",
            period_start=period_start,
            period_end=period_end,
            summary_stats={
                "total_students": len(student_ids),
                "students_with_risks": len(
                    set(
                        r.student_id
                        for r in self.db.query(RiskDB)
                        .filter(
                            RiskDB.student_id.in_(student_ids),
                            RiskDB.created_at >= period_start,
                            RiskDB.created_at <= period_end,
                        )
                        .all()
                    )
                ),
            },
            competency_distribution=competency_dist,
            risk_distribution=risk_distribution,
            top_risks=top_risks,
            student_summaries=[],
            institutional_recommendations=recommendations,
            at_risk_students=critical_students,
            format="json",
        )

        logger.info(
            "Risk dashboard generated",
            extra={
                "report_id": report.id,
                "critical_students": len(critical_students),
            },
        )

        return {
            "report_id": report.id,
            "course_id": course_id,
            "risk_distribution": risk_distribution,
            "dimension_distribution": dimension_distribution,
            "top_risks": top_risks,
            "students_by_risk_level": students_by_risk_level,
            "risk_trends": risk_trends,
            "critical_students": critical_students,
            "recommendations": recommendations,
        }

    def export_report_to_json(self, report_id: str, output_path: str) -> str:
        """
        Export report to JSON file

        Args:
            report_id: Report ID
            output_path: Output file path

        Returns:
            Path to exported file
        """
        report = self.report_repo.get_by_id(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")

        data = {
            "report_id": report.id,
            "course_id": report.course_id,
            "teacher_id": report.teacher_id,
            "report_type": report.report_type,
            "period_start": report.period_start.isoformat(),
            "period_end": report.period_end.isoformat(),
            "generated_at": report.created_at.isoformat(),
            "summary_stats": report.summary_stats,
            "competency_distribution": report.competency_distribution,
            "risk_distribution": report.risk_distribution,
            "top_risks": report.top_risks,
            "student_summaries": report.student_summaries,
            "institutional_recommendations": report.institutional_recommendations,
            "at_risk_students": report.at_risk_students,
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Update report with export info
        self.report_repo.mark_exported(report_id, str(output_file))

        logger.info(
            "Report exported to JSON",
            extra={"report_id": report_id, "output_path": str(output_file)},
        )
        return str(output_file)

    # ==========================================================================
    # PRIVATE AGGREGATION METHODS
    # ==========================================================================

    def _aggregate_summary_stats(
        self, student_ids: List[str], period_start: datetime, period_end: datetime
    ) -> Dict[str, Any]:
        """Aggregate summary statistics for cohort"""
        # Total sessions
        total_sessions = (
            self.db.query(SessionDB)
            .filter(
                SessionDB.student_id.in_(student_ids),
                SessionDB.start_time >= period_start,
                SessionDB.start_time <= period_end,
            )
            .count()
        )

        # Total interactions (cognitive traces)
        total_interactions = (
            self.db.query(CognitiveTraceDB)
            .filter(
                CognitiveTraceDB.student_id.in_(student_ids),
                CognitiveTraceDB.created_at >= period_start,
                CognitiveTraceDB.created_at <= period_end,
            )
            .count()
        )

        # Average AI dependency
        avg_ai_dependency = (
            self.db.query(func.avg(CognitiveTraceDB.ai_involvement))
            .filter(
                CognitiveTraceDB.student_id.in_(student_ids),
                CognitiveTraceDB.created_at >= period_start,
                CognitiveTraceDB.created_at <= period_end,
            )
            .scalar()
            or 0.0
        )

        # Total risks
        total_risks = (
            self.db.query(RiskDB)
            .filter(
                RiskDB.student_id.in_(student_ids),
                RiskDB.created_at >= period_start,
                RiskDB.created_at <= period_end,
            )
            .count()
        )

        return {
            "total_students": len(student_ids),
            "total_sessions": total_sessions,
            "total_interactions": total_interactions,
            "avg_sessions_per_student": round(total_sessions / len(student_ids), 2)
            if student_ids
            else 0,
            "avg_interactions_per_student": round(
                total_interactions / len(student_ids), 2
            )
            if student_ids
            else 0,
            "avg_ai_dependency": round(float(avg_ai_dependency), 3),
            "total_risks": total_risks,
        }

    def _aggregate_competency_distribution(
        self, student_ids: List[str], period_start: datetime, period_end: datetime
    ) -> Dict[str, int]:
        """Get distribution of competency levels"""
        evaluations = (
            self.db.query(
                EvaluationDB.overall_competency_level,
                func.count(EvaluationDB.id).label("count"),
            )
            .filter(
                EvaluationDB.student_id.in_(student_ids),
                EvaluationDB.created_at >= period_start,
                EvaluationDB.created_at <= period_end,
            )
            .group_by(EvaluationDB.overall_competency_level)
            .all()
        )

        distribution = {level: count for level, count in evaluations}

        # Ensure all levels are present
        for level in ["BASICO", "INTERMEDIO", "AVANZADO", "EXPERTO"]:
            if level not in distribution:
                distribution[level] = 0

        return distribution

    def _aggregate_risk_distribution(
        self, student_ids: List[str], period_start: datetime, period_end: datetime
    ) -> Dict[str, int]:
        """Get distribution of risk levels"""
        risks = (
            self.db.query(RiskDB.risk_level, func.count(RiskDB.id).label("count"))
            .filter(
                RiskDB.student_id.in_(student_ids),
                RiskDB.created_at >= period_start,
                RiskDB.created_at <= period_end,
            )
            .group_by(RiskDB.risk_level)
            .all()
        )

        distribution = {level: count for level, count in risks}

        # Ensure all levels are present (DB stores lowercase)
        for level in ["low", "medium", "high", "critical"]:
            if level not in distribution:
                distribution[level] = 0

        return distribution

    def _aggregate_risk_by_dimension(
        self, student_ids: List[str], period_start: datetime, period_end: datetime
    ) -> Dict[str, int]:
        """Get distribution of risks by dimension"""
        risks = (
            self.db.query(RiskDB.dimension, func.count(RiskDB.id).label("count"))
            .filter(
                RiskDB.student_id.in_(student_ids),
                RiskDB.created_at >= period_start,
                RiskDB.created_at <= period_end,
            )
            .group_by(RiskDB.dimension)
            .all()
        )

        return {dimension: count for dimension, count in risks}

    def _get_top_risks(
        self,
        student_ids: List[str],
        period_start: datetime,
        period_end: datetime,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get top N most frequent risk types"""
        risks = (
            self.db.query(
                RiskDB.risk_type,
                RiskDB.dimension,
                func.count(RiskDB.id).label("count"),
            )
            .filter(
                RiskDB.student_id.in_(student_ids),
                RiskDB.created_at >= period_start,
                RiskDB.created_at <= period_end,
            )
            .group_by(RiskDB.risk_type, RiskDB.dimension)
            .order_by(func.count(RiskDB.id).desc())
            .limit(limit)
            .all()
        )

        return [
            {"risk_type": risk_type, "dimension": dimension, "count": count}
            for risk_type, dimension, count in risks
        ]

    def _generate_student_summaries(
        self, student_ids: List[str], period_start: datetime, period_end: datetime
    ) -> List[Dict[str, Any]]:
        """
        Generate individual student summaries

        FIX Cortez22 DEFECTO 6.1: Replaced N+1 queries with batch loading.
        Original: 5 queries per student (N*5 queries total)
        Fixed: 5 batch queries total regardless of student count
        """
        if not student_ids:
            return []

        # Batch query 1: Sessions count per student
        sessions_query = (
            self.db.query(
                SessionDB.student_id,
                func.count(SessionDB.id).label("count")
            )
            .filter(
                SessionDB.student_id.in_(student_ids),
                SessionDB.start_time >= period_start,
                SessionDB.start_time <= period_end,
            )
            .group_by(SessionDB.student_id)
            .all()
        )
        sessions_by_student = {s.student_id: s.count for s in sessions_query}

        # Batch query 2: AI dependency per student
        ai_dependency_query = (
            self.db.query(
                CognitiveTraceDB.student_id,
                func.avg(CognitiveTraceDB.ai_involvement).label("avg_ai")
            )
            .filter(
                CognitiveTraceDB.student_id.in_(student_ids),
                CognitiveTraceDB.created_at >= period_start,
                CognitiveTraceDB.created_at <= period_end,
            )
            .group_by(CognitiveTraceDB.student_id)
            .all()
        )
        ai_dependency_by_student = {a.student_id: float(a.avg_ai or 0.0) for a in ai_dependency_query}

        # Batch query 3: Latest evaluation per student (using subquery for latest per group)
        from sqlalchemy.orm import aliased
        from sqlalchemy import desc as sql_desc

        # Get latest evaluation ID per student using window function approach
        latest_evals_subquery = (
            self.db.query(
                EvaluationDB.student_id,
                func.max(EvaluationDB.created_at).label("max_created")
            )
            .filter(
                EvaluationDB.student_id.in_(student_ids),
                EvaluationDB.created_at >= period_start,
                EvaluationDB.created_at <= period_end,
            )
            .group_by(EvaluationDB.student_id)
            .subquery()
        )

        latest_evals_query = (
            self.db.query(EvaluationDB)
            .join(
                latest_evals_subquery,
                and_(
                    EvaluationDB.student_id == latest_evals_subquery.c.student_id,
                    EvaluationDB.created_at == latest_evals_subquery.c.max_created
                )
            )
            .all()
        )
        competency_by_student = {
            e.student_id: e.overall_competency_level
            for e in latest_evals_query
        }

        # Batch query 4: Total risks per student
        risks_query = (
            self.db.query(
                RiskDB.student_id,
                func.count(RiskDB.id).label("count")
            )
            .filter(
                RiskDB.student_id.in_(student_ids),
                RiskDB.created_at >= period_start,
                RiskDB.created_at <= period_end,
            )
            .group_by(RiskDB.student_id)
            .all()
        )
        risks_by_student = {r.student_id: r.count for r in risks_query}

        # Batch query 5: Critical risks per student
        critical_risks_query = (
            self.db.query(
                RiskDB.student_id,
                func.count(RiskDB.id).label("count")
            )
            .filter(
                RiskDB.student_id.in_(student_ids),
                RiskDB.risk_level == "critical",
                RiskDB.created_at >= period_start,
                RiskDB.created_at <= period_end,
            )
            .group_by(RiskDB.student_id)
            .all()
        )
        critical_risks_by_student = {c.student_id: c.count for c in critical_risks_query}

        # Build summaries from batch results (no additional queries)
        summaries = []
        for student_id in student_ids:
            summaries.append(
                {
                    "student_id": student_id,
                    "sessions": sessions_by_student.get(student_id, 0),
                    "ai_dependency": round(ai_dependency_by_student.get(student_id, 0.0), 3),
                    "competency": competency_by_student.get(student_id, "N/A"),
                    "risks": risks_by_student.get(student_id, 0),
                    "critical_risks": critical_risks_by_student.get(student_id, 0),
                }
            )

        return summaries

    def _identify_at_risk_students(
        self, student_summaries: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify students requiring intervention"""
        at_risk = []

        for summary in student_summaries:
            # Criteria for at-risk:
            # 1. Critical risks > 0
            # 2. AI dependency > 0.7
            # 3. Low sessions (< 3)
            # 4. Competency is BASICO or N/A

            if (
                summary["critical_risks"] > 0
                or summary["ai_dependency"] > 0.7
                or (summary["sessions"] < 3 and summary["sessions"] > 0)
                or summary["competency"] in ["BASICO", "N/A"]
            ):
                at_risk.append(summary["student_id"])

        return at_risk

    def _generate_institutional_recommendations(
        self,
        summary_stats: Dict[str, Any],
        competency_distribution: Dict[str, int],
        risk_distribution: Dict[str, int],
        top_risks: List[Dict[str, Any]],
    ) -> List[str]:
        """Generate institutional recommendations based on data"""
        recommendations = []

        # High AI dependency
        if summary_stats.get("avg_ai_dependency", 0) > 0.6:
            recommendations.append(
                "ALERTA: Dependencia promedio de IA alta (>0.6). "
                "Considerar talleres sobre uso crítico de IA y autonomía cognitiva."
            )

        # Low sessions per student
        if summary_stats.get("avg_sessions_per_student", 0) < 3:
            recommendations.append(
                "Bajo engagement: promedio <3 sesiones por estudiante. "
                "Considerar mejorar comunicación sobre disponibilidad del sistema."
            )

        # High critical risks (DB stores lowercase)
        if risk_distribution.get("critical", 0) > 0:
            recommendations.append(
                f"URGENTE: {risk_distribution['critical']} riesgos críticos detectados. "
                "Requiere intervención docente inmediata."
            )

        # Low competency levels
        basic_count = competency_distribution.get("BASICO", 0)
        total_evaluated = sum(competency_distribution.values())
        if total_evaluated > 0 and (basic_count / total_evaluated) > 0.4:
            recommendations.append(
                "Alta proporción de competencia BASICA (>40%). "
                "Considerar reforzar contenidos fundamentales o ajustar evaluación."
            )

        # Top risk patterns
        if top_risks:
            top_risk_type = top_risks[0]["risk_type"]
            recommendations.append(
                f"Riesgo más frecuente: {top_risk_type}. "
                "Considerar intervención pedagógica focalizada."
            )

        # Default positive message if no issues
        if not recommendations:
            recommendations.append(
                "Cohorte en buen estado general. Continuar monitoreo regular."
            )

        return recommendations

    def _categorize_students_by_risk(
        self, student_ids: List[str], period_start: datetime, period_end: datetime
    ) -> Dict[str, List[str]]:
        """
        Categorize students by highest risk level

        FIX Cortez22 DEFECTO 6.2: Replaced N+1 queries with single batch query.
        Original: 1 query per student
        Fixed: 1 query total using GROUP BY and MAX CASE
        """
        # Keys match DB lowercase values
        categorized: Dict[str, List[str]] = {"critical": [], "high": [], "medium": [], "low": [], "none": []}

        if not student_ids:
            return categorized

        # Batch query: Get highest risk level per student using MAX CASE
        highest_risk_query = (
            self.db.query(
                RiskDB.student_id,
                func.max(
                    func.case(
                        (RiskDB.risk_level == "critical", 4),
                        (RiskDB.risk_level == "high", 3),
                        (RiskDB.risk_level == "medium", 2),
                        (RiskDB.risk_level == "low", 1),
                        else_=0,
                    )
                ).label("severity")
            )
            .filter(
                RiskDB.student_id.in_(student_ids),
                RiskDB.created_at >= period_start,
                RiskDB.created_at <= period_end,
            )
            .group_by(RiskDB.student_id)
            .all()
        )

        # Map severity score back to risk level
        severity_to_level = {4: "critical", 3: "high", 2: "medium", 1: "low", 0: "none"}
        highest_risk_by_student = {
            r.student_id: severity_to_level.get(r.severity, "none")
            for r in highest_risk_query
        }

        # Categorize all students
        for student_id in student_ids:
            risk_level = highest_risk_by_student.get(student_id, "none")
            categorized[risk_level].append(student_id)

        return categorized

    def _analyze_risk_trends(
        self, student_ids: List[str], period_start: datetime, period_end: datetime
    ) -> Dict[str, Any]:
        """Analyze risk trends over time"""
        # Get risks grouped by week
        risks = (
            self.db.query(RiskDB)
            .filter(
                RiskDB.student_id.in_(student_ids),
                RiskDB.created_at >= period_start,
                RiskDB.created_at <= period_end,
            )
            .all()
        )

        # Group by week
        weekly_counts: Dict[str, int] = {}
        for risk in risks:
            week_key = risk.created_at.strftime("%Y-W%W")
            weekly_counts[week_key] = weekly_counts.get(week_key, 0) + 1

        # Calculate trend (increasing, stable, decreasing)
        if len(weekly_counts) >= 2:
            weeks = sorted(weekly_counts.keys())
            first_half = sum(weekly_counts[w] for w in weeks[: len(weeks) // 2])
            second_half = sum(weekly_counts[w] for w in weeks[len(weeks) // 2 :])

            if second_half > first_half * 1.2:
                trend = "increasing"
            elif second_half < first_half * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {"weekly_counts": weekly_counts, "trend": trend}
