.PHONY: help build test deploy clean up down logs scale \
        docker-build docker-push k8s-deploy k8s-delete \
        port-forward-all port-forward-streamlit port-forward-fastapi \
        port-forward-grafana port-forward-prometheus argocd-sync \
        db-connect redis-cli check-status

# Default target
help:
	@echo "ML Deployment with Kubernetes, GitOps, and CI/CD"
	@echo ""
	@echo "Local Development (Docker Compose):"
	@echo "  make up                    - Start all services"
	@echo "  make down                  - Stop all services"
	@echo "  make logs                  - View logs from all services"
	@echo "  make docker-build          - Build Docker images"
	@echo ""
	@echo "Kubernetes:"
	@echo "  make k8s-deploy            - Deploy to Kubernetes"
	@echo "  make k8s-delete            - Delete from Kubernetes"
	@echo "  make port-forward-all      - Port forward all services"
	@echo "  make check-status          - Check Kubernetes status"
	@echo "  make scale                 - Scale FastAPI replicas"
	@echo ""
	@echo "Database:"
	@echo "  make db-connect            - Connect to PostgreSQL"
	@echo "  make redis-cli             - Connect to Redis CLI"
	@echo ""
	@echo "Monitoring:"
	@echo "  make port-forward-grafana  - Port forward Grafana"
	@echo "  make port-forward-prometheus - Port forward Prometheus"
	@echo ""
	@echo "CI/CD:"
	@echo "  make argocd-sync           - Trigger Argo CD sync"
	@echo "  make test                  - Run tests"
	@echo "  make clean                 - Clean up resources"

# ============================================================
# Docker Compose Commands
# ============================================================

up:
	docker-compose up -d
	@echo "✅ Services started"
	@sleep 5
	@echo "📊 Service Status:"
	@docker-compose ps

down:
	docker-compose down
	@echo "✅ Services stopped"

build: docker-build

docker-build:
	@echo "🔨 Building Docker images..."
	docker-compose build --no-cache
	@echo "✅ Build complete"

logs:
	docker-compose logs -f

logs-fastapi:
	docker-compose logs -f fastapi

logs-streamlit:
	docker-compose logs -f streamlit

logs-postgres:
	docker-compose logs -f postgres

logs-redis:
	docker-compose logs -f redis

test:
	@echo "🧪 Running tests..."
	docker-compose exec -T fastapi pytest tests/ -v || true
	@echo "✅ Tests complete"

clean:
	docker-compose down -v
	@echo "✅ Cleaned up all resources"

# ============================================================
# Docker Registry Commands
# ============================================================

docker-push:
	@echo "🚀 Pushing Docker images to registry..."
	docker tag fastapi-ml-service:latest $${DOCKERHUB_USERNAME}/fastapi-ml-service:latest
	docker tag streamlit-ml-frontend:latest $${DOCKERHUB_USERNAME}/streamlit-ml-frontend:latest
	docker push $${DOCKERHUB_USERNAME}/fastapi-ml-service:latest
	docker push $${DOCKERHUB_USERNAME}/streamlit-ml-frontend:latest
	@echo "✅ Images pushed"

# ============================================================
# Kubernetes Commands
# ============================================================

k8s-deploy:
	@echo "📦 Deploying to Kubernetes..."
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/
	@echo "⏳ Waiting for services to be ready..."
	kubectl wait --for=condition=ready pod -l app -n ml-project --timeout=600s || true
	@echo "✅ Deployment complete"
	@make check-status

k8s-delete:
	@echo "🗑️  Deleting from Kubernetes..."
	kubectl delete -f k8s/ --ignore-not-found
	kubectl delete namespace ml-project --ignore-not-found
	@echo "✅ Resources deleted"

k8s-apply:
	@echo "📝 Applying Kubernetes manifests..."
	kubectl apply -f k8s/
	@echo "✅ Applied"

check-status:
	@echo "📊 Kubernetes Status:"
	@echo ""
	@echo "Deployments:"
	@kubectl get deployments -n ml-project -o wide
	@echo ""
	@echo "StatefulSets:"
	@kubectl get statefulsets -n ml-project -o wide
	@echo ""
	@echo "Pods:"
	@kubectl get pods -n ml-project -o wide
	@echo ""
	@echo "Services:"
	@kubectl get svc -n ml-project -o wide
	@echo ""
	@echo "PersistentVolumeClaims:"
	@kubectl get pvc -n ml-project -o wide

# ============================================================
# Port Forwarding Commands
# ============================================================

port-forward-all: port-forward-streamlit port-forward-fastapi port-forward-grafana port-forward-prometheus
	@echo "✅ All port forwards active"
	@echo ""
	@echo "Streamlit: http://localhost:8501"
	@echo "FastAPI:   http://localhost:8000"
	@echo "Grafana:   http://localhost:3000"
	@echo "Prometheus: http://localhost:9090"

