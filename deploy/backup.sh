#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="/opt/vpn-bot"
ENV_FILE="$PROJECT_DIR/.env"
BACKUP_DIR="/var/backups/vpn-bot"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
NAME="justvpn_${TIMESTAMP}"

WORKDIR="$(mktemp -d)"
ARCHIVE="$BACKUP_DIR/${NAME}.tar.gz"
ENCRYPTED="${ARCHIVE}.enc"

if [[ "$(id -u)" -ne 0 ]]; then
    echo "ERROR: run as root"
    exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: $ENV_FILE not found"
    exit 1
fi

set -a
source "$ENV_FILE"
set +a

if [[ -z "${BACKUP_PASSPHRASE:-}" ]]; then
    echo "ERROR: BACKUP_PASSPHRASE is empty"
    exit 1
fi

cleanup() {
    rm -rf "$WORKDIR"
    rm -f "$ARCHIVE"
}

trap cleanup EXIT

mkdir -p \
    "$BACKUP_DIR" \
    "$WORKDIR/justvpn" \
    "$WORKDIR/env" \
    "$WORKDIR/systemd" \
    "$WORKDIR/nginx" \
    "$WORKDIR/meta"

chmod 700 "$WORKDIR"

echo "===== BACKUP JUSTVPN DB ====="

if [[ -f "$PROJECT_DIR/data/vpn.db" ]]; then

    sqlite3 "$PROJECT_DIR/data/vpn.db" \
        ".backup '$WORKDIR/justvpn/vpn.db'"

    echo "vpn.db = OK"

else

    echo "WARNING: vpn.db not found"

fi

echo
echo "===== BACKUP ENV ====="

cp "$ENV_FILE" "$WORKDIR/env/.env"
chmod 600 "$WORKDIR/env/.env"

echo ".env = OK"

echo
echo "===== BACKUP SYSTEMD ====="

if [[ -f /etc/systemd/system/justvpn.service ]]; then

    cp -a \
        /etc/systemd/system/justvpn.service \
        "$WORKDIR/systemd/"

    echo "justvpn.service = OK"

else

    echo "WARNING: justvpn.service not found"

fi

echo
echo "===== BACKUP NGINX ====="

if [[ -f /etc/nginx/sites-available/justvpn-web ]]; then

    cp -a \
        /etc/nginx/sites-available/justvpn-web \
        "$WORKDIR/nginx/justvpn-web"

    echo "nginx config = OK"

else

    echo "WARNING: justvpn-web config not found"

fi

echo
echo "===== METADATA ====="

{
    echo "created_at=$(date --iso-8601=seconds)"
    echo "hostname=$(hostname)"
    echo "public_ip=${VPN_HOST:-unknown}"
    echo "git_commit=$(git -C "$PROJECT_DIR" rev-parse HEAD 2>/dev/null || echo unknown)"
    echo "python_version=$(python3 --version 2>&1)"
    echo "backup_type=justvpn-backend"
} > "$WORKDIR/meta/backup-info.txt"

tar \
    -C "$WORKDIR" \
    -czf "$ARCHIVE" \
    .

openssl enc \
    -aes-256-cbc \
    -salt \
    -pbkdf2 \
    -iter 200000 \
    -pass env:BACKUP_PASSPHRASE \
    -in "$ARCHIVE" \
    -out "$ENCRYPTED"

sha256sum "$ENCRYPTED" > "${ENCRYPTED}.sha256"

chmod 600 \
    "$ENCRYPTED" \
    "${ENCRYPTED}.sha256"

echo
echo "BACKUP CREATED:"
echo "$ENCRYPTED"
echo "${ENCRYPTED}.sha256"
