#!/bin/bash

# Script để push zonal_ecu repository lên GitHub
# Usage: ./setup_github.sh <github-username> <repo-name>

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          GitHub Setup Script - Zonal ECU Repository             ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check arguments
if [ $# -lt 2 ]; then
    echo -e "${RED}❌ Error: Missing arguments${NC}"
    echo ""
    echo "Usage: $0 <github-username> <repo-name>"
    echo ""
    echo "Example:"
    echo "  $0 minhtuan958 zonal-ecu"
    echo ""
    exit 1
fi

GITHUB_USER=$1
REPO_NAME=$2
REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "  GitHub Username: ${GITHUB_USER}"
echo "  Repository Name: ${REPO_NAME}"
echo "  Repository URL:  ${REPO_URL}"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo -e "${RED}❌ Error: Not a git repository${NC}"
    echo "Please run this script from the zonal_ecu directory"
    exit 1
fi

# Check if remote already exists
if git remote | grep -q "^origin$"; then
    echo -e "${YELLOW}⚠️  Remote 'origin' already exists${NC}"
    CURRENT_REMOTE=$(git remote get-url origin)
    echo "  Current remote: ${CURRENT_REMOTE}"
    echo ""
    read -p "Do you want to update it? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}🔄 Updating remote URL...${NC}"
        git remote set-url origin "${REPO_URL}"
        echo -e "${GREEN}✅ Remote updated${NC}"
    else
        echo -e "${YELLOW}⏭️  Skipping remote update${NC}"
    fi
else
    echo -e "${BLUE}🔗 Adding remote repository...${NC}"
    git remote add origin "${REPO_URL}"
    echo -e "${GREEN}✅ Remote added${NC}"
fi

echo ""
echo -e "${BLUE}📤 Pushing to GitHub...${NC}"
echo ""

# Push to GitHub
if git push -u origin main; then
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    ✅ SUCCESS!                                   ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}🎉 Code đã được push lên GitHub thành công!${NC}"
    echo ""
    echo -e "${YELLOW}📋 Next Steps:${NC}"
    echo ""
    echo "1️⃣  Cấu hình GitHub Actions permissions:"
    echo "   https://github.com/${GITHUB_USER}/${REPO_NAME}/settings/actions"
    echo "   → Chọn 'Read and write permissions'"
    echo ""
    echo "2️⃣  Kiểm tra workflow:"
    echo "   https://github.com/${GITHUB_USER}/${REPO_NAME}/actions"
    echo ""
    echo "3️⃣  Sau khi build xong, pull image:"
    echo "   docker pull ghcr.io/${GITHUB_USER}/${REPO_NAME}:latest"
    echo ""
else
    echo ""
    echo -e "${RED}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                    ❌ FAILED!                                    ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${RED}❌ Push failed!${NC}"
    echo ""
    echo -e "${YELLOW}💡 Troubleshooting:${NC}"
    echo ""
    echo "1. Đảm bảo repository đã được tạo trên GitHub:"
    echo "   https://github.com/new"
    echo ""
    echo "2. Nếu gặp lỗi authentication, sử dụng SSH:"
    echo "   git remote set-url origin git@github.com:${GITHUB_USER}/${REPO_NAME}.git"
    echo "   git push -u origin main"
    echo ""
    echo "3. Hoặc tạo Personal Access Token:"
    echo "   https://github.com/settings/tokens"
    echo "   Scopes: repo, write:packages, read:packages"
    echo ""
    exit 1
fi
