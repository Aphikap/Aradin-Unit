# 🐳 Docker ในโปรเจค Aradin Converter

> เอกสารอธิบายว่า Docker คืออะไร ใช้ทำอะไรในโปรเจคนี้ ถ้าไม่มีจะเกิดอะไรขึ้น และจำเป็นต้องใช้ไหม

---

## 1. Docker คืออะไร (สั้นๆ)

**Docker** คือเครื่องมือที่จับโปรแกรม + dependencies + OS-level config มาห่อรวมเป็น "**กล่อง**" เดียว เรียกว่า **container** กล่องนี้รันที่ไหนก็ได้ที่มี Docker ติดอยู่ — โดย "ผลลัพธ์เหมือนกันทุกเครื่อง"

| คำศัพท์ | ความหมาย | เปรียบเทียบ |
|--------|---------|-------------|
| **Image** | template ที่ build ไว้แล้ว | ไฟล์ `.iso` ของ OS |
| **Container** | image ที่ถูกรันขึ้นมาจริง | คอมที่ install OS แล้วเปิดใช้ |
| **Dockerfile** | สูตรสำหรับ build image | recipe ทำกับข้าว |
| **Registry / Hub** | ที่เก็บ image ออนไลน์ | GitHub แต่เก็บ container image |

---

## 2. Docker ทำหน้าที่อะไรในโปรเจคนี้

ดู Architecture ใน [README.md](../README.md):

```
GitHub ──webhook──▶ Jenkins ──build──▶ Docker Image ──push──▶ Docker Hub
                                                                  │
                                                                  ▼ pull
                                                           Kubernetes Pods
```

Docker ในโปรเจคนี้ทำ **3 หน้าที่**:

### 2.1 Package แอปให้พกพาได้
- Flask + Python 3.11 + dependencies (flask, prometheus-client, ฯลฯ) ถูกห่อใน image เดียว
- ใครก็ตามที่ `docker pull aphikap/aradin-converter:latest` แล้วรันได้ทันที โดยไม่ต้องลง Python หรือ pip install

### 2.2 ส่งต่อระหว่าง Jenkins → Docker Hub → Kubernetes
- Jenkins build image → push ขึ้น Docker Hub
- Kubernetes ดึง image จาก Hub มา deploy เป็น Pod
- ถ้าไม่มี image กลาง ทุกเครื่องต้อง build เองทุกครั้ง

### 2.3 ทำให้ environment ตรงกันทุกที่
- เครื่อง dev / Jenkins / production cluster รัน image **ตัวเดียวกันเป๊ะ**
- หมดปัญหา "ที่เครื่องผมรันได้นะ" (works-on-my-machine)

---

## 3. ไฟล์ที่เกี่ยวข้องในโปรเจคนี้

| ไฟล์ | หน้าที่ |
|------|---------|
| [app/Dockerfile](../app/Dockerfile) | สูตร build image (FROM python:3.11-slim, install deps, COPY code, run app) |
| [Jenkinsfile](../Jenkinsfile) | stage `Docker Build` + `Push to Hub` ใช้ Docker CLI |
| [k8s/deployment.yaml](../k8s/deployment.yaml) | ระบุ `image: aphikap/aradin-converter:latest` ให้ K8s ดึงจาก Hub |
| [ansible/playbook.yml](../ansible/playbook.yml) | รัน Prometheus + Grafana ผ่าน docker container ด้วย collection `community.docker` |

---

## 4. ถ้าไม่มี Docker จะเกิดอะไรขึ้น

### 4.1 ทุกเครื่องต้องลง Python + dependencies เอง
ทุกครั้งที่ deploy / Jenkins build / สมาชิกทีมคนใหม่เข้ามา ต้อง:
```bash
sudo apt install python3.11
pip install -r requirements.txt
# pray that versions match
```
**ปัญหา:** ถ้าเครื่อง production มี Python 3.10 แต่ dev ใช้ 3.11 — bug ที่หาไม่เจอจนระเบิดบน prod

### 4.2 Kubernetes deploy ไม่ได้
K8s รัน workload ในรูปแบบ **container เท่านั้น** (Pod = ห่อรอบ container) — ไม่มี Docker image = ไม่มี Pod
> _เทคนิค: K8s รุ่นใหม่ใช้ containerd แทน Docker engine ได้ก็จริง แต่ "image format" ยังเป็น OCI/Docker เหมือนเดิม_

### 4.3 Jenkins pipeline ขาด 2 stage
Pipeline ใน [Jenkinsfile](../Jenkinsfile) มี 6 stages — ถ้าไม่มี Docker:
- ❌ stage `Docker Build` — build ไม่ได้
- ❌ stage `Push to Hub` — ไม่มีอะไรไป push
- ⚠️ stage `Deploy` — `kubectl set image` หา image ไม่เจอ pipeline ล้ม

