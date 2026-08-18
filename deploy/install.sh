#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="/opt/vpn-bot"
ENV_FILE="$PROJECT_DIR/.env"

APP_DOMAIN="app.justfastvpn.ru"
API_DOMAIN="s.justfastvpn.ru"

MINIAPP_DIR="$PROJECT_DIR/miniapp"
WEB_ROOT="/var/www/justvpn-miniapp"

NGINX_SOURCE="$PROJECT_DIR/deploy/nginx/justvpn-web.conf"
NGINX_TARGET="/etc/nginx/sites-available/justvpn-web"
NGINX_ENABLED="/etc/nginx/sites-enabled/justvpn-web"

NODE_MAJOR="24"

if [[ "$(id -u)" -ne 0 ]]; then
    echo "ERROR: run as root"
    exit 1
fi

if [[ ! -d "$PROJECT_DIR" ]]; then
    echo "ERROR: project directory not found: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

echo "=========================================="
echo " JustVPN Production Installer"
echo "=========================================="

echo
echo "===== BASE PACKAGES ====="

apt update

DEBIAN_FRONTEND=noninteractive apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    build-essential \
    git \
    curl \
    wget \
    jq \
    sqlite3 \
    ca-certificates \
    openssl \
    tar \
    xz-utils \
    nginx \
    snapd

echo
echo "===== ENV ====="

if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: .env not found"
    echo "Run:"
    echo "  ./deploy/init_env.sh"
    exit 2
fi

chmod 600 "$ENV_FILE"

set -a
source "$ENV_FILE"
set +a

required_vars=(
    BOT_TOKEN
    ADMIN_ID
    BACKEND_API_KEY
    JWT_SECRET
    XUI_API_URL
    XUI_API_TOKEN
    VPN_HOST
)

for var in "${required_vars[@]}"; do
    if [[ -z "${!var:-}" ]]; then
        echo "ERROR: required variable $var is empty"
        exit 1
    fi
done

echo "ENV OK"

echo
echo "===== PYTHON VENV ====="

if [[ ! -d .venv ]]; then
    python3 -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo
echo "===== DIRECTORIES ====="

mkdir -p \
    "$PROJECT_DIR/data" \
    "$PROJECT_DIR/logs" \
    /var/backups/vpn-bot \
    "$WEB_ROOT"

echo
echo "===== DATABASE ====="

.venv/bin/python - <<'PY'
from app.database.schema import create_tables

create_tables()

print("DATABASE READY")
PY

echo
echo "===== NODE.JS ====="

need_node=1

if command -v node >/dev/null 2>&1; then
    CURRENT_NODE_MAJOR="$(
        node -p 'process.versions.node.split(".")[0]' 2>/dev/null || true
    )"

    if [[ "$CURRENT_NODE_MAJOR" == "$NODE_MAJOR" ]]; then
        need_node=0
        echo "Node $(node -v) already installed"
    fi
fi

if [[ "$need_node" -eq 1 ]]; then

    ARCH="$(uname -m)"

    case "$ARCH" in
        x86_64)
            NODE_ARCH="x64"
            ;;
        aarch64|arm64)
            NODE_ARCH="arm64"
            ;;
        *)
            echo "ERROR: unsupported architecture: $ARCH"
            exit 1
            ;;
    esac

    NODE_FILE="$(
        curl -fsSL \
            "https://nodejs.org/dist/latest-v${NODE_MAJOR}.x/" \
        | grep -oE \
            "node-v${NODE_MAJOR}\.[0-9]+\.[0-9]+-linux-${NODE_ARCH}\.tar\.xz" \
        | head -1
    )"

    if [[ -z "$NODE_FILE" ]]; then
        echo "ERROR: could not determine Node.js package"
        exit 1
    fi

    echo "Installing $NODE_FILE"

    TMP_NODE="$(mktemp -d)"

    curl -fsSL \
        "https://nodejs.org/dist/latest-v${NODE_MAJOR}.x/$NODE_FILE" \
        -o "$TMP_NODE/node.tar.xz"

    tar -xJf "$TMP_NODE/node.tar.xz" \
        -C /usr/local \
        --strip-components=1

    rm -rf "$TMP_NODE"
