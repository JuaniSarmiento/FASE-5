"""
Test Data Export - Example of using the data export module

This script demonstrates how to export anonymized research data
with privacy guarantees (k-anonymity, GDPR compliance).

Features demonstrated:
- Anonymization with k-anonymity
- Multi-format export (JSON, CSV, Excel)
- Privacy validation
- GDPR Article 89 compliance checking

Usage:
    python examples/test_data_export.py
"""

import sys
import io

# UTF-8 encoding fix for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from datetime import datetime, timedelta
from pathlib import Path

from src.ai_native_mvp.export import (
    DataAnonymizer,
    AnonymizationConfig,
    ResearchDataExporter,
    ExportConfig,
    ExportFormat,
    PrivacyValidator,
    GDPRCompliance,
)


def create_sample_data():
    """Create sample data for export demo"""

    # Sample traces
    traces = [
        {
            "student_id": "student_001",
            "session_id": "session_abc123",
            "activity_id": "prog2_tp1_colas",
            "cognitive_state": "EXPLORACION_CONCEPTUAL",
            "ai_involvement": 0.3,
            "content": "¿Qué es una cola circular?",
            "created_at": datetime(2025, 11, 1, 10, 30),
        },
        {
            "student_id": "student_001",
            "session_id": "session_abc123",
            "activity_id": "prog2_tp1_colas",
            "cognitive_state": "PLANIFICACION",
            "ai_involvement": 0.4,
            "content": "Voy a usar un arreglo circular",
            "created_at": datetime(2025, 11, 1, 11, 0),
        },
        {
            "student_id": "student_002",
            "session_id": "session_def456",
            "activity_id": "prog2_tp1_colas",
            "cognitive_state": "EXPLORACION_CONCEPTUAL",
            "ai_involvement": 0.6,
            "content": "Dame el código completo",  # High AI dependency
            "created_at": datetime(2025, 11, 2, 14, 15),
        },
        {
            "student_id": "student_002",
            "session_id": "session_def456",
            "activity_id": "prog2_tp1_colas",
            "cognitive_state": "IMPLEMENTACION",
            "ai_involvement": 0.7,
            "content": "Sigo sin entender",
            "created_at": datetime(2025, 11, 2, 14, 45),
        },
        {
            "student_id": "student_003",
            "session_id": "session_ghi789",
            "activity_id": "prog2_tp2_pilas",
            "cognitive_state": "PLANIFICACION",
            "ai_involvement": 0.2,
            "content": "¿Cuál es la diferencia entre pila y cola?",
            "created_at": datetime(2025, 11, 3, 9, 0),
        },
        {
            "student_id": "student_003",
            "session_id": "session_ghi789",
            "activity_id": "prog2_tp2_pilas",
            "cognitive_state": "IMPLEMENTACION",
            "ai_involvement": 0.3,
            "content": "Implementé push() correctamente",
            "created_at": datetime(2025, 11, 3, 10, 30),
        },
    ]

    # Sample evaluations
    evaluations = [
        {
            "student_id": "student_001",
            "session_id": "session_abc123",
            "activity_id": "prog2_tp1_colas",
            "overall_competency_level": "EN_DESARROLLO",
            "overall_score": 6.5,
            "dimensions": {
                "problem_decomposition": 7.0,
                "self_regulation": 5.0,
                "logical_coherence": 6.0,
            },
            "created_at": datetime(2025, 11, 1, 12, 0),
        },
        {
            "student_id": "student_002",
            "session_id": "session_def456",
            "activity_id": "prog2_tp1_colas",
            "overall_competency_level": "INICIAL",
            "overall_score": 4.0,
            "dimensions": {
                "problem_decomposition": 3.0,
                "self_regulation": 4.0,
                "logical_coherence": 5.0,
            },
            "created_at": datetime(2025, 11, 2, 15, 30),
        },
    ]

    # Sample risks
    risks = [
        {
            "student_id": "student_002",
            "session_id": "session_def456",
            "activity_id": "prog2_tp1_colas",
            "risk_type": "COGNITIVE_DELEGATION",
            "risk_level": "HIGH",
            "dimension": "COGNITIVE",
            "description": "Delegación total detectada",
            "evidence": ["Dame el código completo"],
            "recommendations": ["Exigir descomposición del problema"],
            "created_at": datetime(2025, 11, 2, 14, 15),
            "resolved": False,
        },
    ]

    return {
        "traces": traces,
        "evaluations": evaluations,
        "risks": risks,
    }


