#!/bin/bash

# AI-Native MVP - Monitoring Script
# Author: Mag. Alberto Cortez
# Date: 2025-11-24

NAMESPACE="ai-native-staging"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear

echo "=========================================="
echo "AI-Native MVP - Real-time Monitoring"
echo "=========================================="
echo ""

# Menu
echo "Select monitoring option:"
echo ""
echo "1) Watch all pods (live updates)"
echo "2) Watch backend logs (live)"
echo "3) Watch frontend logs (live)"
echo "4) Watch PostgreSQL logs (live)"
echo "5) Watch Redis logs (live)"
echo "6) Show resource usage (CPU/Memory)"
echo "7) Show recent events"
echo "8) Show ingress status"
echo "9) Test API endpoints"
echo "10) Show HPA status"
echo "11) Full dashboard (combined view)"
echo "12) Exit"
echo ""
read -p "Enter option (1-12): " OPTION

case $OPTION in
    1)
        echo ""
        echo "Watching all pods in namespace '$NAMESPACE'..."
        echo "Press Ctrl+C to stop"
        echo ""
        watch -n 2 "kubectl get pods -n $NAMESPACE"
        ;;

    2)
        echo ""
        echo "Backend logs (live)..."
        echo "Press Ctrl+C to stop"
        echo ""
        kubectl logs -f -l app=ai-native-backend -n $NAMESPACE --tail=100 --prefix
        ;;

    3)
        echo ""
        echo "Frontend logs (live)..."
        echo "Press Ctrl+C to stop"
        echo ""
        kubectl logs -f -l app=ai-native-frontend -n $NAMESPACE --tail=100 --prefix
        ;;

    4)
        echo ""
        echo "PostgreSQL logs (live)..."
        echo "Press Ctrl+C to stop"
        echo ""
        kubectl logs -f postgresql-0 -n $NAMESPACE --tail=100
        ;;

    5)
        echo ""
        echo "Redis logs (live)..."
        echo "Press Ctrl+C to stop"
        echo ""
        kubectl logs -f -l app=redis -n $NAMESPACE --tail=100
        ;;

    6)
        echo ""
        echo "Resource Usage:"
        echo "================================================"
        echo ""

        if kubectl top pods -n $NAMESPACE >/dev/null 2>&1; then
            echo "Pod Resource Usage:"
            kubectl top pods -n $NAMESPACE
            echo ""

            echo "Node Resource Usage:"
            kubectl top nodes
            echo ""

            echo "Backend HPA Status:"
            kubectl get hpa ai-native-backend-hpa -n $NAMESPACE 2>/dev/null || echo "HPA not found"
        else
            echo -e "${YELLOW}⚠ metrics-server not installed${NC}"
            echo ""
            echo "To install metrics-server:"
            echo "  kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml"
        fi

        echo ""
        read -p "Press Enter to continue..."
        ;;

    7)
        echo ""
        echo "Recent Events (last 20):"
        echo "================================================"
        kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -20
        echo ""
        read -p "Press Enter to continue..."
        ;;

    8)
        echo ""
        echo "Ingress Status:"
        echo "================================================"
        kubectl get ingress -n $NAMESPACE
        echo ""

        echo "LoadBalancer IP:"
        INGRESS_IP=$(kubectl get ingress ai-native-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
        if [ -n "$INGRESS_IP" ]; then
            echo -e "${GREEN}✓ $INGRESS_IP${NC}"
        else
            echo -e "${YELLOW}⚠ Not assigned yet${NC}"
        fi
        echo ""

        echo "TLS Certificate Status:"
        CERT_READY=$(kubectl get certificate ai-native-staging-tls -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)
        if [ "$CERT_READY" = "True" ]; then
            echo -e "${GREEN}✓ Certificate ready${NC}"
        else
            echo -e "${YELLOW}⚠ Certificate not ready${NC}"
            kubectl describe certificate ai-native-staging-tls -n $NAMESPACE 2>/dev/null | grep -A 5 "Events:"
        fi
        echo ""

        read -p "Press Enter to continue..."
        ;;

    9)
        echo ""
        echo "Testing API Endpoints:"
        echo "================================================"

        INGRESS_IP=$(kubectl get ingress ai-native-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)

        if [ -z "$INGRESS_IP" ]; then
            echo -e "${RED}✗ No LoadBalancer IP assigned yet${NC}"
        else
            echo "Testing with IP: $INGRESS_IP"
            echo ""

            echo -n "Health endpoint: "
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$INGRESS_IP/api/v1/health 2>/dev/null)
            if [ "$HTTP_CODE" = "200" ]; then
                echo -e "${GREEN}✓ HTTP $HTTP_CODE${NC}"
            else
                echo -e "${RED}✗ HTTP $HTTP_CODE${NC}"
            fi

            echo -n "Ping endpoint: "
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$INGRESS_IP/api/v1/health/ping 2>/dev/null)
            if [ "$HTTP_CODE" = "200" ]; then
                echo -e "${GREEN}✓ HTTP $HTTP_CODE${NC}"
            else
                echo -e "${RED}✗ HTTP $HTTP_CODE${NC}"
            fi

            echo ""
            echo "Full health response:"
            curl -s http://$INGRESS_IP/api/v1/health | jq '.' 2>/dev/null || curl -s http://$INGRESS_IP/api/v1/health
        fi

        echo ""
        read -p "Press Enter to continue..."
        ;;

    10)
        echo ""
        echo "HPA (Horizontal Pod Autoscaler) Status:"
        echo "================================================"
        kubectl get hpa -n $NAMESPACE
        echo ""

        echo "Backend HPA Details:"
        kubectl describe hpa ai-native-backend-hpa -n $NAMESPACE 2>/dev/null || echo -e "${YELLOW}⚠ HPA not found${NC}"
        echo ""

        read -p "Press Enter to continue..."
        ;;

    11)
        # Full dashboard view
        while true; do
            clear
            echo "=========================================="
            echo "AI-Native MVP - Live Dashboard"
            echo "Updated: $(date '+%Y-%m-%d %H:%M:%S')"
            echo "=========================================="
            echo ""

            echo "📦 POD STATUS:"
            echo "--------------------------------------"
            kubectl get pods -n $NAMESPACE -o wide | grep -E "NAME|ai-native|postgresql|redis"
            echo ""

            echo "📊 RESOURCE USAGE:"
            echo "--------------------------------------"
            kubectl top pods -n $NAMESPACE 2>/dev/null || echo "metrics-server not available"
            echo ""

            echo "🔄 HPA STATUS:"
            echo "--------------------------------------"
            kubectl get hpa -n $NAMESPACE 2>/dev/null || echo "HPA not configured"
            echo ""

            echo "🌐 INGRESS STATUS:"
            echo "--------------------------------------"
            kubectl get ingress -n $NAMESPACE
            echo ""

            echo "⚡ RECENT EVENTS:"
            echo "--------------------------------------"
            kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -5
            echo ""

            echo "Press Ctrl+C to exit dashboard"
            sleep 5
        done
        ;;

    12)
        echo "Exiting..."
        exit 0
        ;;

    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac