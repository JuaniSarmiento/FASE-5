"""
Submodelo 5: Agente IA de Gobernanza Institucional (GOV-IA)

Operacionaliza la gobernanza institucional de IA generativa
"""
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
import re


class PolicyLevel(str, Enum):
    """Niveles de política"""
    INSTITUTIONAL = "institutional"
    PROGRAM = "program"
    COURSE = "course"
    ACTIVITY = "activity"


class ComplianceStatus(str, Enum):
    """Estado de cumplimiento"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"


class GobernanzaAgent:
    """
    GOV-IA: Agente de Gobernanza Institucional

    Implementa marcos:
    - UNESCO (2021): Ética de IA
    - OECD AI Principles (2019)
    - IEEE Ethically Aligned Design (2019)
    - ISO/IEC 23894:2023: Risk Management
    - ISO/IEC 42001:2023: AI Management System

    Funciones:
    1. Verificar cumplimiento de políticas
    2. Gestión del riesgo en tiempo real
    3. Auditoría y trazabilidad
    4. Generación de reportes institucionales
    """

    def __init__(self, llm_provider=None, config: Optional[Dict[str, Any]] = None):
        self.llm_provider = llm_provider
        self.config = config or {}

        # Políticas institucionales (configurables)
        self.policies = {
            "max_ai_assistance_level": 0.7,  # 0-1
            "require_explicit_ai_usage": True,
            "block_complete_solutions": True,
            "require_traceability": True,
            "enforce_academic_integrity": True,
        }

        # Cargar políticas del config
        if config and "policies" in config:
            self.policies.update(config["policies"])
        
        # Patrones regex para detectar PII (Información Personal Identificable)
        self.pii_patterns = {
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "dni": re.compile(r'\b\d{7,8}\b'),  # DNI argentino
            "phone": re.compile(r'\b\d{2,4}[-.\s]?\d{4}[-.\s]?\d{4}\b'),  # Teléfono
            "credit_card": re.compile(r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b'),
        }

    def sanitize_prompt(self, prompt: str) -> tuple[str, bool]:
        """
        Filtra PII (Información Personal Identificable) del prompt antes de enviarlo al LLM.
        
        Args:
            prompt: Texto original del prompt
            
        Returns:
            Tupla (prompt_sanitizado, pii_detectado)
        """
        sanitized = prompt
        pii_found = False
        
        # Detectar y reemplazar emails
        if self.pii_patterns["email"].search(sanitized):
            sanitized = self.pii_patterns["email"].sub("[EMAIL_REDACTED]", sanitized)
            pii_found = True
            
        # Detectar y reemplazar DNI
        if self.pii_patterns["dni"].search(sanitized):
            sanitized = self.pii_patterns["dni"].sub("[DNI_REDACTED]", sanitized)
            pii_found = True
            
        # Detectar y reemplazar teléfonos
        if self.pii_patterns["phone"].search(sanitized):
            sanitized = self.pii_patterns["phone"].sub("[PHONE_REDACTED]", sanitized)
            pii_found = True
            
        # Detectar y reemplazar tarjetas de crédito
        if self.pii_patterns["credit_card"].search(sanitized):
            sanitized = self.pii_patterns["credit_card"].sub("[CARD_REDACTED]", sanitized)
            pii_found = True
        
        return sanitized, pii_found

    def verify_compliance(
        self,
        trace_sequence=None,
        policies: Optional[Dict[str, Any]] = None,
        action: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verifica cumplimiento de políticas antes de ejecutar una acción

        Args:
            trace_sequence: TraceSequence a verificar (nueva API)
            policies: Políticas específicas a verificar (opcional)
            action: Acción a verificar (API antigua, backward compatibility)
            context: Contexto de la acción (API antigua, backward compatibility)

        Returns:
            Diccionario con resultado de verificación
        """
        violations = []
        warnings = []

        # Merge policies específicas con policies del agente
        active_policies = {**self.policies}
        if policies:
            active_policies.update(policies)

        # Si se usa la nueva API (trace_sequence)
        if trace_sequence is not None:
            # Verificar dependencia de IA
            if "max_ai_dependency" in active_policies:
                max_allowed = active_policies["max_ai_dependency"]
                if trace_sequence.ai_dependency_score > max_allowed:
                    violations.append({
                        "policy": "max_ai_dependency",
                        "description": f"Dependencia de IA ({trace_sequence.ai_dependency_score:.2%}) excede máximo ({max_allowed:.0%})",
                        "action_required": "reduce_ai_dependency"
                    })

            # Verificar trazabilidad
            if active_policies.get("require_traceability", False):
                if not trace_sequence.traces:
                    violations.append({
                        "policy": "require_traceability",
                        "description": "Se requiere trazabilidad N4 completa",
                        "action_required": "ensure_traceability"
                    })

            # Verificar delegación total
            if active_policies.get("block_full_delegation", False):
                delegation_count = sum(
                    1 for t in trace_sequence.traces
                    if "código completo" in t.content.lower() or "hacé todo" in t.content.lower()
                )
                if delegation_count > 0:
                    violations.append({
                        "policy": "block_full_delegation",
                        "description": f"Detectados {delegation_count} intentos de delegación total",
                        "action_required": "block_and_redirect"
                    })

        # API antigua (backward compatibility)
        elif context is not None:
            # Verificar política de soluciones completas
            if active_policies.get("block_complete_solutions", False):
                if self._is_complete_solution_request(context):
                    violations.append({
                        "policy": "block_complete_solutions",
                        "description": "Solicitud de solución completa sin mediación",
                        "action_required": "block_and_redirect"
                    })

            # Verificar nivel de asistencia
            requested_help_level = context.get("help_level", 0.5)
            if requested_help_level > active_policies.get("max_ai_assistance_level", 0.7):
                warnings.append({
                    "policy": "max_ai_assistance_level",
                    "description": f"Nivel de ayuda ({requested_help_level}) excede máximo permitido",
                    "action_required": "cap_assistance_level"
                })

        # Determinar estado de cumplimiento
        if violations:
            status = ComplianceStatus.VIOLATION
        elif warnings:
            status = ComplianceStatus.WARNING
        else:
            status = ComplianceStatus.COMPLIANT

        return {
            "compliant": status == ComplianceStatus.COMPLIANT,
            "status": status,
            "violations": violations,
            "warnings": warnings,
            "allow_action": len(violations) == 0,
            "required_adjustments": self._generate_adjustments(violations, warnings)
        }

    def _is_complete_solution_request(self, context: Dict[str, Any]) -> bool:
        """Detecta si se solicita una solución completa"""
        classification = context.get("classification", {})
        return classification.get("is_total_delegation", False)

    def _generate_adjustments(
        self,
        violations: List[Dict],
        warnings: List[Dict]
    ) -> List[str]:
        """Genera ajustes requeridos para cumplimiento"""
        adjustments = []

        for violation in violations:
            if violation["action_required"] == "block_and_redirect":
                adjustments.append("redirect_to_pedagogical_interaction")

        for warning in warnings:
            if warning["action_required"] == "cap_assistance_level":
                adjustments.append("reduce_help_level_to_maximum")

        return adjustments

    def generate_audit_report(
        self,
        time_period: Dict[str, datetime],
        scope: str = "institutional"
    ) -> Dict[str, Any]:
        """
        Genera reporte de auditoría para acreditación

        Args:
            time_period: Período de tiempo
            scope: Alcance (institutional, program, course)

        Returns:
            Reporte de auditoría completo
        """
        return {
            "report_id": f"audit_{datetime.now().isoformat()}",
            "scope": scope,
            "time_period": time_period,
            "compliance_summary": {
                "total_interactions": 0,  # Placeholder
                "compliant_interactions": 0,
                "violations": 0,
                "warnings": 0,
            },
            "policy_effectiveness": {
                "block_complete_solutions": {"enforced": True, "violations": 0},
                "require_traceability": {"enforced": True, "coverage": "100%"},
            },
            "recommendations": [
                "Revisar umbrales de asistencia según resultados de aprendizaje",
                "Actualizar políticas según normativa vigente"
            ]
        }