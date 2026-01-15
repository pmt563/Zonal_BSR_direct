# Baby-Safety-Reminder

## Zonal ECU component

## 🚀 GitHub Actions CI/CD (ARM64)

Workflow tự động build Docker image cho ARM64 architecture và push lên GitHub Container Registry.

**Quick Start:**
```bash
# Push code lên GitHub để trigger workflow
git add .
git commit -m "Trigger ARM64 build"
git push origin main

# Pull image đã build
docker pull ghcr.io/<username>/<repo>:latest
```

📖 **Chi tiết:** Xem [.github/workflows/README.md](.github/workflows/README.md)

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