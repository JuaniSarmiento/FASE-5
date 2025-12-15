#!/bin/bash

# AI-Native MVP - Rollback Script
# Author: Mag. Alberto Cortez
# Date: 2025-11-24

set -e

echo "=========================================="
echo "AI-Native MVP - Rollback Tool"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

NAMESPACE="ai-native-staging"

# Menu
echo "Select rollback option:"
echo ""
echo "1) Rollback backend deployment (to previous version)"
echo "2) Rollback frontend deployment (to previous version)"
echo "3) Delete all resources (DANGER: full cleanup)"
echo "4) Rollback to specific backend revision"
echo "5) Rollback to specific frontend revision"
echo "6) Show deployment history"
echo "7) Exit"
echo ""
read -p "Enter option (1-7): " OPTION

case $OPTION in
    1)
        echo ""
        echo "Rolling back backend deployment to previous version..."
        kubectl rollout undo deployment/ai-native-backend -n $NAMESPACE

        echo -e "${YELLOW}⏳ Waiting for rollback to complete...${NC}"
        kubectl rollout status deployment/ai-native-backend -n $NAMESPACE

        echo -e "${GREEN}✓ Backend rollback complete${NC}"
        echo ""
        echo "Verify with:"
        echo "  kubectl get pods -n $NAMESPACE -l app=ai-native-backend"
        echo "  kubectl logs -f -l app=ai-native-backend -n $NAMESPACE"
        ;;

    2)
        echo ""
        echo "Rolling back frontend deployment to previous version..."
        kubectl rollout undo deployment/ai-native-frontend -n $NAMESPACE

        echo -e "${YELLOW}⏳ Waiting for rollback to complete...${NC}"
        kubectl rollout status deployment/ai-native-frontend -n $NAMESPACE

        echo -e "${GREEN}✓ Frontend rollback complete${NC}"
        echo ""
        echo "Verify with:"
        echo "  kubectl get pods -n $NAMESPACE -l app=ai-native-frontend"
        ;;

    3)
        echo ""
        echo -e "${RED}WARNING: This will DELETE ALL RESOURCES in namespace '$NAMESPACE'${NC}"
        echo "This includes:"
        echo "  - All pods (backend, frontend, PostgreSQL, Redis)"
        echo "  - All data in PostgreSQL (PERMANENT DATA LOSS)"
        echo "  - All ConfigMaps and Secrets"
        echo "  - Ingress configuration"
        echo ""
        read -p "Are you ABSOLUTELY SURE? Type 'DELETE' to confirm: " CONFIRM

        if [ "$CONFIRM" = "DELETE" ]; then
            echo ""
            echo "Deleting all resources..."

            # Delete in reverse order to respect dependencies
            kubectl delete -f 08-ingress.yaml --ignore-not-found=true
            kubectl delete -f 07-frontend.yaml --ignore-not-found=true
            kubectl delete -f 06-backend.yaml --ignore-not-found=true
            kubectl delete -f 05-redis.yaml --ignore-not-found=true
            kubectl delete -f 04-postgresql.yaml --ignore-not-found=true
            kubectl delete -f 02-configmap.yaml --ignore-not-found=true
            kubectl delete secret ai-native-secrets -n $NAMESPACE --ignore-not-found=true

            # Delete PVCs (persistent volume claims)
            kubectl delete pvc -n $NAMESPACE --all

            echo ""
            read -p "Do you want to delete the namespace too? (y/N): " DELETE_NS
            if [[ $DELETE_NS =~ ^[Yy]$ ]]; then
                kubectl delete -f 01-namespace.yaml --ignore-not-found=true
                echo -e "${GREEN}✓ Namespace deleted${NC}"
            else
                echo -e "${YELLOW}⚠ Namespace kept (empty)${NC}"
            fi

            echo ""
            echo -e "${GREEN}✓ All resources deleted${NC}"
            echo ""
            echo "To redeploy:"
            echo "  ./deploy.sh"
        else
            echo ""
            echo "Deletion cancelled."
        fi
        ;;

    4)
        echo ""
        echo "Backend deployment history:"
        kubectl rollout history deployment/ai-native-backend -n $NAMESPACE
        echo ""
        read -p "Enter revision number to rollback to: " REVISION

        if [ -n "$REVISION" ]; then
            echo ""
            echo "Rolling back to revision $REVISION..."
            kubectl rollout undo deployment/ai-native-backend -n $NAMESPACE --to-revision=$REVISION

            echo -e "${YELLOW}⏳ Waiting for rollback to complete...${NC}"
            kubectl rollout status deployment/ai-native-backend -n $NAMESPACE

            echo -e "${GREEN}✓ Backend rollback to revision $REVISION complete${NC}"
        else
            echo "Invalid revision number."
        fi
        ;;

    5)
        echo ""
        echo "Frontend deployment history:"
        kubectl rollout history deployment/ai-native-frontend -n $NAMESPACE
        echo ""
        read -p "Enter revision number to rollback to: " REVISION

        if [ -n "$REVISION" ]; then
            echo ""
            echo "Rolling back to revision $REVISION..."
            kubectl rollout undo deployment/ai-native-frontend -n $NAMESPACE --to-revision=$REVISION

            echo -e "${YELLOW}⏳ Waiting for rollback to complete...${NC}"
            kubectl rollout status deployment/ai-native-frontend -n $NAMESPACE

            echo -e "${GREEN}✓ Frontend rollback to revision $REVISION complete${NC}"
        else
            echo "Invalid revision number."
        fi
        ;;

    6)
        echo ""
        echo "Backend deployment history:"
        kubectl rollout history deployment/ai-native-backend -n $NAMESPACE
        echo ""
        echo "Frontend deployment history:"
        kubectl rollout history deployment/ai-native-frontend -n $NAMESPACE
        echo ""
        echo "To see details of a specific revision:"
        echo "  kubectl rollout history deployment/ai-native-backend -n $NAMESPACE --revision=N"
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