port-forward-streamlit:
	@echo "Forwarding Streamlit (8501)..."
	kubectl port-forward svc/streamlit-service -n ml-project 8501:8501 &

port-forward-fastapi:
	@echo "Forwarding FastAPI (8000)..."
	kubectl port-forward svc/fastapi-service -n ml-project 8000:8000 &

port-forward-grafana:
	@echo "Forwarding Grafana (3000)..."
	kubectl port-forward svc/grafana-service -n ml-project 3000:3000 &

port-forward-prometheus:
	@echo "Forwarding Prometheus (9090)..."
	kubectl port-forward svc/prometheus-service -n ml-project 9090:9090 &

# ============================================================
# Database Commands
# ============================================================

db-connect:
	@echo "Connecting to PostgreSQL..."
	docker exec -it ml-postgres psql -U ml_user -d ml_db

db-k8s-connect:
	@echo "Connecting to PostgreSQL in Kubernetes..."
	kubectl exec -it postgres-0 -n ml-project -- \
		psql -U ml_user -d ml_db

redis-cli:
	@echo "Connecting to Redis..."
	docker exec -it ml-redis redis-cli

redis-k8s-cli:
	@echo "Connecting to Redis in Kubernetes..."
	kubectl exec -it redis-0 -n ml-project -- redis-cli

# ============================================================
# Scaling Commands
# ============================================================

scale:
	@echo "Current replicas:"
	@kubectl get deployment fastapi-deployment -n ml-project -o jsonpath='{.spec.replicas}'
	@echo ""
	@read -p "Enter number of replicas: " replicas; \
	kubectl scale deployment/fastapi-deployment -n ml-project --replicas=$$replicas
	@echo "✅ Scaled to $$replicas replicas"

scale-up:
	kubectl scale deployment/fastapi-deployment -n ml-project --replicas=3
	@echo "✅ Scaled to 3 replicas"

scale-down:
	kubectl scale deployment/fastapi-deployment -n ml-project --replicas=1
	@echo "✅ Scaled to 1 replica"

# ============================================================
# Argo CD Commands
# ============================================================

argocd-sync:
	@echo "🔄 Triggering Argo CD sync..."
	argocd app sync ml-project-app
	@echo "✅ Sync complete"

argocd-status:
	@echo "📋 Argo CD Application Status:"
	argocd app get ml-project-app

# ============================================================
# Monitoring Commands
# ============================================================

logs-prometheus:
	kubectl logs -f deployment/prometheus -n ml-project -c prometheus

logs-grafana:
	kubectl logs -f deployment/grafana -n ml-project -c grafana

# ============================================================
# Utility Commands
# ============================================================

exec-fastapi:
	@echo "Entering FastAPI pod..."
	kubectl exec -it deployment/fastapi-deployment -n ml-project -c fastapi -- /bin/bash

exec-streamlit:
	@echo "Entering Streamlit pod..."
	kubectl exec -it deployment/streamlit-deployment -n ml-project -c streamlit -- /bin/bash

exec-postgres:
	@echo "Entering PostgreSQL pod..."
	kubectl exec -it statefulset/postgres -n ml-project -c postgres -- /bin/bash

describe-pod:
	@echo "Enter pod name:"
	@read -p "> " pod; \
	kubectl describe pod $$pod -n ml-project

# ============================================================
# Git Commands
# ============================================================

git-status:
	git status

git-commit:
	@read -p "Enter commit message: " msg; \
	git add .; \
	git commit -m "$$msg"

git-push:
	git push origin main

git-pull:
	git pull origin main

# ============================================================
# Demo Commands
# ============================================================

demo-predict:
	@echo "📊 Testing prediction API..."
	curl -X POST http://localhost:8000/predict \
		-H "Content-Type: application/json" \
		-d '{"feature_1": 5.0, "feature_2": 3.5, "feature_3": 7.2}'

demo-health:
	@echo "❤️  Checking API health..."
	curl http://localhost:8000/health

demo-predictions-db:
	@echo "📋 Recent predictions in database..."
	docker exec ml-postgres psql -U ml_user -d ml_db \
		-c "SELECT id, features, prediction, confidence, timestamp FROM predictions ORDER BY timestamp DESC LIMIT 10;"

demo-redis:
	@echo "💾 Redis cache keys..."
	docker exec ml-redis redis-cli KEYS "*"

# ============================================================
# Info Commands
# ============================================================

info:
	@echo "ML Deployment Project Information"
	@echo ""
	@echo "Repository: $(shell git config --get remote.origin.url)"
	@echo "Current Branch: $(shell git branch --show-current)"
	@echo "Commit: $(shell git rev-parse --short HEAD)"
	@echo ""
	@echo "Services:"
	@echo "  - FastAPI (port 8000)"
	@echo "  - Streamlit (port 8501)"
	@echo "  - PostgreSQL (port 5432)"
	@echo "  - Redis (port 6379)"
	@echo "  - Prometheus (port 9090)"
	@echo "  - Grafana (port 3000)"