fi

echo "Node: $(node -v)"
echo "npm:  $(npm -v)"

echo
echo "===== MINI APP BUILD ====="

cd "$MINIAPP_DIR"

npm ci
npm run build

rm -rf "$WEB_ROOT"
mkdir -p "$WEB_ROOT"

cp -a "$MINIAPP_DIR/dist/." "$WEB_ROOT/"

chown -R www-data:www-data "$WEB_ROOT"

echo "MINI APP READY"

echo
echo "===== SYSTEMD ====="

cd "$PROJECT_DIR"

install -m 644 \
    deploy/systemd/justvpn.service \
    /etc/systemd/system/justvpn.service

systemctl daemon-reload
systemctl enable justvpn

echo
echo "===== START JUSTVPN ====="

systemctl restart justvpn

echo "Waiting for backend..."

backend_ok=0

for i in {1..45}; do

    if curl -fsS \
        http://127.0.0.1:8000/api/v1/health \
        >/dev/null 2>&1; then

        backend_ok=1
        echo "BACKEND HEALTH OK"
        break
    fi

    sleep 1
done

if [[ "$backend_ok" -ne 1 ]]; then
    echo "ERROR: backend health check failed"
    journalctl -u justvpn -n 120 --no-pager
    exit 1
fi

echo
echo "===== NGINX ====="

install -m 644 \
    "$NGINX_SOURCE" \
    "$NGINX_TARGET"

ln -sf \
    "$NGINX_TARGET" \
    "$NGINX_ENABLED"

rm -f /etc/nginx/sites-enabled/default

nginx -t

systemctl enable nginx
systemctl restart nginx

echo
echo "===== CERTBOT ====="

if ! command -v certbot >/dev/null 2>&1; then

    snap install core >/dev/null 2>&1 || true
    snap refresh core >/dev/null 2>&1 || true

    apt remove -y certbot >/dev/null 2>&1 || true

    snap install --classic certbot

    ln -sf \
        /snap/bin/certbot \
        /usr/local/bin/certbot

fi

echo "Certbot: $(certbot --version)"

CERT_PATH="/etc/letsencrypt/live/${APP_DOMAIN}/fullchain.pem"

if [[ -f "$CERT_PATH" ]]; then

    echo "Existing certificate found."

    CERT_INFO="$(certbot certificates 2>/dev/null || true)"

    if grep -Fq "$APP_DOMAIN" <<< "$CERT_INFO" \
        && grep -Fq "$API_DOMAIN" <<< "$CERT_INFO"; then

        echo "Certificate already covers both domains."

    else

        echo "Existing certificate does not cover both domains."
        echo "Requesting updated certificate..."

        certbot --nginx \
            --non-interactive \
            --agree-tos \
            --register-unsafely-without-email \
            --redirect \
            --expand \
            -d "$APP_DOMAIN" \
            -d "$API_DOMAIN"

    fi

else

    echo "No certificate found."
    echo "Requesting Let's Encrypt certificate..."

    certbot --nginx \
        --non-interactive \
        --agree-tos \
        --register-unsafely-without-email \
        --redirect \
        -d "$APP_DOMAIN" \
        -d "$API_DOMAIN"

fi

echo
echo "===== FINAL NGINX CHECK ====="

nginx -t
systemctl reload nginx

echo
echo "===== LOCAL BACKEND ====="

curl -fsS \
    http://127.0.0.1:8000/api/v1/health

echo
echo
echo "===== PUBLIC MINI APP ====="

curl -fsSI \
    "https://${APP_DOMAIN}/" \
    | head -1

echo
echo "===== PUBLIC API ====="

curl -fsS \
    "https://${API_DOMAIN}/api/v1/health"

echo
echo
echo "===== IMPORTANT PORTS ====="

ss -lntup \
    | grep -E ':80|:443|:4443|:20554|:8000' \
    || true

echo
echo "===== SERVICES ====="

for service in \
    justvpn \
    nginx
do
    if systemctl is-active --quiet "$service"; then
        echo "$service = ACTIVE"
    else
        echo "$service = FAILED"
    fi
done

echo
echo "=========================================="
echo " JUSTVPN INSTALL COMPLETED"
echo "=========================================="
