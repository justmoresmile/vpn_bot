#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/opt/vpn-bot"
REPO_URL="git@github.com:justmoresmile/vpn_bot.git"
BRANCH="main"

if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: bootstrap.sh must be run as root"
    exit 1
fi

echo "=========================================="
echo " JustVPN bootstrap"
echo "=========================================="

echo
echo "===== BASE PACKAGES ====="

apt update

apt install -y \
    git \
    ca-certificates \
    openssh-client \
    python3 \
    sqlite3

echo
echo "===== PROJECT ====="

if [ ! -d "$PROJECT_DIR/.git" ]; then

    mkdir -p "$(dirname "$PROJECT_DIR")"

    git clone \
        --branch "$BRANCH" \
        "$REPO_URL" \
        "$PROJECT_DIR"

else

    cd "$PROJECT_DIR"

    git fetch origin "$BRANCH"

    git checkout "$BRANCH"

    git pull --ff-only origin "$BRANCH"

fi

cd "$PROJECT_DIR"

chmod +x \
    deploy/init_env.sh \
    deploy/install.sh

echo
echo "===== INITIALIZE ENV ====="

./deploy/init_env.sh

echo
echo "===== MANUAL SECRETS CHECK ====="

missing=0

required_manual=(
    BOT_TOKEN
    ADMIN_ID
    XUI_API_TOKEN
)

for key in "${required_manual[@]}"; do

    value=$(
        grep "^${key}=" .env 2>/dev/null \
            | head -1 \
            | cut -d= -f2- || true
    )

    if [ -z "$value" ]; then
        echo "$key = REQUIRED"
        missing=1
    else
        echo "$key = OK"
    fi

done

echo
echo "===== OPTIONAL PAYMENT SECRETS ====="

optional=(
    YOOKASSA_SHOP_ID
    YOOKASSA_SECRET_KEY
)

for key in "${optional[@]}"; do

    value=$(
        grep "^${key}=" .env 2>/dev/null \
            | head -1 \
            | cut -d= -f2- || true
    )

    if [ -z "$value" ]; then
        echo "$key = NOT SET"
    else
        echo "$key = OK"
    fi

done

if [ "$missing" -ne 0 ]; then

    echo
    echo "=========================================="
    echo " Bootstrap paused"
    echo "=========================================="
    echo
    echo "Fill required values in:"
    echo
    echo "  $PROJECT_DIR/.env"
    echo
    echo "Then run:"
    echo
    echo "  cd $PROJECT_DIR"
    echo "  ./deploy/bootstrap.sh"
    echo

    exit 2
fi

echo
echo "===== INSTALL JUSTVPN ====="

exec "$PROJECT_DIR/deploy/install.sh"