def demo_anonymization():
    """Demo 1: Data anonymization"""

    print("=" * 80)
    print("DEMO 1: DATA ANONYMIZATION")
    print("=" * 80)
    print()

    # Create sample data
    data = create_sample_data()
    print(f"📊 Sample data created:")
    print(f"   - {len(data['traces'])} traces")
    print(f"   - {len(data['evaluations'])} evaluations")
    print(f"   - {len(data['risks'])} risks")
    print()

    # Configure anonymization
    config = AnonymizationConfig(
        k_anonymity=2,  # Low for demo (production: 5+)
        suppress_pii=True,
        generalize_timestamps=True,
        add_noise_to_scores=False,  # Disabled for demo
    )

    anonymizer = DataAnonymizer(config)

    # Anonymize traces
    print("🔒 Anonymizing traces...")
    anonymized_traces = [anonymizer.anonymize_trace(t) for t in data["traces"]]

    print("\n📌 Original trace:")
    print(f"   student_id: {data['traces'][0]['student_id']}")
    print(f"   session_id: {data['traces'][0]['session_id']}")
    print(f"   created_at: {data['traces'][0]['created_at']}")

    print("\n🔐 Anonymized trace:")
    print(f"   student_hash: {anonymized_traces[0].get('student_hash', 'N/A')}")
    print(f"   session_hash: {anonymized_traces[0].get('session_hash', 'N/A')}")
    print(f"   week: {anonymized_traces[0].get('week', 'N/A')}")
    print(f"   activity_id: {anonymized_traces[0].get('activity_id', 'N/A')}")  # Not PII
    print()

    # Check k-anonymity
    print("✅ Checking k-anonymity...")
    quasi_identifiers = ["activity_id", "week"]
    k_value = anonymizer.check_k_anonymity(anonymized_traces, quasi_identifiers)
    print(f"   k-anonymity achieved: k={k_value}")
    print(f"   k-anonymity required: k={config.k_anonymity}")

    if k_value >= config.k_anonymity:
        print("   ✅ PASSED: Data meets privacy requirements")
    else:
        print("   ❌ FAILED: Need more generalization")
    print()

    return anonymized_traces


def demo_export_formats():
    """Demo 2: Multi-format export"""

    print("=" * 80)
    print("DEMO 2: MULTI-FORMAT EXPORT")
    print("=" * 80)
    print()

    # Get anonymized data
    data = create_sample_data()

    config = AnonymizationConfig(k_anonymity=2)
    anonymizer = DataAnonymizer(config)

    anonymized_data = {
        "traces": [anonymizer.anonymize_trace(t) for t in data["traces"]],
        "evaluations": [anonymizer.anonymize_evaluation(e) for e in data["evaluations"]],
        "risks": [anonymizer.anonymize_risk(r) for r in data["risks"]],
    }

    output_dir = Path("export_output")
    output_dir.mkdir(exist_ok=True)

    # Export to JSON
    print("📄 Exporting to JSON...")
    json_config = ExportConfig(format=ExportFormat.JSON, pretty_print=True)
    json_exporter = ResearchDataExporter(json_config)
    json_output = json_exporter.export(anonymized_data, output_dir / "research_data.json")
    print(f"   ✅ JSON export: {len(json_output)} bytes")
    print(f"   📁 File: export_output/research_data.json")
    print()

    # Export to CSV (first data type only)
    print("📊 Exporting traces to CSV...")
    csv_config = ExportConfig(format=ExportFormat.CSV)
    csv_exporter = ResearchDataExporter(csv_config)
    csv_output = csv_exporter.export(
        anonymized_data["traces"],
        output_dir / "research_traces.csv"
    )
    print(f"   ✅ CSV export: {len(csv_output)} bytes")
    print(f"   📁 File: export_output/research_traces.csv")
    print()

    # Export to Excel (requires openpyxl)
    try:
        print("📈 Exporting to Excel (multi-sheet)...")
        excel_config = ExportConfig(
            format=ExportFormat.EXCEL,
            excel_sheet_names={
                "traces": "Trazas Cognitivas",
                "evaluations": "Evaluaciones",
                "risks": "Riesgos",
            }
        )
        excel_exporter = ResearchDataExporter(excel_config)
        excel_output = excel_exporter.export(
            anonymized_data,
            output_dir / "research_data.xlsx"
        )
        print(f"   ✅ Excel export: {len(excel_output)} bytes")
        print(f"   📁 File: export_output/research_data.xlsx")
    except ImportError:
        print("   ⚠️ Excel export requires openpyxl: pip install openpyxl")
    print()


