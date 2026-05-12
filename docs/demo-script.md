# 🎬 Demo Script + Q&A Prep

> Script สำหรับ live demo + รายการคำถามที่อาจารย์น่าจะถาม (Bonus 10 pts)

---

## 0. After Reboot — Start ทุกอย่างก่อน Pre-Check

> ถ้าเพิ่งรีบูตเครื่อง / ปิด Docker Desktop / wake from sleep — ทำส่วนนี้ก่อนทำ §1 Pre-Check
> **ทำไมต้องมี:** 3 containers ของเราตั้ง restart policy เป็น `no` / `on-failure` → ไม่ auto-start หลัง reboot + docker.sock perms reset ทุกครั้ง

```powershell
# 1. รอ Docker Desktop พร้อม (~30-60s หลังรีบูต)
docker info >$null 2>&1; if ($?) { Write-Output "Docker ready" } else { Write-Output "Docker still starting, รออีกซักครู่..." }

# 2. start ทั้ง 3 containers
docker start aradin-control-plane aradin-jenkins aradin-smee

# 3. chmod docker.sock (perms กลับเป็น 660 ทุก Docker Desktop restart — ดู §1.5 อาการ E)
#    ถ้าข้ามขั้นนี้: Docker Build stage ของ Jenkins จะ fail ทันที (permission denied)
docker run --rm -v //var/run/docker.sock:/var/run/docker.sock alpine chmod 666 /var/run/docker.sock

# 4. verify ครบทุกชั้น (ทุกบรรทัดต้องผ่าน)
kubectl get pods -n aradin                                                       # 2/2 Running
Invoke-WebRequest http://localhost:30080 -UseBasicParsing | % StatusCode          # 200
(Invoke-WebRequest http://localhost:8080 -UseBasicParsing).StatusCode             # 200/403 (Jenkins login)
docker logs aradin-smee --tail 3                                                  # ต้องเห็น "Connected"
```

### ทำให้ครั้งหน้าไม่ต้อง start เอง (one-time, recommend)

```powershell
# ตั้ง restart policy ครั้งเดียว — ครั้งต่อๆ ไปรีบูตแล้ว 3 containers ขึ้นเองหมด
# (ยังต้อง chmod docker.sock อยู่ เพราะ perms reset ที่ระดับ Docker Desktop ไม่ใช่ container)
docker update --restart unless-stopped aradin-control-plane aradin-jenkins aradin-smee
```

### Risk หลังรีบูต ที่อาจเจอ (rare, มี recovery ใน §1.5)

| อาการ | แก้ที่ §1.5 |
|---|---|
| `docker port aradin-control-plane` ไม่ขึ้น 30080 / 6443 | อาการ B (recreate kind ด้วย `kind-config.yaml`) |
| Jenkins ได้ bridge IP ใหม่ ≠ 172.17.0.4 → smee forward ผิด | recreate smee ด้วย `--target` ใหม่ |
| Jenkins Deploy stage fail หลัง recreate kind | อาการ D (regen `.local/jenkins-kubeconfig` + insecure-skip-tls-verify) |

---

## 1. Pre-Demo Checklist (ก่อนเข้าห้อง 30 นาที)

> **กฎเหล็ก:** ถ้าข้อใดข้อหนึ่ง fail → **อย่าเริ่ม demo สด** ใช้ backup video แทน (§6)
> ทุก command ในส่วนนี้เป็น "ตรวจระบบ" ไม่ใช่ part demo — รันใน PowerShell ส่วนตัว ก่อนเข้าห้อง