### 4.4 Ansible playbook รัน Prometheus/Grafana ไม่ได้
[ansible/playbook.yml:40-65](../ansible/playbook.yml#L40-L65) ใช้ `community.docker.docker_container` — ไม่มี Docker = task fail

### 4.5 หมดความสามารถ "rollback ทันที"
Docker Hub เก็บ image แต่ละ build (tag `1`, `2`, `3`, ...) — ถ้า build ใหม่พัง สั่ง:
```bash
kubectl set image deployment/aradin-converter aradin-converter=aphikap/aradin-converter:1
```
แล้ว rollback กลับไป build เก่าได้ใน 10 วินาที

---

## 5. จำเป็นต้องใช้ไหม

### ✅ จำเป็น **อย่างยิ่ง** สำหรับโปรเจคนี้ เพราะ:

| เหตุผล | รายละเอียด |
|--------|-----------|
| 1. Architecture บังคับ | README ระบุ flow `Docker Build → Docker Hub → Kubernetes` ชัดเจน |
| 2. Kubernetes บังคับ | K8s ทำงานกับ container image เท่านั้น |
| 3. Jenkins pipeline ออกแบบรอบ Docker | 2 ใน 6 stages เป็น Docker โดยตรง |
| 4. คะแนนรายวิชา | ENG23 3074 (DevOps) วัด end-to-end pipeline — ขาด Docker = ขาด core ของวิชา |

### ❌ ทางเลือกอื่นที่ "พอทำได้" แต่ไม่แนะนำ:

| ทางเลือก | ข้อจำกัด |
|---------|----------|
| รัน Flask ตรงๆ บนเครื่อง prod | ไม่มี isolation, dependency conflict, scale ไม่ได้ |
| ใช้ Podman แทน | API คล้าย Docker แต่ Jenkins pipeline ต้องเขียนใหม่ + Docker Hub login flow ต่างกัน |
| ใช้ Vagrant + VM | image หนัก GB+, deploy ช้า, ไม่เข้ากับ K8s |

> 💡 **สรุป:** ในวิชา DevOps ปัจจุบัน Docker คือ "มาตรฐานอุตสาหกรรม" — ไม่ใช้ = ทวนกระแส และเชื่อมกับ tool อื่น (K8s, Jenkins, Ansible) ยากขึ้นมาก

---

## 6. คำสั่ง Docker ที่ใช้บ่อยในโปรเจคนี้

### 6.1 Build & Run บนเครื่องตัวเอง
```bash
# Build image
docker build -t aphikap/aradin-converter:latest ./app

# รัน container
docker run -d --name aradin-test -p 5000:5000 aphikap/aradin-converter:latest

# ดู status
docker ps

# ดู log
docker logs aradin-test

# หยุด + ลบ
docker stop aradin-test && docker rm aradin-test
```

### 6.2 Push ขึ้น Docker Hub
```bash
docker login                                          # ใส่ user/password ครั้งแรก
docker tag <local-image> aphikap/aradin-converter:1   # tag ตาม build number
docker push aphikap/aradin-converter:1
docker push aphikap/aradin-converter:latest
```

### 6.3 ดึง image กลับมารันที่เครื่องอื่น
```bash
docker pull aphikap/aradin-converter:latest
docker run -p 5000:5000 aphikap/aradin-converter:latest
```

### 6.4 Cleanup (เปลือง disk)
```bash
docker image prune -f      # ลบ image ที่ไม่ได้ใช้
docker system prune -a     # ⚠️ ลบหมดทุกอย่างที่ไม่ active
```

---

## 7. Docker Hub กับโปรเจคนี้

- **Repository:** https://hub.docker.com/r/aphikap/aradin-converter
- **Tags ปัจจุบัน:**
  - `latest` — build ล่าสุด
  - `1` — build แรก (Jenkins จะใช้ `${BUILD_NUMBER}` เพิ่มทีละ 1: `2`, `3`, ...)
- **Visibility:** public — ใครก็ pull ได้โดยไม่ต้อง login
- **ใช้ใน:**
  - [k8s/deployment.yaml:29](../k8s/deployment.yaml#L29) — K8s ดึงตอนสร้าง Pod
  - [Jenkinsfile:60-61](../Jenkinsfile#L60-L61) — Jenkins push หลัง build เสร็จ

---

## 8. Troubleshooting Docker

| อาการ | สาเหตุ / วิธีแก้ |
|------|----------------|
| `docker: command not found` | ยังไม่ได้ติดตั้ง Docker Desktop → https://www.docker.com/products/docker-desktop |
| `Cannot connect to the Docker daemon` | Docker Desktop ยังไม่เปิด — เปิดแอป Docker Desktop ก่อน |
| `denied: requested access to the resource is denied` ตอน push | tag ไม่ตรงกับ Hub username (case-sensitive) หรือยังไม่ `docker login` |
| Container ขึ้น แต่เข้า `localhost:5000` ไม่ได้ | ลืม `-p 5000:5000` ตอน `docker run` |
| Container ตาย restart loop | ดู `docker logs <container>` หา error — มักเป็น dependency ขาดใน Dockerfile |
| Build ช้า / ใช้ network เยอะ | layer caching พัง — ตรวจว่า `COPY requirements.txt` มาก่อน `COPY . .` ใน Dockerfile |

---

## 📚 อ่านเพิ่ม

- [Docker Official Docs](https://docs.docker.com/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Hub](https://hub.docker.com/)
- [PROGRESS.md — Phase 4](../PROGRESS.md) — สถานะ Docker ในโปรเจค
