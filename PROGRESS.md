# 📊 สถานะโปรเจค Aradin Converter

> สรุปสถานะ ณ วันที่ **2026-05-11** (อัพเดตล่าสุด 17:13 — Phase 5 + 11 webhook ปิด end-to-end ผ่าน) เทียบกับ checklist ใน [README.md](README.md)

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
| **3. Git / GitHub** | ✅ push ขึ้น remote + branch protection main/dev (require PR) | 100% |
| **4. Docker** | ✅ build + run + push Docker Hub (`aphikap/aradin-converter` tags :1–:11) | 100% |
| **5. Jenkins CI/CD** | ✅ Build #10 manual + Build #11 webhook-triggered ผ่านทั้ง 6/6 stages | 100% |
| **6. Terraform** | ✅ รัน native + รันใน Jenkins Deploy stage (import + apply idempotent) | 100% |
| **7. Ansible** | ✅ playbook 5/5 tasks ใน Jenkins (skip_monitoring=true) + 7/7 tasks native | 100% |
| **8. Kubernetes** | ✅ kind cluster `aradin` + 2 pods Running + Service 30080 + rolling update via Jenkins | 100% |
| **9. Prometheus** | ✅ container `aradin-prom` รัน + target `aradin-converter` UP | 100% |
| **10. Grafana** | ✅ container `aradin-grafana` + dashboard import + 4 panels query OK | 100% |
| **11. Presentation & Demo** | 🟡 diagram + demo script + Q&A doc + end-to-end ผ่านของจริง เหลือซ้อมจริง | 90% |

---

## 🎯 Mapping → เกณฑ์การให้คะแนน (Rubric 100 คะแนน)

ตารางนี้คือการเทียบ 10 phase ของ PROGRESS.md ↔ 5 rubric phase + Bonus ของวิชา