```powershell
# === 1. ตรวจ kind cluster (K8s ของเรา) ===
# คืออะไร: สั่ง kubectl คุยกับ cluster ชื่อ "kind-aradin" ขอ list nodes
# ทำไมต้องเช็ค: ถ้า cluster ดับ → ไม่มี pod → demo ไม่ได้
kubectl --context kind-aradin get nodes
# คาดหวัง: aradin-control-plane Ready
# ถ้าพัง ("connection refused"): start ใหม่ → kind create cluster --name aradin

# === 2. ตรวจ pods ใน namespace aradin ===
# คืออะไร: ดู pod ทั้งหมดใน namespace "aradin" (-n = namespace flag)
# ทำไมต้องเช็ค: ต้องมี 2 pods Running 1/1 ก่อน demo เริ่ม
kubectl get pods -n aradin
# คาดหวัง: 2 pods Running 1/1 (ชื่อขึ้นต้น aradin-converter-XXX)

# === 3. Port-forward (สำคัญ! ต้องเปิด terminal แยกทิ้งไว้ตลอด demo) ===
# คืออะไร: เปิดท่อจาก localhost:30080 ของเครื่อง → Service "aradin-converter-svc" port 5000 ใน K8s
# ทำไมต้องมี: kind ไม่ expose NodePort ออกมาตรง ๆ ต้องใช้ port-forward เป็นสะพาน
# ⚠️ ห้ามปิด terminal นี้! ปิดเมื่อไหร่ http://localhost:30080 เข้าไม่ได้ทันที
kubectl port-forward -n aradin svc/aradin-converter-svc 30080:5000

# === 4. ตรวจ Prometheus + Grafana containers ===
# คืออะไร: list docker container ที่ name มี "prom" หรือ "grafana" (substring match)
# หมายเหตุ: ใช้ filter "prom" ไม่ใช่ "prometheus" เพื่อให้ match ได้ทั้ง prometheus, aradin-prom
docker rm -f prometheus

docker run -d --name prometheus --rm -p 9090:9090 -v "${PWD}/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro" prom/prometheus:v2.51.0

docker ps --filter "name=prom" --filter "name=grafana"
# คาดหวัง: ทั้ง 2 ขึ้น Up + Ports 9090 (prom), 3000 (grafana)
# ⚠️ ชื่อ container จริงในเครื่องนี้คือ "prometheus" และ "grafana" (ไม่ใช่ aradin-prom/aradin-grafana)
# ถ้าไม่ขึ้น: docker start prometheus grafana
# ถ้า "No such container": ต้อง start ใหม่จาก scratch ตาม PROGRESS.md Phase 9-10
#   docker run -d --name prometheus --rm -p 9090:9090 `
#     -v "${PWD}/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro" `
#     prom/prometheus:v2.51.0

# === 5. ตรวจ Jenkins ===
docker ps --filter "name=jenkins"
docker start aradin-jenkins
# คืออะไร: ลองเปิด UI Jenkins ที่ port 8080 + login admin/admin
# ทำไมต้องเช็ค: Jenkins ตายเงียบบ่อย (exit code 255) ต้องเห็นหน้า login จริง ๆ
# วิธีตรวจ: เปิด http://localhost:8080 ใน browser
# ถ้าไม่ขึ้น: docker logs aradin-jenkins --tail 50 ดู error → docker start aradin-jenkins

# === 6. Smee webhook relay (สำหรับ webhook) ===
# คืออะไร: smee.io = public webhook relay service — GitHub ส่ง webhook → smee.io → smee-client ในเครื่อง → Jenkins
# ทำไมเลือก smee แทน cloudflared:
#   - URL คงที่ (https://smee.io/ZMFe6XTP7cHqLEHu) ไม่ต้อง update GitHub webhook ทุกครั้งที่ restart
#   - รันเป็น docker container ไม่ต้องเปิด terminal แยกทิ้งไว้
#   - ไม่ต้องสนเรื่อง QUIC / HTTP/2 / protocol block
# Setup ที่ตั้งไว้แล้วในเครื่องนี้:
#   - GitHub webhook URL: https://smee.io/ZMFe6XTP7cHqLEHu (ตั้งครั้งเดียวจบ)
#   - container: aradin-smee (image deltaprojects/smee-client) → forward ไป http://172.17.0.4:8080/github-webhook/
# Start container (ถ้ายังไม่รัน) + ตรวจว่าเชื่อม smee.io ได้:
docker start aradin-smee
docker logs aradin-smee --tail 20
# คาดหวังเห็นบรรทัด: "Connected" หรือ "Forwarding ... to http://172.17.0.4:8080/github-webhook/"
# ⚠️ ถ้า Jenkins container IP เปลี่ยน (เช่นหลัง Docker Desktop restart) → smee จะ forward ไป IP เก่าไม่เจอ
# เช็ค Jenkins IP ปัจจุบัน:
#   docker inspect aradin-jenkins --format '{{.NetworkSettings.IPAddress}}'
# ถ้า IP ไม่ใช่ 172.17.0.4 → ต้อง recreate aradin-smee ด้วย --target ใหม่

