# 🔧 Jenkins Setup Guide

> Step-by-step ติดตั้ง Jenkins + Pipeline + Webhook สำหรับโปรเจค Aradin Converter
> ใช้เวลา ~30-45 นาที (ครั้งแรก)

---

## 1. ติดตั้ง Jenkins

### Windows (แนะนำ)
```powershell
# วิธี A: ดาวน์โหลด installer ตรง
# 1. ไปที่ https://www.jenkins.io/download/
# 2. เลือก "LTS" → Windows → ดาวน์โหลด .msi
# 3. รัน installer (ติดตั้ง Java 17 มาให้ด้วย)
# 4. ตั้งให้รันเป็น Windows service บน port 8080

# วิธี B: ถ้ามี chocolatey + admin PowerShell
choco install jenkins-lts -y
```

### Linux/WSL
```bash
sudo apt update
sudo apt install -y openjdk-17-jre
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key \
  | sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" \
  | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt update
sudo apt install -y jenkins
sudo systemctl start jenkins
```

---

## 2. ปลดล็อค Jenkins ครั้งแรก

1. เปิด browser → `http://localhost:8080`
2. หาไฟล์ `initialAdminPassword`:
   - **Windows:** `C:\ProgramData\Jenkins\.jenkins\secrets\initialAdminPassword`
   - **Linux:** `/var/lib/jenkins/secrets/initialAdminPassword`
   ```powershell
   Get-Content "C:\ProgramData\Jenkins\.jenkins\secrets\initialAdminPassword"
   ```
3. Paste password → **Continue**
4. เลือก **Install suggested plugins** (รอ ~5 นาที)
5. สร้าง admin user (เก็บ user/pass ไว้)

---

## 3. ติดตั้ง Plugins เพิ่ม

**Manage Jenkins → Plugins → Available plugins** → ค้นหาและติดตั้ง:

| Plugin | ใช้ทำอะไร |
|--------|----------|
| **Docker Pipeline** | รัน docker build/push ใน pipeline |
| **Pipeline: Stage View** | ดู visualization ของ 6 stages |
| **GitHub Integration Plugin** | รับ webhook จาก GitHub |
| **Credentials Binding** | ใช้ Docker Hub credentials ใน pipeline |

→ ติ๊กทั้งหมด → **Install** → restart Jenkins ตามคำสั่ง

---

## 4. เพิ่ม Docker Hub Credentials

