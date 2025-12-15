#!/usr/bin/env python3
"""
Create Test Users for UAT - AI-Native MVP

This script creates 5 test students and 1 instructor for User Acceptance Testing.

Usage:
    python create-test-users.py [--database-url DATABASE_URL]

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (default: from .env or SQLite)
"""

import sys
import os
import io
import argparse
import hashlib
import secrets
from datetime import datetime
from pathlib import Path

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ai_native_mvp.database import get_db_session, init_database
from src.ai_native_mvp.database.models import Base
from sqlalchemy import create_engine, text


# ============================================================================
# User Profiles for UAT
# ============================================================================

UAT_USERS = {
    "students": [
        {
            "id": "E01",
            "name": "Estudiante 1",
            "email": "estudiante1@uat.ai-native.edu",
            "password": "UAT2025_E01!",
            "profile": "AVANZADO",
            "description": "Estudiante avanzado con experiencia previa en programación",
        },
        {
            "id": "E02",
            "name": "Estudiante 2",
            "email": "estudiante2@uat.ai-native.edu",
            "password": "UAT2025_E02!",
            "profile": "INTERMEDIO",
            "description": "Estudiante intermedio, confiado pero con lagunas conceptuales",
        },
        {
            "id": "E03",
            "name": "Estudiante 3",
            "email": "estudiante3@uat.ai-native.edu",
            "password": "UAT2025_E03!",
            "profile": "INTERMEDIO",
            "description": "Estudiante intermedio, disciplinado y organizado",
        },
        {
            "id": "E04",
            "name": "Estudiante 4",
            "email": "estudiante4@uat.ai-native.edu",
            "password": "UAT2025_E04!",
            "profile": "INICIAL",
            "description": "Estudiante inicial con dificultades, frustración frecuente",
        },
        {
            "id": "E05",
            "name": "Estudiante 5",
            "email": "estudiante5@uat.ai-native.edu",
            "password": "UAT2025_E05!",
            "profile": "INTERMEDIO",
            "description": "Estudiante intermedio, curioso y proactivo",
        },
    ],
    "instructors": [
        {
            "id": "INST01",
            "name": "Instructor UAT",
            "email": "instructor@uat.ai-native.edu",
            "password": "UAT2025_INST!",
            "role": "INSTRUCTOR",
            "description": "Supervisor de UAT con acceso completo al dashboard",
        },
    ],
}


