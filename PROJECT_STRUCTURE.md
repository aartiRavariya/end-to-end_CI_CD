# 📦 Project Structure & File Reference

## Complete Directory Tree

```
end-to-end_CI_CD/
│
├── 📂 fastapi-app/
│   ├── app.py                    # FastAPI application with ML model & endpoints
│   ├── requirements.txt          # Python dependencies for FastAPI
│   ├── Dockerfile                # Multi-stage Docker build for FastAPI
│   └── .dockerignore             # Files to exclude from Docker build
│
├── 📂 streamlit-app/
│   ├── app.py                    # Streamlit interactive frontend UI
│   ├── requirements.txt          # Python dependencies for Streamlit
│   ├── Dockerfile                # Docker build for Streamlit
│   └── .dockerignore             # Files to exclude from Docker build
│
├── 📂 k8s/                       # Kubernetes manifests
│   ├── namespace.yaml            # ml-project namespace creation
│   ├── configmap.yaml            # Application configuration (non-sensitive)
│   ├── secrets.yaml              # Sensitive credentials (⚠️ UPDATE PASSWORDS!)
│   ├── rbac.yaml                 # Role-based access control for services
│   │
│   ├── fastapi-deployment.yaml   # FastAPI Deployment (2 replicas, rolling update)
│   ├── fastapi-service.yaml      # FastAPI Service for internal DNS/load balancing
│   │
│   ├── streamlit-deployment.yaml # Streamlit Deployment (1 replica)
│   ├── streamlit-service.yaml    # Streamlit Service for internal DNS
│   │
│   ├── postgres-statefulset.yaml # PostgreSQL StatefulSet with PVC
│   ├── postgres-service.yaml     # Postgres headless Service
│   │
│   ├── redis-statefulset.yaml    # Redis StatefulSet with PVC
│   ├── redis-service.yaml        # Redis headless Service
│   │
│   ├── ingress.yaml              # Nginx Ingress for external access
│   └── kustomization.yaml        # Kustomize base configuration (optional)
│
├── 📂 monitoring/                # Observability stack
│   ├── prometheus-config.yaml    # Prometheus scrape configuration
│   ├── prometheus-deployment.yaml# Prometheus Deployment with PVC
│   ├── prometheus-service.yaml   # Prometheus Service
│   ├── prometheus-rbac.yaml      # Prometheus RBAC permissions
│   ├── prometheus.yml            # Prometheus config for Docker Compose
│   │
│   ├── grafana-config.yaml       # Grafana datasources & dashboards
│   ├── grafana-deployment.yaml   # Grafana Deployment with PVC
│   ├── grafana-service.yaml      # Grafana Service
│
├── 📂 .github/workflows/
│   └── ci-cd.yml                 # GitHub Actions CI/CD workflow
│                                  # - Builds Docker images
│                                  # - Pushes to Docker Hub
│                                  # - Updates K8s manifests
│                                  # - Commits changes
│
├── 📂 argo/
│   └── argocd-application.yaml   # Argo CD Application for GitOps
│                                  # - Watches GitHub repo
│                                  # - Auto-syncs cluster
│
├── docker-compose.yml            # Docker Compose for local development
│                                  # All services with networking & volumes
│
├── README.md                     # Comprehensive project documentation
│                                  # - Architecture diagrams
│                                  # - Setup instructions
│                                  # - Deployment flows
│                                  # - Demo scenarios
│                                  # - Troubleshooting
│
├── QUICKSTART.md                 # Quick start guide
│                                  # - Fast setup steps
│                                  # - Docker Compose quick start
│                                  # - K8s local quick start
│                                  # - Common tasks
│
├── Makefile                      # Convenient command shortcuts
│                                  # - Docker commands
│                                  # - K8s commands
│                                  # - Port forwarding
│                                  # - Database access
│
├── .env.example                  # Environment variables template
│                                  # - Copy to .env and fill values
│
└── .gitignore                    # Git ignore patterns
                                   # - Python, Docker, K8s files
```

## 📄 Key Files Overview

### Application Files

| File | Purpose |
|------|---------|
| `fastapi-app/app.py` | FastAPI ML prediction service with /predict endpoint |
| `streamlit-app/app.py` | Interactive web UI for making predictions |

### Container Files

| File | Purpose |
|------|---------|
| `fastapi-app/Dockerfile` | Multi-stage build for FastAPI |
| `streamlit-app/Dockerfile` | Docker build for Streamlit |
| `docker-compose.yml` | Local development with all services |

### Kubernetes Core

| File | Purpose |
|------|---------|
| `k8s/namespace.yaml` | ml-project namespace |
| `k8s/configmap.yaml` | Application configuration |
| `k8s/secrets.yaml` | Database credentials |
| `k8s/rbac.yaml` | Service account & permissions |

### Kubernetes Deployments

| Service | Files |
|---------|-------|
| **FastAPI** | `fastapi-deployment.yaml`, `fastapi-service.yaml` |
| **Streamlit** | `streamlit-deployment.yaml`, `streamlit-service.yaml` |
| **PostgreSQL** | `postgres-statefulset.yaml`, `postgres-service.yaml` |
| **Redis** | `redis-statefulset.yaml`, `redis-service.yaml` |
| **Ingress** | `ingress.yaml` |

### Monitoring Stack

