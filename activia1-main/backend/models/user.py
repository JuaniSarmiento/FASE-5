"""
User-related enums and constants.

FIX Cortez25: The User ORM model has been consolidated into UserDB in database/models.py
to avoid duplicate table definitions that cause SQLite index conflicts.

Use:
- `from backend.database.models import UserDB` for the ORM model
- `from backend.models.user import UserRole` for the role enum
"""
import enum


class UserRole(str, enum.Enum):
    """User roles for authorization"""
    STUDENT = "student"
    TUTOR = "tutor"
    ADMIN = "admin"


# FIX Cortez25: User class removed - use UserDB from backend.database.models instead
# The duplicate User class caused SQLite index conflicts on startup:
# "sqlite3.OperationalError: index ix_users_email already exists"
#
# If you need the User model, import it as:
#   from backend.database.models import UserDB as User