#!/bin/bash

# AI-Native MVP - Staging Deployment Verification Script
# Author: Mag. Alberto Cortez
# Date: 2025-11-24

set -e

echo "=========================================="
echo "AI-Native MVP - Staging Verification"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

NAMESPACE="ai-native-staging"
ERRORS=0
WARNINGS=0

# Helper functions
check_command() {
    if command -v $1 >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is not installed"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

check_pod_status() {
    local app_label=$1
    local expected_count=$2
    local pod_name=$3

    echo -n "Checking $pod_name pods... "

    READY_COUNT=$(kubectl get pods -n $NAMESPACE -l app=$app_label -o json | \
        jq -r '.items[] | select(.status.phase=="Running") | select(.status.conditions[] | select(.type=="Ready" and .status=="True")) | .metadata.name' | wc -l)

    if [ "$READY_COUNT" -ge "$expected_count" ]; then
        echo -e "${GREEN}✓${NC} ($READY_COUNT/$expected_count ready)"
        return 0
    else
        echo -e "${RED}✗${NC} ($READY_COUNT/$expected_count ready)"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

test_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3

    echo -n "Testing $description... "

    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -k "$url" 2>/dev/null || echo "000")

    if [ "$HTTP_CODE" = "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} (HTTP $HTTP_CODE)"
        return 0
    else
        echo -e "${RED}✗${NC} (HTTP $HTTP_CODE, expected $expected_status)"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

test_endpoint_json() {
    local url=$1
    local json_path=$2
    local expected_value=$3
    local description=$4

    echo -n "Testing $description... "

    RESPONSE=$(curl -s -k "$url" 2>/dev/null || echo "{}")
    ACTUAL_VALUE=$(echo "$RESPONSE" | jq -r "$json_path" 2>/dev/null || echo "null")

    if [ "$ACTUAL_VALUE" = "$expected_value" ]; then
        echo -e "${GREEN}✓${NC} ($json_path = $expected_value)"
        return 0
    else
        echo -e "${RED}✗${NC} ($json_path = $ACTUAL_VALUE, expected $expected_value)"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

# 1. Check Prerequisites
echo "Step 1: Checking prerequisites..."
check_command kubectl
check_command curl
check_command jq
echo ""

# 2. Check Namespace
echo "Step 2: Verifying namespace..."
if kubectl get namespace $NAMESPACE >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Namespace '$NAMESPACE' exists"
else
    echo -e "${RED}✗${NC} Namespace '$NAMESPACE' not found"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 3. Check ConfigMap and Secrets
echo "Step 3: Verifying configuration..."
if kubectl get configmap ai-native-config -n $NAMESPACE >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} ConfigMap exists"
else
    echo -e "${RED}✗${NC} ConfigMap not found"
    ERRORS=$((ERRORS + 1))
fi

if kubectl get secret ai-native-secrets -n $NAMESPACE >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Secrets exist"
else
    echo -e "${RED}✗${NC} Secrets not found"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 4. Check Pod Status
echo "Step 4: Verifying pod status..."
check_pod_status "postgresql" 1 "PostgreSQL"
check_pod_status "redis" 1 "Redis"
check_pod_status "ai-native-backend" 3 "Backend"
check_pod_status "ai-native-frontend" 2 "Frontend"
echo ""

# 5. Check Services
echo "Step 5: Verifying services..."
for service in ai-native-postgresql redis ai-native-backend ai-native-frontend; do
    if kubectl get svc $service -n $NAMESPACE >/dev/null 2>&1; then
        CLUSTER_IP=$(kubectl get svc $service -n $NAMESPACE -o jsonpath='{.spec.clusterIP}')
        echo -e "${GREEN}✓${NC} Service $service exists (ClusterIP: $CLUSTER_IP)"
    else
        echo -e "${RED}✗${NC} Service $service not found"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# 6. Check Ingress
echo "Step 6: Verifying ingress..."
if kubectl get ingress ai-native-ingress -n $NAMESPACE >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Ingress exists"

    # Check LoadBalancer IP
    INGRESS_IP=$(kubectl get ingress ai-native-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    if [ -n "$INGRESS_IP" ]; then
        echo -e "${GREEN}✓${NC} LoadBalancer IP assigned: $INGRESS_IP"
    else
        echo -e "${YELLOW}⚠${NC} LoadBalancer IP not yet assigned"
        WARNINGS=$((WARNINGS + 1))
    fi

    # Check TLS certificate
    CERT_READY=$(kubectl get certificate ai-native-staging-tls -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "False")
    if [ "$CERT_READY" = "True" ]; then
        echo -e "${GREEN}✓${NC} TLS certificate is ready"
    else
        echo -e "${YELLOW}⚠${NC} TLS certificate not ready yet (this is normal, can take 5-10 minutes)"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}✗${NC} Ingress not found"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# 7. Check HPA
echo "Step 7: Verifying HPA..."
if kubectl get hpa ai-native-backend-hpa -n $NAMESPACE >/dev/null 2>&1; then
    CURRENT_REPLICAS=$(kubectl get hpa ai-native-backend-hpa -n $NAMESPACE -o jsonpath='{.status.currentReplicas}')
    DESIRED_REPLICAS=$(kubectl get hpa ai-native-backend-hpa -n $NAMESPACE -o jsonpath='{.status.desiredReplicas}')
    echo -e "${GREEN}✓${NC} HPA exists (current: $CURRENT_REPLICAS, desired: $DESIRED_REPLICAS)"
else
    echo -e "${YELLOW}⚠${NC} HPA not found (metrics-server might not be installed)"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# 8. Get Ingress Hosts
API_HOST=$(kubectl get ingress ai-native-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[0].host}' 2>/dev/null)
APP_HOST=$(kubectl get ingress ai-native-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[1].host}' 2>/dev/null)

# 9. Test Endpoints (if DNS is configured)
echo "Step 8: Testing API endpoints..."
if [ -n "$INGRESS_IP" ]; then
    # Test with IP + Host header (before DNS)
    echo "Testing with LoadBalancer IP ($INGRESS_IP)..."

    # Health check
    test_endpoint "http://$INGRESS_IP/api/v1/health" "200" "Health endpoint"

    # Ping endpoint
    test_endpoint "http://$INGRESS_IP/api/v1/health/ping" "200" "Ping endpoint"

    # Test JSON response
    test_endpoint_json "http://$INGRESS_IP/api/v1/health" ".status" "healthy" "Health status"

    echo ""
    echo "If DNS is configured, test with:"
    echo "  curl https://$API_HOST/api/v1/health"
    echo "  curl https://$APP_HOST/"
else
    echo -e "${YELLOW}⚠${NC} Skipping endpoint tests (no LoadBalancer IP yet)"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# 10. Check Resource Usage
echo "Step 9: Checking resource usage..."
if command -v kubectl >/dev/null 2>&1; then
    echo "Pod resource usage:"
    kubectl top pods -n $NAMESPACE 2>/dev/null || echo -e "${YELLOW}⚠${NC} metrics-server not available"
    echo ""

    echo "Node resource usage:"
    kubectl top nodes 2>/dev/null || echo -e "${YELLOW}⚠${NC} metrics-server not available"
fi
echo ""

# 11. Check Logs for Errors
echo "Step 10: Checking recent logs for errors..."
echo "Backend logs (last 20 lines):"
kubectl logs -n $NAMESPACE -l app=ai-native-backend --tail=20 --since=5m 2>/dev/null | grep -i error || echo "  No errors found"
echo ""

# 12. Summary Report
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "Your staging environment is fully operational."
    echo ""
    echo "Access URLs:"
    echo "  API:      https://$API_HOST"
    echo "  Frontend: https://$APP_HOST"
    echo "  Swagger:  https://$API_HOST/docs"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ All critical checks passed with $WARNINGS warnings${NC}"
    echo ""
    echo "Common warnings (usually resolve automatically):"
    echo "  - LoadBalancer IP not assigned yet (wait 1-2 minutes)"
    echo "  - TLS certificate provisioning (wait 5-10 minutes)"
    echo "  - Metrics server not installed (HPA won't work)"
    echo ""
    echo "Monitor with:"
    echo "  watch kubectl get pods -n $NAMESPACE"
    echo "  kubectl describe certificate ai-native-staging-tls -n $NAMESPACE"
    exit 0
else
    echo -e "${RED}✗ Verification failed with $ERRORS errors and $WARNINGS warnings${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "  1. Check pod status:    kubectl get pods -n $NAMESPACE"
    echo "  2. Check pod logs:      kubectl logs -f <pod-name> -n $NAMESPACE"
    echo "  3. Describe pod:        kubectl describe pod <pod-name> -n $NAMESPACE"
    echo "  4. Check events:        kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'"
    echo ""
    echo "Common issues:"
    echo "  - Secrets not created:  See README.md 'Step 3: Secrets'"
    echo "  - Image pull failed:    Update image in 06-backend.yaml and 07-frontend.yaml"
    echo "  - Database not ready:   Check postgresql pod logs"
    exit 1
fi