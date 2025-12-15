#!/bin/bash

# ============================================================================
# Setup UAT Environment - AI-Native MVP
# ============================================================================
#
# This script prepares the complete UAT environment:
# 1. Create test users (5 students + 1 instructor)
# 2. Create test activity (TP1 - Colas Circulares)
# 3. Configure bug reporting system
# 4. Setup monitoring and logging
# 5. Generate credentials file
#
# Usage:
#   ./setup-uat-environment.sh [--staging|--local]
#
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default environment
ENVIRONMENT="${1:-local}"

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}UAT ENVIRONMENT SETUP - AI-Native MVP${NC}"
echo -e "${BLUE}============================================================================${NC}"

echo -e "\n${YELLOW}Environment: ${ENVIRONMENT}${NC}\n"

# ============================================================================
# 1. Verify Prerequisites
# ============================================================================

echo -e "${BLUE}[1/6] Verifying prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python 3 found: $(python3 --version)"

# Check virtual environment
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not found - creating...${NC}"
    python3 -m venv .venv
fi
echo -e "${GREEN}✓${NC} Virtual environment ready"

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Check database
if [ "$ENVIRONMENT" == "staging" ]; then
    # Check PostgreSQL connection
    if [ -z "$DATABASE_URL" ]; then
        echo -e "${YELLOW}⚠ DATABASE_URL not set - using default staging DB${NC}"
        export DATABASE_URL="postgresql://ai_native:password@localhost:5432/ai_native_staging"
    fi
    echo -e "${GREEN}✓${NC} Using PostgreSQL: ${DATABASE_URL}"
else
    # Local SQLite
    echo -e "${GREEN}✓${NC} Using SQLite: ai_native.db"
fi

# ============================================================================
# 2. Initialize Database
# ============================================================================

echo -e "\n${BLUE}[2/6] Initializing database...${NC}"

if [ "$ENVIRONMENT" == "staging" ]; then
    # Run database initialization for PostgreSQL
    python scripts/init_database.py --database-url "$DATABASE_URL"
else
    # Run database initialization for SQLite
    python scripts/init_database.py
fi

echo -e "${GREEN}✓${NC} Database initialized"

# ============================================================================
# 3. Create Test Users
# ============================================================================

echo -e "\n${BLUE}[3/6] Creating test users...${NC}"

if [ "$ENVIRONMENT" == "staging" ]; then
    python user-acceptance-testing/setup/create-test-users.py \
        --database-url "$DATABASE_URL" \
        --output user-acceptance-testing/setup/credentials/uat-credentials.md
else
    python user-acceptance-testing/setup/create-test-users.py \
        --output user-acceptance-testing/setup/credentials/uat-credentials.md
fi

echo -e "${GREEN}✓${NC} Test users created (5 students + 1 instructor)"

# ============================================================================
# 4. Create Test Activity
# ============================================================================

echo -e "\n${BLUE}[4/6] Creating test activity...${NC}"

if [ "$ENVIRONMENT" == "staging" ]; then
    python user-acceptance-testing/setup/create-test-activity.py \
        --database-url "$DATABASE_URL"
else
    python user-acceptance-testing/setup/create-test-activity.py
fi

echo -e "${GREEN}✓${NC} Test activity created (TP1 - Colas Circulares)"

# ============================================================================
# 5. Configure Bug Reporting System
# ============================================================================

echo -e "\n${BLUE}[5/6] Configuring bug reporting system...${NC}"

# Create bugs directory if it doesn't exist
mkdir -p user-acceptance-testing/bugs

# Create bug tracking file
cat > user-acceptance-testing/bugs/bug-tracker.json <<EOF
{
  "bugs": [],
  "metadata": {
    "created_at": "$(date -Iseconds)",
    "total_bugs": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  }
}
EOF

echo -e "${GREEN}✓${NC} Bug tracking system configured"

# ============================================================================
# 6. Setup Monitoring and Logging
# ============================================================================

echo -e "\n${BLUE}[6/6] Setting up monitoring and logging...${NC}"

# Create logs directory
mkdir -p logs/uat

# Create monitoring configuration
cat > logs/uat/monitoring-config.json <<EOF
{
  "log_level": "INFO",
  "log_to_file": true,
  "log_file": "logs/uat/uat-session.log",
  "metrics": {
    "track_response_time": true,
    "track_errors": true,
    "track_user_actions": true
  },
  "alerts": {
    "critical_bugs": {
      "enabled": true,
      "email": "instructor@uat.ai-native.edu"
    },
    "high_errors": {
      "enabled": true,
      "threshold": 10,
      "window_minutes": 5
    }
  }
}
EOF

echo -e "${GREEN}✓${NC} Monitoring and logging configured"

# ============================================================================
# Final Summary
# ============================================================================

echo -e "\n${BLUE}============================================================================${NC}"
echo -e "${GREEN}UAT ENVIRONMENT SETUP COMPLETE${NC}"
echo -e "${BLUE}============================================================================${NC}"

echo -e "\n${YELLOW}📊 Summary:${NC}"
echo -e "   Environment: ${ENVIRONMENT}"
echo -e "   Database: $([ "$ENVIRONMENT" == "staging" ] && echo "PostgreSQL" || echo "SQLite")"
echo -e "   Users created: 6 (5 students + 1 instructor)"
echo -e "   Activities created: 1 (TP1 - Colas Circulares)"
echo -e "   Bug tracking: Enabled"
echo -e "   Monitoring: Enabled"

echo -e "\n${YELLOW}📁 Generated Files:${NC}"
echo -e "   Credentials: user-acceptance-testing/setup/credentials/uat-credentials.md"
echo -e "   Bug tracker: user-acceptance-testing/bugs/bug-tracker.json"
echo -e "   Monitoring config: logs/uat/monitoring-config.json"

echo -e "\n${YELLOW}🚀 Next Steps:${NC}"
echo -e "   1. Review credentials file (CONFIDENTIAL)"
echo -e "   2. Send credentials to participants via SECURE channel"
echo -e "   3. Start API server:"
if [ "$ENVIRONMENT" == "staging" ]; then
    echo -e "      ${BLUE}python scripts/run_api.py --production${NC}"
else
    echo -e "      ${BLUE}python scripts/run_api.py${NC}"
fi
echo -e "   4. Test login with one student account"
echo -e "   5. Begin UAT execution (2 weeks)"

echo -e "\n${YELLOW}📞 Support:${NC}"
echo -e "   Email: instructor@uat.ai-native.edu"
echo -e "   Slack: #uat-ai-native"
echo -e "   Phone: [Contact number]"

echo -e "\n${BLUE}============================================================================${NC}"

# Deactivate virtual environment
deactivate

exit 0