# === 7. ทดสอบ webhook ใน GitHub ===
# คืออะไร: ตรวจว่า GitHub ส่ง webhook ถึง Jenkins ได้จริง
# วิธีตรวจ: GitHub → Settings → Webhooks → คลิก webhook → Recent Deliveries
# คาดหวัง: response ล่าสุด 200 OK (สีเขียว)
# ถ้าแดง (404/500/timeout): tunnel ตาย หรือ URL ใน webhook ไม่ตรงกับ tunnel ปัจจุบัน
```

---

## 1.5 Recovery Commands (เมื่อ pre-check fail)

> **เคสจริงที่เคยเจอ (2026-05-12):** Docker Desktop restart ตอนค้าง → kind container "Up" แต่ port mapping `6443/tcp` หาย → kubectl เชื่อมไม่ได้ทุก context + `kind export kubeconfig` ก็ลบ context ทิ้งก่อนใส่ใหม่ไม่สำเร็จ
> ลำดับการแก้: diagnose → แก้ตามอาการ → ถ้าไม่ได้ใช้ backup §6

### Step 1 — Diagnose (รู้ก่อนว่าพังตรงไหน)

```powershell
# คืออะไร: ดู context ที่ kubectl ใช้อยู่ + ลองคุยกับ API server
kubectl config current-context
kubectl cluster-info
# ผลที่บอกได้:
#   "connection refused 127.0.0.1:XXXXX" → cluster ไม่ฟัง port นั้น (หาย/ผิด)
#   "context was not found"                → kubeconfig ไม่มี context นี้แล้ว

# คืออะไร: ดู container ของ kind/jenkins/smee สถานะปัจจุบัน + port mapping
docker ps -a --filter "name=aradin" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# คืออะไร: เช็คว่า kind control-plane มี host port map ไป 6443/tcp ไหม
# ถ้าผลคือ {"6443/tcp":[]} หรือ {"6443/tcp":null} = port mapping หาย → Step 2B
docker inspect aradin-control-plane --format '{{json .NetworkSettings.Ports}}'
```

### Step 2 — แก้ตามอาการ

**อาการ A — kubeconfig point ผิด port (cluster ยังดี, port ใหม่):**
```powershell
# คืออะไร: ให้ kind เขียน kubeconfig ใหม่จาก port ปัจจุบันของ container
kind export kubeconfig --name aradin
kubectl get nodes  # verify เห็น aradin-control-plane Ready
```

**อาการ B — Container "Up" แต่ port mapping หาย (จาก `docker stop/start`):**
```powershell
# ⚠️ kind ไม่มี API แก้ port mapping ของ container ที่รันอยู่ — ต้องลบสร้างใหม่
# ผลข้างเคียง: pods/services/configmaps ใน cluster หายหมด → ต้อง apply manifest ใหม่

# 1. ลบ cluster เก่า
kind delete cluster --name aradin

# 2. สร้างใหม่ (default config — repo นี้ไม่มี kind-config.yaml)
kind create cluster --name aradin

# 3. สร้าง namespace + apply manifests
kubectl create namespace aradin
kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml

# 4. รอ pods พร้อม
kubectl wait --for=condition=ready pod -l app=aradin-converter -n aradin --timeout=120s

# 5. verify
kubectl get pods -n aradin
```

**อาการ C — Jenkins/Smee container Exited (255):**
```powershell
# Exit 255 มัก = killed โดย Docker Desktop restart, start ทับได้เลย
docker start aradin-jenkins aradin-smee
docker ps --filter "name=aradin"
# ถ้ายัง Exited ทันทีหลัง start: ดู error จริง
docker logs aradin-jenkins --tail 50
```

**อาการ D — Jenkins Deploy stage fail ทันที (<100ms) หลัง recreate kind (อาการ B):**
```powershell
# คืออะไร: Jenkins มี kubeconfig ของตัวเองที่ bind-mount เข้า container — ไฟล์อยู่ที่
#   .local/jenkins-kubeconfig (host) → /var/jenkins_home/.kube/config (Jenkins)
# หลัง kind delete + create ใหม่ → API server port เปลี่ยน + CA cert ใหม่
# Jenkins ยังถือ kubeconfig เดิม → kubectl connect ไป port เก่าที่ตายแล้ว → exit ภายใน ms
# อาการบน Jenkins UI: stage "Deploy" สีแดง runtime ~50ms (เร็วเกินกว่าจะเป็น logic error)
# คนละ kubeconfig กับของ user — แก้ kubeconfig user ไม่ช่วย ต้องแก้ไฟล์ Jenkins ต่างหาก

# 1. Diagnose — เทียบ port ที่ Jenkins ถือ vs port จริงของ kind
Select-String -Path .local\jenkins-kubeconfig -Pattern "server:"
docker port aradin-control-plane 6443/tcp
# ถ้าเลข port ไม่ตรง → stale แน่นอน

# 2. Backup ไฟล์เดิมก่อนเขียนทับ
Copy-Item .local\jenkins-kubeconfig .local\jenkins-kubeconfig.bak

