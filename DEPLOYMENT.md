# AWS EC2 프리티어 배포 가이드 (Celery 포함)

## 아키텍처 구성
```
                    ┌─────────────┐
                    │   Nginx     │
                    │ (Reverse    │
                    │   Proxy)    │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐
    │  Next.js  │    │  Django   │    │   Redis   │
    │ Frontend  │    │  Backend  │    │  (Broker) │
    │  :3000    │    │  :8000    │    │  :6379    │
    └───────────┘    └─────┬─────┘    └─────┬─────┘
                           │                │
                     ┌─────▼────────────────▼─────┐
                     │        Celery              │
                     │  ┌─────────┐ ┌──────────┐  │
                     │  │ Worker  │ │   Beat   │  │
                     │  │(작업실행)│ │(스케줄러) │  │
                     │  └─────────┘ └──────────┘  │
                     └────────────────────────────┘
```

## 1. EC2 인스턴스 생성

### AWS Console에서:
1. EC2 Dashboard → **Launch Instance**
2. 설정:
   - **Name**: pizza-scheduler
   - **OS**: Ubuntu Server 22.04 LTS (프리티어)
   - **Instance Type**: `t2.micro` (프리티어) 또는 `t2.small`
   - **Key Pair**: 새로 생성 (.pem 파일 다운로드 필수!)
   - **Storage**: 20GB (프리티어 최대 30GB)
   - **Security Group**:
     | Type | Port | Source | 설명 |
     |------|------|--------|------|
     | SSH | 22 | 내 IP | SSH 접속 |
     | HTTP | 80 | 0.0.0.0/0 | 웹 트래픽 |
     | HTTPS | 443 | 0.0.0.0/0 | SSL 트래픽 |

3. **Launch Instance** 클릭

## 2. EC2 접속

```bash
# .pem 파일 권한 설정
chmod 400 your-key.pem

# SSH 접속
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

## 3. 서버 초기 설정

```bash
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib \
    nginx git curl redis-server

# Node.js 18 LTS 설치
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Redis 시작 및 자동 시작 설정
sudo systemctl enable redis-server
sudo systemctl start redis-server

# 버전 확인
python3 --version  # 3.10+
node --version     # 18+
redis-cli ping     # PONG
```

## 4. PostgreSQL 설정

```bash
# PostgreSQL 접속
sudo -u postgres psql

# 데이터베이스 및 사용자 생성
CREATE DATABASE pizza_db;
CREATE USER pizza_user WITH PASSWORD 'your_secure_password_here';
ALTER ROLE pizza_user SET client_encoding TO 'utf8';
ALTER ROLE pizza_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pizza_user SET timezone TO 'Asia/Seoul';
GRANT ALL PRIVILEGES ON DATABASE pizza_db TO pizza_user;
\q
```

## 5. 프로젝트 배포

```bash
# 프로젝트 클론
cd /home/ubuntu
git clone https://github.com/YOUR_USERNAME/pizza.git
cd pizza

# Python 가상환경 설정
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# .env.production 설정
nano .env.production
```

### .env.production 수정 내용:
```env
# Django
SECRET_KEY=생성한_랜덤_시크릿키
DJANGO_ENVIRONMENT=production
DEBUG=False
ALLOWED_HOSTS=your-domain.com,YOUR_EC2_IP

# Database
DB_NAME=pizza_db
DB_USER=pizza_user
DB_PASSWORD=위에서_설정한_비밀번호
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=앱_비밀번호

# Frontend URL
FRONTEND_URL=https://your-domain.com

# Redis
REDIS_URL=redis://localhost:6379/0

# Kakao
KAKAO_JAVASCRIPT_KEY=카카오_자바스크립트_키

# Solapi SMS
SOLAPI_API_KEY=솔라피_API_키
SOLAPI_API_SECRET=솔라피_시크릿_키
SOLAPI_SENDER_NUMBER=발신번호
```

```bash
# Django 초기 설정
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser
```

## 6. 프론트엔드 빌드

```bash
cd /home/ubuntu/pizza/frontend
npm install

# .env.local 설정
nano .env.local
```

### frontend/.env.local:
```env
NEXT_PUBLIC_API_URL=https://your-domain.com
NEXT_PUBLIC_FRONTEND_URL=https://your-domain.com
NEXT_PUBLIC_KAKAO_JAVASCRIPT_KEY=카카오_자바스크립트_키
```

```bash
# 프로덕션 빌드
npm run build
```

## 7. 로그 디렉토리 생성

```bash
sudo mkdir -p /var/log/gunicorn /var/log/celery
sudo chown ubuntu:ubuntu /var/log/gunicorn /var/log/celery
```

## 8. Systemd 서비스 설정

```bash
# 서비스 파일 복사
sudo cp /home/ubuntu/pizza/deploy/pizza-backend.service /etc/systemd/system/
sudo cp /home/ubuntu/pizza/deploy/pizza-frontend.service /etc/systemd/system/
sudo cp /home/ubuntu/pizza/deploy/pizza-celery-worker.service /etc/systemd/system/
sudo cp /home/ubuntu/pizza/deploy/pizza-celery-beat.service /etc/systemd/system/