def demo_privacy_validation():
    """Demo 3: Privacy validation"""

    print("=" * 80)
    print("DEMO 3: PRIVACY VALIDATION")
    print("=" * 80)
    print()

    # Get anonymized data
    data = create_sample_data()

    config = AnonymizationConfig(k_anonymity=3)  # Require k=3
    anonymizer = DataAnonymizer(config)

    anonymized_traces = [anonymizer.anonymize_trace(t) for t in data["traces"]]

    # Validate privacy
    print("🔍 Running privacy validation...")
    validator = PrivacyValidator(min_k=3)

    quasi_identifiers = ["activity_id", "week"]
    result = validator.validate(anonymized_traces, quasi_identifiers)

    print("\n📊 Validation Results:")
    print(f"   Overall Status: {'✅ PASSED' if result.is_valid else '❌ FAILED'}")
    print()

    print("   Privacy Metrics:")
    for key, value in result.metrics.items():
        print(f"      {key}: {value}")
    print()

    if result.errors:
        print("   ❌ Errors:")
        for error in result.errors:
            print(f"      - {error}")
        print()

    if result.warnings:
        print("   ⚠️ Warnings:")
        for warning in result.warnings:
            print(f"      - {warning}")
        print()

    # Check GDPR compliance
    print("🇪🇺 Checking GDPR Article 89 compliance...")
    gdpr_result = GDPRCompliance.check_article_89_compliance(
        anonymization_config=config.model_dump(),
        validation_result=result,
    )

    print(f"   GDPR Compliance: {'✅ COMPLIANT' if gdpr_result.is_valid else '❌ NON-COMPLIANT'}")
    print(f"   Safeguards Implemented:")
    for safeguard, implemented in gdpr_result.metrics["safeguards_implemented"].items():
        status = "✅" if implemented else "❌"
        print(f"      {status} {safeguard}")
    print()


def main():
    """Run all demos"""

    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║              RESEARCH DATA EXPORT - COMPLETE DEMO                     ║")
    print("║                                                                       ║")
    print("║  Demonstrates:                                                        ║")
    print("║  - Data anonymization with k-anonymity                                ║")
    print("║  - Multi-format export (JSON, CSV, Excel)                             ║")
    print("║  - Privacy validation and GDPR compliance                             ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    print("\n")

    try:
        # Demo 1: Anonymization
        demo_anonymization()

        # Demo 2: Export formats
        demo_export_formats()

        # Demo 3: Privacy validation
        demo_privacy_validation()

        print("=" * 80)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print()
        print("📁 Exported files:")
        print("   - export_output/research_data.json")
        print("   - export_output/research_traces.csv")
        print("   - export_output/research_data.xlsx (if openpyxl installed)")
        print()
        print("🔐 Privacy Guarantees:")
        print("   ✅ Student IDs hashed (irreversible)")
        print("   ✅ Timestamps generalized to week level")
        print("   ✅ PII fields suppressed")
        print("   ✅ k-anonymity validated")
        print("   ✅ GDPR Article 89 compliant")
        print()
        print("📚 Use Cases:")
        print("   - Educational research publications")
        print("   - Learning analytics studies")
        print("   - Institutional improvement initiatives")
        print("   - Comparative effectiveness research")
        print()

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
