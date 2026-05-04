# 📊 สถานะโปรเจค Aradin Converter

> สรุปสถานะ ณ วันที่ **2026-05-04** เทียบกับ checklist ใน [README.md](README.md)

**สัญลักษณ์:**
- ✅ = เสร็จแล้ว มีหลักฐาน (test/run/log)
- 🟡 = สร้างไฟล์/code แล้ว แต่ **ยังไม่ได้รันจริงบนระบบเป้าหมาย**
- ❌ = ยังไม่ได้ทำเลย ต้องลงมือ
- 👤 = งานที่ต้องทำด้วยมือผ่าน UI/Cloud (Claude ทำให้ไม่ได้)

---

## 🗺️ สรุปภาพรวม

| Phase | สถานะ | %  |
|-------|------|----|
| **1. โครงสร้าง Repo + ไฟล์** | ✅ เสร็จ | 100% |
| **2. Local development** | ✅ เสร็จ | 100% |
| **3. Git / GitHub** | ✅ push ขึ้น remote แล้ว | 100% |
| **4. Docker** | 🟡 มี Dockerfile แต่ยังไม่ได้ build/run | 0% |
| **5. Jenkins CI/CD** | 🟡 มี Jenkinsfile แต่ยังไม่ตั้ง Jenkins | 0% |
| **6. Terraform** | 🟡 มีไฟล์ แต่ยังไม่ได้ apply | 0% |
| **7. Ansible** | 🟡 มีไฟล์ แต่ยังไม่ได้รัน playbook | 0% |
| **8. Kubernetes** | 🟡 มี manifests แต่ยังไม่มี cluster ที่ apply | 0% |
| **9. Prometheus** | 🟡 มี config แต่ยังไม่ได้รัน | 0% |
| **10. Grafana** | 🟡 มี dashboard JSON แต่ยังไม่ได้ import | 0% |

---

## ✅ Phase 1 — โครงสร้าง Repository (เสร็จแล้ว)

ตามตาราง "โครงสร้าง Repository" ใน README สร้างครบทุกไฟล์:

| ไฟล์ | สถานะ | หมายเหตุ |
|------|--------|---------|
| `app/templates/index.html` | ✅ | Web UI แบบ form + JS fetch |
| `app/static/style.css` | ✅ | Dark theme |
| `app/app.py` | ✅ | Flask + 4 endpoints |
| `app/conversions.py` | ✅ | logic แปลงหน่วย (เพิ่มจาก README) |
| `app/test_conversions.py` | ✅ | unit tests 12 ข้อ (เพิ่มจาก README) |
| `app/requirements.txt` | ✅ | flask, prometheus-flask-exporter, prometheus-client, pytest |
| `app/Dockerfile` | ✅ | python:3.11-slim, non-root, healthcheck |
| `Jenkinsfile` | ✅ | 6 stages |
| `terraform/main.tf` | ✅ | provider kubernetes + namespace |
| `terraform/variables.tf` | ✅ | namespace, kubeconfig_path |
| `terraform/outputs.tf` | ✅ | namespace_name |
| `ansible/inventory` | ✅ | localhost |
| `ansible/playbook.yml` | ✅ | apply k8s + run Prom/Grafana |
| `k8s/deployment.yaml` | ✅ | 2 replicas, probes, resource limits |
| `k8s/service.yaml` | ✅ | NodePort 30080 |
| `monitoring/prometheus.yml` | ✅ | scrape ทุก 15s |
| `monitoring/grafana-dashboard.json` | ✅ | 4 panels ตรง PromQL ใน README |
| `README.md` | ✅ | (ของเดิม ไม่ได้แก้) |

ไฟล์เพิ่มเติมที่สร้างขึ้น (ไม่ได้อยู่ใน README แต่จำเป็น):
- `.gitignore` ✅
- `docs/superpowers/specs/2026-05-04-aradin-converter-design.md` ✅ (design spec)
- `PROGRESS.md` ✅ (ไฟล์นี้)

---

## ✅ Phase 2 — Local Development (เสร็จแล้ว)

### 2.1 ติดตั้ง dependencies
```bash
pip install -r app/requirements.txt
```
**สถานะ:** ✅ ติดตั้งแล้วบนเครื่องนี้ (Python 3.13.2)

### 2.2 รันแอป
```bash
cd app && python app.py
```
**สถานะ:** ✅ รันที่ `http://localhost:5000` ได้

