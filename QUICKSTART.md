# Quick Start Guide

## 🚀 Quick Start (Local Development with Docker Compose)

### Prerequisites
- Docker & Docker Compose
- Python 3.9+

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/end-to-end_CI_CD.git
cd end-to-end_CI_CD
```

### 2. Setup Environment
```bash
cp .env.example .env
# Edit .env and update credentials (optional for local dev)
```

### 3. Start Services
```bash
docker-compose up -d

# Wait for all services to be healthy
docker-compose ps
```

### 4. Access Applications
- **Streamlit UI**: http://localhost:8501
- **FastAPI API**: http://localhost:8000
- **FastAPI Docs**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/grafana)

### 5. Test Prediction API
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"feature_1": 5.0, "feature_2": 3.5, "feature_3": 7.2}'
```

### 6. View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f fastapi
docker-compose logs -f streamlit
```

### 7. Stop Services
```bash
docker-compose down

# With volume cleanup
docker-compose down -v
```

---

## 🐳 Quick Start (Kubernetes Local - minikube/Docker Desktop)

### Prerequisites
- Kubernetes cluster (minikube, Docker Desktop, or similar)
- kubectl configured
- Docker images built and pushed to registry

### 1. Create Namespace & Deploy
```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy all resources
kubectl apply -f k8s/

# Wait for deployments
kubectl wait --for=condition=ready pod -l app -n ml-project --timeout=600s
```

### 2. Port Forward Services
```bash
# In separate terminals:

# Streamlit
kubectl port-forward svc/streamlit-service -n ml-project 8501:8501

# FastAPI
kubectl port-forward svc/fastapi-service -n ml-project 8000:8000

# Grafana
kubectl port-forward svc/grafana-service -n ml-project 3000:3000

# Prometheus
kubectl port-forward svc/prometheus-service -n ml-project 9090:9090
```

### 3. Access Services
- Streamlit: http://localhost:8501
- FastAPI: http://localhost:8000
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

### 4. Check Status
```bash
# All pods
kubectl get pods -n ml-project

# All services
kubectl get svc -n ml-project

# All deployments
kubectl get deployments -n ml-project

# Storage
kubectl get pvc -n ml-project
```

### 5. Scale FastAPI
```bash
kubectl scale deployment/fastapi-deployment -n ml-project --replicas=3
```

### 6. View Logs
```bash
# FastAPI
kubectl logs -f deployment/fastapi-deployment -n ml-project -c fastapi

# Streamlit
kubectl logs -f deployment/streamlit-deployment -n ml-project -c streamlit
```

---

## 📋 Development Workflow

### 1. Make Code Changes
```bash
# Edit files locally
nano fastapi-app/app.py
```

### 2. Build & Test Locally
```bash
# Using Docker Compose (recommended)
docker-compose up -d --build

# Or build image manually
docker build -t fastapi-ml-service:dev ./fastapi-app
```

### 3. Test Changes
```bash
# Run integration tests
python -m pytest tests/

# Test API manually
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"feature_1": 5.0, "feature_2": 3.5, "feature_3": 7.2}'
```

### 4. Commit & Push
```bash
git add .
git commit -m "feat: update ML model"
git push origin main
```

### 5. GitHub Actions Triggers
- Images built and pushed to Docker Hub
- K8s manifests updated with new tags
- Argo CD automatically syncs

### 6. Monitor Deployment
```bash
# Watch Kubernetes rollout
kubectl rollout status deployment/fastapi-deployment -n ml-project

# Check pod status
kubectl get pods -n ml-project -w
```

---

## 🔍 Troubleshooting Quick Checks

### Services Not Starting
```bash
# Check Docker Compose
docker-compose logs fastapi
docker-compose ps

# Check Kubernetes
kubectl describe pod <pod-name> -n ml-project
kubectl logs <pod-name> -n ml-project
```

### Database Connection Issues
```bash
# Test Postgres locally (Docker Compose)
docker exec ml-postgres psql -U ml_user -d ml_db -c "SELECT 1;"

# Test from K8s pod
kubectl exec -it <fastapi-pod> -n ml-project -- \
  psql -h postgres-service -U ml_user -d ml_db -c "SELECT 1;"
```

### Redis Connection Issues
```bash
# Test Redis locally
docker exec ml-redis redis-cli ping

# Test from K8s pod
kubectl exec -it <fastapi-pod> -n ml-project -- \
  redis-cli -h redis-service ping
```

### Image Pull Errors
```bash
# Verify image exists locally
docker images | grep fastapi

# Push to registry
docker push dockerhub_username/fastapi-ml-service:latest

# Check Kubernetes ImagePullBackOff
kubectl describe pod <pod-name> -n ml-project
```

---

## 📚 Useful Commands Reference

### Docker Compose
```bash
docker-compose up -d              # Start services
docker-compose down               # Stop services
docker-compose logs -f            # View logs
docker-compose ps                 # List services
docker-compose exec <service> /bin/bash  # Enter container
```

### Kubernetes
```bash
kubectl apply -f k8s/              # Deploy all manifests
kubectl delete -f k8s/             # Delete all manifests
kubectl get pods -n ml-project     # List pods
kubectl describe pod <pod> -n ml-project  # Pod details
kubectl logs -f <pod> -n ml-project       # Pod logs
kubectl scale deployment/<name> --replicas=3  # Scale
kubectl port-forward svc/<service> <local>:<remote>  # Port forward
```

### Git
```bash
git status                         # Check changes
git add .                          # Stage changes
git commit -m "message"            # Commit
git push origin main               # Push to main
git pull                           # Pull latest
```

### Docker
```bash
docker build -t image:tag .        # Build image
docker run -d --name container image  # Run container
docker ps                          # List containers
docker logs -f container           # View logs
docker exec -it container /bin/bash   # Enter container
```

---

## 🎯 Common Tasks

### Update FastAPI Code
```bash
# Edit code
nano fastapi-app/app.py

# Test locally
docker-compose up -d --build fastapi

# Commit and push
git add fastapi-app/
git commit -m "update: ML model changes"
git push

# Automatic deployment via GitHub Actions + Argo CD
```

### Update FastAPI Replicas
```bash
# Option 1: Edit manifests (GitOps)
sed -i 's/replicas: 2/replicas: 3/g' k8s/fastapi-deployment.yaml
git commit -am "scale: increase replicas"
git push
# Argo CD auto-syncs

# Option 2: Direct kubectl
kubectl scale deployment/fastapi-deployment -n ml-project --replicas=3
```

### View Predictions in Database
```bash
# From Docker Compose
docker exec ml-postgres psql -U ml_user -d ml_db \
  -c "SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 10;"

# From Kubernetes
kubectl exec -it postgres-0 -n ml-project -- \
  psql -U ml_user -d ml_db -c "SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 10;"
```

### Check Redis Cache
```bash
# From Docker Compose
docker exec ml-redis redis-cli KEYS "*"
docker exec ml-redis redis-cli GET "prediction:..."

# From Kubernetes
kubectl exec -it redis-0 -n ml-project -- \
  redis-cli KEYS "*"
```

---

Need more help? See the main [README.md](README.md) for detailed documentation!
