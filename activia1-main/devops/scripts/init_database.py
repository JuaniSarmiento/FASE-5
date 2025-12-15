"""
Initialize the AI-Native MVP database

This script creates all necessary tables and can optionally populate
with sample data for testing.

Usage:
    python scripts/init_database.py [--sample-data] [--database-url URL]
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import init_database, get_db_session
from backend.database.repositories import (
    SessionRepository,
    TraceRepository,
    RiskRepository,
)


def create_sample_data():
    """Create sample data for testing"""
    print("Creating sample data...")

    with get_db_session() as session:
        # Create repositories
        session_repo = SessionRepository(session)
        trace_repo = TraceRepository(session)
        risk_repo = RiskRepository(session)

        # Create a sample session
        db_session = session_repo.create(
            student_id="student_001",
            activity_id="prog2_tp1_colas",
            mode="TUTOR"
        )
        print(f"  [OK] Created session: {db_session.id}")

        print("  [OK] Sample data created successfully")


def main():
    parser = argparse.ArgumentParser(description="Initialize AI-Native MVP database")
    parser.add_argument(
        "--database-url",
        help="Database URL (default: sqlite:///ai_native_mvp.db)",
        default=None,
    )
    parser.add_argument(
        "--sample-data",
        action="store_true",
        help="Populate database with sample data",
    )
    parser.add_argument(
        "--drop-existing",
        action="store_true",
        help="Drop existing tables before creating (WARNING: data loss!)",
    )
    parser.add_argument(
        "--echo",
        action="store_true",
        help="Echo SQL statements",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("AI-Native MVP - Database Initialization")
    print("=" * 70)

    # Initialize database
    db_config = init_database(
        database_url=args.database_url,
        echo=args.echo,
        create_tables=False,  # We'll do this manually
    )

    print(f"\nDatabase URL: {db_config.database_url}")

    # Drop existing tables if requested
    if args.drop_existing:
        print("\n[WARNING] Dropping all existing tables...")
        response = input("Are you sure? (yes/no): ")
        if response.lower() == "yes":
            db_config.drop_all_tables()
            print("  [OK] Tables dropped")
        else:
            print("  Aborted")
            return

    # Create tables
    print("\nCreating database tables...")
    db_config.create_all_tables()
    print("  [OK] Tables created successfully")

    # Create sample data if requested
    if args.sample_data:
        create_sample_data()

    print("\n" + "=" * 70)
    print("[SUCCESS] Database initialization completed successfully")
    print("=" * 70)


if __name__ == "__main__":
    main()