# ============================================================================
# Helper Functions
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt (simplified for UAT)."""
    # In production, use bcrypt or similar
    salt = "uat_salt_2025"
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


def generate_token() -> str:
    """Generate random token for password reset."""
    return secrets.token_urlsafe(32)


def create_users_table(engine):
    """Create users table if it doesn't exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL DEFAULT 'STUDENT',
        profile VARCHAR(50),
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        password_reset_token VARCHAR(255),
        password_reset_expires TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
    CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
    """

    with engine.connect() as conn:
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in create_table_sql.split(';') if s.strip()]
        for statement in statements:
            conn.execute(text(statement))
        conn.commit()


def create_user(session, user_data: dict):
    """Create a single user in the database."""
    # Check if user already exists
    result = session.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": user_data["email"]}
    )
    existing = result.fetchone()

    if existing:
        print(f"⚠️  User {user_data['id']} ({user_data['email']}) already exists - skipping")
        return False

    # Hash password
    password_hash = hash_password(user_data["password"])

    # Insert user
    insert_sql = """
    INSERT INTO users (id, name, email, password_hash, role, profile, description, created_at, is_active)
    VALUES (:id, :name, :email, :password_hash, :role, :profile, :description, :created_at, :is_active)
    """

    session.execute(text(insert_sql), {
        "id": user_data["id"],
        "name": user_data["name"],
        "email": user_data["email"],
        "password_hash": password_hash,
        "role": user_data.get("role", "STUDENT"),
        "profile": user_data.get("profile"),
        "description": user_data.get("description"),
        "created_at": datetime.utcnow(),
        "is_active": True,
    })

    print(f"✅ Created user {user_data['id']}: {user_data['name']} ({user_data['email']})")
    return True


def print_credentials_summary(users: dict):
    """Print summary of created users with credentials."""
    print("\n" + "="*80)
    print("UAT USER CREDENTIALS - CONFIDENTIAL")
    print("="*80)

    print("\n📚 STUDENTS (5 total):")
    print("-" * 80)
    for student in users["students"]:
        print(f"\n{student['id']} - {student['name']} ({student['profile']})")
        print(f"  Email:       {student['email']}")
        print(f"  Password:    {student['password']}")
        print(f"  Description: {student['description']}")

    print("\n\n👨‍🏫 INSTRUCTORS (1 total):")
    print("-" * 80)
    for instructor in users["instructors"]:
        print(f"\n{instructor['id']} - {instructor['name']}")
        print(f"  Email:    {instructor['email']}")
        print(f"  Password: {instructor['password']}")
        print(f"  Role:     {instructor['role']}")

    print("\n" + "="*80)
    print("⚠️  IMPORTANT:")
    print("   1. Send credentials to participants via SECURE channel (encrypted email)")
    print("   2. Instruct users to change passwords on first login")
    print("   3. Delete this output after distribution")
    print("="*80)


def save_credentials_to_file(users: dict, output_path: Path):
    """Save credentials to encrypted file for distribution."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# UAT User Credentials - CONFIDENTIAL\n")
        f.write("# Generated: {}\n".format(datetime.utcnow().isoformat()))
        f.write("# DO NOT SHARE PUBLICLY\n\n")

        f.write("## Students\n\n")
        for student in users["students"]:
            f.write(f"### {student['id']} - {student['name']}\n")
            f.write(f"- **Email**: {student['email']}\n")
            f.write(f"- **Password**: `{student['password']}`\n")
            f.write(f"- **Profile**: {student['profile']}\n")
            f.write(f"- **Description**: {student['description']}\n\n")

        f.write("## Instructors\n\n")
        for instructor in users["instructors"]:
            f.write(f"### {instructor['id']} - {instructor['name']}\n")
            f.write(f"- **Email**: {instructor['email']}\n")
            f.write(f"- **Password**: `{instructor['password']}`\n")
            f.write(f"- **Role**: {instructor['role']}\n\n")

        f.write("\n---\n\n")
        f.write("**SECURITY NOTES**:\n")
        f.write("1. These are temporary passwords for UAT only\n")
        f.write("2. Users MUST change passwords on first login\n")
        f.write("3. Passwords expire after 30 days\n")
        f.write("4. All sessions will be logged for UAT analysis\n")

    print(f"\n✅ Credentials saved to: {output_path}")
    print(f"   File size: {output_path.stat().st_size} bytes")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Create UAT test users")
    parser.add_argument(
        "--database-url",
        type=str,
        help="Database connection URL (default: from .env or SQLite)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent / "credentials" / "uat-credentials.md",
        help="Output file for credentials (default: credentials/uat-credentials.md)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be created without actually creating users",
    )

    args = parser.parse_args()

    print("="*80)
    print("UAT USER CREATION - AI-Native MVP")
    print("="*80)

    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No users will be created\n")

    # Initialize database
    try:
        if args.database_url:
            init_database(database_url=args.database_url)
            engine = create_engine(args.database_url)
        else:
            # Use default from .env or SQLite
            from src.ai_native_mvp.database.config import get_db_config
            init_database()
            config = get_db_config()
            engine = config.get_engine()

        print(f"\n✅ Database connection established")
        print(f"   URL: {str(engine.url).split('@')[-1] if '@' in str(engine.url) else engine.url}")

    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        sys.exit(1)

    # Create users table if it doesn't exist
    try:
        print("\n📋 Creating users table (if not exists)...")
        create_users_table(engine)
        print("✅ Users table ready")
    except Exception as e:
        print(f"❌ Failed to create users table: {e}")
        sys.exit(1)

    if args.dry_run:
        print("\n📊 Would create the following users:\n")
        print_credentials_summary(UAT_USERS)
        print("\n✅ Dry run complete - no changes made")
        return

    # Create users
    with get_db_session() as session:
        created_count = 0
        skipped_count = 0

        print("\n👥 Creating students...")
        for student in UAT_USERS["students"]:
            if create_user(session, student):
                created_count += 1
            else:
                skipped_count += 1

        print("\n👨‍🏫 Creating instructors...")
        for instructor in UAT_USERS["instructors"]:
            if create_user(session, instructor):
                created_count += 1
            else:
                skipped_count += 1

        session.commit()

        print(f"\n✅ User creation complete:")
        print(f"   Created: {created_count}")
        print(f"   Skipped: {skipped_count}")

    # Print credentials summary
    print_credentials_summary(UAT_USERS)

    # Save credentials to file
    try:
        save_credentials_to_file(UAT_USERS, args.output)
    except Exception as e:
        print(f"\n⚠️  Failed to save credentials file: {e}")

    # Verify users were created
    with get_db_session() as session:
        result = session.execute(text("SELECT COUNT(*) FROM users"))
        total_users = result.scalar()
        print(f"\n✅ Verification: {total_users} total users in database")

    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Review credentials in:", args.output)
    print("2. Send credentials to participants via SECURE channel")
    print("3. Configure password reset functionality")
    print("4. Test login with one student account")
    print("5. Enable password change on first login")
    print("="*80)


if __name__ == "__main__":
    main()