| Rubric (จากภาพ) | ข้อย่อย | คะแนน | Phase ใน PROGRESS.md | สถานะ |
|---|---|---|---|---|
| **Rubric Phase 1**<br>Git & Source Code | Git repo + branching strategy | 3 | Phase 3 | ✅ main + dev + classic branch protection (require PR) |
| (10 pts) | App code runs + Dockerfile valid | 5 | Phase 2 + 4 | ✅ |
|  | README.md setup instructions | 2 | Phase 1 ([README §93](README.md#L93)) | ✅ |
| **Rubric Phase 2**<br>Jenkins CI/CD + Docker | Jenkinsfile 6 stages | 10 | Phase 5.6 | ✅ Build #10 + #11 SUCCESS 6/6 stages |
| (25 pts) | Webhook triggers pipeline | 5 | Phase 5.5 | ✅ Build #11 "Started by GitHub push by Aphikap" via Cloudflare tunnel |
|  | Docker build & push to Hub | 10 | Phase 4 | ✅ tags `:1`..`:11` |
| **Rubric Phase 3**<br>Terraform + Ansible | Terraform provisions infra | 7 | Phase 6 | ✅ Jenkins Deploy stage import + apply (idempotent) |
| (15 pts) | Ansible configures env | 5 | Phase 7 | ✅ Jenkins Deploy stage 5/5 tasks (skip_monitoring=true) |
|  | Both integrated in Deploy stage | 3 | Phase 5.6 | ✅ verified in Build #10 + #11 |
| **Rubric Phase 4**<br>Kubernetes | deployment.yaml + image + replicas | 10 | Phase 1 + 8 | ✅ apply + rolling update via Jenkins |
| (25 pts) | service.yaml NodePort | 7 | Phase 1 + 8 | ✅ Service NodePort `5000:30080` |
|  | Pods running & accessible | 8 | Phase 8.3 | ✅ smoke test ผ่าน 4/4 endpoints |
| **Rubric Phase 5**<br>Prometheus + Grafana | `/metrics` exposed | 5 | Phase 2.3 + 9 | ✅ |
| (15 pts) | Prometheus scrapes target UP | 5 | Phase 9 | ✅ target `aradin-converter` UP |
|  | Grafana ≥3 panels meaningful | 5 | Phase 10 (มี 4 panels) | ✅ 4 panels query สำเร็จทั้งหมด |
| **Rubric Bonus**<br>Presentation & Demo | Live demo: push → pods running | 5 | **Phase 11** ([docs/demo-script.md](docs/demo-script.md)) | 🟡 ลองจริงแล้วผ่าน (Build #11) ต้องซ้อมพูด |
| (10 pts) | Architecture diagram clear | 3 | **Phase 11** ([README.md](README.md#L26)) | ✅ Mermaid ใน README |
|  | Q&A team answers | 2 | **Phase 11** ([docs/demo-script.md §3](docs/demo-script.md)) | 🟡 Q&A doc พร้อม ต้องอ่าน |

**สรุปคะแนนที่ได้ตอนนี้ (มีหลักฐาน ✅):** ~95 pts (จาก 110 — 100 base + 10 bonus)
- Phase 1 Git/App/README: 10 ✅ ครบ (branching + protection 3, code 5, README 2)
- Phase 2 Jenkins + Docker: 25 ✅ ครบ (Jenkinsfile run 10, webhook 5, push 10)
- Phase 3 Terraform + Ansible: 15 ✅ ครบ
- Phase 4 K8s: 25 ✅ ครบ
- Phase 5 Monitoring: 15 ✅ ครบ
- Phase 11 Bonus: 5/10 (Architecture diagram 3 ✅, ขาด live demo 5 + Q&A 2 ที่ต้องทำหน้าห้อง)

**คะแนนที่ต้องทำตอน present:** 5 pts (live demo) + 2 pts (Q&A) = 7 pts

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
- `docs/docker.md` ✅ (อธิบายบทบาทของ Docker ในโปรเจค)
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
| สร้าง branch `dev` + push | ✅ | fast-forward จาก main แล้ว push (2026-05-11 15:40) — `dev` track `origin/dev` |
| Protected branches (main, dev) | ✅ | classic branch protection — require PR before merging (rule id main=76780666, dev=76780721) |
| PR merge tested | ✅ | PR `e2e-test-version-bump → main` (commit 7a48736) — merged สำเร็จ และ webhook fire ทันที |

---

## ✅ Phase 4 — Docker (เสร็จแล้ว)

| ขั้นตอน | สถานะ | คำสั่ง / หมายเหตุ |
|--------|------|--------|
| มี Dockerfile | ✅ | `app/Dockerfile` |
| Build image | ✅ | local 201 MB / compressed 46.3 MB (python:3.11-slim) |
| Run container | ✅ | container `aradin-test` ขึ้น healthy ภายใน 30s |
| `/health` ตอบ 200 | ✅ | `{"status":"ok"}` |
| `/convert` length 1500 m → km | ✅ | result `1.5` |
| `/convert` temp 100 °C → °F | ✅ | result `212.0` |
| `/metrics` มี flask histogram | ✅ | `flask_http_request_duration_seconds_bucket` |
| HEALTHCHECK ใน Dockerfile | ✅ | report `(healthy)` ใน `docker ps` |
| Push to Docker Hub | ✅ | https://hub.docker.com/r/aphikap/aradin-converter (tags `latest`, `1`) |
| ไฟล์ config ใช้ image ใหม่ | ✅ | แก้แล้วใน [Jenkinsfile:5](Jenkinsfile#L5), [k8s/deployment.yaml:29](k8s/deployment.yaml#L29), [ansible/playbook.yml:9](ansible/playbook.yml#L9) |

**บันทึก gotcha:** payload ของ `/convert` ใช้ key `from` / `to` (ไม่ใช่ `from_unit` / `to_unit`) — ดู [app/app.py:48-51](app/app.py#L48-L51)

---

## ✅ Phase 5 — Jenkins CI/CD (100% — Build #10 manual + Build #11 webhook-triggered ผ่านทั้ง 6/6 stages)

> **อ่าน:** [docs/jenkins-setup.md](docs/jenkins-setup.md) (197 บรรทัด) — step-by-step setup guide
> **ไฟล์ helper:** [.local/jenkins-job-config.xml](.local/jenkins-job-config.xml) — job config XML พร้อม import, [.local/jenkins-kubeconfig](.local/jenkins-kubeconfig) — kubeconfig สำหรับ Jenkins ใช้คุยกับ kind

### 5.1 ติดตั้ง Jenkins
| ขั้นตอน | สถานะ |
|--------|------|
| ติดตั้ง Jenkins (≥ 2.4xx) | ✅ | docker container `aradin-jenkins` รันบน port 8080 (skip setup wizard) |
| Mount docker.sock + kubeconfig | ✅ | bind mount `/var/run/docker.sock` + `.local/jenkins-kubeconfig:/var/jenkins_home/.kube/config` |
| เปิดที่ `http://localhost:8080` | ✅ | HTTP 403 (auth ทำงาน — ต้อง login) |

### 5.2 ติดตั้ง Plugins
| Plugin | สถานะ |
|--------|------|
| Git, workflow-aggregator, docker-workflow, github, credentials-binding, pipeline-stage-view, github-branch-source, plain-credentials, timestamper, configuration-as-code | ✅ 77 plugins enabled (pre-installed ใน custom Jenkins image) |

### 5.3 Credentials
| Credential | สถานะ |
|-----------|------|
| `dockerhub-credentials` (username + Docker Hub PAT) | ✅ เพิ่มผ่าน Jenkins Script Console API |

### 5.4 Pipeline Job
| ขั้นตอน | สถานะ |
|--------|------|
| สร้าง Pipeline job ใหม่ | ✅ สร้างจาก init.groovy ตอน Jenkins boot |
| ชี้ไปที่ repo `https://github.com/Aphikap/Aradin-Unit` | ✅ |
| ตั้ง Branch Specifier `*/main` | ✅ (แก้จาก `*/dev` ผ่าน config.xml POST) |

### 5.5 GitHub Webhook
| ขั้นตอน | สถานะ |
|--------|------|
| Cloudflare Tunnel ออก internet | ✅ `https://capture-site-had-quotations.trycloudflare.com` (cloudflared `--protocol http2`) |
| Payload URL: `https://capture-site-had-quotations.trycloudflare.com/github-webhook/` | ✅ |
| Content type: `application/json` | ✅ |
| Trigger: Just the push event | ✅ |
| First delivery | ✅ "Last delivery was successful" (ping event) |

### 5.6 Pipeline Stages (Build #11 — webhook-triggered)
| Stage | สถานะ | Duration | สิ่งที่ทำ |
|-------|------|---------|------|
| Checkout | ✅ | 0.7s | `checkout scm` — refs/remotes/origin/main |
| Build | ✅ | 2.0s | `python -m venv .venv && pip install -r requirements.txt` |
| Test | ✅ | 0.3s | `pytest -v` (12 tests passed) |
| Docker Build | ✅ | 17.4s | `docker build` พร้อม tag `:11` + `:latest` |
| Push to Hub | ✅ | 16.4s | `docker login` + `docker push :11 :latest` (ใช้ credential `dockerhub-credentials`) |
| **Deploy** | ✅ | 41.2s | **รวม Terraform + Ansible + kubectl**:<br>1. `terraform init` + `terraform state list \| grep -q kubernetes_namespace.aradin \|\| terraform import` + `terraform apply -auto-approve` (idempotent — 0 changes)<br>2. `ansible-galaxy collection install community.docker` + `pip3 install docker requests` + `ansible-playbook --extra-vars skip_monitoring=true` (5/5 tasks ผ่าน)<br>3. `kubectl apply -f k8s/` + `kubectl set image ...=aphikap/aradin-converter:11` + `kubectl rollout status --timeout=120s` |

**Total pipeline time:** ~78s (Build #10) / ~78s (Build #11)

> ✅ **Rubric Phase 2 ข้อ "Jenkinsfile 6 stages (10 pts)"** — verified ด้วย Build #10 + #11<br>
> ✅ **Rubric Phase 2 ข้อ "Webhook triggers pipeline (5 pts)"** — Build #11 console log "Started by GitHub push by Aphikap"<br>
> ✅ **Rubric Phase 3 ข้อ "Both integrated in Deploy stage (3 pts)"** — Deploy stage รัน Terraform + Ansible + kubectl ครบ

### 5.7 ปัญหาที่เจอ + วิธีแก้ระหว่างรัน 5 builds
| Build | Failure stage | สาเหตุ | Fix |
|-------|---------------|--------|-----|
| #1–#3 | Push to Hub | ขาด credential `dockerhub-credentials` | เพิ่มผ่าน Jenkins Script Console |
| #4 | Deploy | `terraform apply` พบ namespace มีอยู่แล้ว แต่ state ว่าง | Jenkinsfile: เพิ่ม `terraform import \|\| true` ก่อน apply |
| #5 | Deploy | backslash continuation ใน groovy `'''...'''` กิน import line | เขียนใหม่เป็น `if ! terraform state list ...; then import; fi` |
| #6 | Deploy | Jenkins job branch spec ผิด (`*/dev`) | PATCH config.xml ผ่าน REST API → `*/main` |
| #7 | Ansible | `community.docker` collection ติดตั้งเป็น root jenkins user หาไม่เจอ | Jenkinsfile: `ansible-galaxy collection install community.docker` runtime |
| #8 | Ansible | `No module named 'requests'` (docker SDK ขาด) | Jenkinsfile: `pip3 install docker requests` runtime |
| #9 | Ansible | bind-mount `monitoring/prometheus.yml` path ไม่อยู่บน host | เพิ่ม flag `skip_monitoring=true` ใน playbook + ส่งจาก Jenkinsfile (Prom/Grafana ทำงานอยู่นอก Jenkins อยู่แล้ว) |
| **#10** | — | — | ✅ **SUCCESS** (manual trigger) |
| **#11** | — | — | ✅ **SUCCESS** (webhook trigger จาก PR merge) |

---

## ✅ Phase 6 — Terraform (เสร็จแล้ว — รัน native บน WSL Ubuntu)

| ขั้นตอน | สถานะ | คำสั่ง / ผลลัพธ์ |
|--------|------|--------|
| มีไฟล์ครบ | ✅ | `terraform/main.tf, variables.tf, outputs.tf` |
| Terraform CLI ติดตั้ง | ✅ | v1.15.2 (`apt install terraform` ใน WSL Ubuntu 24.04 ผ่าน hashicorp.com repo) |
| `terraform init` | ✅ | hashicorp/kubernetes v2.38.0 provider |
| `terraform plan` | ✅ | `No changes. Your infrastructure matches the configuration.` |
| `terraform apply` | ✅ | `Apply complete! Resources: 0 added, 0 changed, 0 destroyed.` (idempotent) |
| Output `namespace_name` | ✅ | `"aradin"` |
| Verify labels บน namespace | ✅ | `{app: aradin-converter, managed_by: terraform}` |

**สิ่งที่พบระหว่างทำ:**
- kind cluster ใช้ port `127.0.0.1:62569` (random) — WSL2 mirrored networking ทำให้ `localhost:62569` จาก WSL → host loopback ใช้ได้
- ต้อง copy kubeconfig จาก `/mnt/c/Users/Aphi/.kube/config` ไปไว้ใน WSL filesystem (เพราะ NTFS permissions block chown)
- รันเป็น root user ใน WSL เพื่อให้ access `.terraform/` ที่สร้างจาก docker run ก่อนหน้า (อยู่ใน NTFS)

---

## ✅ Phase 7 — Ansible (เสร็จแล้ว — playbook ผ่าน 7/7 tasks)

| ขั้นตอน | สถานะ | คำสั่ง / ผลลัพธ์ |
|--------|------|--------|
| มี inventory + playbook | ✅ | |
| Ansible CLI ติดตั้ง | ✅ | core 2.16.3 + community 9.2.0 (apt ใน WSL Ubuntu) |
| ติดตั้ง collection `community.docker` | ✅ | v5.2.0 (`ansible-galaxy collection install community.docker`) |
| รัน playbook | ✅ | `ok=7 changed=3 unreachable=0 failed=0` |

**Bug ที่พบ + แก้แล้ว:** [ansible/playbook.yml:51,65](ansible/playbook.yml#L51) เดิมใช้ `extra_hosts:` ซึ่ง deprecated ใน community.docker ≥ 3.x — เปลี่ยนเป็น `etc_hosts:` แล้ว

**Tasks ใน playbook ที่รันได้:**
| Task | สถานะ | หมายเหตุ |
|------|------|---------|
| Verify kubectl is on PATH | ✅ | kubectl v1.34.1 |
| Ensure namespace exists | ✅ | |
| Apply namespace | ✅ | `namespace/aradin unchanged` (idempotent) |
| Apply Kubernetes manifests | ✅ | `deployment/service unchanged` |
| Wait for deployment rollout | ✅ | `successfully rolled out` |
| Run Prometheus container | ✅ | container `prometheus` Up port 9090 |
| Run Grafana container | ✅ | container `grafana` Up port 3000 |

**คำสั่งที่ใช้:**
```bash
# จาก WSL Ubuntu (rootful)
cd /mnt/c/Users/Aphi/Downloads/Aradin-Converter
ansible-galaxy collection install community.docker
ansible-playbook -i ansible/inventory ansible/playbook.yml
```

---

## ✅ Phase 8 — Kubernetes (เสร็จแล้ว — รันบน kind cluster)

### 8.1 ติดตั้ง cluster
| Tool | สถานะ | เวอร์ชัน |
|------|------|---------|
| `kubectl` | ✅ | v1.34.1 |
| **kind** (แทน minikube) | ✅ | v0.22.0 |
| Cluster `kind-aradin` ทำงาน | ✅ | k8s v1.29.2, 1 control-plane node Ready |

### 8.2 Apply manifests
| คำสั่ง | สถานะ | ผลลัพธ์ |
|--------|------|--------|
| `kubectl create namespace aradin` | ✅ | `namespace/aradin created` |
| `kubectl apply -f k8s/deployment.yaml` | ✅ | `deployment.apps/aradin-converter created` |
| `kubectl apply -f k8s/service.yaml` | ✅ | `service/aradin-converter-svc created` |
| `kubectl rollout status` | ✅ | `successfully rolled out` ภายใน 40s |

### 8.3 ตรวจสถานะ
| คำสั่ง | สถานะ | ผลลัพธ์ |
|--------|------|--------|
| `kubectl get pods -n aradin` | ✅ | **2 pods Running 1/1** (`aradin-converter-65b968b9b7-kjmqn` + `-lfbjq`) |
| `kubectl get svc -n aradin` | ✅ | NodePort `5000:30080/TCP`, ClusterIP `10.96.151.182` |
| เข้าผ่าน port-forward → `http://localhost:30080` | ✅ | ใช้ `kubectl port-forward svc/aradin-converter-svc 30080:5000` |
| Smoke test 4 endpoints | ✅ | `/health` 200, `/convert` length+temp ถูกต้อง, `/metrics` มี data |

**หมายเหตุ:** kind ไม่ expose NodePort ออก host โดยตรง ใช้ `kubectl port-forward` แทน (effect เหมือนกัน) ถ้าใช้ minikube จะเข้าตรง NodePort ได้

---

## ✅ Phase 9 — Prometheus (เสร็จแล้ว — รันเป็น docker container)

| ขั้นตอน | สถานะ | หมายเหตุ |
|--------|------|---------|
| มีไฟล์ `monitoring/prometheus.yml` | ✅ | scrape interval 15s |
| รัน Prometheus container | ✅ | `prom/prometheus:v2.51.0` ชื่อ `aradin-prom` |
| เปิด UI ที่ `http://localhost:9090` | ✅ | `/-/ready` ตอบ 200 |
| ตรวจ target `aradin-converter` ขึ้น UP | ✅ | scrape `http://host.docker.internal:30080/metrics` สำเร็จ |
| ตรวจ target `prometheus` self-scrape | ✅ | UP |
| Generate traffic + Query `http_requests_total` | ✅ | นับ 130 requests ได้ใน 30s |
| Query `rate(http_requests_total[1m])` | ✅ | คืน 3 series (3 endpoints) |
| Query `histogram_quantile(0.95, ...)` (latency) | ✅ | คืน 1 series |
| Query `up{job="aradin-converter"}` | ✅ | คืน 1 series |

**คำสั่งที่ใช้:**
```bash
docker run -d --name aradin-prom --rm -p 9090:9090 \
  -v "$PWD/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro" \
  prom/prometheus:v2.51.0
```

> Ansible playbook ก็รัน Prometheus เป็น docker container เหมือนกัน (ผ่าน `community.docker.docker_container`)

---

## ✅ Phase 10 — Grafana (เสร็จแล้ว — auto-provision ผ่าน API)

| ขั้นตอน | สถานะ | หมายเหตุ |
|--------|------|---------|
| มีไฟล์ `monitoring/grafana-dashboard.json` | ✅ | 4 panels |
| รัน Grafana container | ✅ | `grafana/grafana:10.4.2` ชื่อ `aradin-grafana` |
| เปิด `http://localhost:3000` | ✅ | `/api/health` ตอบ `database: ok` |
| Login admin/admin | ✅ | (anonymous access ก็เปิดด้วย `GF_AUTH_ANONYMOUS_ENABLED=true`) |
| เพิ่ม Data source: Prometheus → `http://host.docker.internal:9090` | ✅ | provision ผ่าน `POST /api/datasources` (uid `prometheus`) |
| Import dashboard | ✅ | provision ผ่าน `POST /api/dashboards/db` (uid `aradin-converter`) |
| **4 panels ทำงานได้:** | | |
| • Request Rate: `rate(http_requests_total[1m])` | ✅ | 3 series |
| • Error Rate (5xx): `rate(http_requests_total{status=~"5.."}[1m])` | ✅ | empty (= healthy ไม่มี 5xx) |
| • Latency p95: `histogram_quantile(0.95, ...)` | ✅ | 1 series |
| • Pod Health: `up{job="aradin-converter"}` | ✅ | 1 series |

**URL ของ dashboard:** http://localhost:3000/d/aradin-converter/aradin-converter

**คำสั่งที่ใช้ (ทั้งหมดทำผ่าน API ไม่ต้องคลิกใน UI):**
```bash
# Start Grafana
docker run -d --name aradin-grafana --rm -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  -e GF_AUTH_ANONYMOUS_ENABLED=true \
  grafana/grafana:10.4.2

# Provision Prometheus datasource
curl -X POST http://admin:admin@localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d '{"name":"Prometheus","type":"prometheus","uid":"prometheus","url":"http://host.docker.internal:9090","access":"proxy","isDefault":true}'

# Import dashboard
python3 -c "import json; d=json.load(open('monitoring/grafana-dashboard.json')); print(json.dumps({'dashboard': d, 'overwrite': True}))" \
  | curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
    -H "Content-Type: application/json" -d @-
```

---

## 🟡 Phase 11 — Presentation & Demo Prep (Bonus 10 pts — 5/10 done)

> เกณฑ์นี้วัดวันที่ present สด ต้องเตรียมล่วงหน้า ไม่ใช่ทำตอน demo

### 11.1 Live Demo: `git push → pods Running` (5 pts)

**สิ่งที่ต้องเตรียมก่อนวัน present:**

| รายการ | สถานะ | หมายเหตุ |
|--------|------|---------|
| Jenkins ออนไลน์ + login ได้ | ✅ | http://localhost:8080 admin/admin |
| Cloudflare Tunnel ต่อ Jenkins ออก internet | ✅ | `https://capture-site-had-quotations.trycloudflare.com` (cloudflared HTTP2) |
| GitHub webhook ใช้งานได้ (เห็น Recent Delivery 200 OK) | ✅ | "Last delivery was successful" |
| kind cluster `aradin` รัน | ✅ | `kind-aradin` cluster, 1 control-plane Ready |
| Prometheus + Grafana รันอยู่ + dashboard import แล้ว | ✅ | `aradin-prom` :9090, `aradin-grafana` :3000 |
| End-to-end ผ่านของจริง 1 รอบ | ✅ | Build #11 PR merge → webhook → 6/6 stages → tag `:11` Docker Hub |
| ซ้อม flow เต็ม 2-3 รอบ (จับเวลา ≤ 5 นาที) | ❌ | สำคัญที่สุด — ทำหน้าวัน present |
| Backup video record ของ flow ทั้งหมด | ❌ | เผื่อ live fail (มี Build #11 console log + GitHub PR เป็นหลักฐาน backup) |

**สคริปต์ demo (เปิด tab ตามลำดับ):**

| # | หน้าจอ | คาดหวัง |
|---|--------|---------|
| 1 | Terminal: `git commit -m "demo" && git push` | push สำเร็จ |
| 2 | GitHub → Settings → Webhooks → Recent Deliveries | webhook POST 200 OK |
| 3 | Jenkins UI → job page | build #N เริ่ม + 6 stages ผ่านทีละขั้น |
| 4 | Docker Hub → tags page | tag ใหม่ขึ้น (timestamp ล่าสุด) |
| 5 | Terminal: `kubectl get pods -n aradin -w` | 2 pods ใหม่ Running 1/1 |
| 6 | Browser: `http://<minikube-ip>:30080` | UI ใหม่ใช้งานได้ |
| 7 | Browser: Grafana dashboard | 4 panels มีข้อมูลเรียลไทม์ |

### 11.2 Architecture Diagram (3 pts) ✅

| ตัวเลือก | สถานะ |
|---------|------|
| (A) Slide ใน PowerPoint/Google Slides | ❌ |
| **(B) Mermaid diagram ใน [README.md](README.md#L26)** | ✅ **ใช้แล้ว** — render บน GitHub อัตโนมัติ + มี ASCII fallback |
| (C) ไฟล์ PNG/drawio ใน `docs/` | ❌ |
| (D) วาดสดบนกระดาน | ❌ |

**ที่ครอบคลุมในภาพ:**
- ✅ กล่อง: Developer, GitHub, Jenkins, Docker Hub, Terraform, Ansible, K8s Cluster (Pods + Service), Prometheus, Grafana
- ✅ ลูกศร: `git push`, `webhook`, `build & push`, `Deploy stage → TF + Ansible`, `pull image`, `scrape /metrics`, `query`
- ✅ ระบุ port: NodePort 30080, Prom 9090, Grafana 3000
- ✅ Color-coded ตามประเภท (source/CI/registry/IaC/monitoring)

**ตอน present ให้พูดประมาณนี้ (30 วินาที):**
> "Developer push code ขึ้น GitHub — GitHub ส่ง webhook ไป Jenkins — Jenkins build + push image ขึ้น Docker Hub แล้ว Deploy stage จะเรียก Terraform สร้าง namespace กับ Ansible apply manifests และ start monitoring stack — Kubernetes ดึง image จาก Docker Hub มารัน 2 pods หลัง Service NodePort 30080 — ส่วน Prometheus scrape /metrics ทุก 15 วินาทีแล้ว Grafana แสดงเป็น 4 panels"

### 11.3 Q&A Prep (2 pts)

ใครรับคำถามเรื่องอะไร (ตาม [README ตารางสมาชิก](README.md)):

| สมาชิก | คำถามที่อาจโดน |
|--------|---------------|
| B6626259 ณภัทร (Git/App) | ทำไมเลือก Flask? unit test cover อะไรบ้าง? branching strategy ใช้แบบไหน? |
| B6615994 ธนภัทร (Jenkins/Docker) | Jenkinsfile แต่ละ stage ทำอะไร? ถ้า stage Test fail จะเกิดอะไร? ทำไมต้อง Docker Hub credential? |
| B6628611 อภิชาติ (Terraform/Ansible) | ทำไม Terraform กับ Ansible ทำงานต่างกัน? idempotent คืออะไร? ถ้า apply ซ้ำ 2 ครั้งเกิดอะไร? |
| B6628857 อาระดิน (K8s/Monitoring) | ทำไมต้อง 2 replicas? NodePort vs LoadBalancer? Prometheus pull vs push? panel แต่ละอันอ่านอะไร? |

**คำถามยอดฮิตที่ต้องตอบได้:**
- "ถ้า push code แล้ว test fail จะเกิดอะไร?" → Jenkins stop ที่ stage Test, Docker ไม่ build, K8s ไม่ deploy
- "rollback ยังไง?" → `kubectl set image deployment/aradin-converter aradin-converter=aphikap/aradin-converter:<old-tag>`
- "ทำไมต้องใช้ทั้ง Terraform และ Ansible?" → TF จัดการ infra (namespace), Ansible จัดการ config + apps (Prom/Grafana) — แยกหน้าที่ชัดเจน
- "Grafana panel ดูยังไงว่า healthy?" → Pod Health ต้องเป็น 1, Error Rate ≤ 1%, p95 latency < 200ms

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

### I. สร้าง dev branch + Branch Protection (Rubric Phase 1 ข้อ 1, 3 pts)
```bash
git checkout -b dev
git push -u origin dev
```
**Branch protection (ทำใน GitHub UI 👤):**
- Settings → Branches → Add rule → pattern `main`
- ✓ Require pull request before merging
- ✓ Require status checks (เลือก Jenkins build)
- ทำซ้ำสำหรับ `dev` (เลือกแค่ require PR)

### J. เตรียม Demo + Architecture Diagram (Bonus 10 pts)
1. **ซ้อม live demo** ครบ flow `git push → pods Running` อย่างน้อย 2 รอบ จับเวลา
2. **บันทึกวิดีโอ backup** ของ flow ทั้งหมด (เผื่อ live fail)
3. **วาด architecture diagram** เลือก 1 รูปแบบ:
   - แนะนำ: เพิ่ม Mermaid block ใน [README.md](README.md) (render บน GitHub อัตโนมัติ)
   - หรือ slide ใน PowerPoint/Google Slides
4. **แบ่งหน้าที่ Q&A** ตาม Phase 11.3 ในไฟล์นี้

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

- [x] `git push` → PR merge → Jenkins รันอัตโนมัติ ✅ (Build #11 "Started by GitHub push by Aphikap")
- [x] Pipeline ผ่านทั้ง 6 stages โดยไม่ต้องแก้ ✅ (Build #10 + #11 ทั้งคู่ SUCCESS 6/6)
- [x] Image ขึ้น Docker Hub `aphikap/aradin-converter:<build_number>` ✅ (tags `:1`..`:11`)
- [x] `kubectl get pods -n aradin` แสดง 2 pods Running 1/1 ✅ (kind cluster + Jenkins rolling update)
- [x] เปิด `http://localhost:30080` แล้วแปลงหน่วยได้ ✅
- [x] Prometheus UI (`:9090`) target `aradin-converter` แสดง UP ✅
- [x] Grafana dashboard (`:3000`) แสดง 4 panels มีข้อมูล ✅
- [x] Branch `dev` push ขึ้น GitHub แล้ว ✅
- [x] Branch protection (main, dev) ตั้งใน GitHub แล้ว ✅ (classic rule, require PR)
- [x] GitHub webhook + tunnel ทำงานแล้ว ✅
- [x] Architecture diagram พร้อม — Mermaid ใน [README.md](README.md#L26) ✅
- [ ] ซ้อม live demo เต็ม flow ≥ 2 รอบ (สำคัญที่สุดก่อน present)
- [ ] ส่งงานก่อน deadline ของรายวิชา ENG23 3074

## 🎯 What's left

ทุก phase ที่ Claude ทำให้ได้ **เสร็จ 100%** แล้ว มีเหลือแค่ 2 อย่างที่ user ต้องลงมือเอง:
1. **ซ้อม live demo** (5 pts bonus) — ใช้ flow ใน [docs/demo-script.md](docs/demo-script.md) ยึด Build #11 เป็น reference (PR merge → webhook → pipeline)
2. **ส่งงาน + ตอบคำถาม Q&A** (2 pts bonus) — แบ่งหน้าที่ตาม [§11.3](#113-qa-prep-2-pts)

**Important:** ตัวอ้างอิงสำหรับวันส่งงาน
- Cloudflare tunnel URL ที่ใช้: `https://capture-site-had-quotations.trycloudflare.com` — มีอายุจน cloudflared process หยุด (รันด้วย `--protocol http2` เพราะ network block QUIC) ถ้า restart Jenkins/PC ต้อง start tunnel ใหม่ + update webhook URL ใน GitHub
- Docker Hub PAT ที่ใช้สร้าง credential `dockerhub-credentials`: leak ใน screenshot ตอนสร้าง — **ควร revoke ทิ้งหลัง present เสร็จ** ที่ https://app.docker.com/accounts/aphikap/settings/personal-access-tokens
- ไฟล์ที่แก้ระหว่าง debug Jenkins build 5 รอบ commit ใน main branch แล้ว (fc129d7 → 823c548 → 84876d7 → 72beb08 → 95e6745 → PR-merged 7a48736)

---

## 📞 ปัญหาที่อาจพบ (ดูเพิ่มใน README หัวข้อ Troubleshooting)

- **Pod stuck `Pending`** → `kubectl describe pod <name> -n aradin` ดู Events
- **Jenkins Docker Build fail** → `sudo usermod -aG docker jenkins` แล้ว restart
- **Prometheus target DOWN** → ตรวจว่า `host.docker.internal` resolve ได้ใน Prometheus container
- **Grafana panel ว่างเปล่า** → ตรวจ Data source UID ตรงกับใน JSON (`prometheus`)
