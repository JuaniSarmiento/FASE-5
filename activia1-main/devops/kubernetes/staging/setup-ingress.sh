#!/bin/bash

# Setup Nginx Ingress Controller and Cert-Manager
# Author: Mag. Alberto Cortez
# Date: 2025-11-24

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "Ingress Controller Setup"
echo "=========================================="
echo ""

# Check prerequisites
command -v helm >/dev/null 2>&1 || { echo -e "${RED}ERROR: helm is not installed${NC}"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}ERROR: kubectl is not installed${NC}"; exit 1; }

# Add Helm repos
echo "Step 1: Adding Helm repositories..."
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add jetstack https://charts.jetstack.io
helm repo update
echo -e "${GREEN}✓ Helm repos added${NC}"
echo ""

# Install Nginx Ingress Controller
echo "Step 2: Installing Nginx Ingress Controller..."
if helm list -n ingress-nginx | grep -q ingress-nginx; then
    echo -e "${YELLOW}⚠ Nginx Ingress already installed${NC}"
else
    helm install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.replicaCount=2 \
        --set controller.service.type=LoadBalancer \
        --set controller.metrics.enabled=true \
        --set controller.podAnnotations."prometheus\.io/scrape"=true \
        --set controller.podAnnotations."prometheus\.io/port"=10254

    echo -e "${YELLOW}⏳ Waiting for Nginx Ingress to be ready...${NC}"
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=120s

    echo -e "${GREEN}✓ Nginx Ingress installed${NC}"
fi
echo ""

# Get LoadBalancer IP
echo "Step 3: Getting LoadBalancer IP..."
EXTERNAL_IP=""
while [ -z "$EXTERNAL_IP" ]; do
    echo "Waiting for external IP..."
    EXTERNAL_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    [ -z "$EXTERNAL_IP" ] && sleep 5
done
echo -e "${GREEN}✓ LoadBalancer IP: $EXTERNAL_IP${NC}"
echo ""

# Install Cert-Manager
echo "Step 4: Installing Cert-Manager..."
if kubectl get namespace cert-manager >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Cert-Manager namespace already exists${NC}"
else
    helm install cert-manager jetstack/cert-manager \
        --namespace cert-manager \
        --create-namespace \
        --version v1.13.0 \
        --set installCRDs=true \
        --set prometheus.enabled=true

    echo -e "${YELLOW}⏳ Waiting for Cert-Manager to be ready...${NC}"
    kubectl wait --namespace cert-manager \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/instance=cert-manager \
        --timeout=120s

    echo -e "${GREEN}✓ Cert-Manager installed${NC}"
fi
echo ""

# Create ClusterIssuer
echo "Step 5: Creating ClusterIssuers..."

# Staging ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: admin@tu-institucion.edu.ar
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Production ClusterIssuer (for future use)
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@tu-institucion.edu.ar
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

echo -e "${GREEN}✓ ClusterIssuers created${NC}"
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "LoadBalancer IP: $EXTERNAL_IP"
echo ""
echo "Next steps:"
echo "1. Configure DNS records:"
echo "   api-staging.ai-native.tu-institucion.edu.ar → $EXTERNAL_IP"
echo "   app-staging.ai-native.tu-institucion.edu.ar → $EXTERNAL_IP"
echo ""
echo "2. Wait for DNS propagation (can take 5-60 minutes)"
echo ""
echo "3. Verify DNS:"
echo "   nslookup api-staging.ai-native.tu-institucion.edu.ar"
echo ""
echo "4. Deploy application:"
echo "   ./deploy.sh"
echo ""