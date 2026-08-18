#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="/opt/vpn-bot"
ENV_FILE="$PROJECT_DIR/.env"

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 /path/to/backup.tar.gz.enc"
    exit 1
fi

BACKUP="$1"
CHECKSUM="${BACKUP}.sha256"

if [[ ! -f "$BACKUP" ]]; then
    echo "ERROR: backup not found: $BACKUP"
    exit 1
fi

if [[ ! -f "$CHECKSUM" ]]; then
    echo "ERROR: checksum not found: $CHECKSUM"
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

TMPDIR="$(mktemp -d)"
DECRYPTED="$TMPDIR/backup.tar.gz"
EXTRACTED="$TMPDIR/extracted"

cleanup() {
    rm -rf "$TMPDIR"
}
trap cleanup EXIT

mkdir -p "$EXTRACTED"

echo "===== VERIFY CHECKSUM ====="
(
    cd "$(dirname "$BACKUP")"
    sha256sum -c "$(basename "$CHECKSUM")"
)

echo
echo "===== DECRYPT ====="

openssl enc \
    -d \
    -aes-256-cbc \
    -pbkdf2 \
    -iter 200000 \
    -pass env:BACKUP_PASSPHRASE \
    -in "$BACKUP" \
    -out "$DECRYPTED"

tar -xzf "$DECRYPTED" -C "$EXTRACTED"

echo
echo "===== STOP SERVICES ====="

systemctl stop justvpn 2>/dev/null || true
systemctl stop x-ui 2>/dev/null || true

echo
echo "===== RESTORE JUSTVPN DB ====="

mkdir -p "$PROJECT_DIR/data"

if [[ -f "$EXTRACTED/justvpn/vpn.db" ]]; then
    cp -a "$EXTRACTED/justvpn/vpn.db" \
        "$PROJECT_DIR/data/vpn.db"

    chmod 600 "$PROJECT_DIR/data/vpn.db"
fi

echo
echo "===== RESTORE X-UI DB ====="

if [[ -f "$EXTRACTED/x-ui/x-ui.db" ]]; then
    mkdir -p /etc/x-ui

    cp -a "$EXTRACTED/x-ui/x-ui.db" \
        /etc/x-ui/x-ui.db

    chmod 600 /etc/x-ui/x-ui.db
else
    echo "ERROR: x-ui database missing from backup"
    exit 1
fi

echo
echo "===== RESTORE X-UI CERTS ====="

if [[ -d "$EXTRACTED/x-ui/cert" ]]; then
    rm -rf /root/cert
    cp -a "$EXTRACTED/x-ui/cert" /root/cert
fi

echo
echo "===== RESTORE SYSTEMD ====="

if [[ -f "$EXTRACTED/systemd/justvpn.service" ]]; then
    cp -a "$EXTRACTED/systemd/justvpn.service" \
        /etc/systemd/system/justvpn.service
fi

systemctl daemon-reload

echo
echo "===== START X-UI ====="

systemctl enable x-ui >/dev/null 2>&1 || true
systemctl restart x-ui

sleep 3

if ! systemctl is-active --quiet x-ui; then
    echo "ERROR: x-ui failed to start"
    journalctl -u x-ui -n 50 --no-pager
    exit 1
fi

echo
echo "===== RESTORED INBOUNDS ====="

sqlite3 -header -column /etc/x-ui/x-ui.db "
SELECT id,remark,protocol,listen,port,enable
FROM inbounds
ORDER BY id;
"

echo
echo "RESTORE COMPLETED"
