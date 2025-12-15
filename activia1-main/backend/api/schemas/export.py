"""
Export API Schemas - Request/Response DTOs for data export endpoints

Defines Pydantic models for:
- Export configuration requests
- Export responses
- Privacy validation reports
- GDPR compliance reports
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from ...export.exporter import ExportFormat


class ExportRequest(BaseModel):
    """Request to export anonymized research data"""

    start_date: Optional[datetime] = Field(
        default=None, description="Start date for data export (inclusive)"
    )
    end_date: Optional[datetime] = Field(
        default=None, description="End date for data export (inclusive)"
    )
    activity_ids: Optional[List[str]] = Field(
        default=None, description="Filter by specific activities (None = all)"
    )
    student_hashes: Optional[List[str]] = Field(
        default=None,
        description="Filter by specific student hashes (for longitudinal studies)",
    )
    include_traces: bool = Field(
        default=True, description="Include cognitive traces"
    )
    include_evaluations: bool = Field(
        default=True, description="Include evaluation reports"
    )
    include_risks: bool = Field(
        default=True, description="Include risk detections"
    )
    include_sessions: bool = Field(
        default=True, description="Include session metadata"
    )
    format: ExportFormat = Field(
        default=ExportFormat.JSON, description="Export format"
    )
    compress: bool = Field(
        default=False, description="Compress output (ZIP)"
    )
    k_anonymity: int = Field(
        default=5, ge=2, le=50, description="Minimum k for k-anonymity"
    )
    add_noise: bool = Field(
        default=False, description="Add differential privacy noise to scores"
    )
    noise_epsilon: float = Field(
        default=0.1,
        ge=0.01,
        le=1.0,
        description="Privacy budget for differential privacy",
    )

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v, info):
        """Validate that end_date is after start_date"""
        if v and info.data.get("start_date") and v < info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class PrivacyMetrics(BaseModel):
    """Privacy metrics from validation"""

    k_anonymity_achieved: int = Field(description="Achieved k-anonymity level")
    k_anonymity_required: int = Field(description="Required k-anonymity level")
    total_records: int = Field(description="Total records in export")
    total_equivalence_classes: int = Field(
        description="Number of equivalence classes"
    )
    average_class_size: float = Field(
        description="Average equivalence class size"
    )
    pii_fields_detected: int = Field(
        default=0, description="Number of fields with PII detected"
    )
    forbidden_fields_detected: int = Field(
        default=0, description="Number of forbidden fields detected"
    )
    unhashed_ids_found: int = Field(
        default=0, description="Number of unhashed identifiers found"
    )


class ValidationReport(BaseModel):
    """Privacy validation report"""

    is_valid: bool = Field(description="Whether data passed validation")
    errors: List[str] = Field(
        default_factory=list, description="Validation errors"
    )
    warnings: List[str] = Field(
        default_factory=list, description="Validation warnings"
    )
    metrics: PrivacyMetrics = Field(description="Privacy metrics")
    gdpr_article_89_compliant: bool = Field(
        description="GDPR Article 89 compliance status"
    )


class ExportMetadata(BaseModel):
    """Metadata about the export"""

    export_timestamp: datetime = Field(description="When export was generated")
    export_format: ExportFormat = Field(description="Format of export")
    total_records: int = Field(description="Total records exported")
    data_types: List[str] = Field(
        description="Types of data included (traces, evaluations, etc.)"
    )
    anonymization_applied: bool = Field(
        default=True, description="Whether anonymization was applied"
    )
    privacy_standard: str = Field(
        default="k-anonymity", description="Privacy standard applied"
    )
    date_range: Optional[Dict[str, datetime]] = Field(
        default=None, description="Date range of exported data"
    )


class ExportResponse(BaseModel):
    """Response from export endpoint"""

    success: bool = Field(description="Whether export succeeded")
    message: str = Field(description="Human-readable message")
    metadata: ExportMetadata = Field(description="Export metadata")
    validation_report: ValidationReport = Field(description="Privacy validation report")
    download_url: Optional[str] = Field(
        default=None, description="URL to download export file (if applicable)"
    )
    file_size_bytes: Optional[int] = Field(
        default=None, description="Size of export file in bytes"
    )
    export_id: str = Field(description="Unique export ID for tracking")


class ExportSummary(BaseModel):
    """Summary of previous exports (for admin dashboard)"""

    export_id: str = Field(description="Unique export ID")
    created_at: datetime = Field(description="When export was created")
    created_by: str = Field(description="User who created export")
    format: ExportFormat = Field(description="Export format")
    total_records: int = Field(description="Total records in export")
    file_size_bytes: int = Field(description="File size in bytes")
    k_anonymity: int = Field(description="k-anonymity level used")
    validation_passed: bool = Field(description="Whether validation passed")


class ExportHistoryResponse(BaseModel):
    """Response listing previous exports"""

    success: bool = Field(description="Whether request succeeded")
    total_exports: int = Field(description="Total number of exports")
    exports: List[ExportSummary] = Field(description="List of exports")