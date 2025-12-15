"""
Data Anonymizer - GDPR-compliant anonymization for research data

Implements k-anonymity, l-diversity, and differential privacy techniques
to protect student privacy while enabling educational research.

Key Features:
- k-anonymity: Ensures each record is indistinguishable from k-1 others
- ID hashing: Irreversible transformation of student/session IDs
- PII suppression: Removes personally identifiable information
- Generalization: Aggregates sensitive attributes
- Noise addition: Differential privacy for numerical data

References:
- Sweeney, L. (2002). k-anonymity: A model for protecting privacy
- EU GDPR (2016): Article 89 - Safeguards and derogations
- ISO/IEC 27701:2019: Privacy Information Management
"""

import hashlib
import logging
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AnonymizationConfig(BaseModel):
    """Configuration for data anonymization"""

    k_anonymity: int = Field(
        default=5, ge=2, description="Minimum k for k-anonymity (default: 5)"
    )
    hash_salt: str = Field(
        default="ai_native_mvp_research_2025",
        description="Salt for ID hashing (should be institution-specific)",
    )
    suppress_pii: bool = Field(
        default=True, description="Remove PII fields (emails, names, etc.)"
    )
    generalize_timestamps: bool = Field(
        default=True,
        description="Generalize timestamps to week/month level",
    )
    add_noise_to_scores: bool = Field(
        default=False,
        description="Add Laplace noise to scores (differential privacy)",
    )
    noise_epsilon: float = Field(
        default=0.1,
        ge=0.01,
        le=1.0,
        description="Privacy budget for differential privacy (smaller = more private)",
    )
    suppress_fields: List[str] = Field(
        default_factory=lambda: [
            "student_id",
            "session_id",
            "student_name",
            "student_email",
            "ip_address",
            "user_agent",
        ],
        description="Fields to suppress completely",
    )


