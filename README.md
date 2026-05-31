# ML Deployment with Kubernetes, GitOps, and CI/CD

A complete end-to-end solution for deploying machine learning services using Kubernetes, GitOps (Argo CD), and automated CI/CD pipelines.

## 📋 Table of Contents

- [Project Architecture](#project-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Deployment Flow](#deployment-flow)
- [Demo & Usage](#demo--usage)
- [Monitoring & Observability](#monitoring--observability)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🏗️ Project Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GitHub Repository                           │
│                  (Code → Docker → Kubernetes)                      │
└──────────┬──────────────────────────────────────────────────────────┘
           │
           ├─► FastAPI App (ML Model Server)
           ├─► Streamlit App (Frontend)
           └─► K8s Manifests (GitOps)
           
           │ GitHub Actions Workflow
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Docker Registry (Docker Hub)                   │
│                                                                     │
│  ┌──────────────────┐        ┌──────────────────────┐              │
│  │ FastAPI Image    │        │ Streamlit Image      │              │
│  │ with ML Model    │        │ with UI              │              │
│  └──────────────────┘        └──────────────────────┘              │
└──────────┬──────────────────────────────────────────────────────────┘
           │
           │ Argo CD watches GitHub
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Kubernetes Cluster (ml-project namespace)              │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ FastAPI Pods (2 replicas)    ← Service Load Balancer       │   │
│  │ • ML Model                                                  │   │
│  │ • Health checks & Auto-healing                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                            ▲                                        │
│                            │ Caching                               │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────────┐        │
│  │ Redis Cache    │  │ PostgreSQL   │  │ Streamlit App   │        │
│  │ (StatefulSet)  │  │ (StatefulSet)│  │ (1 replica)     │        │
│  └────────────────┘  └──────────────┘  └──────────────────┘        │
│                                              ▼                      │
│  ┌──────────────────────────────────────────────────┐              │
│  │           Ingress (Nginx)                        │              │
│  │  streamlit.ml-project.local → Streamlit UI       │              │
│  │  api.ml-project.local → FastAPI Endpoints       │              │
│  └──────────────────────────────────────────────────┘              │
│                                                                     │
│  ┌──────────────────┐      ┌──────────────────────┐                │
│  │ Prometheus       │      │ Grafana              │                │
│  │ (Metrics)        │──────│ (Dashboards)         │                │
│  └──────────────────┘      └──────────────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
           │
           │ GitOps: Declarative sync
           │ Auto-healing & Self-service scaling
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Rancher Dashboard (Kubernetes Mgmt UI)                 │
│                  • Monitor cluster health                           │
│                  • Manage workloads                                 │
│                  • View logs & metrics                              │
└─────────────────────────────────────────────────────────────────────┘
```

## 🛠️ Technology Stack

### Backend & ML
- **FastAPI**: Modern Python web framework for building APIs
- **scikit-learn**: Machine learning model library
- **PostgreSQL**: Persistent data storage for predictions
- **Redis**: In-memory caching for recent predictions

### Frontend
- **Streamlit**: Interactive web application framework
- **Requests**: HTTP client for API communication

### Containerization & Orchestration
- **Docker**: Container runtime for packaging applications
- **Kubernetes**: Container orchestration platform
- **Argo CD**: GitOps continuous deployment tool
- **Helm** (optional): Kubernetes package manager

### CI/CD
- **GitHub Actions**: Workflow automation
- **Docker Hub**: Docker image registry
- **Trivy**: Container image vulnerability scanner

### Monitoring & Observability
- **Prometheus**: Metrics collection and storage
- **Grafana**: Metrics visualization and dashboards

### Management
- **Rancher**: Kubernetes management platform

## 📁 Project Structure

```
end-to-end_CI_CD/
│
├── fastapi-app/                    # ML Prediction Service
│   ├── app.py                      # FastAPI application with ML model
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Multi-stage Docker build
│   └── .dockerignore               # Docker build context exclusions
│
├── streamlit-app/                  # Frontend UI
│   ├── app.py                      # Streamlit interactive app
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Docker build
│   └── .dockerignore               # Docker build context exclusions
│
├── k8s/                            # Kubernetes Manifests
│   ├── namespace.yaml              # ml-project namespace
│   ├── configmap.yaml              # Application configuration
│   ├── secrets.yaml                # Database credentials (CHANGE THESE!)
│   ├── fastapi-deployment.yaml     # FastAPI service (2 replicas)
│   ├── fastapi-service.yaml        # FastAPI service discovery
│   ├── streamlit-deployment.yaml   # Streamlit frontend (1 replica)
│   ├── streamlit-service.yaml      # Streamlit service discovery
│   ├── postgres-statefulset.yaml   # PostgreSQL database with PVC
│   ├── postgres-service.yaml       # Postgres DNS & connectivity
│   ├── redis-statefulset.yaml      # Redis cache with PVC
│   ├── redis-service.yaml          # Redis DNS & connectivity
│   ├── ingress.yaml                # Nginx Ingress for external access
│   ├── rbac.yaml                   # Role-based access control
│   └── kustomization.yaml          # (Optional) Kustomize base
│
├── monitoring/                     # Observability Stack
│   ├── prometheus-config.yaml      # Prometheus scrape config
│   ├── prometheus-deployment.yaml  # Prometheus deployment
│   ├── prometheus-service.yaml     # Prometheus DNS
│   ├── prometheus-rbac.yaml        # RBAC for Prometheus
│   ├── grafana-config.yaml         # Grafana datasources & dashboards
│   ├── grafana-deployment.yaml     # Grafana deployment
│   └── grafana-service.yaml        # Grafana DNS
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml               # GitHub Actions pipeline
│
├── argo/
│   └── argocd-application.yaml     # Argo CD Application manifest
│
├── README.md                       # Project documentation (this file)
├── .gitignore                      # Git ignore file
└── .env.example                    # Environment variables template
```

## 📋 Prerequisites

Before you begin, ensure you have:

1. **GitHub Account**
   - Repository created with this codebase
   - Docker Hub credentials configured as repository secrets
   - Personal Access Token (for automated commits)

2. **Docker Hub Account**
   - Username and access token for image publishing
   - Public repositories created for images

3. **Kubernetes Cluster**
   - Kubernetes v1.24+ (minikube, Docker Desktop, EKS, GKE, AKS, or local)
   - kubectl configured and authenticated
   - StorageClass available for PersistentVolumes

4. **Local Development Tools**
   - Docker: `docker --version`
   - kubectl: `kubectl version --client`
   - git: `git --version`
   - Python 3.9+: `python --version`

5. **Cluster Add-ons**
   - Ingress Controller (nginx-ingress)
   - Argo CD
   - Prometheus & Grafana (optional)
   - Rancher (optional)

## 🚀 Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/end-to-end_CI_CD.git
cd end-to-end_CI_CD
```

### Step 2: Configure Secrets and Credentials

#### 2.1 Update Docker Credentials in Manifests

Replace `dockerhub_username` with your actual Docker Hub username in the following files:

```bash
# Update in k8s manifests
sed -i 's/dockerhub_username/YOUR_DOCKER_USERNAME/g' k8s/fastapi-deployment.yaml
sed -i 's/dockerhub_username/YOUR_DOCKER_USERNAME/g' k8s/streamlit-deployment.yaml

# Update in Argo CD manifest
sed -i 's/YOUR_GITHUB_USERNAME/YOUR_ACTUAL_USERNAME/g' argo/argocd-application.yaml
```

#### 2.2 Update GitHub Secrets

Add the following secrets to your GitHub repository (Settings → Secrets and Variables):

```
DOCKERHUB_USERNAME=your_dockerhub_username
DOCKERHUB_TOKEN=your_dockerhub_token_or_password
GITHUB_TOKEN=github_personal_access_token
ARGOCD_SERVER=your-argocd-server.example.com:443
ARGOCD_USERNAME=argocd_admin
ARGOCD_PASSWORD=argocd_password
```

#### 2.3 Update Kubernetes Secrets

⚠️ **IMPORTANT**: Update the database and Redis passwords in `k8s/secrets.yaml`

```bash
# Edit the secrets file
nano k8s/secrets.yaml

# Update these values:
# DB_USER: ml_user
# DB_PASSWORD: CHANGE_THIS_STRONG_PASSWORD
# POSTGRES_PASSWORD: CHANGE_THIS_STRONG_PASSWORD
```

### Step 3: Set Up Kubernetes Cluster

#### 3.1 Create Namespace and ConfigMaps

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create configmaps
kubectl apply -f k8s/configmap.yaml

# Create secrets (with updated passwords!)
kubectl apply -f k8s/secrets.yaml
```

#### 3.2 Create RBAC Resources

```bash
kubectl apply -f k8s/rbac.yaml
```

#### 3.3 Deploy PostgreSQL

```bash
kubectl apply -f k8s/postgres-statefulset.yaml
kubectl apply -f k8s/postgres-service.yaml

# Wait for the pod to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n ml-project --timeout=300s

# Verify PostgreSQL is running
kubectl get statefulset,pvc -n ml-project
```

#### 3.4 Deploy Redis

```bash
kubectl apply -f k8s/redis-statefulset.yaml
kubectl apply -f k8s/redis-service.yaml

# Wait for the pod to be ready
kubectl wait --for=condition=ready pod -l app=redis -n ml-project --timeout=300s
```

### Step 4: Deploy FastAPI Service

```bash
kubectl apply -f k8s/fastapi-deployment.yaml
kubectl apply -f k8s/fastapi-service.yaml

# Monitor deployment
kubectl rollout status deployment/fastapi-deployment -n ml-project

# Check pod status
kubectl get pods -n ml-project
```

### Step 5: Deploy Streamlit Frontend

```bash
kubectl apply -f k8s/streamlit-deployment.yaml
kubectl apply -f k8s/streamlit-service.yaml

# Monitor deployment
kubectl rollout status deployment/streamlit-deployment -n ml-project
```

### Step 6: Configure Ingress

Update the hostnames in `k8s/ingress.yaml` and deploy:

```bash
# Update ingress hosts for your domain
nano k8s/ingress.yaml

# Deploy
kubectl apply -f k8s/ingress.yaml

# Verify Ingress is created
kubectl get ingress -n ml-project
```

### Step 7: Deploy Monitoring Stack

```bash
# Deploy Prometheus
kubectl apply -f monitoring/prometheus-rbac.yaml
kubectl apply -f monitoring/prometheus-config.yaml
kubectl apply -f monitoring/prometheus-deployment.yaml
kubectl apply -f monitoring/prometheus-service.yaml

# Deploy Grafana
kubectl apply -f monitoring/grafana-config.yaml
kubectl apply -f monitoring/grafana-deployment.yaml
kubectl apply -f monitoring/grafana-service.yaml

# Verify deployments
kubectl get deployments -n ml-project
```

### Step 8: Install and Configure Argo CD

```bash
# Create argocd namespace
kubectl create namespace argocd

# Install Argo CD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for Argo CD to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=300s

# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Create the application
kubectl apply -f argo/argocd-application.yaml
```

## 📊 Deployment Flow

### 1. **Code Commit to GitHub**
```bash
# Make changes to code
git add .
git commit -m "feat: update ML model"
git push origin main
```

### 2. **GitHub Actions CI/CD Pipeline**

The `.github/workflows/ci-cd.yml` workflow:
- Builds Docker images for FastAPI and Streamlit
- Pushes images to Docker Hub
- Scans images for vulnerabilities
- Updates Kubernetes manifests with new image tags
- Commits changes back to repository

**Pipeline Steps:**
```
Code Push → Build Images → Scan → Push Registry → Update Manifests → Commit
```

### 3. **Argo CD GitOps Sync**

Argo CD continuously monitors the GitHub repository:
- Detects changes in `k8s/` directory
- Automatically syncs cluster state with Git
- Updates deployments with new images
- Performs auto-healing on divergence
- Maintains desired state

**Sync Process:**
```
GitHub Repo Changes → Argo CD Detection → Reconciliation → Cluster Update
```

### 4. **Kubernetes Rolling Updates**

RollingUpdate strategy ensures zero-downtime deployments:
```
New Pod → Health Checks → Traffic Routing → Old Pod Termination
```

## 🎮 Demo & Usage

### Demo 1: Basic Prediction Flow

#### 1.1 Access the Streamlit UI

```bash
# Port forward to Streamlit
kubectl port-forward svc/streamlit-service -n ml-project 8501:8501 &

# Open browser
open http://localhost:8501
```

#### 1.2 Test Prediction

1. Fill in feature values (0-10 range)
2. Click "Get Prediction"
3. Observe:
   - Prediction result
   - Confidence score
   - Cache status (Fresh/Cached)
   - Timestamp

#### 1.3 Test Caching

1. Submit the same features twice
2. Second request should show "✅ Cached" in the Cache Status

### Demo 2: Scaling FastAPI Replicas

#### 2.1 View Current Replicas

```bash
kubectl get deployment fastapi-deployment -n ml-project
kubectl get pods -n ml-project -l app=fastapi
```

#### 2.2 Scale Up to 3 Replicas

```bash
kubectl scale deployment fastapi-deployment -n ml-project --replicas=3

# Monitor scaling
kubectl get pods -n ml-project -l app=fastapi -w
```

#### 2.3 Observe Load Balancing

```bash
# Send multiple requests and observe which pod handles them
for i in {1..10}; do
  kubectl logs -n ml-project -l app=fastapi -c fastapi --tail=1
done
```

#### 2.4 Scale Down

```bash
kubectl scale deployment fastapi-deployment -n ml-project --replicas=2
```

### Demo 3: Pod Failure & Self-Healing

#### 3.1 Kill a Pod

```bash
# Get pod name
FASTAPI_POD=$(kubectl get pods -n ml-project -l app=fastapi -o jsonpath='{.items[0].metadata.name}')

# Delete pod
kubectl delete pod $FASTAPI_POD -n ml-project

# Observe: Kubernetes automatically creates a new pod
kubectl get pods -n ml-project -l app=fastapi -w
```

#### 3.2 Verify Service Continuity

```bash
# Service load balancer directs traffic to healthy pods
kubectl get svc fastapi-service -n ml-project -o wide
```

### Demo 4: Access API Directly

#### 4.1 Port Forward to FastAPI

```bash
kubectl port-forward svc/fastapi-service -n ml-project 8000:8000 &
```

#### 4.2 Make Predictions

```bash
# Health check
curl http://localhost:8000/health

# Make prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"feature_1": 5.0, "feature_2": 3.5, "feature_3": 7.2}'
```

### Demo 5: Monitoring with Grafana

#### 5.1 Access Grafana Dashboard

```bash
# Port forward to Grafana
kubectl port-forward svc/grafana-service -n ml-project 3000:3000 &

# Open browser
open http://localhost:3000

# Login (default credentials)
# Username: admin
# Password: grafana_password_change_me (from secrets)
```

#### 5.2 View Metrics

- Navigate to Dashboards → ML Project Dashboard
- Observe FastAPI service status
- Monitor PostgreSQL and Redis metrics
- View Prometheus alerts

### Demo 6: Argo CD GitOps Deployment

#### 6.1 Access Argo CD UI

```bash
# Port forward to Argo CD
kubectl port-forward svc/argocd-server -n argocd 6443:443 &

# Open browser
open https://localhost:6443

# Login
# Username: admin
# Password: (from step 8 in Setup)
```

#### 6.2 View Application Status

- Application Name: `ml-project-app`
- Namespace: `ml-project`
- Sync Status: Synced
- Health Status: Healthy

#### 6.3 Manual Sync

```bash
# Use Argo CD UI or CLI
argocd app sync ml-project-app
```

#### 6.4 Update and Re-sync

```bash
# Make a change in Git
sed -i 's/replicas: 2/replicas: 3/g' k8s/fastapi-deployment.yaml
git add k8s/fastapi-deployment.yaml
git commit -m "scale: increase fastapi replicas"
git push

# Argo CD automatically syncs and updates
# Or manually trigger sync in UI
```

### Demo 7: Using Rancher Dashboard

#### 7.1 Access Rancher

```bash
# If Rancher is installed
open https://your-rancher-url
```

#### 7.2 Monitor Cluster

- View cluster health
- Monitor workload deployments
- Access pod logs
- Scale workloads from UI
- Delete/update resources

## 📈 Monitoring & Observability

### Prometheus

**URL:** `http://prometheus-service.ml-project.svc.cluster.local:9090`

**Key Metrics:**
- `up{job="fastapi"}`: FastAPI pod status
- `http_requests_total`: Total requests to FastAPI
- `http_request_duration_seconds`: Request latency
- Custom metrics from FastAPI (if instrumented)

**Query Examples:**
```promql
# FastAPI service status
up{job="fastapi"}

# Request rate (per second)
rate(http_requests_total[5m])

# Latency percentiles
histogram_quantile(0.95, http_request_duration_seconds)
```

### Grafana

**URL:** `http://grafana-service.ml-project.svc.cluster.local:3000`

**Default Dashboard:** "ML Project Dashboard"

**Pre-configured Panels:**
- FastAPI Service Status
- Request Rate & Latency
- Database Connection Pool
- Redis Cache Hit Ratio

### Logging

```bash
# View FastAPI logs
kubectl logs -f deployment/fastapi-deployment -n ml-project -c fastapi

# View Streamlit logs
kubectl logs -f deployment/streamlit-deployment -n ml-project -c streamlit

# View Postgres logs
kubectl logs -f statefulset/postgres -n ml-project -c postgres

# View all logs in namespace
kubectl logs -f -n ml-project --all-containers=true --prefix=true
```

## 🔧 Troubleshooting

### Issue 1: Pods Stuck in Pending State

```bash
# Check events
kubectl describe pod <pod-name> -n ml-project

# Check node resources
kubectl top nodes
kubectl top pods -n ml-project

# Check PVC status
kubectl get pvc -n ml-project
kubectl describe pvc <pvc-name> -n ml-project
```

### Issue 2: Database Connection Errors

```bash
# Check if Postgres is running
kubectl get statefulset postgres -n ml-project
kubectl logs -f statefulset/postgres -n ml-project

# Test connection from FastAPI pod
kubectl exec -it <fastapi-pod> -n ml-project -- \
  psql -h postgres-service.ml-project.svc.cluster.local -U ml_user -d ml_db

# Check secrets are mounted
kubectl exec -it <fastapi-pod> -n ml-project -- env | grep DB_
```

### Issue 3: Images Not Pulling from Docker Hub

```bash
# Verify Docker Hub credentials
kubectl get secret regcred -n ml-project

# Check image availability
docker pull dockerhub_username/fastapi-ml-service:latest

# Create ImagePullSecret if needed
kubectl create secret docker-registry regcred \
  --docker-server=docker.io \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_TOKEN \
  -n ml-project
```

### Issue 4: Argo CD Not Syncing

```bash
# Check Argo CD server
kubectl get pod -n argocd

# Check application status
argocd app get ml-project-app

# Force sync
argocd app sync ml-project-app --force

# View Argo CD logs
kubectl logs -f deployment/argocd-application-controller -n argocd
```

### Issue 5: Ingress Not Working

```bash
# Check Ingress Controller
kubectl get pods -n ingress-nginx

# Verify Ingress resource
kubectl describe ingress ml-ingress -n ml-project

# Check DNS resolution
kubectl exec -it <any-pod> -n ml-project -- \
  nslookup streamlit.ml-project.local

# Test from pod
kubectl exec -it <any-pod> -n ml-project -- \
  curl -v http://streamlit-service.ml-project.svc.cluster.local:8501
```

## 📚 Additional Resources

### Documentation
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Argo CD Documentation](https://argo-cd.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/grafana/)

### Tools & CLIs
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Install Argo CD CLI
curl -sSL -o argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Useful kubectl Commands

```bash
# Get all resources in namespace
kubectl get all -n ml-project

# Describe a pod
kubectl describe pod <pod-name> -n ml-project

# Execute command in pod
kubectl exec -it <pod-name> -n ml-project -- /bin/bash

# Forward local port to service
kubectl port-forward svc/<service-name> -n ml-project <local-port>:<service-port>

# Scale deployment
kubectl scale deployment <deployment-name> -n ml-project --replicas=<count>

# Update image
kubectl set image deployment/<deployment-name> <container>=<new-image> -n ml-project

# Watch resource changes
kubectl get <resource> -n ml-project -w

# Delete all resources
kubectl delete all --all -n ml-project
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
- Open an Issue on GitHub
- Check Troubleshooting section above
- Review logs: `kubectl logs -f <pod-name> -n ml-project`

---

**Happy Deploying! 🚀**

Last Updated: 2024