### 2.3 ผลลัพธ์ smoke test
| Endpoint | Method | ผลลัพธ์ |
|---|---|---|
| `/health` | GET | ✅ `{"status":"ok"}` |
| `/convert` 1500m → km | POST | ✅ `{"result":1.5,...}` |
| `/convert` 100°C → °F | POST | ✅ `{"result":212.0,...}` |
| `/metrics` | GET | ✅ มีทั้ง `http_requests_total` และ `flask_http_request_duration_seconds_bucket` |

### 2.4 Unit tests
```bash
cd app && pytest -v
```
**สถานะ:** ✅ **12 passed** ใน 0.04s

---

## ✅ Phase 3 — Git / GitHub (เสร็จแล้ว)

| ขั้นตอน | สถานะ | หมายเหตุ |
|--------|------|---------|
| `git init -b main` | ✅ | local repo |
| Initial commit (20 files) | ✅ | hash `2e3a7dc` |
| `git remote add origin` | ✅ | https://github.com/Aphikap/Aradin-Unit |
| `git push -u origin main` | ✅ | branch `main` track `origin/main` |
| สร้าง branch `dev` | ❌ | ยังไม่ได้ทำ |
| Protected branches (main, dev) | ❌ 👤 | ตั้งใน GitHub Settings → Branches |

---

## 🟡 Phase 4 — Docker (ยังไม่ได้ทดสอบ)

| ขั้นตอน | สถานะ | คำสั่ง |
|--------|------|--------|
| มี Dockerfile | ✅ | `app/Dockerfile` |
| Build image | ❌ | `docker build -t aradin/aradin-converter:latest ./app` |
| Run container | ❌ | `docker run -p 5000:5000 aradin/aradin-converter:latest` |
| ทดสอบเข้าผ่าน browser | ❌ | http://localhost:5000 |
| Push to Docker Hub | ❌ 👤 | ต้อง login Docker Hub ก่อน (`docker login`) |

**สิ่งที่ต้องทำต่อ:**
1. ติดตั้ง Docker Desktop (ถ้ายังไม่ได้ติด)
2. รัน build/run ตามคำสั่งข้างบน
3. สมัคร Docker Hub account ในชื่อ `aradin` (หรือชื่อจริงของกลุ่ม)

---

## 🟡 Phase 5 — Jenkins CI/CD (ยังไม่ได้ตั้งค่า)

### 5.1 ติดตั้ง Jenkins
| ขั้นตอน | สถานะ |
|--------|------|
| ติดตั้ง Jenkins (≥ 2.4xx) | ❌ 👤 |
| เปิดที่ `http://localhost:8080` | ❌ 👤 |

### 5.2 ติดตั้ง Plugins
| Plugin | สถานะ |
|--------|------|
| Git | ❌ 👤 |
| Pipeline | ❌ 👤 |
| Docker Pipeline | ❌ 👤 |

### 5.3 Credentials
| Credential | สถานะ |
|-----------|------|
| `dockerhub-credentials` (username/password) | ❌ 👤 ต้องเพิ่มใน Manage Jenkins → Credentials |

### 5.4 Pipeline Job
| ขั้นตอน | สถานะ |
|--------|------|
| สร้าง Pipeline job ใหม่ | ❌ 👤 |
| ชี้ไปที่ repo `https://github.com/Aphikap/Aradin-Unit` | ❌ 👤 |
| ตั้ง Branch Specifier `*/main` | ❌ 👤 |

### 5.5 GitHub Webhook
| ขั้นตอน | สถานะ |
|--------|------|
| เข้า GitHub repo → Settings → Webhooks → Add webhook | ❌ 👤 |
| Payload URL: `http://[jenkins-host]:8080/github-webhook/` | ❌ 👤 |
| Content type: `application/json` | ❌ 👤 |
| Trigger: Just the push event | ❌ 👤 |

### 5.6 Pipeline Stages (เมื่อรัน build แล้ว)
| Stage | สถานะ |
|-------|------|
| Checkout | ❌ |
| Build | ❌ |
| Test | ❌ |
| Docker Build | ❌ |
| Push to Hub | ❌ |
| Deploy | ❌ |

---

## 🟡 Phase 6 — Terraform (ยังไม่ได้ apply)

| ขั้นตอน | สถานะ | คำสั่ง |
|--------|------|--------|
| มีไฟล์ครบ | ✅ | `terraform/main.tf, variables.tf, outputs.tf` |
| `terraform init` | ❌ | ดาวน์โหลด provider plugin |
| `terraform plan` | ❌ | ดูว่าจะสร้างอะไร |
| `terraform apply` | ❌ | สร้างจริง (namespace `aradin`) |

