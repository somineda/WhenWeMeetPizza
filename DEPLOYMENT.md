# AWS EC2 배포 가이드

## 1. EC2 인스턴스 생성

### AWS Console에서:
1. EC2 Dashboard → Launch Instance
2. 설정:
   - **Name**: pizza-scheduler
   - **OS**: Ubuntu Server 22.04 LTS
   - **Instance Type**: t2.medium (최소 t2.small)
   - **Key Pair**: 새로 생성하거나 기존 키 사용 (.pem 파일 다운로드)
   - **Security Group**:
     - SSH (22) - 내 IP
     - HTTP (80) - 0.0.0.0/0
     - HTTPS (443) - 0.0.0.0/0
     - Custom TCP (8000) - 127.0.0.1 (백엔드, 로컬만)
     - Custom TCP (3000) - 127.0.0.1 (프론트엔드, 로컬만)

3. Launch Instance

## 2. EC2 접속

```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

## 3. 서버 초기 설정

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib \
    nginx git curl redis-server

# Node.js 설치 (v18 LTS)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 확인
python3 --version
node --version
npm --version
```

## 4. PostgreSQL 설정

```bash
# PostgreSQL 접속
sudo -u postgres psql

# 데이터베이스 생성
CREATE DATABASE pizza_db;
CREATE USER pizza_user WITH PASSWORD 'your_secure_password';
ALTER ROLE pizza_user SET client_encoding TO 'utf8';
ALTER ROLE pizza_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pizza_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE pizza_db TO pizza_user;
\q
```

## 5. 코드 배포

```bash
# 프로젝트 클론
cd /home/ubuntu
git clone YOUR_GITHUB_REPO pizza
cd pizza

# 백엔드 설정
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# .env.production 파일 수정
nano .env.production
# SECRET_KEY, DB_PASSWORD, ALLOWED_HOSTS, FRONTEND_URL 수정

# Django 설정
python manage.py collectstatic --noinput
python manage.py migrate

# 슈퍼유저 생성
python manage.py createsuperuser

# 프론트엔드 설정
cd frontend
npm install

# .env.local 수정
nano .env.local
# NEXT_PUBLIC_FRONTEND_URL을 실제 도메인으로 변경

# 프로덕션 빌드
npm run build
```

## 6. Gunicorn 설정

```bash
# 로그 디렉토리 생성
sudo mkdir -p /var/log/gunicorn
sudo chown ubuntu:ubuntu /var/log/gunicorn

# Gunicorn 테스트
cd /home/ubuntu/pizza
source venv/bin/activate
gunicorn --config gunicorn_config.py config.wsgi:application

# Ctrl+C로 중지 후 systemd 서비스 설정
sudo cp deploy/pizza-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pizza-backend
sudo systemctl start pizza-backend
sudo systemctl status pizza-backend
```

## 7. Next.js 설정

```bash
sudo cp deploy/pizza-frontend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pizza-frontend
sudo systemctl start pizza-frontend
sudo systemctl status pizza-frontend
```

## 8. Nginx 설정

```bash
# nginx 설정 복사
sudo cp deploy/nginx.conf /etc/nginx/sites-available/pizza
sudo ln -s /etc/nginx/sites-available/pizza /etc/nginx/sites-enabled/

# 기본 설정 제거
sudo rm /etc/nginx/sites-enabled/default

# your-domain.com을 실제 도메인으로 변경
sudo nano /etc/nginx/sites-available/pizza

# 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
```

## 9. 도메인 연결

### Route 53 또는 도메인 제공업체에서:
1. A 레코드 생성
   - Name: @ (또는 빈칸)
   - Value: EC2 Public IP

2. A 레코드 생성 (www)
   - Name: www
   - Value: EC2 Public IP

## 10. SSL 인증서 (Let's Encrypt)

```bash
# Certbot 설치
sudo apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 이메일 입력, 약관 동의
# 자동 HTTPS 리다이렉션 선택: 2

# 자동 갱신 확인
sudo certbot renew --dry-run
```

## 11. 카카오 개발자 플랫폼 설정

1. https://developers.kakao.com
2. 내 애플리케이션 선택
3. **플랫폼 설정** → **Web 플랫폼 등록**
4. 사이트 도메인 추가:
   - `https://your-domain.com`
   - `https://www.your-domain.com`

## 12. 배포 완료 확인

```bash
# 서비스 상태 확인
sudo systemctl status pizza-backend
sudo systemctl status pizza-frontend
sudo systemctl status nginx

# 로그 확인
sudo tail -f /var/log/gunicorn/error.log
sudo tail -f /var/log/nginx/error.log

# 방화벽 확인
sudo ufw status
```

## 브라우저에서 접속

- Frontend: https://your-domain.com
- Backend API: https://your-domain.com/api/v1/
- Admin: https://your-domain.com/admin

## 문제 해결

### 502 Bad Gateway
```bash
sudo systemctl restart pizza-backend
sudo systemctl restart pizza-frontend
```

### Static files 안 보임
```bash
cd /home/ubuntu/pizza
source venv/bin/activate
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### 권한 문제
```bash
sudo chown -R ubuntu:www-data /home/ubuntu/pizza
sudo chmod -R 755 /home/ubuntu/pizza
```

## 코드 업데이트

```bash
cd /home/ubuntu/pizza
git pull

# 백엔드 업데이트
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart pizza-backend

# 프론트엔드 업데이트
cd frontend
npm install
npm run build
sudo systemctl restart pizza-frontend
```

## 모니터링

```bash
# CPU/메모리 사용량
htop

# 디스크 사용량
df -h

# 서비스 로그 실시간 확인
sudo journalctl -u pizza-backend -f
sudo journalctl -u pizza-frontend -f
```

---

배포 완료! 🎉
