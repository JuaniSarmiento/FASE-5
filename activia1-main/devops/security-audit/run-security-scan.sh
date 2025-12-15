#!/bin/bash

# AI-Native MVP - Security Audit Runner
# Author: Mag. Alberto Cortez
# Date: 2025-11-24

set -e

echo "=========================================="
echo "AI-Native MVP - Security Audit"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Create reports directory
mkdir -p ./reports

# Menu
echo "Select security scan type:"
echo ""
echo "1) Full scan (OWASP ZAP + Trivy + Kubesec) - 45 minutes"
echo "2) Quick scan (OWASP ZAP baseline only) - 5 minutes"
echo "3) Container scan (Trivy only) - 2 minutes"
echo "4) Kubernetes manifest scan (Kubesec only) - 1 minute"
echo "5) Secrets scan (TruffleHog) - 3 minutes"
echo "6) Custom OWASP ZAP scan (use zap-scan-config.yaml)"
echo "7) Exit"
echo ""
read -p "Enter option (1-7): " SCAN_TYPE

case $SCAN_TYPE in
    1)
        echo ""
        echo "Running FULL security audit..."
        echo "This will take approximately 45 minutes."
        echo ""

        # Get target URL
        read -p "Enter target URL (default: http://localhost:8000): " TARGET_URL
        TARGET_URL=${TARGET_URL:-http://localhost:8000}

        echo ""
        echo "=========================================="
        echo "Step 1/5: OWASP ZAP Full Scan"
        echo "=========================================="
        echo ""

        # Check if ZAP is installed
        if command -v zap.sh >/dev/null 2>&1; then
            echo "Running OWASP ZAP full scan..."
            zap.sh -cmd -autorun zap-scan-config.yaml -config api.key=$(uuidgen)
        elif command -v docker >/dev/null 2>&1; then
            echo "Running OWASP ZAP via Docker..."
            docker run --rm -v $(pwd):/zap/wrk/:rw \
                -t softwaresecurityproject/zap-stable \
                zap-full-scan.py -t $TARGET_URL \
                -r ./reports/zap-full-report.html \
                -J ./reports/zap-full-report.json \
                -x ./reports/zap-full-report.xml || true
        else
            echo -e "${YELLOW}⚠ ZAP not installed. Skipping OWASP ZAP scan.${NC}"
        fi

        echo ""
        echo "=========================================="
        echo "Step 2/5: Container Vulnerability Scan (Trivy)"
        echo "=========================================="
        echo ""

        if command -v trivy >/dev/null 2>&1; then
            echo "Scanning backend container image..."
            trivy image --severity HIGH,CRITICAL \
                --format json \
                --output ./reports/trivy-backend.json \
                ai-native-backend:latest || echo "Image not found locally"

            trivy image --severity HIGH,CRITICAL \
                --format table \
                ai-native-backend:latest || echo "Image not found locally"
        else
            echo -e "${YELLOW}⚠ Trivy not installed. Skipping container scan.${NC}"
            echo "Install: https://aquasecurity.github.io/trivy/latest/getting-started/installation/"
        fi

        echo ""
        echo "=========================================="
        echo "Step 3/5: Kubernetes Manifest Security (Kubesec)"
        echo "=========================================="
        echo ""

        if command -v kubesec >/dev/null 2>&1; then
            echo "Scanning Kubernetes manifests..."
            kubesec scan ../kubernetes/staging/*.yaml > ./reports/kubesec-report.json
            cat ./reports/kubesec-report.json | jq '.[] | {file: .object, score: .score, critical: .scoring.critical}'
        else
            echo -e "${YELLOW}⚠ Kubesec not installed. Skipping Kubernetes scan.${NC}"
            echo "Install: https://github.com/controlplaneio/kubesec"
        fi

        echo ""
        echo "=========================================="
        echo "Step 4/5: Secrets Detection (TruffleHog)"
        echo "=========================================="
        echo ""

        if command -v trufflehog >/dev/null 2>&1; then
            echo "Scanning for secrets in Git history..."
            trufflehog git file://$(git rev-parse --show-toplevel) \
                --json \
                --output ./reports/trufflehog-report.json || true

            if [ -s ./reports/trufflehog-report.json ]; then
                echo -e "${RED}❌ SECRETS FOUND!${NC}"
                cat ./reports/trufflehog-report.json | jq -r '.SourceMetadata.Data.Git.file' | sort | uniq
            else
                echo -e "${GREEN}✓ No secrets detected${NC}"
            fi
        else
            echo -e "${YELLOW}⚠ TruffleHog not installed. Skipping secrets scan.${NC}"
            echo "Install: https://github.com/trufflesecurity/trufflehog"
        fi

        echo ""
        echo "=========================================="
        echo "Step 5/5: Dependency Vulnerability Scan (Safety)"
        echo "=========================================="
        echo ""

        if command -v safety >/dev/null 2>&1; then
            echo "Scanning Python dependencies..."
            safety check --json --output ./reports/safety-report.json || true
            safety check || true
        else
            echo -e "${YELLOW}⚠ Safety not installed. Skipping dependency scan.${NC}"
            echo "Install: pip install safety"
        fi

        echo ""
        echo -e "${GREEN}=========================================="
        echo "Full Security Audit Complete!"
        echo "==========================================${NC}"
        ;;

    2)
        echo ""
        echo "Running OWASP ZAP baseline scan (quick)..."

        read -p "Enter target URL (default: http://localhost:8000): " TARGET_URL
        TARGET_URL=${TARGET_URL:-http://localhost:8000}

        if command -v docker >/dev/null 2>&1; then
            docker run --rm -v $(pwd):/zap/wrk/:rw \
                -t softwaresecurityproject/zap-stable \
                zap-baseline.py -t $TARGET_URL \
                -r ./reports/zap-baseline-report.html \
                -J ./reports/zap-baseline-report.json || true
            echo ""
            echo -e "${GREEN}✓ Baseline scan complete${NC}"
            echo "Report: ./reports/zap-baseline-report.html"
        else
            echo -e "${RED}ERROR: Docker is required for ZAP baseline scan${NC}"
            exit 1
        fi
        ;;

    3)
        echo ""
        echo "Running Trivy container scan..."

        if ! command -v trivy >/dev/null 2>&1; then
            echo -e "${RED}ERROR: Trivy not installed${NC}"
            echo "Install: https://aquasecurity.github.io/trivy/latest/getting-started/installation/"
            exit 1
        fi

        read -p "Enter image name (default: ai-native-backend:latest): " IMAGE_NAME
        IMAGE_NAME=${IMAGE_NAME:-ai-native-backend:latest}

        echo ""
        echo "Scanning $IMAGE_NAME..."
        trivy image --severity HIGH,CRITICAL $IMAGE_NAME

        echo ""
        echo "Generating JSON report..."
        trivy image --severity HIGH,CRITICAL \
            --format json \
            --output ./reports/trivy-scan.json \
            $IMAGE_NAME

        echo ""
        echo -e "${GREEN}✓ Container scan complete${NC}"
        echo "Report: ./reports/trivy-scan.json"
        ;;

    4)
        echo ""
        echo "Running Kubesec manifest scan..."

        if ! command -v kubesec >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠ Kubesec not installed. Using online API...${NC}"

            for manifest in ../kubernetes/staging/*.yaml; do
                echo "Scanning $(basename $manifest)..."
                curl -sSX POST --data-binary @$manifest https://v2.kubesec.io/scan
            done
        else
            kubesec scan ../kubernetes/staging/*.yaml > ./reports/kubesec-report.json
            cat ./reports/kubesec-report.json | jq '.[] | {file: .object, score: .score}'
            echo ""
            echo -e "${GREEN}✓ Kubernetes manifest scan complete${NC}"
            echo "Report: ./reports/kubesec-report.json"
        fi
        ;;

    5)
        echo ""
        echo "Running TruffleHog secrets scan..."

        if ! command -v trufflehog >/dev/null 2>&1; then
            echo -e "${RED}ERROR: TruffleHog not installed${NC}"
            echo "Install: https://github.com/trufflesecurity/trufflehog"
            exit 1
        fi

        echo "Scanning Git repository for secrets..."
        trufflehog git file://$(git rev-parse --show-toplevel) \
            --json \
            --output ./reports/trufflehog-report.json || true

        if [ -s ./reports/trufflehog-report.json ]; then
            echo -e "${RED}❌ SECRETS FOUND!${NC}"
            echo ""
            cat ./reports/trufflehog-report.json | jq -r '.SourceMetadata.Data.Git.file' | sort | uniq
            echo ""
            echo "Review: ./reports/trufflehog-report.json"
            exit 1
        else
            echo -e "${GREEN}✓ No secrets detected${NC}"
        fi
        ;;

    6)
        echo ""
        echo "Running custom OWASP ZAP scan using zap-scan-config.yaml..."

        read -p "Enter target URL (default: http://localhost:8000): " TARGET_URL
        TARGET_URL=${TARGET_URL:-http://localhost:8000}

        # Update config with target URL
        sed -i.bak "s|http://localhost:8000|$TARGET_URL|g" zap-scan-config.yaml

        if command -v zap.sh >/dev/null 2>&1; then
            zap.sh -cmd -autorun zap-scan-config.yaml
        elif command -v docker >/dev/null 2>&1; then
            docker run --rm -v $(pwd):/zap/wrk/:rw \
                -t softwaresecurityproject/zap-stable \
                zap-automation.py -autorun /zap/wrk/zap-scan-config.yaml
        else
            echo -e "${RED}ERROR: ZAP not installed${NC}"
            exit 1
        fi

        # Restore backup
        mv zap-scan-config.yaml.bak zap-scan-config.yaml

        echo ""
        echo -e "${GREEN}✓ Custom scan complete${NC}"
        ;;

    7)
        echo "Exiting..."
        exit 0
        ;;

    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Security Scan Summary"
echo "=========================================="
echo ""
echo "Reports generated in: ./reports/"
ls -lh ./reports/ | grep -v "^total"
echo ""
echo "Next steps:"
echo "  1. Review HTML reports: firefox ./reports/*.html"
echo "  2. Analyze JSON reports for CI/CD integration"
echo "  3. Address HIGH and CRITICAL findings"
echo "  4. Document false positives"
echo "  5. Re-run scan after fixes"
echo ""