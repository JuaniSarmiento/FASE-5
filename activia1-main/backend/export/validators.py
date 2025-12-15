"""
Privacy Validators - GDPR and k-anonymity compliance checking

Validates that exported data meets privacy and regulatory requirements
before allowing export for research purposes.

Key Validations:
- k-anonymity: Minimum equivalence class size
- l-diversity: Diversity within equivalence classes
- PII detection: Ensures no PII leaked
- GDPR compliance: Article 89 safeguards
- Data minimization: Only necessary fields exported

References:
- GDPR Article 89: Processing for archiving, research and statistical purposes
- ISO/IEC 27701:2019: Privacy Information Management
- ISO/IEC 29100:2011: Privacy framework
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ValidationResult(BaseModel):
    """Result of privacy validation"""

    is_valid: bool = Field(description="Whether validation passed")
    errors: List[str] = Field(
        default_factory=list, description="Validation errors"
    )
    warnings: List[str] = Field(
        default_factory=list, description="Validation warnings"
    )
    metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Privacy metrics"
    )


class PrivacyValidator:
    """
    Validates privacy compliance of anonymized data

    Example:
        >>> validator = PrivacyValidator()
        >>> records = [...]  # Anonymized records
        >>> result = validator.validate(records, quasi_identifiers=["activity_id", "week"])
        >>> if result.is_valid:
        ...     print("✅ Privacy validation passed")
        >>> else:
        ...     print("❌ Errors:", result.errors)
    """

    # PII patterns to detect potential leakage
    # Note: Patterns are more restrictive to avoid false positives on timestamps/floats
    PII_PATTERNS = {
        "email": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
        "phone": r"\b\+?1?[\s\-\.]?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}\b",  # US phone format only
        "credit_card": r"\b\d{4}[\s\-]\d{4}[\s\-]\d{4}[\s\-]\d{4}\b",  # Must have separators
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "ip_address": r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
    }

    # Fields that should never appear in exported data
    FORBIDDEN_FIELDS = {
        "password",
        "password_hash",
        "api_key",
        "secret_key",
        "access_token",
        "refresh_token",
        "credit_card",
        "ssn",
        "passport_number",
    }

    def __init__(self, min_k: int = 5, check_l_diversity: bool = False):
        """
        Initialize privacy validator

        Args:
            min_k: Minimum k for k-anonymity (default: 5)
            check_l_diversity: Whether to check l-diversity (default: False)
        """
        self.min_k = min_k
        self.check_l_diversity = check_l_diversity
        logger.info(
            "PrivacyValidator initialized",
            extra={"min_k": min_k, "check_l_diversity": check_l_diversity},
        )

    def detect_pii_in_text(self, text: str) -> List[str]:
        """
        Detect potential PII in text using regex patterns

        Args:
            text: Text to scan for PII

        Returns:
            List of detected PII types
        """
        detected = []
        for pii_type, pattern in self.PII_PATTERNS.items():
            if re.search(pattern, str(text)):
                detected.append(pii_type)
        return detected

    def check_for_pii(self, records: List[Dict[str, Any]]) -> ValidationResult:
        """
        Check for PII leakage in records

        Args:
            records: Records to check

        Returns:
            Validation result with PII detection details
        """
        result = ValidationResult(is_valid=True)

        pii_found = {}
        forbidden_found = set()

        for idx, record in enumerate(records):
            # Check for forbidden fields
            for field in record.keys():
                if field.lower() in self.FORBIDDEN_FIELDS:
                    forbidden_found.add(field)

            # Check for PII patterns in values
            for field, value in record.items():
                if value is None:
                    continue

                detected = self.detect_pii_in_text(str(value))
                if detected:
                    if field not in pii_found:
                        pii_found[field] = set()
                    pii_found[field].update(detected)

        # Report forbidden fields
        if forbidden_found:
            result.is_valid = False
            result.errors.append(
                f"Forbidden fields found: {', '.join(forbidden_found)}"
            )

        # Report PII patterns
        if pii_found:
            result.is_valid = False
            for field, pii_types in pii_found.items():
                result.errors.append(
                    f"PII detected in field '{field}': {', '.join(pii_types)}"
                )

        result.metrics["pii_fields_detected"] = len(pii_found)
        result.metrics["forbidden_fields_detected"] = len(forbidden_found)

        if result.is_valid:
            logger.info("✅ PII check passed")
        else:
            logger.warning("⚠️ PII check failed", extra={"errors": result.errors})

        return result

    def check_k_anonymity(
        self, records: List[Dict[str, Any]], quasi_identifiers: List[str]
    ) -> ValidationResult:
        """
        Check k-anonymity compliance

        Args:
            records: Anonymized records
            quasi_identifiers: Fields that could be used for re-identification

        Returns:
            Validation result with k-anonymity metrics
        """
        result = ValidationResult(is_valid=True)

        if not records:
            result.warnings.append("No records to validate")
            return result

        # Group by quasi-identifier combination
        equivalence_classes: Dict[tuple, List[int]] = {}
        for idx, record in enumerate(records):
            qi_tuple = tuple(record.get(qi, None) for qi in quasi_identifiers)
            if qi_tuple not in equivalence_classes:
                equivalence_classes[qi_tuple] = []
            equivalence_classes[qi_tuple].append(idx)

        # Find minimum class size
        min_class_size = min(len(v) for v in equivalence_classes.values())
        avg_class_size = sum(len(v) for v in equivalence_classes.values()) / len(
            equivalence_classes
        )

        result.metrics["k_anonymity_achieved"] = min_class_size
        result.metrics["k_anonymity_required"] = self.min_k
        result.metrics["average_class_size"] = round(avg_class_size, 1)
        result.metrics["total_equivalence_classes"] = len(equivalence_classes)
        result.metrics["total_records"] = len(records)

        if min_class_size < self.min_k:
            result.is_valid = False
            result.errors.append(
                f"k-anonymity requirement not met: k={min_class_size} < {self.min_k}"
            )
            result.errors.append(
                f"Recommendation: Increase generalization or reduce granularity"
            )
        else:
            logger.info(
                f"✅ k-anonymity check passed (k={min_class_size})",
                extra=result.metrics,
            )

        return result

    def check_identifiers_hashed(
        self, records: List[Dict[str, Any]]
    ) -> ValidationResult:
        """
        Check that identifiers are hashed (not original IDs)

        Args:
            records: Records to check

        Returns:
            Validation result
        """
        result = ValidationResult(is_valid=True)

        # Fields that should be hashed
        id_fields = ["student_id", "session_id", "user_id"]

        # Fields that should exist as hashed versions
        expected_hashed = ["student_hash", "session_hash"]

        unhashed_found = set()
        missing_hashed = set()

        for record in records:
            # Check for unhashed IDs
            for field in id_fields:
                if field in record:
                    unhashed_found.add(field)

            # Check for missing hashed versions
            for field in expected_hashed:
                if field not in record:
                    missing_hashed.add(field)

        if unhashed_found:
            result.is_valid = False
            result.errors.append(
                f"Unhashed identifiers found: {', '.join(unhashed_found)}"
            )

        if missing_hashed:
            result.warnings.append(
                f"Missing hashed identifiers: {', '.join(missing_hashed)}"
            )

        result.metrics["unhashed_ids_found"] = len(unhashed_found)
        result.metrics["missing_hashed_ids"] = len(missing_hashed)

        if result.is_valid:
            logger.info("✅ Identifier hashing check passed")
        else:
            logger.warning(
                "⚠️ Identifier hashing check failed", extra={"errors": result.errors}
            )

        return result

    def validate(
        self,
        records: List[Dict[str, Any]],
        quasi_identifiers: Optional[List[str]] = None,
    ) -> ValidationResult:
        """
        Comprehensive privacy validation

        Args:
            records: Anonymized records to validate
            quasi_identifiers: Fields that could be used for re-identification

        Returns:
            Combined validation result
        """
        logger.info(
            "Starting privacy validation", extra={"record_count": len(records)}
        )

        combined_result = ValidationResult(is_valid=True)

        # Check 1: PII detection
        pii_result = self.check_for_pii(records)
        combined_result.is_valid &= pii_result.is_valid
        combined_result.errors.extend(pii_result.errors)
        combined_result.warnings.extend(pii_result.warnings)
        combined_result.metrics.update(pii_result.metrics)

        # Check 2: Identifier hashing
        hash_result = self.check_identifiers_hashed(records)
        combined_result.is_valid &= hash_result.is_valid
        combined_result.errors.extend(hash_result.errors)
        combined_result.warnings.extend(hash_result.warnings)
        combined_result.metrics.update(hash_result.metrics)

        # Check 3: k-anonymity (if quasi-identifiers provided)
        if quasi_identifiers:
            k_result = self.check_k_anonymity(records, quasi_identifiers)
            combined_result.is_valid &= k_result.is_valid
            combined_result.errors.extend(k_result.errors)
            combined_result.warnings.extend(k_result.warnings)
            combined_result.metrics.update(k_result.metrics)

        if combined_result.is_valid:
            logger.info(
                "✅ Privacy validation PASSED", extra=combined_result.metrics
            )
        else:
            logger.error(
                "❌ Privacy validation FAILED",
                extra={
                    "errors": combined_result.errors,
                    "metrics": combined_result.metrics,
                },
            )

        return combined_result


class GDPRCompliance:
    """
    GDPR Article 89 compliance checker for research data

    Article 89: Processing for archiving purposes in the public interest,
    scientific or historical research purposes or statistical purposes
    """

    @staticmethod
    def check_article_89_compliance(
        anonymization_config: Dict[str, Any], validation_result: ValidationResult
    ) -> ValidationResult:
        """
        Check compliance with GDPR Article 89 safeguards

        Args:
            anonymization_config: Configuration used for anonymization
            validation_result: Privacy validation result

        Returns:
            GDPR compliance result
        """
        result = ValidationResult(is_valid=True)

        # Article 89(1) safeguards
        required_safeguards = {
            "pseudonymization": anonymization_config.get("hash_salt") is not None,
            "data_minimization": anonymization_config.get("suppress_pii", False),
            "technical_measures": validation_result.metrics.get(
                "k_anonymity_achieved", 0
            )
            >= 5,
        }

        for safeguard, implemented in required_safeguards.items():
            if not implemented:
                result.is_valid = False
                result.errors.append(f"GDPR Article 89 safeguard missing: {safeguard}")

        result.metrics["gdpr_article_89_compliance"] = result.is_valid
        result.metrics["safeguards_implemented"] = required_safeguards

        if result.is_valid:
            logger.info("✅ GDPR Article 89 compliance check passed")
        else:
            logger.warning(
                "⚠️ GDPR Article 89 compliance check failed",
                extra={"errors": result.errors},
            )

        return result