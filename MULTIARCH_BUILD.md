# Multi-Architecture Docker Build Guide

## 📋 Tổng quan

Zonal ECU hiện hỗ trợ build Docker image cho **2 kiến trúc**:

- **AMD64** (x86_64) - Máy tính thông thường, servers
- **ARM64** (aarch64) - Raspberry Pi, AWS Graviton, Apple Silicon

---

## 🏗️ Cấu trúc thư mục

```
zonal_ecu/
├── Dockerfile              # Legacy (ARM64 only)
├── Dockerfile_multiarch    # Multi-arch (AMD64 + ARM64)
└── src/
    ├── amd64/
    │   ├── libcontrolcanfd.so
    │   └── libcontrolcanfd.a
    ├── arm64/
    │   ├── libcontrolcanfd.so
    │   └── libcontrolcanfd.a
    ├── zonal_app.py
    └── can_driver.py
```

---

### Kết quả

```bash
# Pull image
docker pull ghcr.io/<username>/zonal-ecu:latest

# Docker tự động chọn:
# - Trên máy AMD64 → pull AMD64 image
# - Trên máy ARM64 → pull ARM64 image
```

---

## Build Local

### Yêu cầu

```bash
# Cài Docker Buildx (thường đã có sẵn)
docker buildx version

# Tạo builder mới (nếu chưa có)
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap
```

### Build Multi-Arch

#### 1. Build cho cả 2 kiến trúc

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f Dockerfile_multiarch \
  -t zonal_app:multiarch \
  --load \
  .
```

**Lưu ý**: `--load` chỉ hoạt động với 1 platform. Để build cả 2, dùng `--push` hoặc build riêng.

#### 2. Build AMD64 only

```bash
docker buildx build \
  --platform linux/amd64 \
  -f Dockerfile_multiarch \
  -t zonal_app:amd64 \
  --load \
  .
```

#### 3. Build ARM64 only

```bash
docker buildx build \
  --platform linux/arm64 \
  -f Dockerfile_multiarch \
  -t zonal_app:arm64 \
  --load \
  .
```

### Build và Push

```bash
# Build cả 2 kiến trúc và push lên registry
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f Dockerfile_multiarch \
  -t ghcr.io/<username>/zonal-ecu:latest \
  --push \
  .
```

---
