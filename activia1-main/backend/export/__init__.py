"""
Export Module - Data Anonymization and Export for Research

This module provides functionality to export anonymized data for institutional
research purposes, ensuring GDPR compliance and k-anonymity.

Components:
- anonymizer: Data anonymization with k-anonymity
- exporter: Multi-format export (JSON, CSV, Excel)
- validators: Privacy and compliance validation
"""

from .anonymizer import DataAnonymizer, AnonymizationConfig
from .exporter import ResearchDataExporter, ExportFormat, ExportConfig
from .validators import PrivacyValidator, GDPRCompliance, ValidationResult

__all__ = [
    "DataAnonymizer",
    "AnonymizationConfig",
    "ResearchDataExporter",
    "ExportFormat",
    "ExportConfig",
    "PrivacyValidator",
    "GDPRCompliance",
    "ValidationResult",
]