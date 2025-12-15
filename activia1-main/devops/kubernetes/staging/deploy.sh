#!/bin/bash

# AI-Native MVP - Staging Deployment Script
# Author: Mag. Alberto Cortez
# Date: 2025-11-24

set -e  # Exit on error

echo "=========================================="
echo "AI-Native MVP - Staging Deployment"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Step 1: Checking prerequisites..."
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}ERROR: kubectl is not installed${NC}"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo -e "${RED}ERROR: helm is not installed${NC}"; exit 1; }

echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# Verify cluster access
echo "Step 2: Verifying cluster access..."
kubectl cluster-info >/dev/null 2>&1 || { echo -e "${RED}ERROR: Cannot connect to Kubernetes cluster${NC}"; exit 1; }
echo -e "${GREEN}✓ Cluster accessible${NC}"
echo ""

# Create namespace and base resources
echo "Step 3: Creating namespace and base resources..."
kubectl apply -f 01-namespace.yaml
echo -e "${GREEN}✓ Namespace created${NC}"
echo ""

# Create ConfigMap
echo "Step 4: Creating ConfigMap..."
kubectl apply -f 02-configmap.yaml
echo -e "${GREEN}✓ ConfigMap created${NC}"
echo ""

# Check if secrets exist
echo "Step 5: Checking secrets..."
if kubectl get secret ai-native-secrets -n ai-native-staging >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Secrets already exist. Skipping creation.${NC}"
    echo -e "${YELLOW}  To recreate secrets, delete them first:${NC}"
    echo -e "${YELLOW}  kubectl delete secret ai-native-secrets -n ai-native-staging${NC}"
else
    echo -e "${RED}ERROR: Secrets not found!${NC}"
    echo ""
    echo "Please create secrets manually:"
    echo ""
    echo "  JWT_SECRET=\$(python -c \"import secrets; print(secrets.token_urlsafe(32))\")"
    echo "  POSTGRES_PASSWORD=\$(python -c \"import secrets; print(secrets.token_urlsafe(16))\")"
    echo ""
    echo "  kubectl create secret generic ai-native-secrets \\"
    echo "    --namespace=ai-native-staging \\"
    echo "    --from-literal=JWT_SECRET_KEY=\"\$JWT_SECRET\" \\"
    echo "    --from-literal=DATABASE_URL=\"postgresql://ai_native:\$POSTGRES_PASSWORD@ai-native-postgresql:5432/ai_native\" \\"
    echo "    --from-literal=POSTGRES_PASSWORD=\"\$POSTGRES_PASSWORD\" \\"
    echo "    --from-literal=OPENAI_API_KEY=\"\${OPENAI_API_KEY:-}\" \\"
    echo "    --from-literal=GEMINI_API_KEY=\"\${GEMINI_API_KEY:-}\""
    echo ""
    exit 1
fi
echo ""

# Deploy PostgreSQL
echo "Step 6: Deploying PostgreSQL..."
kubectl apply -f 04-postgresql.yaml
echo -e "${YELLOW}⏳ Waiting for PostgreSQL to be ready (timeout: 120s)...${NC}"
kubectl wait --for=condition=ready pod -l app=postgresql -n ai-native-staging --timeout=120s || {
    echo -e "${RED}ERROR: PostgreSQL pod not ready${NC}"
    kubectl describe pod -l app=postgresql -n ai-native-staging
    exit 1
}
echo -e "${GREEN}✓ PostgreSQL ready${NC}"
echo ""

# Deploy Redis
echo "Step 7: Deploying Redis..."
kubectl apply -f 05-redis.yaml
echo -e "${YELLOW}⏳ Waiting for Redis to be ready (timeout: 60s)...${NC}"
kubectl wait --for=condition=ready pod -l app=redis -n ai-native-staging --timeout=60s || {
    echo -e "${RED}ERROR: Redis pod not ready${NC}"
    kubectl describe pod -l app=redis -n ai-native-staging
    exit 1
}
echo -e "${GREEN}✓ Redis ready${NC}"
echo ""

# Deploy Backend
echo "Step 8: Deploying Backend..."
kubectl apply -f 06-backend.yaml
echo -e "${YELLOW}⏳ Waiting for Backend to be ready (timeout: 180s)...${NC}"
kubectl wait --for=condition=ready pod -l app=ai-native-backend -n ai-native-staging --timeout=180s || {
    echo -e "${RED}ERROR: Backend pods not ready${NC}"
    kubectl describe pod -l app=ai-native-backend -n ai-native-staging
    exit 1
}
echo -e "${GREEN}✓ Backend ready${NC}"
echo ""

# Deploy Frontend
echo "Step 9: Deploying Frontend..."
kubectl apply -f 07-frontend.yaml
echo -e "${YELLOW}⏳ Waiting for Frontend to be ready (timeout: 120s)...${NC}"
kubectl wait --for=condition=ready pod -l app=ai-native-frontend -n ai-native-staging --timeout=120s || {
    echo -e "${RED}ERROR: Frontend pods not ready${NC}"
    kubectl describe pod -l app=ai-native-frontend -n ai-native-staging
    exit 1
}
echo -e "${GREEN}✓ Frontend ready${NC}"
echo ""

# Deploy Ingress
echo "Step 10: Deploying Ingress..."
kubectl apply -f 08-ingress.yaml
echo -e "${GREEN}✓ Ingress created${NC}"
echo ""

# Summary
echo "=========================================="
echo "Deployment Summary"
echo "=========================================="
kubectl get pods -n ai-native-staging
echo ""
echo "Services:"
kubectl get svc -n ai-native-staging
echo ""
echo "Ingress:"
kubectl get ingress -n ai-native-staging
echo ""

echo -e "${GREEN}=========================================="
echo "✅ Staging Deployment Complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Configure DNS to point to Ingress LoadBalancer IP"
echo "2. Wait for SSL/TLS certificate to be issued"
echo "3. Test health endpoint: https://api-staging.ai-native.tu-institucion.edu.ar/api/v1/health"
echo "4. Access frontend: https://app-staging.ai-native.tu-institucion.edu.ar"
echo ""
echo "Monitoring:"
echo "- View logs: kubectl logs -f -l app=ai-native-backend -n ai-native-staging"
echo "- Check metrics: kubectl top pods -n ai-native-staging"
echo "- Describe pod: kubectl describe pod <pod-name> -n ai-native-staging"
echo ""