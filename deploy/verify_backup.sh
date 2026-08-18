#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="/opt/vpn-bot"

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
    echo "ERROR: $PROJECT_DIR/.env not found"
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
echo "===== JUSTVPN DB ====="

if [[ -f "$EXTRACTED/justvpn/vpn.db" ]]; then

    RESULT="$(
        sqlite3 \
            "$EXTRACTED/justvpn/vpn.db" \
            "PRAGMA integrity_check;"
    )"

    echo "$RESULT"

    if [[ "$RESULT" != "ok" ]]; then
        echo "ERROR: JustVPN database integrity failed"
        exit 1
    fi

    for table in \
        users \
        servers \
        subscriptions \
        payments
    do

        EXISTS="$(
            sqlite3 "$EXTRACTED/justvpn/vpn.db" \
                "SELECT COUNT(*)
                 FROM sqlite_master
                 WHERE type='table'
                   AND name='$table';"
        )"

        if [[ "$EXISTS" == "1" ]]; then

            COUNT="$(
                sqlite3 "$EXTRACTED/justvpn/vpn.db" \
                    "SELECT COUNT(*) FROM $table;"
            )"

            echo "$table=$COUNT"

        else

            echo "$table=NOT_PRESENT"

        fi

    done

else

    echo "WARNING: JustVPN DB not present"

fi

echo
echo "===== ENV ====="

if [[ -f "$EXTRACTED/env/.env" ]]; then
    echo ".env = PRESENT"
else
    echo ".env = MISSING"
    exit 1
fi

echo
echo "===== SYSTEMD ====="

if [[ -f "$EXTRACTED/systemd/justvpn.service" ]]; then
    echo "justvpn.service = PRESENT"
else
    echo "justvpn.service = MISSING"
fi

echo
echo "===== NGINX ====="

if [[ -f "$EXTRACTED/nginx/justvpn-web" ]]; then
    echo "justvpn-web = PRESENT"
else
    echo "justvpn-web = MISSING"
fi

echo
echo "===== METADATA ====="

cat \
    "$EXTRACTED/meta/backup-info.txt" \
    2>/dev/null || true

echo
echo "BACKUP VERIFIED SUCCESSFULLY"