# 3. Regenerate — ดึง kubeconfig ใหม่จาก kind + แทน 127.0.0.1 → host.docker.internal
#   (host.docker.internal = ชื่อพิเศษให้ container เข้าถึง host loopback ผ่าน Docker Desktop)
#   ถ้าใช้ 127.0.0.1 ตรง ๆ → จาก inside Jenkins container = ตัวมันเอง ไม่ใช่ host
kind get kubeconfig --name aradin | ForEach-Object { $_ -replace '127\.0\.0\.1', 'host.docker.internal' } | Set-Content -Encoding utf8 .local\jenkins-kubeconfig

# 4. ⚠️ สำคัญ: ตั้ง insecure-skip-tls-verify
#   kind cert ออกให้ hostname "kubernetes/127.0.0.1" ไม่รวม host.docker.internal
#   → TLS handshake fail → Deploy stage ตายภายใน ~2s (เร็วเกินกว่าจะเป็น logic error)
#   วิธีแก้: skip TLS verify (OK สำหรับ local dev, ห้ามทำใน prod)
kubectl --kubeconfig .local\jenkins-kubeconfig config set-cluster kind-aradin --insecure-skip-tls-verify=true
# คำสั่งนี้จะลบ certificate-authority-data + ใส่ insecure-skip-tls-verify: true ในไฟล์ให้อัตโนมัติ
# (จะมี warning เกี่ยวกับ cert ที่หายไป ไม่เป็นไร)

# 5. Verify — ควรเห็น "server: https://host.docker.internal:<new-port>"
Select-String -Path .local\jenkins-kubeconfig -Pattern "server:|insecure"

# 6. ไม่ต้อง restart Jenkins — bind mount อ่านไฟล์ใหม่ทันที
#    trigger build อีกครั้ง (push commit หรือ Build Now) → Deploy stage ควรเขียวแล้ว
```

**อาการ E — Docker Build stage fail (200-400ms) ด้วย "permission denied" บน docker.sock:**
```powershell
# คืออะไร: หลัง Docker Desktop restart socket ถูก reset perms กลับเป็น root:root 660
# Jenkins user (uid 1000) ไม่อยู่ใน root group → อ่าน /var/run/docker.sock ไม่ได้
# (ก่อน restart ครั้งแรก perms อาจเปิดกว่า เลย build เก่าผ่านได้)
# Error ที่เห็นใน console: "permission denied while trying to connect to the docker API at unix:///var/run/docker.sock"
# Side effect ที่ทำให้สับสน: error tar "Can't add file .pytest_cache" เป็นแค่ผลพวงจาก daemon ตัดการเชื่อมต่อ ไม่ใช่สาเหตุ

# 1. Diagnose — เช็ค socket perms ผ่าน throwaway alpine container
docker run --rm -v //var/run/docker.sock:/var/run/docker.sock alpine ls -la /var/run/docker.sock
# ถ้าเห็น srw-rw---- (660) root root → confirm ปัญหา perms
# ถ้าเห็น srw-rw-rw- (666) → permission ดี อาจเป็นปัญหาอื่น

# 2. Quick fix — chmod ผ่าน helper container (alpine รันเป็น root ใน container ของตัวเอง chmod socket ที่ mount เข้ามาได้)
docker run --rm -v //var/run/docker.sock:/var/run/docker.sock alpine chmod 666 /var/run/docker.sock

# 3. Verify
docker run --rm -v //var/run/docker.sock:/var/run/docker.sock alpine ls -la /var/run/docker.sock
# คาดหวัง: srw-rw-rw-

# 4. ไม่ต้อง restart Jenkins — trigger build ใหม่ได้เลย (Docker Build ควรผ่าน)

# ⚠️ chmod 666 ไม่ persist — Docker Desktop restart จะ reset กลับ 660 ทุกครั้ง ต้องรันซ้ำ
# ⚠️ 666 = ใครก็เข้า docker.sock ได้ → root access เครื่อง ห้ามทำบนเครื่อง shared/prod
#    บนเครื่อง dev ส่วนตัวสำหรับ demo OK
# Permanent fix: recreate Jenkins ด้วย --user root หรือ --group-add ตาม GID ของ socket

# chmod socket ให้ทุก user อ่าน/เขียนได้ ผ่าน helper container ที่รันเป็น root
docker run --rm -v //var/run/docker.sock:/var/run/docker.sock alpine chmod 666 /var/run/docker.sock

# verify
docker run --rm -v //var/run/docker.sock:/var/run/docker.sock alpine ls -la /var/run/docker.sock
# คาดหวัง: srw-rw-rw- (666)
```

### Step 3 — Last resort

ถ้า Step 1-2 ไม่ทันก่อนถึงคิว demo → **อย่าฝืน debug ต่อหน้ากรรมการ** ใช้ Backup Plan §6 (video/screenshots) ทันที


docker rm -f aradin-smee
docker run -d --name aradin-smee --restart unless-stopped `
  deltaprojects/smee-client `
  --url https://smee.io/ZMFe6XTP7cHqLEHu `
  --target http://172.17.0.3:8080/github-webhook/
