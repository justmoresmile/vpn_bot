#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="/opt/vpn-bot"
ENV_FILE="$PROJECT_DIR/.env"
BACKUP_DIR="/var/backups/vpn-bot"

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

mkdir -p "$BACKUP_DIR"

STAMP="$(date +%Y%m%d_%H%M%S)"
WORKDIR="$(mktemp -d)"
ARCHIVE="$BACKUP_DIR/justvpn_${STAMP}.tar.gz"
ENCRYPTED="${ARCHIVE}.enc"

cleanup() {
    rm -rf "$WORKDIR"
    rm -f "$ARCHIVE"
}
trap cleanup EXIT

mkdir -p \
    "$WORKDIR/justvpn" \
    "$WORKDIR/x-ui" \
    "$WORKDIR/systemd" \
    "$WORKDIR/meta"

echo "===== BACKUP JUSTVPN DB ====="

if [[ -f "$PROJECT_DIR/data/vpn.db" ]]; then
    sqlite3 "$PROJECT_DIR/data/vpn.db" \
        ".backup '$WORKDIR/justvpn/vpn.db'"
fi

echo "===== BACKUP X-UI DB ====="

if [[ -f /etc/x-ui/x-ui.db ]]; then
    sqlite3 /etc/x-ui/x-ui.db \
        ".backup '$WORKDIR/x-ui/x-ui.db'"
fi

echo "===== BACKUP X-UI CERTIFICATES ====="

if [[ -d /root/cert ]]; then
    cp -a /root/cert "$WORKDIR/x-ui/"
fi

echo "===== BACKUP SYSTEMD ====="

if [[ -f /etc/systemd/system/justvpn.service ]]; then
    cp -a /etc/systemd/system/justvpn.service \
        "$WORKDIR/systemd/"
fi

echo "===== METADATA ====="

{
    echo "created_at=$(date --iso-8601=seconds)"
    echo "hostname=$(hostname)"
    echo "public_ip=${VPN_HOST:-unknown}"
    echo "git_commit=$(git -C "$PROJECT_DIR" rev-parse HEAD 2>/dev/null || echo unknown)"
    echo "xui_version=$(x-ui version 2>/dev/null | head -1 || true)"
    echo "python_version=$(python3 --version 2>&1)"
} > "$WORKDIR/meta/backup-info.txt"

tar -C "$WORKDIR" -czf "$ARCHIVE" .

openssl enc \
    -aes-256-cbc \
    -salt \
    -pbkdf2 \
    -iter 200000 \
    -pass env:BACKUP_PASSPHRASE \
    -in "$ARCHIVE" \
    -out "$ENCRYPTED"

sha256sum "$ENCRYPTED" > "${ENCRYPTED}.sha256"

chmod 600 "$ENCRYPTED" "${ENCRYPTED}.sha256"

echo
echo "BACKUP CREATED:"
echo "$ENCRYPTED"
echo "${ENCRYPTED}.sha256"
