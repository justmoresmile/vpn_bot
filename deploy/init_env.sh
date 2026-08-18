#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/opt/vpn-bot"
ENV_FILE="$PROJECT_DIR/.env"
ENV_EXAMPLE="$PROJECT_DIR/.env.example"

cd "$PROJECT_DIR"

if [ ! -f "$ENV_FILE" ]; then
    if [ ! -f "$ENV_EXAMPLE" ]; then
        echo "ERROR: .env.example not found"
        exit 1
    fi

    cp "$ENV_EXAMPLE" "$ENV_FILE"
    chmod 600 "$ENV_FILE"

    echo ".env created"
fi

set_value() {
    local key="$1"
    local value="$2"

    [ -z "$value" ] && return 0

    local current=""
    current=$(grep "^${key}=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d= -f2- || true)

    # Never overwrite an existing value
    if [ -n "$current" ]; then
        return 0
    fi

    if grep -q "^${key}=" "$ENV_FILE"; then
        sed -i "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
    else
        printf '%s=%s\n' "$key" "$value" >> "$ENV_FILE"
    fi
}

generate_hex() {
    python3 - <<'PY'
import secrets
print(secrets.token_hex(32))
PY
}

generate_secret() {
    python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
}

echo "===== JUSTVPN ENV INITIALIZER ====="

# --------------------------------------------------
# Static application settings
# --------------------------------------------------

set_value "JWT_ALGORITHM" "HS256"
set_value "JWT_EXPIRE_DAYS" "30"

set_value \
    "BACKEND_API_URL" \
    "http://127.0.0.1:8000/api/v1"

set_value \
    "DATABASE_PATH" \
    "/opt/vpn-bot/data/vpn.db"

set_value "VPN_NAME" "Helsinki"
set_value "VPN_COUNTRY" "Finland"

set_value "ENABLE_VLESS" "true"
set_value "VPN_WG_DNS" "1.1.1.1"

set_value \
    "MINIAPP_URL" \
    "https://app.justfastvpn.ru"

set_value \
    "PUBLIC_SUBSCRIPTION_BASE_URL" \
    "https://s.justfastvpn.ru"

set_value \
    "PAYMENT_RETURN_URL" \
    "https://app.justfastvpn.ru"

set_value "DEBUG" "false"

# --------------------------------------------------
# Generate internal secrets
# --------------------------------------------------

set_value \
    "BACKEND_API_KEY" \
    "$(generate_hex)"

set_value \
    "JWT_SECRET" \
    "$(generate_secret)"

set_value \
    "BACKUP_PASSPHRASE" \
    "$(generate_secret)"

# --------------------------------------------------
# Detect server IPv4
# --------------------------------------------------

VPN_HOST=""

VPN_HOST=$(
    ip -4 route get 1.1.1.1 2>/dev/null \
        | sed -n 's/.* src \([^ ]*\).*/\1/p' \
        | head -1
)

if [ -z "$VPN_HOST" ]; then
    VPN_HOST=$(
        hostname -I 2>/dev/null \
            | awk '{print $1}'
    )
fi

set_value "VPN_HOST" "$VPN_HOST"

# --------------------------------------------------
# External VPN node settings
# --------------------------------------------------

# These values cannot be reliably detected on the backend server.
# Configure them manually for the VPN node:
#
# XUI_API_URL
# XUI_API_TOKEN
# VPN_VLESS_INBOUND
# VPN_WIREGUARD_INBOUND

chmod 600 "$ENV_FILE"

echo
echo "===== RESULT ====="

for key in \
    BOT_TOKEN \
    ADMIN_ID \
    BACKEND_API_KEY \
    JWT_SECRET \
    XUI_API_URL \
    XUI_API_TOKEN \
    VPN_HOST \
    VPN_VLESS_INBOUND \
    VPN_WIREGUARD_INBOUND \
    YOOKASSA_SHOP_ID \
    YOOKASSA_SECRET_KEY \
    BACKUP_PASSPHRASE
do

    value=$(
        grep "^${key}=" "$ENV_FILE" 2>/dev/null \
            | head -1 \
            | cut -d= -f2- || true
    )

    if [ -n "$value" ]; then
        echo "$key = OK"
    else
        echo "$key = MANUAL"
    fi

done

echo
echo "Environment initialization complete."
