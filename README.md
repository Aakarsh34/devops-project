# Local Production-Style CI/CD Demo

This project has been converted from an app-controlled Flask demo into a generic CI/CD system driven by Jenkins, Docker, and Kubernetes.

## Final Review Status

This project is review-ready as a complete local DevOps demonstration.

- CI/CD automation is implemented through Jenkins and GitHub webhooks.
- Kubernetes handles rolling deployment, service-based load balancing, self-healing, and HPA-based scaling.
- Prometheus and Grafana are included for monitoring and review evidence.
- MTTR is not calculated by HPA itself, but this project now exposes the monitoring data and alert timing needed to discuss recovery time during final review.

## What changed

- Removed Flask routes that scaled pods or deleted pods directly.
- Kept the sample app generic and added `/healthz`, `/readyz`, and `/metrics`.
- Added a Jenkins pipeline that:
  - triggers on GitHub push
  - checks out source
  - detects Python, Node.js, or C++
  - runs a basic build
  - runs tests when they exist
  - builds a Docker image
  - pushes the image to Docker Hub
  - deploys to Kubernetes with `kubectl`
- Upgraded Kubernetes manifests for rolling updates, self-healing, and HPA.
- Added Prometheus and Grafana manifests for local monitoring.
- Added a local Jenkins container setup with required plugins.

## Files

- [Jenkinsfile](./Jenkinsfile)
- [deployment.yaml](./deployment.yaml)
- [service.yaml](./service.yaml)
- [hpa.yaml](./hpa.yaml)
- [prometheus.yaml](./prometheus.yaml)
- [grafana.yaml](./grafana.yaml)
- [metrics-server.yaml](./metrics-server.yaml)
- [README.md](./README.md)
- [Dockerfile](./Dockerfile)
- [docker-compose.yaml](./docker-compose.yaml)
- [jenkins/Dockerfile](./jenkins/Dockerfile)
- [jenkins/plugins.txt](./jenkins/plugins.txt)

## Prerequisites

- Docker Desktop installed
- Docker Desktop Kubernetes enabled
- GitHub repository for this project
- Docker Hub account

## Step 1: Push this project to GitHub

Create a repository and push these files so Jenkins can clone it and GitHub can send webhooks.

## Step 2: Start Jenkins locally

From the project root:

```powershell
docker compose up -d --build
```

Open Jenkins at `http://localhost:8080`.

Get the initial admin password:

```powershell
docker exec local-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

## Step 3: Install Kubernetes metrics support

HPA needs the Kubernetes metrics API. Apply:

```powershell
kubectl apply -f metrics-server.yaml
kubectl get pods -n kube-system
kubectl top nodes
```

If `kubectl top nodes` returns metrics, HPA is ready.

## Step 4: Create Jenkins credentials

Create these credentials in Jenkins:

1. `docker-registry-credentials`
   Use Docker Hub username/password or a Docker Hub access token.

2. `kubeconfig`
   Add your local kubeconfig file as a secret file credential.

## Step 5: Create the Jenkins pipeline job

Create a `Pipeline` job in Jenkins and point it at your GitHub repository.

Use these build parameters:

- `DOCKER_IMAGE_REPO`
  Example: `your-dockerhub-username/generic-app`
- `KUBE_NAMESPACE`
  Usually `default`

## Step 6: Add the GitHub webhook

In your GitHub repository:

- Go to `Settings -> Webhooks`
- Add a webhook URL:
  - local Jenkins: use a tunnel such as `ngrok` and point to `/github-webhook/`
  - example: `https://your-public-url/github-webhook/`
- Content type: `application/json`
- Event: `Just the push event`

Without a public callback URL, GitHub cannot reach your local Jenkins directly.

## Step 7: First deployment

Apply the workload once or let Jenkins do it on the first push:

```powershell
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
kubectl apply -f prometheus.yaml
kubectl apply -f grafana.yaml
```

Access local services:

- App: `http://localhost:30080`
- Prometheus: `http://localhost:30090`
- Grafana: `http://localhost:30300`

Grafana default login:

- user: `admin`
- password: `admin123`

## Step 8: What the demo now shows

- Automatic deployment on code push through GitHub webhook -> Jenkins -> Kubernetes
- Load balancing through the Kubernetes service
- Self-healing because the Deployment controller maintains replica count
- Rolling updates during image changes
- Auto-scaling through HPA when CPU metrics rise
- Metrics collection in Prometheus
- Visualization in Grafana
- Alert rules for service outage and traffic interruption
- Review-ready dashboard provisioning in Grafana

## How stack detection works

The Jenkins pipeline checks the repo content:

- `package.json` -> Node.js
- `requirements.txt` or `pyproject.toml` -> Python
- `Makefile`, `CMakeLists.txt`, or `*.cpp` -> C++

## Notes

- The included sample app is still Python because the repo currently contains a Python app.
- The pipeline is generic, but different repos may still need a custom startup command or a custom Dockerfile.
- For local webhook testing, a tunnel such as `ngrok` is the simplest path.
- HPA helps reduce overload and improve recovery behavior, but it does not compute MTTR directly.
- For final review, discuss MTTR using alert start and recovery timestamps from Prometheus/Grafana.
- For HPA demos, generate CPU load against the app and watch:

```powershell
kubectl get hpa -w
```

## MTTR For Final Review

Use this wording in the review:

- HPA supports resilience by increasing replicas automatically when CPU rises.
- Self-healing comes from the Kubernetes Deployment controller and health probes.
- MTTR is inferred from monitoring evidence, not produced by HPA itself.
- In this project, MTTR can be estimated from the time an alert starts firing to the time service health and replica availability return to normal.

Useful review signals:

- `GenericAppDown` alert firing and clearing in Prometheus
- `GenericAppTrafficStopped` alert if request flow stops
- Grafana dashboard panels for application reachability, request rate, and alert state
- Kubernetes rollout and pod recreation behavior
- `kubectl get hpa -w` showing replica scaling behavior
