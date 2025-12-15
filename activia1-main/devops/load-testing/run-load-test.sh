#!/bin/bash

# AI-Native MVP - Load Testing Runner
# Author: Mag. Alberto Cortez
# Date: 2025-11-24

set -e

echo "=========================================="
echo "AI-Native MVP - Load Testing"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check prerequisites
echo "Step 1: Checking prerequisites..."

if ! command -v node >/dev/null 2>&1; then
    echo -e "${RED}ERROR: Node.js is not installed${NC}"
    echo ""
    echo "Install Node.js:"
    echo "  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -"
    echo "  sudo apt-get install -y nodejs"
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo -e "${RED}ERROR: npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Node.js $(node --version)${NC}"
echo -e "${GREEN}✓ npm $(npm --version)${NC}"
echo ""

# Check if artillery is installed
echo "Step 2: Checking Artillery installation..."
if ! command -v artillery >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Artillery not installed. Installing...${NC}"
    npm install -g artillery
else
    echo -e "${GREEN}✓ Artillery $(artillery version | head -1)${NC}"
fi
echo ""

# Get target URL
echo "Step 3: Configure target..."
read -p "Enter target URL (default: http://localhost:8000): " TARGET_URL
TARGET_URL=${TARGET_URL:-http://localhost:8000}

echo "Target: $TARGET_URL"
echo ""

# Test connectivity
echo "Step 4: Testing connectivity..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $TARGET_URL/api/v1/health 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Target is reachable (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}✗ Target is not reachable (HTTP $HTTP_CODE)${NC}"
    echo ""
    echo "Please ensure:"
    echo "  1. Backend is running"
    echo "  2. URL is correct"
    echo "  3. Network connectivity"
    exit 1
fi
echo ""

# Select test type
echo "Step 5: Select test type..."
echo ""
echo "1) Quick test (1 minute, 10 RPS)"
echo "2) Standard test (5 minutes, 30 RPS)"
echo "3) Stress test (10 minutes, 50-100 RPS)"
echo "4) Full test (15 minutes, as configured in artillery-config.yml)"
echo "5) Spike test (2 minutes, sudden spike to 200 RPS)"
echo ""
read -p "Enter option (1-5): " TEST_TYPE

case $TEST_TYPE in
    1)
        echo ""
        echo "Running quick test..."
        artillery quick --duration 60 --rate 10 $TARGET_URL/api/v1/health
        ;;

    2)
        echo ""
        echo "Running standard test..."
        cat > /tmp/artillery-standard.yml <<EOF
config:
  target: "$TARGET_URL"
  phases:
    - duration: 300
      arrivalRate: 30
      name: "Standard load"
  defaults:
    headers:
      Content-Type: "application/json"

scenarios:
  - name: "Mixed load"
    flow:
      - get:
          url: "/api/v1/health"
EOF
        artillery run /tmp/artillery-standard.yml --output /tmp/artillery-report-standard.json
        echo ""
        echo "Generating HTML report..."
        artillery report /tmp/artillery-report-standard.json --output ./reports/artillery-report-standard.html
        echo -e "${GREEN}✓ Report saved: ./reports/artillery-report-standard.html${NC}"
        ;;

    3)
        echo ""
        echo "Running stress test..."
        cat > /tmp/artillery-stress.yml <<EOF
config:
  target: "$TARGET_URL"
  phases:
    - duration: 300
      arrivalRate: 20
      name: "Warm-up"
    - duration: 300
      arrivalRate: 50
      name: "Stress phase 1"
    - duration: 300
      arrivalRate: 100
      name: "Stress phase 2"
  defaults:
    headers:
      Content-Type: "application/json"

scenarios:
  - name: "Health check"
    weight: 30
    flow:
      - get:
          url: "/api/v1/health"

  - name: "Create session"
    weight: 40
    flow:
      - post:
          url: "/api/v1/sessions"
          json:
            student_id: "load_test_{{ \$randomString() }}"
            activity_id: "prog2_tp1_colas"
            mode: "TUTOR"

  - name: "List sessions"
    weight: 30
    flow:
      - get:
          url: "/api/v1/sessions?page=1&page_size=20"
EOF
        artillery run /tmp/artillery-stress.yml --output /tmp/artillery-report-stress.json
        echo ""
        echo "Generating HTML report..."
        artillery report /tmp/artillery-report-stress.json --output ./reports/artillery-report-stress.html
        echo -e "${GREEN}✓ Report saved: ./reports/artillery-report-stress.html${NC}"
        ;;

    4)
        echo ""
        echo "Running full test (as configured in artillery-config.yml)..."

        # Update target in config
        sed -i.bak "s|target: \".*\"|target: \"$TARGET_URL\"|g" artillery-config.yml

        artillery run artillery-config.yml --output /tmp/artillery-report-full.json
        echo ""
        echo "Generating HTML report..."
        artillery report /tmp/artillery-report-full.json --output ./reports/artillery-report-full.html
        echo -e "${GREEN}✓ Report saved: ./reports/artillery-report-full.html${NC}"

        # Restore backup
        mv artillery-config.yml.bak artillery-config.yml
        ;;

    5)
        echo ""
        echo "Running spike test..."
        cat > /tmp/artillery-spike.yml <<EOF
config:
  target: "$TARGET_URL"
  phases:
    - duration: 60
      arrivalRate: 10
      name: "Baseline"
    - duration: 30
      arrivalRate: 200
      name: "SPIKE"
    - duration: 60
      arrivalRate: 10
      name: "Recovery"
  defaults:
    headers:
      Content-Type: "application/json"

scenarios:
  - name: "Spike load"
    flow:
      - get:
          url: "/api/v1/health"
EOF
        artillery run /tmp/artillery-spike.yml --output /tmp/artillery-report-spike.json
        echo ""
        echo "Generating HTML report..."
        artillery report /tmp/artillery-report-spike.json --output ./reports/artillery-report-spike.html
        echo -e "${GREEN}✓ Report saved: ./reports/artillery-report-spike.html${NC}"
        ;;

    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Load Test Complete!"
echo "=========================================="
echo ""

# Cleanup
rm -f /tmp/artillery-*.yml /tmp/artillery-*.json

# Show summary
echo "Next steps:"
echo "  1. Open HTML report in browser: firefox ./reports/artillery-report-*.html"
echo "  2. Analyze metrics (response times, error rates, throughput)"
echo "  3. Check HPA scaling: kubectl get hpa -n ai-native-staging"
echo "  4. Monitor pods: kubectl top pods -n ai-native-staging"
echo ""