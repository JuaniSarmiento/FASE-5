"""
Tests for Data Export Module

Tests for:
- DataAnonymizer (k-anonymity, hashing, PII suppression)
- ResearchDataExporter (JSON, CSV, Excel)
- PrivacyValidator (k-anonymity, PII detection)
- GDPRCompliance (Article 89 safeguards)
"""

import json
from datetime import datetime
from pathlib import Path

import pytest

from backend.export import (
    DataAnonymizer,
    AnonymizationConfig,
    ResearchDataExporter,
    ExportConfig,
    ExportFormat,
    PrivacyValidator,
    GDPRCompliance,
    ValidationResult,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_trace():
    """Sample cognitive trace"""
    return {
        "id": "trace_123",
        "student_id": "student_001",
        "session_id": "session_abc",
        "activity_id": "prog2_tp1",
        "cognitive_state": "EXPLORACION_CONCEPTUAL",
        "ai_involvement": 0.4,
        "content": "¿Qué es una cola circular?",
        "created_at": datetime(2025, 11, 15, 10, 30),
    }


@pytest.fixture
def sample_evaluation():
    """Sample evaluation"""
    return {
        "id": "eval_456",
        "student_id": "student_001",
        "session_id": "session_abc",
        "activity_id": "prog2_tp1",
        "overall_competency_level": "EN_DESARROLLO",
        "overall_score": 6.5,
        "dimensions": {
            "problem_decomposition": 7.0,
            "self_regulation": 5.0,
        },
        "created_at": datetime(2025, 11, 15, 12, 0),
    }


@pytest.fixture
def sample_risk():
    """Sample risk"""
    return {
        "id": "risk_789",
        "student_id": "student_001",
        "session_id": "session_abc",
        "activity_id": "prog2_tp1",
        "risk_type": "COGNITIVE_DELEGATION",
        "risk_level": "MEDIUM",
        "dimension": "COGNITIVE",
        "description": "Alta dependencia de IA",
        "created_at": datetime(2025, 11, 15, 11, 0),
    }


@pytest.fixture
def multiple_traces():
    """Multiple traces for k-anonymity testing"""
    return [
        {
            "student_id": f"student_{i:03d}",
            "session_id": f"session_{i:03d}",
            "activity_id": "prog2_tp1" if i % 2 == 0 else "prog2_tp2",
            "ai_involvement": 0.3 + (i * 0.1),
            "created_at": datetime(2025, 11, 15 + (i % 7), 10, 0),
        }
        for i in range(10)
    ]


# =============================================================================
# DataAnonymizer Tests
# =============================================================================


class TestDataAnonymizer:
    """Test suite for DataAnonymizer"""

    def test_hash_id_consistency(self):
        """Test that hashing is consistent"""
        anonymizer = DataAnonymizer()

        hash1 = anonymizer.hash_id("student_001")
        hash2 = anonymizer.hash_id("student_001")

        assert hash1 == hash2, "Same ID should produce same hash"

    def test_hash_id_uniqueness(self):
        """Test that different IDs produce different hashes"""
        anonymizer = DataAnonymizer()

        hash1 = anonymizer.hash_id("student_001")
        hash2 = anonymizer.hash_id("student_002")

        assert hash1 != hash2, "Different IDs should produce different hashes"

    def test_hash_id_length(self):
        """Test that hashes are truncated to 12 characters"""
        anonymizer = DataAnonymizer()

        hashed = anonymizer.hash_id("student_001")

        assert len(hashed) == 12, "Hash should be 12 characters"

    def test_generalize_timestamp_to_week(self):
        """Test timestamp generalization to ISO week"""
        config = AnonymizationConfig(generalize_timestamps=True)
        anonymizer = DataAnonymizer(config)

        timestamp = datetime(2025, 11, 15, 10, 30)  # Week 46
        generalized = anonymizer.generalize_timestamp(timestamp)

        assert generalized == "2025-W46", "Should generalize to ISO week format"

    def test_anonymize_trace(self, sample_trace):
        """Test trace anonymization"""
        anonymizer = DataAnonymizer()

        anonymized = anonymizer.anonymize_trace(sample_trace)

        # Check that student_id is hashed
        assert "student_hash" in anonymized
        assert "student_id" not in anonymized

        # Check that session_id is hashed
        assert "session_hash" in anonymized
        assert "session_id" not in anonymized

        # Check that activity_id is preserved (not PII)
        assert anonymized["activity_id"] == "prog2_tp1"

        # Check timestamp generalization
        assert "week" in anonymized
        assert anonymized["week"] == "2025-W46"

    def test_anonymize_evaluation(self, sample_evaluation):
        """Test evaluation anonymization"""
        anonymizer = DataAnonymizer()

        anonymized = anonymizer.anonymize_evaluation(sample_evaluation)

        # Check hashing
        assert "student_hash" in anonymized
        assert "student_id" not in anonymized

        # Check scores preserved
        assert anonymized["overall_score"] == 6.5

    def test_anonymize_risk(self, sample_risk):
        """Test risk anonymization"""
        anonymizer = DataAnonymizer()

        anonymized = anonymizer.anonymize_risk(sample_risk)

        # Check hashing
        assert "student_hash" in anonymized
        assert "student_id" not in anonymized

        # Check risk fields preserved
        assert anonymized["risk_type"] == "COGNITIVE_DELEGATION"
        assert anonymized["dimension"] == "COGNITIVE"

    def test_add_laplace_noise(self):
        """Test differential privacy noise addition"""
        config = AnonymizationConfig(add_noise_to_scores=True, noise_epsilon=0.1)
        anonymizer = DataAnonymizer(config)

        original_value = 7.0
        noisy_value = anonymizer.add_laplace_noise(original_value)

        # Noise should change value slightly
        assert noisy_value != original_value

        # Should stay within valid range [0, 10]
        assert 0.0 <= noisy_value <= 10.0

    def test_no_noise_when_disabled(self):
        """Test that noise is not added when disabled"""
        config = AnonymizationConfig(add_noise_to_scores=False)
        anonymizer = DataAnonymizer(config)

        original_value = 7.0
        noisy_value = anonymizer.add_laplace_noise(original_value)

        assert noisy_value == original_value, "No noise should be added when disabled"

    def test_check_k_anonymity(self, multiple_traces):
        """Test k-anonymity checking"""
        anonymizer = DataAnonymizer()

        # Anonymize traces
        anonymized = [anonymizer.anonymize_trace(t) for t in multiple_traces]

        # Check k-anonymity with activity_id + week as quasi-identifiers
        k_value = anonymizer.check_k_anonymity(anonymized, ["activity_id", "week"])

        # Should have some equivalence classes
        assert k_value > 0, "Should have at least one equivalence class"

    def test_validate_anonymization_success(self, multiple_traces):
        """Test successful anonymization validation"""
        config = AnonymizationConfig(k_anonymity=2)
        anonymizer = DataAnonymizer(config)

        anonymized = [anonymizer.anonymize_trace(t) for t in multiple_traces]

        validation = anonymizer.validate_anonymization(
            anonymized, quasi_identifiers=["activity_id"]
        )

        assert validation["is_valid"] is True
        assert validation["k_anonymity_achieved"] >= 2

    def test_validate_anonymization_failure(self):
        """Test failed anonymization validation (unique combinations)"""
        config = AnonymizationConfig(k_anonymity=5)
        anonymizer = DataAnonymizer(config)

        # Create traces with unique combinations (each will be own equivalence class)
        traces = [
            {
                "student_id": f"student_{i}",
                "activity_id": f"activity_{i}",  # Each unique
                "created_at": datetime(2025, 11, i + 1, 10, 0),
            }
            for i in range(3)
        ]

        anonymized = [anonymizer.anonymize_trace(t) for t in traces]

        validation = anonymizer.validate_anonymization(
            anonymized, quasi_identifiers=["activity_id"]
        )

        # Should fail because k_achieved (1) < k_required (5)
        assert validation["is_valid"] is False
        assert validation["k_anonymity_achieved"] == 1

    def test_suppress_pii_fields(self):
        """Test PII field suppression"""
        config = AnonymizationConfig(suppress_pii=True)
        anonymizer = DataAnonymizer(config)

        data = {
            "student_id": "student_001",
            "student_name": "John Doe",
            "student_email": "john@example.com",
            "activity_id": "prog2_tp1",  # Not PII
            "score": 8.5,  # Not PII
        }

        anonymized = anonymizer.suppress_pii_fields(data)

        # PII should be removed
        assert "student_id" not in anonymized
        assert "student_name" not in anonymized
        assert "student_email" not in anonymized

        # Non-PII should be preserved
        assert "activity_id" in anonymized
        assert "score" in anonymized


# =============================================================================
# ResearchDataExporter Tests
# =============================================================================


class TestResearchDataExporter:
    """Test suite for ResearchDataExporter"""

    def test_export_to_json(self, multiple_traces):
        """Test JSON export"""
        config = ExportConfig(format=ExportFormat.JSON, pretty_print=True)
        exporter = ResearchDataExporter(config)

        anonymizer = DataAnonymizer()
        anonymized = [anonymizer.anonymize_trace(t) for t in multiple_traces]

        json_str = exporter.export_to_json(anonymized, data_type="traces")

        # Should be valid JSON
        data = json.loads(json_str)

        assert "metadata" in data
        assert "data" in data
        assert "traces" in data["data"]
        assert len(data["data"]["traces"]) == len(anonymized)

    def test_export_to_csv(self, multiple_traces):
        """Test CSV export"""
        config = ExportConfig(format=ExportFormat.CSV)
        exporter = ResearchDataExporter(config)

        anonymizer = DataAnonymizer()
        anonymized = [anonymizer.anonymize_trace(t) for t in multiple_traces]

        csv_str = exporter.export_to_csv(anonymized)

        # Should have header + data rows
        lines = csv_str.strip().split("\n")
        assert len(lines) == len(anonymized) + 1  # +1 for header

        # First line should be header
        assert "student_hash" in lines[0] or "activity_id" in lines[0]

    def test_export_to_excel_requires_openpyxl(self, multiple_traces):
        """Test Excel export (or skip if openpyxl not installed)"""
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not installed")

        config = ExportConfig(format=ExportFormat.EXCEL)
        exporter = ResearchDataExporter(config)

        anonymizer = DataAnonymizer()
        anonymized = [anonymizer.anonymize_trace(t) for t in multiple_traces]

        data = {"traces": anonymized}
        excel_bytes = exporter.export_to_excel(data)

        # Should return bytes
        assert isinstance(excel_bytes, bytes)
        assert len(excel_bytes) > 0

    def test_generate_metadata(self):
        """Test metadata generation"""
        exporter = ResearchDataExporter()

        metadata = exporter.generate_metadata(
            record_count=100, data_types=["traces", "evaluations"]
        )

        assert metadata["total_records"] == 100
        assert metadata["data_types"] == ["traces", "evaluations"]
        assert metadata["anonymization_applied"] is True
        assert "export_timestamp" in metadata

    def test_compress_output(self):
        """Test output compression"""
        exporter = ResearchDataExporter()

        data = "This is test data for compression" * 100
        compressed = exporter.compress_output(data, "test_file.txt")

        # Compressed should be bytes
        assert isinstance(compressed, bytes)

        # Should be smaller than original (for repetitive data)
        assert len(compressed) < len(data.encode("utf-8"))


# =============================================================================
# PrivacyValidator Tests
# =============================================================================


class TestPrivacyValidator:
    """Test suite for PrivacyValidator"""

    def test_detect_pii_in_text_email(self):
        """Test PII detection - email"""
        validator = PrivacyValidator()

        text = "Contact: john.doe@example.com"
        detected = validator.detect_pii_in_text(text)

        assert "email" in detected

    def test_detect_pii_in_text_phone(self):
        """Test PII detection - phone"""
        validator = PrivacyValidator()

        text = "Phone: +1-555-123-4567"
        detected = validator.detect_pii_in_text(text)

        assert "phone" in detected

    def test_detect_pii_in_text_ip(self):
        """Test PII detection - IP address"""
        validator = PrivacyValidator()

        text = "IP: 192.168.1.100"
        detected = validator.detect_pii_in_text(text)

        assert "ip_address" in detected

    def test_check_for_pii_clean_data(self, multiple_traces):
        """Test PII check with clean anonymized data"""
        validator = PrivacyValidator()

        anonymizer = DataAnonymizer()
        anonymized = [anonymizer.anonymize_trace(t) for t in multiple_traces]

        result = validator.check_for_pii(anonymized)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_check_for_pii_forbidden_fields(self):
        """Test detection of forbidden fields"""
        validator = PrivacyValidator()

        records = [
            {"student_hash": "abc123", "password": "secret123"},
            {"student_hash": "def456", "api_key": "key_xyz"},
        ]

        result = validator.check_for_pii(records)

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("password" in error.lower() for error in result.errors)

    def test_check_k_anonymity_success(self, multiple_traces):
        """Test k-anonymity check - success"""
        validator = PrivacyValidator(min_k=2)

        anonymizer = DataAnonymizer()
        anonymized = [anonymizer.anonymize_trace(t) for t in multiple_traces]

        result = validator.check_k_anonymity(anonymized, ["activity_id"])

        assert result.is_valid is True
        assert result.metrics["k_anonymity_achieved"] >= 2

    def test_check_k_anonymity_failure(self):
        """Test k-anonymity check - failure"""
        validator = PrivacyValidator(min_k=10)

        # Create only 3 records
        records = [
            {"student_hash": f"hash_{i}", "activity_id": "prog2_tp1"}
            for i in range(3)
        ]

        result = validator.check_k_anonymity(records, ["activity_id"])

        # k=3 < min_k=10, should fail
        assert result.is_valid is False
        assert result.metrics["k_anonymity_achieved"] == 3

    def test_check_identifiers_hashed_success(self):
        """Test that identifiers are properly hashed"""
        validator = PrivacyValidator()

        records = [
            {"student_hash": "abc123", "session_hash": "def456"},
            {"student_hash": "ghi789", "session_hash": "jkl012"},
        ]

        result = validator.check_identifiers_hashed(records)

        assert result.is_valid is True

    def test_check_identifiers_hashed_failure(self):
        """Test detection of unhashed identifiers"""
        validator = PrivacyValidator()

        records = [
            {"student_id": "student_001"},  # Unhashed!
            {"student_hash": "abc123"},
        ]

        result = validator.check_identifiers_hashed(records)

        assert result.is_valid is False
        assert any("student_id" in error.lower() for error in result.errors)

    def test_validate_comprehensive(self, multiple_traces):
        """Test comprehensive validation"""
        validator = PrivacyValidator(min_k=2)

        anonymizer = DataAnonymizer()
        anonymized = [anonymizer.anonymize_trace(t) for t in multiple_traces]

        result = validator.validate(anonymized, quasi_identifiers=["activity_id"])

        assert result.is_valid is True
        assert "k_anonymity_achieved" in result.metrics
        assert "pii_fields_detected" in result.metrics


# =============================================================================
# GDPRCompliance Tests
# =============================================================================


class TestGDPRCompliance:
    """Test suite for GDPR compliance checking"""

    def test_article_89_compliance_success(self):
        """Test successful GDPR Article 89 compliance"""
        anon_config = {
            "hash_salt": "test_salt",
            "suppress_pii": True,
        }

        validation_result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            metrics={"k_anonymity_achieved": 5},
        )

        result = GDPRCompliance.check_article_89_compliance(
            anon_config, validation_result
        )

        assert result.is_valid is True
        assert result.metrics["gdpr_article_89_compliance"] is True

    def test_article_89_compliance_failure_no_salt(self):
        """Test GDPR failure - missing pseudonymization"""
        anon_config = {
            "hash_salt": None,  # Missing!
            "suppress_pii": True,
        }

        validation_result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            metrics={"k_anonymity_achieved": 5},
        )

        result = GDPRCompliance.check_article_89_compliance(
            anon_config, validation_result
        )

        assert result.is_valid is False
        assert any("pseudonymization" in error.lower() for error in result.errors)

    def test_article_89_compliance_failure_low_k(self):
        """Test GDPR failure - insufficient k-anonymity"""
        anon_config = {
            "hash_salt": "test_salt",
            "suppress_pii": True,
        }

        validation_result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            metrics={"k_anonymity_achieved": 2},  # Too low!
        )

        result = GDPRCompliance.check_article_89_compliance(
            anon_config, validation_result
        )

        assert result.is_valid is False
        assert any("technical_measures" in error.lower() for error in result.errors)


