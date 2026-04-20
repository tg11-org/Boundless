#!/bin/bash
# Fix file permissions for the Boundless Docker setup.
# Run this on the server if you hit permission errors after pulling.
#
# Usage: sudo bash docker/fix-perms.sh

set -e
cd "$(dirname "$0")/.."

echo "Fixing ownership to root:root (Docker container runs as root)…"
chown -R root:root .

echo "Fixing directory permissions…"
find . -type d -exec chmod 755 {} +

echo "Fixing file permissions…"
find . -type f -exec chmod 644 {} +

echo "Making scripts executable…"
chmod +x docker/*.sh

echo "Done."
