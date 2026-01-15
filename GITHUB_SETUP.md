# 🚀 Hướng dẫn Push lên GitHub

## Bước 1: Tạo GitHub Repository mới

1. Truy cập: https://github.com/new
2. Điền thông tin:
   - **Repository name**: `zonal-ecu` (hoặc tên bạn muốn)
   - **Description**: "Zonal ECU component for Baby Safety Reminder"
   - **Visibility**: Public hoặc Private
   - ⚠️ **KHÔNG** chọn "Add a README file"
   - ⚠️ **KHÔNG** chọn "Add .gitignore"
3. Click **"Create repository"**

## Bước 2: Push code lên GitHub

Sau khi tạo repository, GitHub sẽ hiển thị hướng dẫn. Chạy các lệnh sau:

```bash
cd /home/minhtuan958/Documents/emtek/sdv/zonal_BSR_huynguyen/BabySafetyReminder/HIL_Realization/Phase3/Implementation/zonal_ecu

# Thêm remote repository (thay <username> bằng GitHub username của bạn)
git remote add origin https://github.com/<username>/zonal-ecu.git

# Push code lên GitHub
git push -u origin main
```

## Bước 3: Cấu hình GitHub Actions permissions

1. Vào repository trên GitHub
2. Click **Settings** → **Actions** → **General**
3. Scroll xuống **"Workflow permissions"**
4. Chọn: ✅ **"Read and write permissions"**
5. Click **Save**

## Bước 4: Trigger workflow

Workflow sẽ tự động chạy sau khi push. Kiểm tra tại:
```
https://github.com/<username>/zonal-ecu/actions
```

## Bước 5: Pull image đã build

Sau khi workflow hoàn thành:

```bash
# Login vào GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u <username> --password-stdin

# Pull image
docker pull ghcr.io/<username>/zonal-ecu:latest

# Run container
docker run --rm -it ghcr.io/<username>/zonal-ecu:latest
```

---

## 📝 Lưu ý quan trọng

### Repository đã được khởi tạo tại:
```
/home/minhtuan958/Documents/emtek/sdv/zonal_BSR_huynguyen/BabySafetyReminder/HIL_Realization/Phase3/Implementation/zonal_ecu
```

### Files đã commit:
- ✅ `.github/workflows/ci.yaml` - GitHub Actions workflow
- ✅ `.dockerignore` - Docker build optimization
- ✅ `.gitignore` - Git ignore rules
- ✅ `Dockerfile` - ARM64 compatible
- ✅ `README.md` - Documentation
- ✅ `src/` - Source code
- ✅ `run.sh` - Run script

### Workflow sẽ trigger khi:
- ✅ Push lên branch `main`
- ✅ Tạo tag `v*.*.*` (ví dụ: v1.0.0)
- ✅ Tạo Pull Request vào `main`
- ✅ Chạy thủ công qua GitHub UI

---

## 🔧 Troubleshooting

### Lỗi: "Permission denied"
```bash
# Sử dụng SSH thay vì HTTPS
git remote set-url origin git@github.com:<username>/zonal-ecu.git
```

### Lỗi: "Authentication failed"
```bash
# Tạo Personal Access Token tại: https://github.com/settings/tokens
# Chọn scopes: repo, write:packages, read:packages
# Sử dụng token thay vì password khi push
```

### Kiểm tra remote
```bash
git remote -v
```

---

## 📦 Cấu trúc Repository

```
zonal_ecu/
├── .github/
│   └── workflows/
│       ├── ci.yaml          # GitHub Actions workflow
│       └── README.md        # Workflow documentation
├── src/
│   ├── zonal_app.py         # Main application
│   ├── can_driver.py        # CAN driver
│   └── libcontrolcanfd.a    # CAN library
├── .dockerignore            # Docker ignore rules
├── .gitignore               # Git ignore rules
├── Dockerfile               # ARM64 Docker build
├── README.md                # Main documentation
├── run.sh                   # Run script
└── GITHUB_SETUP.md          # This file
```

---

## 🎯 Next Steps

1. ✅ Tạo GitHub repository
2. ✅ Push code lên GitHub
3. ✅ Cấu hình permissions
4. ✅ Kiểm tra workflow chạy thành công
5. ✅ Pull và test image

**Chúc bạn thành công! 🎉**