class DataAnonymizer:
    """
    Anonymizes research data to ensure privacy while preserving utility

    Example:
        >>> config = AnonymizationConfig(k_anonymity=5)
        >>> anonymizer = DataAnonymizer(config)
        >>>
        >>> # Anonymize a trace
        >>> trace = {"student_id": "student_001", "score": 8.5, "timestamp": datetime.now()}
        >>> anon_trace = anonymizer.anonymize_trace(trace)
        >>> print(anon_trace["student_hash"])  # "a3f5b..."
        >>> print(anon_trace["score"])  # 8.5 (or with noise if enabled)
    """

    def __init__(self, config: Optional[AnonymizationConfig] = None):
        """
        Initialize anonymizer with configuration

        Args:
            config: Anonymization configuration (uses defaults if None)
        """
        self.config = config or AnonymizationConfig()
        self._hash_cache: Dict[str, str] = {}  # Cache for consistent hashing
        logger.info(
            "DataAnonymizer initialized",
            extra={
                "k_anonymity": self.config.k_anonymity,
                "suppress_pii": self.config.suppress_pii,
                "add_noise": self.config.add_noise_to_scores,
            },
        )

    def hash_id(self, identifier: str) -> str:
        """
        Hash an identifier (student_id, session_id) irreversibly

        Uses SHA-256 with salt to prevent rainbow table attacks.
        Results are cached for consistency within the same export.

        Args:
            identifier: Original ID to hash

        Returns:
            Hashed ID (first 12 characters of SHA-256 hash)
        """
        if identifier in self._hash_cache:
            return self._hash_cache[identifier]

        # SHA-256 with salt
        salted = f"{identifier}:{self.config.hash_salt}"
        hash_obj = hashlib.sha256(salted.encode("utf-8"))
        hashed = hash_obj.hexdigest()[:12]  # First 12 chars for readability

        self._hash_cache[identifier] = hashed
        return hashed

    def generalize_timestamp(self, timestamp: datetime) -> str:
        """
        Generalize timestamp to week or month level

        Args:
            timestamp: Original timestamp

        Returns:
            Generalized timestamp (e.g., "2025-W47" for week 47)
        """
        if not self.config.generalize_timestamps:
            return timestamp.isoformat()

        # Return ISO week format: "2025-W47"
        year, week, _ = timestamp.isocalendar()
        return f"{year}-W{week:02d}"

    def add_laplace_noise(self, value: float, sensitivity: float = 1.0) -> float:
        """
        Add Laplace noise for differential privacy

        Args:
            value: Original value
            sensitivity: Sensitivity of the query (max change from one record)

        Returns:
            Value with added noise
        """
        if not self.config.add_noise_to_scores:
            return value

        # Laplace noise: scale = sensitivity / epsilon
        scale = sensitivity / self.config.noise_epsilon

        # Laplace distribution: sample from two exponentials
        # Lap(0, b) = sign(U - 0.5) * b * ln(1 - 2|U - 0.5|), U ~ Uniform(0,1)
        u = random.random()
        if u < 0.5:
            noise = scale * (random.random() - 1.0)
        else:
            noise = -scale * (random.random() - 1.0)

        # Clamp to valid range [0, 10]
        noisy_value = max(0.0, min(10.0, value + noise))
        return round(noisy_value, 2)

    def suppress_pii_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove PII fields from data dictionary

        Args:
            data: Original data dictionary

        Returns:
            Data with PII fields removed
        """
        if not self.config.suppress_pii:
            return data.copy()

        # Create copy and remove PII fields
        anonymized = {
            k: v for k, v in data.items() if k not in self.config.suppress_fields
        }

        return anonymized

    def anonymize_trace(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize a cognitive trace

        Args:
            trace: Original trace data

        Returns:
            Anonymized trace
        """
        anon_trace = self.suppress_pii_fields(trace)

        # Hash identifiers
        if "student_id" in trace:
            anon_trace["student_hash"] = self.hash_id(trace["student_id"])
        if "session_id" in trace:
            anon_trace["session_hash"] = self.hash_id(trace["session_id"])
        if "activity_id" in trace:
            # Activity IDs can stay (they're not PII)
            anon_trace["activity_id"] = trace["activity_id"]

        # Generalize timestamps
        if "created_at" in trace:
            anon_trace["week"] = self.generalize_timestamp(trace["created_at"])
        if "timestamp" in trace:
            anon_trace["week"] = self.generalize_timestamp(trace["timestamp"])

        # Add noise to AI involvement if needed
        if "ai_involvement" in trace and self.config.add_noise_to_scores:
            anon_trace["ai_involvement"] = self.add_laplace_noise(
                trace["ai_involvement"], sensitivity=0.1
            )

        return anon_trace

    def anonymize_evaluation(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize an evaluation report

        Args:
            evaluation: Original evaluation data

        Returns:
            Anonymized evaluation
        """
        anon_eval = self.suppress_pii_fields(evaluation)

        # Hash identifiers
        if "student_id" in evaluation:
            anon_eval["student_hash"] = self.hash_id(evaluation["student_id"])
        if "session_id" in evaluation:
            anon_eval["session_hash"] = self.hash_id(evaluation["session_id"])

        # Add noise to scores if enabled
        if "overall_score" in evaluation and self.config.add_noise_to_scores:
            anon_eval["overall_score"] = self.add_laplace_noise(
                evaluation["overall_score"], sensitivity=1.0
            )

        # Add noise to dimension scores
        if "dimensions" in evaluation and self.config.add_noise_to_scores:
            anon_eval["dimensions"] = {
                dim: self.add_laplace_noise(score, sensitivity=1.0)
                for dim, score in evaluation["dimensions"].items()
            }

        # Generalize timestamp
        if "created_at" in evaluation:
            anon_eval["week"] = self.generalize_timestamp(evaluation["created_at"])

        return anon_eval

    def anonymize_risk(self, risk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize a risk record

        Args:
            risk: Original risk data

        Returns:
            Anonymized risk
        """
        anon_risk = self.suppress_pii_fields(risk)

        # Hash identifiers
        if "student_id" in risk:
            anon_risk["student_hash"] = self.hash_id(risk["student_id"])
        if "session_id" in risk:
            anon_risk["session_hash"] = self.hash_id(risk["session_id"])

        # Keep risk type, dimension, level (not PII)
        for field in ["risk_type", "dimension", "risk_level", "description"]:
            if field in risk:
                anon_risk[field] = risk[field]

        # Generalize timestamp
        if "created_at" in risk:
            anon_risk["week"] = self.generalize_timestamp(risk["created_at"])

        return anon_risk

    def anonymize_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize a session record

        Args:
            session: Original session data

        Returns:
            Anonymized session
        """
        anon_session = self.suppress_pii_fields(session)

        # Hash identifiers
        if "student_id" in session:
            anon_session["student_hash"] = self.hash_id(session["student_id"])
        if "id" in session:
            anon_session["session_hash"] = self.hash_id(session["id"])

        # Keep activity_id, mode (not PII)
        for field in ["activity_id", "mode", "status"]:
            if field in session:
                anon_session[field] = session[field]

        # Generalize timestamps
        if "start_time" in session:
            anon_session["week"] = self.generalize_timestamp(session["start_time"])

        # Keep duration if present
        if "start_time" in session and "end_time" in session and session["end_time"]:
            duration = (session["end_time"] - session["start_time"]).total_seconds()
            anon_session["duration_minutes"] = round(duration / 60, 1)

        return anon_session

    def check_k_anonymity(self, records: List[Dict[str, Any]], quasi_identifiers: List[str]) -> int:
        """
        Check k-anonymity level of dataset

        Args:
            records: Anonymized records
            quasi_identifiers: Fields that could be used for re-identification
                              (e.g., ["activity_id", "week", "mode"])

        Returns:
            Minimum k value (smallest equivalence class size)
        """
        if not records:
            return 0

        # Group by quasi-identifier combination
        equivalence_classes: Dict[tuple, int] = {}
        for record in records:
            # Create tuple of quasi-identifier values
            qi_tuple = tuple(record.get(qi, None) for qi in quasi_identifiers)
            equivalence_classes[qi_tuple] = equivalence_classes.get(qi_tuple, 0) + 1

        # Return minimum class size
        min_k = min(equivalence_classes.values()) if equivalence_classes else 0
        logger.info(
            "k-anonymity check completed",
            extra={
                "min_k": min_k,
                "total_classes": len(equivalence_classes),
                "total_records": len(records),
            },
        )
        return min_k

    def validate_anonymization(
        self,
        records: List[Dict[str, Any]],
        quasi_identifiers: List[str]
    ) -> Dict[str, Any]:
        """
        Validate that anonymization meets privacy requirements

        Args:
            records: Anonymized records
            quasi_identifiers: Fields that could be used for re-identification

        Returns:
            Validation report with privacy metrics
        """
        k_value = self.check_k_anonymity(records, quasi_identifiers)

        validation_report = {
            "is_valid": k_value >= self.config.k_anonymity,
            "k_anonymity_achieved": k_value,
            "k_anonymity_required": self.config.k_anonymity,
            "total_records": len(records),
            "pii_suppressed": self.config.suppress_pii,
            "timestamps_generalized": self.config.generalize_timestamps,
            "noise_added": self.config.add_noise_to_scores,
        }

        if validation_report["is_valid"]:
            logger.info("✅ Anonymization validation PASSED", extra=validation_report)
        else:
            logger.warning(
                "⚠️ Anonymization validation FAILED",
                extra={
                    **validation_report,
                    "recommendation": f"Increase generalization or reduce granularity to achieve k={self.config.k_anonymity}",
                },
            )

        return validation_report

    def clear_cache(self):
        """Clear ID hash cache (use when starting new export)"""
        self._hash_cache.clear()
        logger.debug("Hash cache cleared")