**ต้องมี kubeconfig และ K8s cluster ก่อนถึงจะ apply ได้** (ดู Phase 8)

---

## 🟡 Phase 7 — Ansible (ยังไม่ได้รัน playbook)

| ขั้นตอน | สถานะ | คำสั่ง |
|--------|------|--------|
| มี inventory + playbook | ✅ | |
| ติดตั้ง Ansible (≥ 2.15) | ❌ 👤 | |
| ติดตั้ง collection `community.docker` | ❌ | `ansible-galaxy collection install community.docker` |
| รัน playbook | ❌ | `ansible-playbook -i ansible/inventory ansible/playbook.yml` |

**Tasks ใน playbook (เมื่อรัน):**
| Task | สถานะ |
|------|------|
| Verify kubectl | ❌ |
| Apply namespace | ❌ |
| Apply k8s manifests | ❌ |
| Wait for rollout | ❌ |
| Run Prometheus container | ❌ |
| Run Grafana container | ❌ |

---

## 🟡 Phase 8 — Kubernetes (ยังไม่มี cluster)

### 8.1 ติดตั้ง cluster
| Tool | สถานะ |
|------|------|
| `kubectl` (≥ 1.28) | ❌ 👤 |
| Minikube หรือ K3s | ❌ 👤 |
| Cluster ทำงาน (`kubectl cluster-info`) | ❌ |

### 8.2 Apply manifests
| คำสั่ง | สถานะ |
|--------|------|
| `kubectl apply -f k8s/deployment.yaml` | ❌ |
| `kubectl apply -f k8s/service.yaml` | ❌ |

### 8.3 ตรวจสถานะ
| คำสั่ง | สถานะ |
|--------|------|
| `kubectl get pods -n aradin` | ❌ |
| `kubectl get svc -n aradin` | ❌ |
| เข้าผ่าน NodePort `http://localhost:30080` | ❌ |

---

## 🟡 Phase 9 — Prometheus (ยังไม่ได้รัน)

| ขั้นตอน | สถานะ |
|--------|------|
| มีไฟล์ `monitoring/prometheus.yml` | ✅ |
| ติดตั้ง Prometheus | ❌ 👤 |
| รัน `prometheus --config.file=monitoring/prometheus.yml` | ❌ |
| เปิด UI ที่ `http://localhost:9090` | ❌ |
| ตรวจ target `aradin-converter` ขึ้น UP | ❌ |
| ตรวจ `/metrics` ของแอป (`curl http://localhost:5000/metrics`) | ✅ ทำแล้วตอน smoke test |

> Ansible playbook สามารถรัน Prometheus เป็น docker container ให้อัตโนมัติ (ผ่าน `community.docker.docker_container`)

---

## 🟡 Phase 10 — Grafana (ยังไม่ได้ import dashboard)

| ขั้นตอน | สถานะ |
|--------|------|
| มีไฟล์ `monitoring/grafana-dashboard.json` | ✅ |
| ติดตั้ง Grafana | ❌ 👤 |
| เปิด `http://localhost:3000` | ❌ |
| Login (admin/admin) | ❌ 👤 |
| เพิ่ม Data source: Prometheus → `http://localhost:9090` | ❌ 👤 |
| **Dashboards → Import** → upload `grafana-dashboard.json` | ❌ 👤 |
| ตรวจ 4 panels:<br>• Request Rate<br>• Error Rate<br>• Latency p95<br>• Pod Health | ❌ |

> Ansible playbook สามารถรัน Grafana เป็น docker container ให้ก่อนได้ (ยังต้อง import dashboard ด้วยมือ)

---

## 🛠️ Step-by-step ขั้นต่อไป (เรียงตามลำดับที่แนะนำ)

### A. ตรวจ Docker ก่อน (5 นาที)
```bash
# ติดตั้ง Docker Desktop ถ้ายังไม่มี → https://www.docker.com/products/docker-desktop
docker --version

# ลอง build และ run
docker build -t aradin/aradin-converter:latest ./app
docker run --rm -p 5000:5000 aradin/aradin-converter:latest
# เปิด browser ไป http://localhost:5000 — ลองแปลงหน่วย
```

### B. ติดตั้ง Local K8s Cluster (15-30 นาที)
```bash
# ติดตั้ง kubectl + minikube (Windows ใช้ winget หรือ choco)
winget install Kubernetes.kubectl
winget install Kubernetes.minikube

# Start cluster
minikube start --driver=docker
kubectl cluster-info
```

