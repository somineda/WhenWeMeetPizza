#!/bin/bash
# EC2 서버 초기 설정 스크립트

set -e

echo "🚀 Pizza Scheduler 배포 시작..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 시스템 업데이트
echo -e "${GREEN}1. 시스템 업데이트 중...${NC}"
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
echo -e "${GREEN}2. 필수 패키지 설치 중...${NC}"
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib \
    nginx git curl redis-server build-essential

# Node.js 설치
echo -e "${GREEN}3. Node.js 설치 중...${NC}"
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 버전 확인
echo -e "${GREEN}설치된 버전:${NC}"
python3 --version
node --version
npm --version
psql --version

echo -e "${GREEN}✅ 초기 설정 완료!${NC}"
echo -e "${YELLOW}다음 단계: PostgreSQL 데이터베이스 설정${NC}"
