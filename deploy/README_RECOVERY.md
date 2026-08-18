# JustVPN Recovery Kit

## Production VPN layout

Do not move or proxy the VPN ports unless explicitly planned.

- VLESS Reality: TCP 443
- Xray WireGuard: UDP port stored in 3x-ui DB
- Backend: localhost port 8000
- 3x-ui database: /etc/x-ui/x-ui.db
- JustVPN database: /opt/vpn-bot/data/vpn.db

## WireGuard Windows roaming

Generated Windows-compatible WireGuard configs should use:

AllowedIPs = 0.0.0.0/1, 128.0.0.0/1
PersistentKeepalive = 25

Using 0.0.0.0/0 caused unstable behavior when changing Wi-Fi networks
in the tested Windows WireGuard client.

## Fresh installation

1. Install Ubuntu.
2. Install and configure 3x-ui.
3. Configure VLESS Reality and WireGuard.
4. Configure GitHub deploy key.
5. Clone repository or run bootstrap.
6. Copy .env.example to .env.
7. Fill secrets locally.
8. Run:

   bash deploy/install.sh

## Backup

Run:

    bash deploy/backup.sh

The backup contains:

- JustVPN SQLite database
- 3x-ui SQLite database
- /root/cert if present
- JustVPN systemd service
- recovery metadata

Backups are encrypted using AES-256-CBC/PBKDF2 with
BACKUP_PASSPHRASE from .env.

## Verify backup

Run:

    bash deploy/verify_backup.sh /var/backups/vpn-bot/FILE.tar.gz.enc

Never rely on an unverified backup.

## Restore

Prepare the repository and .env first, then run:

    bash deploy/restore.sh /path/to/FILE.tar.gz.enc

After restoring x-ui, verify VPN ports before starting other public
services.

## Security

Never commit:

- .env
- private SSH keys
- WireGuard private keys
- Reality private keys
- YooKassa secrets
- Telegram bot token
- JWT secret
- 3x-ui API token

The repository may contain .env.example with empty secret values only.
