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

echo "===== SHA256 ====="
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

echo "DECRYPTION OK"

echo
echo "===== ARCHIVE ====="

tar -tzf "$DECRYPTED" >/dev/null
tar -xzf "$DECRYPTED" -C "$EXTRACTED"

echo "ARCHIVE OK"

echo
echo "===== JUSTVPN DB ====="

if [[ -f "$EXTRACTED/justvpn/vpn.db" ]]; then
    sqlite3 "$EXTRACTED/justvpn/vpn.db" "PRAGMA integrity_check;"

    sqlite3 "$EXTRACTED/justvpn/vpn.db" "
        SELECT 'users=' || COUNT(*) FROM users;
        SELECT 'servers=' || COUNT(*) FROM servers;
        SELECT 'subscriptions=' || COUNT(*) FROM subscriptions;
    "
else
    echo "JustVPN DB not present"
fi

echo
echo "===== X-UI DB ====="

if [[ -f "$EXTRACTED/x-ui/x-ui.db" ]]; then
    sqlite3 "$EXTRACTED/x-ui/x-ui.db" "PRAGMA integrity_check;"

    sqlite3 "$EXTRACTED/x-ui/x-ui.db" "
        SELECT 'inbounds=' || COUNT(*) FROM inbounds;
    "
else
    echo "ERROR: x-ui DB missing"
    exit 1
fi

echo
echo "===== X-UI INBOUNDS ====="

sqlite3 -header -column "$EXTRACTED/x-ui/x-ui.db" "
SELECT id, remark, protocol, listen, port, enable
FROM inbounds
ORDER BY id;
"

echo
echo "===== CERTIFICATES ====="

if [[ -d "$EXTRACTED/x-ui/cert" ]]; then
    find "$EXTRACTED/x-ui/cert" -type f | wc -l
else
    echo "No x-ui certificate directory in backup"
fi

echo
echo "===== METADATA ====="

cat "$EXTRACTED/meta/backup-info.txt" 2>/dev/null || true

echo
echo "BACKUP VERIFIED SUCCESSFULLY"