---

## 2. Live Demo Script (~7-10 นาที)

### หน้าจอที่ต้องเปิดไว้ก่อน (เรียงตามลำดับใช้)

| Tab | URL/Window |
|-----|-----------|
| 1 | Terminal — เตรียมพร้อมรัน git commands |
| 2 | VSCode/Editor — เปิด `app/templates/index.html` |
| 3 | https://github.com/Aphikap/Aradin-Unit (Settings → Webhooks) |
| 4 | http://localhost:8080/job/aradin-converter (Jenkins) |
| 5 | https://hub.docker.com/r/aphikap/aradin-converter/tags |
| 6 | http://localhost:30080 (app) |
| 7 | http://localhost:3000/d/aradin-converter (Grafana) |

git add app/templates/index.html
git commit -m "demo: bump h1 to pre-demo final"
git push -u origin demo/v2-marker

### ขั้นตอน + บทพูด

**[0:00] เปิด:**
> "สวัสดีครับ ทีมเราจะ demo Aradin Converter — Web app แปลงหน่วยที่ deploy ด้วย CI/CD pipeline เต็มระบบ"

**[0:30] แสดง architecture:**
- เปิด [README.md](../README.md#L26) Mermaid diagram
> "ระบบเราเริ่มจาก git push — webhook ไป Jenkins — Jenkins build + push image ขึ้น Docker Hub — Deploy stage เรียก Terraform + Ansible — Kubernetes ดึง image มารัน 2 pods — Prometheus scrape /metrics — Grafana แสดงผล"

**[1:30] แสดงสถานะระบบก่อน demo (proof of base state):**
```bash
# คืออะไร: ดู pod ทั้งหมดใน namespace aradin (เหมือน pre-check ข้อ 2)
# จุดประสงค์ตอน demo: โชว์กรรมการเห็นจุดเริ่มต้น "ก่อน push" — 2 pods ของ image tag เก่า
kubectl get pods -n aradin
# เห็น 2 pods Running จาก image tag ปัจจุบัน เช่น :15
```
- เปิด http://localhost:30080 — แสดง UI ทำงาน + แปลง 1500 m → 1.5 km

**[2:30] แก้ code เล็กน้อย (visible change):**
```html
<!-- app/templates/index.html -->
<h1>🚀 Aradin Converter v2 (LIVE DEMO)</h1>
```

**[3:00] Trigger pipeline:** ⭐ moment ขายของ — 3 commands นี้คือพระเอกของ demo
```bash
# 1. add: บอก git ว่าจะ commit ไฟล์นี้ (เพิ่มเข้า staging area)
git add app/templates/index.html

# 2. commit: บันทึก snapshot เป็น commit ใหม่ (-m = message inline)
git commit -m "demo: add v2 marker to homepage"

# 3. push: ส่ง commit ขึ้น GitHub → trigger ทุกอย่างต่อจากนี้อัตโนมัติ
#    ผลทันที: GitHub ส่ง webhook → Cloudflare tunnel → Jenkins → Build #N เริ่ม
git push origin main
```
> "ตอนนี้เราแค่ push code ขึ้น GitHub ที่เหลือ pipeline จะทำเองทั้งหมด ไม่แตะคำสั่งอีกแล้ว"
> 💡 ยกมือออกจากคีย์บอร์ดให้กรรมการเห็นชัด ๆ ว่าไม่ได้แอบทำอะไร

**[3:30] โชว์ webhook trigger:**
- เปิด GitHub → Settings → Webhooks → Recent Deliveries
- เห็น delivery ล่าสุด **200 OK** ตอนนี้

**[3:45] โชว์ Jenkins รัน:**
- เปลี่ยน tab ไป Jenkins
- Stage View — เห็น Build #N เริ่มอัตโนมัติ
- 6 stages ขึ้นทีละขั้น: ✓ Checkout ✓ Build ✓ Test ✓ Docker Build ✓ Push to Hub ✓ Deploy
> "สังเกตว่า stage Test ต้องผ่านก่อน Docker Build — ถ้า test fail pipeline หยุดเลย ไม่ deploy ของพัง"

**[5:30] โชว์ Docker Hub มี tag ใหม่:**
- เปลี่ยน tab ไป Docker Hub
- Refresh — เห็น tag ใหม่ (เช่น `:16`) timestamp ล่าสุด

**[6:00] โชว์ K8s rolling update:**
```bash
# คืออะไร: เหมือน get pods แต่ -w (watch) = real-time update ทุกครั้งที่ state เปลี่ยน
# จุดประสงค์: โชว์ rolling update สด ๆ ว่า "pod ใหม่ขึ้นก่อน → pod เก่าตายตาม → zero downtime"
# กดออก: Ctrl+C
kubectl get pods -n aradin -w
# เห็น pod ใหม่ Pending → ContainerCreating → Running 1/1
# พร้อมกับ pod เก่า Terminating
# RollingUpdate ทำให้ไม่ downtime
```

**[7:00] เปิดเว็บ — เห็น change:**
- Refresh http://localhost:30080
- เห็น "🚀 Aradin Converter v2 (LIVE DEMO)" — code ที่เพิ่ง push ขึ้นจริง

**[7:30] โชว์ Grafana monitoring:**
- เปิด http://localhost:3000/d/aradin-converter
- ขณะแปลงหน่วยบนเว็บ 5-10 ครั้ง
- Refresh dashboard — เห็น 4 panels:
  - Request Rate spike ขึ้น
  - Error Rate = 0 (healthy)
  - Latency p95 < 50ms
  - Pod Health = 1 (UP)

**[9:00] ปิด:**
> "สรุปเราใช้ 6 tools ครบตาม learning objectives: Git → Jenkins → Docker → Kubernetes → Terraform+Ansible → Prometheus+Grafana ขอบคุณครับ"

---

## 3. Q&A — แบ่งความรับผิดชอบ

### B6626259 ณภัทร (Git, App Development)

**Q: ทำไมเลือก Flask?**
> A: Flask เบา ติดตั้งง่าย รัน prometheus-flask-exporter ได้ทันที — เหมาะกับ teaching demo ที่ต้องการเห็น `/metrics` ได้ใน 5 นาที

**Q: Unit tests cover อะไรบ้าง?**
> A: 12 tests ใน [app/test_conversions.py](../app/test_conversions.py) ครอบคลุม length (m, cm, km, mile), weight (kg, g, lb), temperature (C, F, K) + edge cases (negative, zero, decimal)

**Q: Branching strategy เป็นแบบไหน?**
> A: GitFlow แบบเบา — `main` = production, `dev` = staging, `feature/*` = work in progress ดู [README §Branching](../README.md#L294)

**Q: ทำไมไม่ใช้ FastAPI?**
> A: FastAPI ดีกว่าจริง (async, auto OpenAPI) แต่ Flask + `prometheus-flask-exporter` setup เร็วกว่า + ทีมเคยใช้

---

### B6615994 ธนภัทร (Jenkins, Docker)

**Q: Jenkinsfile แต่ละ stage ทำอะไร?**
> A: ดู [Jenkinsfile](../Jenkinsfile):
> 1. **Checkout** — `checkout scm` ดึง code ล่าสุด
> 2. **Build** — สร้าง venv + `pip install -r requirements.txt`
> 3. **Test** — `pytest -v` (ถ้า fail หยุด pipeline)
> 4. **Docker Build** — สร้าง image tag `${BUILD_NUMBER}` + `latest`
> 5. **Push to Hub** — `docker login` + push 2 tags
> 6. **Deploy** — terraform apply + ansible-playbook + kubectl set image

**Q: ถ้า stage Test fail จะเกิดอะไร?**
> A: Pipeline หยุดทันทีที่ stage Test — Docker Build/Push/Deploy ไม่รัน image เก่ายังคงอยู่ทั้ง Docker Hub และ K8s ไม่มีของพังเข้า prod

**Q: ทำไมต้อง Docker Hub credentials?**
> A: `docker push` ต้องการ authentication — เราเก็บ user/PAT ใน Jenkins Credentials Manager (ID `dockerhub-credentials`) ไม่ฮาร์ดโค้ดใน Jenkinsfile — ปลอดภัย

**Q: Image ของเรามีขนาดเท่าไหร่ ทำไมเล็กแบบนี้?**
> A: ~46 MB compressed ใช้ base image `python:3.11-slim` (debian slim) แทน `python:3.11` (full) ตัด build tools ออก + `--no-cache-dir` ตอน pip install

**Q: รัน container เป็น non-root ไหม?**
> A: ใช่ — ใน [app/Dockerfile](../app/Dockerfile) `USER appuser` + healthcheck endpoint `/health` ทุก 30s

---

### B6628611 อภิชาติ (Terraform, Ansible)

**Q: Terraform vs Ansible — ต่างกันยังไง?**
> A:
> - **Terraform** = Infrastructure provisioning (สร้าง resource ที่ยังไม่มี เช่น namespace, network, VM)
> - **Ansible** = Configuration management (config ของ resource ที่มีอยู่แล้ว เช่น apply manifests, deploy containers)
> - ใช้ร่วมกัน: TF สร้าง infra, Ansible deploy app

**Q: ทำไมต้องใช้ทั้งคู่?**
> A: แยกหน้าที่ชัดเจน — TF เปลี่ยน infra นานๆ ครั้ง (declarative state), Ansible deploy app บ่อย (imperative tasks) ถ้าใช้แค่ตัวเดียวจะ overload หน้าที่

**Q: Idempotent คืออะไร?**
> A: รันคำสั่งเดิมหลายครั้งผลลัพธ์เหมือนเดิม — TF: รัน `apply` 10 ครั้งบน state เดียวกัน → `0 changes` Ansible: รัน playbook ซ้ำ → tasks ที่ทำแล้ว = `ok`, ไม่ใช่ `changed`

**Q: ถ้า terraform apply ซ้ำจะเกิดอะไร?**
> A: TF อ่าน current state จาก K8s, diff กับ config — ถ้าตรงกัน `No changes` ถ้าต่าง modify เฉพาะส่วนที่ต่าง — เราเทสแล้วใน [PROGRESS Phase 6](../PROGRESS.md)

**Q: state file เก็บที่ไหน production?**
> A: ตอนนี้ local `.tfstate` — production ควรใช้ S3 backend หรือ Terraform Cloud (มี state locking + history)

**Q: Ansible playbook ทำกี่ tasks?**
> A: 7 tasks ดู [ansible/playbook.yml](../ansible/playbook.yml) — verify kubectl, namespace, apply manifests, wait rollout, run Prom container, run Grafana container

---

### B6628857 อาระดิน (Kubernetes, Monitoring)

**Q: ทำไม 2 replicas?**
> A: High availability — ถ้า pod 1 ตาย pod 2 ยัง serve traffic ได้ Service load-balance round-robin ระหว่าง 2 pods + RollingUpdate ตอน deploy ใหม่ไม่ downtime

**Q: NodePort vs LoadBalancer ต่างกันยังไง?**
> A:
> - **NodePort** — expose service บน fixed port ทุก node (เช่น 30080) — local/dev OK
> - **LoadBalancer** — provision external LB (AWS ELB, GCP LB) — production แต่เสียค่า cloud
> - **ClusterIP** — internal only เข้าจาก pod อื่นได้ ไม่ external
> - เราใช้ NodePort เพราะ demo บน local cluster

**Q: Liveness vs Readiness probe ต่างกันยังไง?**
> A:
> - **Liveness** — pod ตายหรือยัง ถ้า fail → kubectl kill + restart
> - **Readiness** — pod รับ traffic ได้หรือยัง ถ้า fail → Service ถอด pod ออก endpoints (ไม่ส่ง traffic แต่ไม่ kill)
> - เราใช้ทั้งคู่ใน [deployment.yaml:41-56](../k8s/deployment.yaml#L41) ชี้ไปที่ `/health`

**Q: Prometheus pull vs push?**
> A: Pull model — Prometheus ไปดึง `/metrics` จาก target ทุก 15s (ตามที่กำหนดใน [prometheus.yml:2](../monitoring/prometheus.yml#L2)) ข้อดี: simple, central control ของ scrape config ข้อเสีย: target ต้อง reachable

**Q: Panel แต่ละอันอ่านอะไร?**
> A: 4 panels ดู [README §Panels](../README.md#L283):
> - **Request Rate** — `rate(http_requests_total[1m])` request/sec
> - **Error Rate** — `rate(http_requests_total{status=~"5.."}[1m])` 5xx/sec
> - **Latency p95** — `histogram_quantile(0.95, ...)` 95% ของ request เร็วกว่ากี่วินาที
> - **Pod Health** — `up{job="aradin-converter"}` 1 = scrape ผ่าน, 0 = down

**Q: Rolling Update ทำงานยังไง?**
> A: ตั้งใน [deployment.yaml:13-17](../k8s/deployment.yaml#L13) — `maxSurge: 1` สร้าง pod ใหม่ก่อน 1 ตัว `maxUnavailable: 0` ห้าม pod พร้อมใช้น้อยลง — ผลคือสร้างก่อนค่อยลบ ไม่มี downtime

**Q: รอง rollback ยังไง?**
> A:
> ```bash
> # rollout undo = กลับไป revision ก่อนหน้า (ใช้ K8s history)
> kubectl rollout undo deployment/aradin-converter -n aradin
>
> # --to-revision=3 = กลับไป revision หมายเลข 3 โดยเจาะจง
> # ดู history ก่อน: kubectl rollout history deployment/aradin-converter -n aradin
> kubectl rollout undo deployment/aradin-converter -n aradin --to-revision=3
> ```
> หรือ pin tag เก่า:
> ```bash
> # set image = บอก K8s ใช้ image tag นี้แทนตัวปัจจุบัน
> # format: <container_name>=<image>:<tag>
> kubectl set image deployment/aradin-converter \
>   aradin-converter=aphikap/aradin-converter:5 -n aradin
> ```

---

## 4. คำถาม "หนีตาย" — ที่ฟังดูยากแต่ตอบได้

**Q: ทำไมไม่ใช้ Helm?**
> A: โปรเจคขนาดเล็ก — manifests แค่ 2 ไฟล์ ใช้ kubectl ตรงๆ ง่ายกว่า ถ้า scale ใหญ่ ค่อยเปลี่ยนเป็น Helm chart

**Q: ทำไม Prometheus ไม่ scrape pods ผ่าน service discovery?**
> A: ใน production ใช่ — แต่เราต้องการแยก concern เพื่อ demo: Prom รันใน docker ไม่ใช่ใน K8s + scrape NodePort (ง่ายต่อการเข้าใจ flow ของนักศึกษา)

**Q: ถ้า Jenkins crash ระหว่าง Deploy stage จะเกิดอะไร?**
> A: K8s state อาจครึ่งๆกลางๆ — แต่ idempotent: รัน build ใหม่ apply ทับได้เลย state จะ converge

**Q: Image vulnerability scan?**
> A: ยังไม่ได้ทำใน scope นี้ — production จะใช้ Trivy/Snyk ใน Jenkins stage หลัง Docker Build:
> ```groovy
> // Trivy = tool scan ช่องโหว่ใน image (เทียบกับ CVE database)
> // เพิ่ม stage นี้แทรกระหว่าง Docker Build กับ Push to Hub
> stage('Scan') { sh "trivy image ${FULL_IMAGE}:${IMAGE_TAG}" }
> ```

**Q: Secrets management?**
> A: ตอนนี้ใช้ Jenkins Credentials Manager + K8s Secrets — production: HashiCorp Vault + External Secrets Operator

**Q: HPA (Horizontal Pod Autoscaler)?**
> A: ยังไม่ได้เพิ่ม — ใส่ได้ง่ายๆ:
> ```bash
> # autoscale = สร้าง HPA ที่เพิ่ม pod อัตโนมัติเมื่อ CPU สูง
> # logic: ถ้า CPU เฉลี่ย > 70% เพิ่ม pod (ไม่เกิน max=10), idle ลด pod (ไม่ต่ำกว่า min=2)
> kubectl autoscale deployment aradin-converter -n aradin --min=2 --max=10 --cpu-percent=70
> ```

---

## 5. สิ่งที่ต้อง **อย่า** ทำตอน demo

- ❌ อย่าตอบ "ไม่รู้" — ใช้ "ส่วนนี้ผม/หนูไม่ได้รับผิดชอบ ขอส่งต่อให้เพื่อน" แทน
- ❌ อย่ารัน command สด ๆ ที่ไม่เคยซ้อม — risk crash
- ❌ อย่าเปิด terminal ที่มี `git push --force` ในประวัติ (กรรมการจะเสียวแทน)
- ❌ อย่าให้ดู `.env` หรือไฟล์ credentials
- ❌ อย่ารัน `kubectl delete` ระหว่าง demo (อาจ delete ผิด)

---

## 6. Backup Plan (ถ้า demo สด fail)

มี **2 ชั้น fallback**:

**ชั้นที่ 1:** Pre-recorded video ของ flow ทั้งหมด (record ก่อน 1 วัน)
- ใช้ OBS Studio บันทึก screen
- ตัดเป็น clip ละ 30s ต่อ stage

**ชั้นที่ 2:** Screenshots ของแต่ละ component (10 รูป)
- Jenkins Stage View success
- Docker Hub tags list
- `kubectl get pods` Running
- Grafana 4 panels with data
- App UI

---

## 7. Final Checklist 5 นาที ก่อนขึ้น demo

- [ ] Laptop charger เสียบไว้
- [ ] Network ใช้สาย LAN (ถ้าได้) — WiFi อาจหลุด
- [ ] ปิด notification ทั้งหมด (Slack, Line, Discord)
- [ ] Browser tabs ตามลำดับ (Tab 1-7 ใน §2)
- [ ] Zoom level ของ browser ใหญ่พอให้กรรมการอ่านได้ (Ctrl + +)
- [ ] Terminal font ใหญ่ + theme light (ถ้ามี projector แสง)
- [ ] ทุกคนรู้บทตัวเอง (ดู §3)
- [ ] Backup video พร้อม + พอย้ายมือถือเปิดได้

🍀 Good luck!
