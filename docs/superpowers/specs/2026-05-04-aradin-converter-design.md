# Aradin Converter — Design Spec

**Date:** 2026-05-04
**Course:** ENG23 3074
**Status:** Approved for implementation

## 1. Goal

Scaffold a complete DevOps demo project that satisfies every section of the existing `README.md`: a Flask unit-conversion API + web UI, Dockerized, deployed on Kubernetes via a Jenkins pipeline that runs Terraform and Ansible, and observed by Prometheus + Grafana.

The output is a *working demo* (option A from brainstorming): every file rises above placeholder; running `python app.py` works, `docker build` works, `kubectl apply -f k8s/` works against a local cluster, and the Jenkins pipeline executes end-to-end.

## 2. Identifiers

| Field | Value |
|---|---|
| Docker Hub username | `aradin` |
| Image / app name | `aradin-converter` |
| K8s namespace | `aradin` |
| App port | `5000` |
| NodePort | `30080` |

## 3. Application

### 3.1 Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | HTML form — categories, units, value, result |
| POST | `/convert` | JSON in → JSON out: `{category, from, to, value}` → `{result}` |
| GET | `/health` | `{"status":"ok"}` — used by k8s liveness/readiness probe |
| GET | `/metrics` | Prometheus metrics — `prometheus-flask-exporter` for histograms + a manual `Counter('http_requests_total', ['method','endpoint','status'])` so the README's exact PromQL works |

### 3.2 Conversion units

- **length:** m, km, cm, mm, inch, foot, yard, mile
- **weight:** kg, g, mg, lb, oz
- **temperature:** C, F, K (handled via piecewise formulas, not a factor table)

### 3.3 Code structure

- `app/app.py` — Flask app, route handlers only (~80 lines)
- `app/conversions.py` — pure functions: `convert(category, src, dst, value) -> float`. Length/weight via factor maps to a base unit; temperature via dedicated formulas.
- `app/test_conversions.py` — unit tests run in Jenkins **Test** stage (`pytest`)
- `app/templates/index.html` — single page, vanilla JS, fetch `/convert`
- `app/static/style.css` — minimal modern CSS
- `app/requirements.txt` — `flask`, `prometheus-flask-exporter`, `pytest`
- `app/Dockerfile` — `python:3.11-slim`, non-root user, `EXPOSE 5000`, `CMD ["python","app.py"]`

## 4. CI/CD — Jenkinsfile

Declarative pipeline, 6 stages exactly as the README table:

1. **Checkout** — `checkout scm`
2. **Build** — `pip install -r app/requirements.txt`
3. **Test** — `pytest app/test_conversions.py`
4. **Docker Build** — `docker build -t aradin/aradin-converter:${BUILD_NUMBER} ./app` (also tag `latest`)
5. **Push to Hub** — `withCredentials([usernamePassword(credentialsId:'dockerhub-credentials',...)]) { docker push }`
6. **Deploy** — `terraform -chdir=terraform apply -auto-approve` → `ansible-playbook -i ansible/inventory ansible/playbook.yml` → `kubectl apply -f k8s/`

`agent any`. `BUILD_NUMBER` used as image tag for traceability.

## 5. Infrastructure as Code

### 5.1 Terraform (`terraform/`)

Provider: `kubernetes` (talks to current kubeconfig — works with minikube/k3s).

Resources:
- `kubernetes_namespace.aradin` (name from `var.namespace`)

Files:
- `main.tf` — provider + namespace resource
- `variables.tf` — `namespace` (default `aradin`), `kubeconfig_path`
- `outputs.tf` — `namespace_name`

### 5.2 Ansible (`ansible/`)

- `inventory` — `localhost ansible_connection=local`
- `playbook.yml` — tasks:
  1. Ensure `kubectl` is on PATH (assert; do not install — keeps it portable)
  2. `kubectl apply -f k8s/` (via `command` module)
  3. Wait for deployment ready (`kubectl rollout status`)
  4. Render `monitoring/prometheus.yml` and run Prometheus + Grafana as docker containers (idempotent via `community.docker.docker_container`)

## 6. Kubernetes (`k8s/`)

### 6.1 deployment.yaml
- `kind: Deployment`, namespace `aradin`, name `aradin-converter`
- `replicas: 2`
- container `aradin/aradin-converter:latest`, port 5000
- `resources.requests` 64Mi/100m, `limits` 256Mi/500m
- `livenessProbe` GET `/health` initialDelay 10s, period 10s
- `readinessProbe` GET `/health` initialDelay 3s, period 5s
- annotations `prometheus.io/scrape: "true"`, `prometheus.io/port: "5000"`

### 6.2 service.yaml
- `kind: Service`, type `NodePort`
- selector `app: aradin-converter`
- port 5000, nodePort 30080

## 7. Monitoring

### 7.1 prometheus.yml
- `global.scrape_interval: 15s`
- single job `aradin-converter`, target the NodePort `host.docker.internal:30080` (so Prometheus running in docker can reach the cluster), metrics_path `/metrics`

### 7.2 grafana-dashboard.json
Importable dashboard with 4 panels matching the README table:
- Request Rate — `rate(http_requests_total[1m])`
- Error Rate — `rate(http_requests_total{status=~"5.."}[1m])`
- Latency p95 — `histogram_quantile(0.95, sum(rate(flask_http_request_duration_seconds_bucket[5m])) by (le))`
- Pod Health — `up{job="aradin-converter"}`

Datasource UID set to `prometheus` (the default name when adding the data source).

> **Metric naming note:** `http_requests_total` is emitted by a manual `Counter` in `app.py` (with labels `method`, `endpoint`, `status`). `flask_http_request_duration_seconds_bucket` comes for free from `prometheus-flask-exporter`. Both names match the README PromQL exactly.

## 8. Testing strategy

- **Unit:** `pytest` in `app/test_conversions.py` — covers each category, each direction, edge cases (same unit → same value, F↔C↔K round-trip).
- **Integration:** manually verifiable via `curl localhost:5000/convert -d '{...}'`. No automated integration tests in this iteration.
- **Pipeline:** Jenkins Test stage fails the build if `pytest` exits non-zero.

## 9. Out of scope

- Real cloud (AWS/GCP) Terraform — staying on local k8s
- HTTPS / Ingress — NodePort is enough for the demo
- Persistent storage — app is stateless
- Auth / users
- Rate limiting

## 10. File inventory (all to be created)

```
app/app.py
app/conversions.py
app/test_conversions.py
app/requirements.txt
app/Dockerfile
app/templates/index.html
app/static/style.css
Jenkinsfile
terraform/main.tf
terraform/variables.tf
terraform/outputs.tf
ansible/inventory
ansible/playbook.yml
k8s/deployment.yaml
k8s/service.yaml
monitoring/prometheus.yml
monitoring/grafana-dashboard.json
```

17 files total.
