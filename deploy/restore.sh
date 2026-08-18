#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="/opt/vpn-bot"

if [[ "$(id -u)" -ne 0 ]]; then
    echo "ERROR: run as root"
    exit 1
fi

if [[ $# -ne 1 ]]; then
    echo "Usage:"
    echo "  $0 /var/backups/vpn-bot/justvpn_YYYYMMDD_HHMMSS.tar.gz.enc"
    exit 1
fi

BACKUP_FILE="$1"
CHECKSUM_FILE="${BACKUP_FILE}.sha256"

if [[ ! -f "$BACKUP_FILE" ]]; then
    echo "ERROR: backup not found: $BACKUP_FILE"
    exit 1
fi

if [[ ! -f "$CHECKSUM_FILE" ]]; then
    echo "ERROR: checksum not found: $CHECKSUM_FILE"
    exit 1
fi

if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    echo "ERROR: $PROJECT_DIR/.env is required to read BACKUP_PASSPHRASE"
    echo "Create .env and set BACKUP_PASSPHRASE first."
    exit 1
fi

set -a
source "$PROJECT_DIR/.env"
set +a

if [[ -z "${BACKUP_PASSPHRASE:-}" ]]; then
    echo "ERROR: BACKUP_PASSPHRASE is empty"
    exit 1
fi

WORKDIR="$(mktemp -d)"
ARCHIVE="$WORKDIR/backup.tar.gz"
EXTRACTED="$WORKDIR/extracted"

cleanup() {
    rm -rf "$WORKDIR"
}

trap cleanup EXIT

mkdir -p "$EXTRACTED"

echo "===== SHA256 ====="

(
    cd "$(dirname "$BACKUP_FILE")"
    sha256sum -c "$(basename "$CHECKSUM_FILE")"
)

echo
echo "===== DECRYPT ====="

openssl enc \
    -d \
    -aes-256-cbc \
    -pbkdf2 \
    -iter 200000 \
    -pass env:BACKUP_PASSPHRASE \
    -in "$BACKUP_FILE" \
    -out "$ARCHIVE"

echo "DECRYPTION OK"

echo
echo "===== ARCHIVE ====="

tar -tzf "$ARCHIVE" >/dev/null
tar -xzf "$ARCHIVE" -C "$EXTRACTED"

echo "ARCHIVE OK"

echo
echo "===== STOP JUSTVPN ====="

systemctl stop justvpn 2>/dev/null || true

echo
echo "===== RESTORE ENV ====="

if [[ -f "$EXTRACTED/env/.env" ]]; then

    cp -a "$EXTRACTED/env/.env" \
        "$PROJECT_DIR/.env"

    chmod 600 "$PROJECT_DIR/.env"

    echo ".env restored"

else

    echo "WARNING: .env missing from backup"

fi

echo
echo "===== RESTORE JUSTVPN DB ====="

mkdir -p "$PROJECT_DIR/data"

if [[ -f "$EXTRACTED/justvpn/vpn.db" ]]; then

    cp -a \
        "$EXTRACTED/justvpn/vpn.db" \
        "$PROJECT_DIR/data/vpn.db"

    chmod 600 "$PROJECT_DIR/data/vpn.db"

    echo "vpn.db restored"

else

    echo "WARNING: vpn.db missing from backup"

fi

echo
echo "===== RESTORE SYSTEMD ====="

if [[ -f "$EXTRACTED/systemd/justvpn.service" ]]; then

    cp -a \
        "$EXTRACTED/systemd/justvpn.service" \
        /etc/systemd/system/justvpn.service

    chmod 644 /etc/systemd/system/justvpn.service

    echo "justvpn.service restored"

fi

echo
echo "===== RESTORE NGINX ====="

if [[ -f "$EXTRACTED/nginx/justvpn-web" ]]; then

    mkdir -p \
        /etc/nginx/sites-available \
        /etc/nginx/sites-enabled

    cp -a \
        "$EXTRACTED/nginx/justvpn-web" \
        /etc/nginx/sites-available/justvpn-web

    ln -sf \
        /etc/nginx/sites-available/justvpn-web \
        /etc/nginx/sites-enabled/justvpn-web

    echo "nginx config restored"

fi

systemctl daemon-reload

echo
echo "===== CONFIG CHECK ====="

if command -v nginx >/dev/null 2>&1; then
    nginx -t
fi

echo
echo "RESTORE COMPLETED"
echo
echo "Run:"
echo "  cd $PROJECT_DIR"
echo "  ./deploy/install.sh"
echo