# Systemd 리로드
sudo systemctl daemon-reload

# 서비스 활성화 및 시작
sudo systemctl enable pizza-backend pizza-frontend pizza-celery-worker pizza-celery-beat
sudo systemctl start pizza-backend pizza-frontend pizza-celery-worker pizza-celery-beat

# 상태 확인
sudo systemctl status pizza-backend
sudo systemctl status pizza-frontend
sudo systemctl status pizza-celery-worker
sudo systemctl status pizza-celery-beat
```

## 9. Nginx 설정

```bash
# Nginx 설정 파일 복사
sudo cp /home/ubuntu/pizza/deploy/nginx.conf /etc/nginx/sites-available/pizza
sudo ln -sf /etc/nginx/sites-available/pizza /etc/nginx/sites-enabled/

# 기본 설정 제거
sudo rm -f /etc/nginx/sites-enabled/default

# 도메인 수정
sudo nano /etc/nginx/sites-available/pizza
# your-domain.com을 실제 도메인으로 변경

# 설정 테스트 및 재시작
sudo nginx -t
sudo systemctl restart nginx
```

## 10. 도메인 연결

### DNS 설정 (Route 53 또는 도메인 업체):
| 타입 | 이름 | 값 |
|------|------|------|
| A | @ | EC2 Public IP |
| A | www | EC2 Public IP |

## 11. SSL 인증서 (Let's Encrypt)

```bash
# Certbot 설치
sudo apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 자동 갱신 테스트
sudo certbot renew --dry-run
```

## 12. 카카오 개발자 설정

1. https://developers.kakao.com 접속
2. 내 애플리케이션 → 플랫폼 → Web
3. 사이트 도메인 추가:
   - `https://your-domain.com`
   - `https://www.your-domain.com`

## 13. 배포 완료 확인

```bash
# 모든 서비스 상태 확인
sudo systemctl status pizza-backend pizza-frontend pizza-celery-worker pizza-celery-beat nginx redis-server

# 로그 확인
sudo journalctl -u pizza-celery-worker -f  # Celery 워커 로그
sudo journalctl -u pizza-celery-beat -f    # Celery 비트 로그
sudo tail -f /var/log/nginx/error.log      # Nginx 에러 로그
```

## 접속 URL

- **메인**: https://your-domain.com
- **API 문서**: https://your-domain.com/api/v1/docs
- **Admin**: https://your-domain.com/admin

---

## Celery 리마인더 기능

### 동작 방식:
1. **최종 시간 확정 시**:
   - 참가자에게 즉시 이메일/SMS 발송
   - 당일 오전 7시 리마인더 스케줄링

2. **리마인더 발송**:
   - 확정된 날짜 당일 오전 7시에 자동 발송
   - 이메일 + SMS 동시 발송

### Celery 명령어:
```bash
# 워커 수동 실행 (디버그용)
cd /home/ubuntu/pizza
source venv/bin/activate
celery -A config worker -l INFO

# 비트 수동 실행 (스케줄러)
celery -A config beat -l INFO

# 현재 스케줄된 태스크 확인 (Django Admin에서)
# https://your-domain.com/admin/django_celery_beat/
```

---

## 문제 해결

### 502 Bad Gateway
```bash
sudo systemctl restart pizza-backend pizza-frontend
sudo nginx -t && sudo systemctl restart nginx
```

### Celery 작업 안 됨
```bash
# Redis 확인
redis-cli ping

# 워커 재시작
sudo systemctl restart pizza-celery-worker pizza-celery-beat
```

### 메모리 부족 (t2.micro)
```bash
# 스왑 메모리 추가 (1GB)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 영구 설정
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 로그 확인
```bash
# 모든 로그 한번에
sudo journalctl -u pizza-backend -u pizza-frontend -u pizza-celery-worker -u pizza-celery-beat --since "1 hour ago"
```

---

## 코드 업데이트

```bash
cd /home/ubuntu/pizza
git pull

# 백엔드
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# 프론트엔드
cd frontend
npm install
npm run build

# 모든 서비스 재시작
sudo systemctl restart pizza-backend pizza-frontend pizza-celery-worker pizza-celery-beat
```

---

## 비용 예상 (프리티어)

| 서비스 | 프리티어 한도 | 초과 시 비용 |
|--------|--------------|-------------|
| EC2 t2.micro | 750시간/월 | ~$8/월 |
| EBS Storage | 30GB | $0.10/GB |
| 데이터 전송 | 15GB/월 | $0.09/GB |

**참고**: 프리티어 1년 후 또는 한도 초과 시 과금

---

배포 완료!