1. **Manage Jenkins → Credentials → System → Global credentials → Add Credentials**
2. กรอก:
   - Kind: **Username with password**
   - Scope: **Global**
   - **Username:** `aphikap` (Docker Hub username)
   - **Password:** Docker Hub PAT (สร้างที่ https://hub.docker.com/settings/security)
   - **ID:** `dockerhub-credentials` ⚠️ **ต้องตรงกับใน [Jenkinsfile:54](../Jenkinsfile#L54) เป๊ะ**
   - Description: `Docker Hub for aradin-converter`
3. **Create**

---

## 5. ติดตั้ง CLI tools ที่ Jenkins agent ต้องใช้

Pipeline ใน [Jenkinsfile](../Jenkinsfile) เรียก: `python3`, `pytest`, `docker`, `terraform`, `ansible-playbook`, `kubectl`

ต้องลงทั้งหมดบนเครื่องที่ Jenkins ทำงาน (default = master node):

```bash
# WSL/Linux
sudo apt install -y python3 python3-pip docker.io
pip install pytest

# Terraform (ดู docs/local-setup.md)
# Ansible (ดู docs/local-setup.md)
# kubectl (ดู docs/local-setup.md)

# เพิ่ม jenkins user เข้า docker group
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

---

## 6. สร้าง Pipeline Job

1. **New Item** → ตั้งชื่อ `aradin-converter` → เลือก **Pipeline** → OK
2. ในหน้า config:
   - **General → ติ๊ก** `GitHub project` → URL: `https://github.com/Aphikap/Aradin-Unit`
   - **Build Triggers → ติ๊ก** `GitHub hook trigger for GITScm polling`
   - **Pipeline:**
     - Definition: **Pipeline script from SCM**
     - SCM: **Git**
     - Repository URL: `https://github.com/Aphikap/Aradin-Unit.git`
     - Branch Specifier: `*/main`
     - Script Path: `Jenkinsfile`
3. **Save**

---

## 7. ทดสอบ Build ครั้งแรก (Manual)

ก่อนต่อ webhook ลอง trigger เองดูก่อน:

1. คลิก **Build Now**
2. ดู **Stage View** — ต้องผ่าน 6 stages: Checkout → Build → Test → Docker Build → Push to Hub → Deploy
3. ถ้ามี stage fail:
   - Checkout fail → ตรวจ Git URL/credentials
   - Build/Test fail → ตรวจ python/pip ในเครื่อง
   - Docker Build fail → ตรวจ `docker --version` รันได้ + user ใน docker group
   - Push fail → ตรวจ credentials `dockerhub-credentials`
   - Deploy fail → ตรวจ kubectl/terraform/ansible ลงครบ + kubeconfig

---

## 8. ตั้ง GitHub Webhook

Jenkins ต้องเข้าได้จาก internet ก่อน — ถ้ารัน localhost ใช้ tunnel:

```powershell
# วิธี A: ngrok (ง่ายสุด ฟรี 8 ชม.)
# 1. ดาวน์โหลด https://ngrok.com/download
# 2. รัน:
ngrok http 8080
# 3. copy URL เช่น https://abc123.ngrok-free.app

# วิธี B: Cloudflare Tunnel (ฟรี ถาวร)
cloudflared tunnel --url http://localhost:8080
```

แล้วไป GitHub:

1. **Repository → Settings → Webhooks → Add webhook**
2. กรอก:
   - **Payload URL:** `https://abc123.ngrok-free.app/github-webhook/` ⚠️ ลงท้าย `/` ห้ามขาด
   - **Content type:** `application/json`
   - **Trigger:** Just the push event
3. **Add webhook**

GitHub จะส่ง ping ทันที — ดูใน **Recent Deliveries** ต้องเป็น **200 OK**

---

## 9. ทดสอบ End-to-End

```bash
# แก้ code นิดเดียว
echo "<!-- test build -->" >> app/templates/index.html
git add . && git commit -m "test: trigger pipeline" && git push origin main
```

ดูใน Jenkins:
- Build #N เริ่มทำงานอัตโนมัติภายใน 10-30 วินาที
- 6 stages ผ่านครบ
- Docker Hub: https://hub.docker.com/r/aphikap/aradin-converter/tags — มี tag ใหม่
- `kubectl get pods -n aradin` — pods ใหม่ Rolling Update

ถ้าครบนี้ = **Rubric Phase 2 + Bonus Demo ผ่าน 30 pts** 🎉

---

## 🐛 Troubleshooting

| อาการ | สาเหตุ / วิธีแก้ |
|------|----------------|
| `docker: command not found` ใน Build stage | jenkins user ไม่อยู่ใน docker group → `sudo usermod -aG docker jenkins && sudo systemctl restart jenkins` |
| `denied: requested access to the resource is denied` ตอน push | credentials `dockerhub-credentials` ผิด — สร้าง PAT ใหม่ (อย่าใช้ password บัญชี) |
| Webhook ไม่ trigger build | URL ลืม `/` ท้าย / ngrok หมดอายุ / Build Triggers ไม่ติ๊ก GitHub hook |
| Test stage fail แต่รันเครื่องตัวเองได้ | path ของ pytest หรือ working directory ไม่ตรง → ดู [Jenkinsfile:34-41](../Jenkinsfile#L34-L41) |
| Deploy stage `kubectl: command not found` | kubectl ไม่อยู่บน Jenkins agent → ติดตั้งหรือใช้ Docker Pipeline image |
| `terraform: command not found` | terraform ไม่อยู่บน Jenkins agent → ลงตาม [docs/local-setup.md](local-setup.md) |

---

## 📚 อ่านเพิ่ม

- [Jenkinsfile syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [GitHub webhook docs](https://docs.github.com/en/webhooks)
- [Docker Hub PAT](https://docs.docker.com/security/for-developers/access-tokens/)