### C. Apply Manifests ตรงๆ ก่อน (เพื่อทดสอบ K8s) (10 นาที)
```bash
kubectl create namespace aradin
kubectl apply -f k8s/
kubectl get pods -n aradin -w     # รอจน Running 1/1
kubectl get svc -n aradin

# ทดสอบ
minikube service aradin-converter-svc -n aradin
# หรือ
curl http://$(minikube ip):30080/health
```

### D. ทดสอบ Terraform (10 นาที)
```bash
# ลบ namespace ก่อน เพื่อให้ Terraform สร้างใหม่
kubectl delete namespace aradin

cd terraform
terraform init
terraform plan
terraform apply
# ควรได้ namespace อีกครั้ง
```

### E. ทดสอบ Ansible (15 นาที)
```bash
# ติดตั้ง Ansible ใน WSL หรือ Linux VM (Windows native ไม่ค่อย support)
pip install ansible
ansible-galaxy collection install community.docker

cd ansible
ansible-playbook -i inventory playbook.yml
# จะ apply k8s + start Prometheus + Grafana ให้
```

### F. Setup Jenkins (1-2 ชม.)
1. ติดตั้ง Jenkins LTS → https://www.jenkins.io/download/
2. ปลดล็อค admin password (`/var/jenkins_home/secrets/initialAdminPassword`)
3. ติดตั้ง Suggested plugins + Docker Pipeline plugin
4. **Manage Jenkins → Credentials** เพิ่ม `dockerhub-credentials` (Docker Hub user/pass)
5. **New Item → Pipeline** → ชื่อ `aradin-converter`
   - Pipeline → Definition: **Pipeline script from SCM**
   - SCM: Git, URL `https://github.com/Aphikap/Aradin-Unit.git`
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`
6. กด **Build Now** ลองครั้งแรก

### G. Setup GitHub Webhook (5 นาที)
1. **GitHub repo → Settings → Webhooks → Add webhook**
2. Payload URL: `http://<jenkins-public-host>:8080/github-webhook/`
   - ถ้า Jenkins อยู่ local ต้องใช้ ngrok หรือ Cloudflare Tunnel
3. Content type: `application/json`
4. Just the push event ✓

### H. Setup Branch Protection (3 นาที 👤)
**GitHub repo → Settings → Branches → Add rule**:
- Branch name pattern: `main`
- ✓ Require pull request before merging
- ✓ Require status checks (Jenkins build)

### I. สร้าง dev branch
```bash
git checkout -b dev
git push -u origin dev
```

---

## 👥 ใครต้องทำอะไร (ตามตาราง README)

| สมาชิก | ความรับผิดชอบ | Phase ที่เกี่ยวข้อง |
|--------|--------------|------------------|
| B6626259 ณภัทร | Git, App Development | ✅ Phase 1, 2, 3 (เสร็จแล้ว) |
| B6615994 ธนภัทร | Jenkins, Docker | 🟡 Phase 4, 5 |
| B6628611 อภิชาติ | Terraform, Ansible | 🟡 Phase 6, 7 |
| B6628857 อาระดิน | Kubernetes, Monitoring | 🟡 Phase 8, 9, 10 |

---

## 📌 Definition of Done (โปรเจคเสร็จเมื่อ)

- [ ] `git push` ไป main → Jenkins รันอัตโนมัติ
- [ ] Pipeline ผ่านทั้ง 6 stages โดยไม่ต้องแก้
- [ ] Image ขึ้น Docker Hub `aradin/aradin-converter:<build_number>`
- [ ] `kubectl get pods -n aradin` แสดง 2 pods Running 1/1
- [ ] เปิด `http://<minikube-ip>:30080` แล้วแปลงหน่วยได้
- [ ] Prometheus UI (`:9090`) target `aradin-converter` แสดง UP
- [ ] Grafana dashboard (`:3000`) แสดง 4 panels มีข้อมูล
- [ ] ส่งงานก่อน deadline ของรายวิชา ENG23 3074

---

## 📞 ปัญหาที่อาจพบ (ดูเพิ่มใน README หัวข้อ Troubleshooting)

- **Pod stuck `Pending`** → `kubectl describe pod <name> -n aradin` ดู Events
- **Jenkins Docker Build fail** → `sudo usermod -aG docker jenkins` แล้ว restart
- **Prometheus target DOWN** → ตรวจว่า `host.docker.internal` resolve ได้ใน Prometheus container
- **Grafana panel ว่างเปล่า** → ตรวจ Data source UID ตรงกับใน JSON (`prometheus`)