| Component | Files |
|-----------|-------|
| **Prometheus** | `prometheus-config.yaml`, `prometheus-deployment.yaml`, `prometheus-rbac.yaml` |
| **Grafana** | `grafana-config.yaml`, `grafana-deployment.yaml` |

### CI/CD & GitOps

| File | Purpose |
|------|---------|
| `.github/workflows/ci-cd.yml` | GitHub Actions pipeline (build, push, update manifests) |
| `argo/argocd-application.yaml` | Argo CD GitOps configuration |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Complete project documentation |
| `QUICKSTART.md` | Quick start guide for fast setup |
| `Makefile` | Command shortcuts for common operations |
| `.env.example` | Environment variables template |

## 🔄 Data Flow

```
Code Changes
    ↓
Git Push (main branch)
    ↓
GitHub Actions Workflow (.github/workflows/ci-cd.yml)
    ├─ Build Docker images (fastapi-app, streamlit-app)
    ├─ Scan for vulnerabilities (Trivy)
    ├─ Push to Docker Hub
    └─ Update k8s manifests with new image tags
    ↓
Commit changes back to GitHub
    ↓
Argo CD (argo/argocd-application.yaml) detects changes
    ├─ Pulls latest from GitHub
    ├─ Compares with current cluster state
    ├─ Applies new manifests
    └─ Auto-syncs and heals divergence
    ↓
Kubernetes Deployment
    ├─ Rolling update of pods
    ├─ Health checks & readiness probes
    └─ Service load balancing
    ↓
Application Running
    ├─ FastAPI serves /predict endpoint
    ├─ PostgreSQL logs predictions
    ├─ Redis caches recent predictions
    ├─ Streamlit UI displays results
    ├─ Prometheus scrapes metrics
    └─ Grafana visualizes dashboards
```

## 🗂️ Environment Variables

See `.env.example` for complete list:

### Docker Hub
- `DOCKERHUB_USERNAME` - Your Docker Hub username
- `DOCKERHUB_TOKEN` - Docker Hub access token

### Database
- `DB_HOST` - PostgreSQL host
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_NAME` - Database name

### Redis
- `REDIS_HOST` - Redis host
- `REDIS_PORT` - Redis port

### Services
- `FASTAPI_URL` - FastAPI base URL
- `USE_REDIS` - Enable Redis caching

### Monitoring
- `GF_SECURITY_ADMIN_PASSWORD` - Grafana admin password

## 📊 Configuration Hierarchy

```
1. Git Repository (.env, secrets)
   ↓
2. GitHub Actions Secrets
   ├─ DOCKERHUB_USERNAME
   ├─ DOCKERHUB_TOKEN
   └─ ARGOCD_PASSWORD
   ↓
3. Kubernetes ConfigMaps (k8s/configmap.yaml)
   ├─ Application settings (non-sensitive)
   ├─ Database endpoints
   └─ Redis configuration
   ↓
4. Kubernetes Secrets (k8s/secrets.yaml)
   ├─ Database credentials
   ├─ Passwords
   └─ API tokens
   ↓
5. Pod Environment Variables
   ├─ From ConfigMaps
   └─ From Secrets
```

## 🚀 Deployment Checklist

Before deploying, verify:

- [ ] Updated Docker Hub credentials in `k8s/fastapi-deployment.yaml` and `k8s/streamlit-deployment.yaml`
- [ ] Updated database passwords in `k8s/secrets.yaml`
- [ ] GitHub repository secrets configured (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN)
- [ ] Kubernetes cluster accessible (`kubectl get nodes`)
- [ ] Storage class available (`kubectl get storageclass`)
- [ ] Ingress controller installed
- [ ] Argo CD installed in argocd namespace
- [ ] GitHub repository URL updated in `argo/argocd-application.yaml`

## 📋 Quick Command Reference

```bash
# Docker Compose
docker-compose up -d                    # Start all services
docker-compose down                     # Stop all services
docker-compose logs -f                  # View logs

# Kubernetes
kubectl apply -f k8s/                   # Deploy
kubectl delete -f k8s/                  # Delete
kubectl scale deployment/fastapi-deployment -n ml-project --replicas=3

# Monitoring
kubectl port-forward svc/grafana-service -n ml-project 3000:3000
kubectl port-forward svc/prometheus-service -n ml-project 9090:9090

# Using Makefile
make up                                 # Start Docker Compose
make k8s-deploy                        # Deploy to Kubernetes
make port-forward-all                  # Forward all services
make db-connect                        # Connect to PostgreSQL
```

## 🔗 Service URLs

### Local Development (Docker Compose)
- **Streamlit**: http://localhost:8501
- **FastAPI**: http://localhost:8000
- **FastAPI Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000

### Kubernetes (after port forwarding)
- **Streamlit**: http://localhost:8501
- **FastAPI**: http://localhost:8000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000

### Default Credentials
- **Grafana**: admin / grafana_password_change_me
- **PostgreSQL**: ml_user / ml_password_change_me
- **Argo CD**: admin / (check with: `kubectl -n argocd get secret argocd-initial-admin-secret`)

---

**Next Steps:**
1. Read [README.md](README.md) for detailed setup instructions
2. Check [QUICKSTART.md](QUICKSTART.md) for fast start
3. Use [Makefile](Makefile) for convenient commands
