# Baby-Safety-Reminder

## Zonal ECU component

## 🚀 GitHub Actions CI/CD (ARM64)

Workflow tự động build Docker image cho ARM64 architecture và push lên GitHub Container Registry.

### Quick Setup (Recommended)

**Bước 1:** Tạo repository trên GitHub: https://github.com/new

**Bước 2:** Chạy script tự động:
```bash
./setup_github.sh <github-username> <repo-name>

# Ví dụ:
./setup_github.sh minhtuan958 zonal-ecu
```

**Bước 3:** Cấu hình permissions và kiểm tra workflow chạy!

### Manual Setup

```bash
# Thêm remote repository
git remote add origin https://github.com/<username>/<repo>.git

# Push code
git push -u origin main

# Pull image sau khi build xong
docker pull ghcr.io/<username>/<repo>:latest
```

📖 **Hướng dẫn chi tiết:** 
- [GITHUB_SETUP.md](GITHUB_SETUP.md) - Setup từng bước
- [.github/workflows/README.md](.github/workflows/README.md) - Workflow documentation

---

### Build (Local)
```bash
sudo podman build -t zonal_app .
```

### Save image
```bash
sudo podman save -o zonal_app.tar localhost/zonal_app:latest
```

### Load
```bash
sudo podman load -i zonal_app.tar
```

### Run
```bash
# sudo podman run --rm -it --device=/dev/bus/usb/001/006 zonal_app -loopback=1 192.168.0.3:55555
sudo ./run.sh <image> [optional] <brokerIP:brokerPORT>
```

### Run local Kuksa databroker
```bash
sudo podman run -it --rm --name Server --network kuksa ghcr.io/eclipse-kuksa/kuksa-databroker:main --insecure
```
Open new terminal
```bash
sudo podman run -it --rm --network kuksa ghcr.io/eclipse-kuksa/kuksa-databroker-cli:main --server Server1:55555
```
Get local Kuksa databroker IP
```bash
sudo podman inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' Server2
```