# =============================================================================
# Integration Tests
# =============================================================================


class TestExportIntegration:
    """Integration tests for complete export workflow"""

    def test_complete_export_workflow(self, multiple_traces, tmp_path):
        """Test complete export workflow from anonymization to file export"""

        # Step 1: Anonymize
        config = AnonymizationConfig(k_anonymity=2)
        anonymizer = DataAnonymizer(config)

        anonymized = [anonymizer.anonymize_trace(t) for t in multiple_traces]

        # Step 2: Validate
        validator = PrivacyValidator(min_k=2)
        validation = validator.validate(anonymized, quasi_identifiers=["activity_id"])

        assert validation.is_valid is True

        # Step 3: Export to JSON
        export_config = ExportConfig(format=ExportFormat.JSON)
        exporter = ResearchDataExporter(export_config)

        output_file = tmp_path / "export_test.json"
        exporter.export(anonymized, output_file)

        # Verify file exists and is valid JSON
        assert output_file.exists()

        with output_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        assert "metadata" in data
        assert "data" in data

    def test_export_with_validation_failure_scenario(self):
        """Test that validation catches privacy violations"""

        # Create data with unique combinations (k=1 for each)
        traces = [
            {
                "student_id": f"student_{i}",
                "activity_id": f"unique_activity_{i}",  # Each unique!
                "created_at": datetime(2025, 11, i + 1, 10, 0),
            }
            for i in range(3)
        ]

        config = AnonymizationConfig(k_anonymity=5)  # Require k=5
        anonymizer = DataAnonymizer(config)

        anonymized = [anonymizer.anonymize_trace(t) for t in traces]

        # Validation should fail
        validator = PrivacyValidator(min_k=5)
        validation = validator.validate(anonymized, quasi_identifiers=["activity_id"])

        assert validation.is_valid is False
        assert validation.metrics["k_anonymity_achieved"] < 5
