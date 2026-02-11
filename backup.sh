#!/bin/bash
# Automated Backup Script
# Creates timestamped backups of the entire project

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_NAME="sage-reports-backup-${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

echo -e "${BLUE}=== Creating Backup ===${NC}"

# Create backups directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Create the backup (excluding node_modules, __pycache__, etc.)
echo -e "${BLUE}Copying files...${NC}"
rsync -av --progress \
    --exclude 'node_modules' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.git' \
    --exclude 'backups' \
    --exclude 'logs' \
    --exclude 'venv' \
    --exclude '.DS_Store' \
    . "${BACKUP_PATH}/"

# Create a manifest
echo "Backup created: ${TIMESTAMP}" > "${BACKUP_PATH}/BACKUP_INFO.txt"
echo "Git commit: $(git rev-parse HEAD)" >> "${BACKUP_PATH}/BACKUP_INFO.txt"
echo "Git branch: $(git branch --show-current)" >> "${BACKUP_PATH}/BACKUP_INFO.txt"

# Create a zip archive
echo -e "${BLUE}Creating archive...${NC}"
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"
rm -rf "${BACKUP_NAME}"
cd ..

BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)

echo ""
echo -e "${GREEN}✅ Backup created successfully!${NC}"
echo -e "${GREEN}Location: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz${NC}"
echo -e "${GREEN}Size: ${BACKUP_SIZE}${NC}"
echo ""
echo -e "${YELLOW}To restore from this backup:${NC}"
echo -e "  cd \"${BACKUP_DIR}\""
echo -e "  tar -xzf ${BACKUP_NAME}.tar.gz"
echo -e "  # Then copy files from ${BACKUP_NAME}/ to your project"

# Clean up old backups (keep last 10)
echo ""
echo -e "${BLUE}Cleaning up old backups...${NC}"
cd "${BACKUP_DIR}"
ls -t sage-reports-backup-*.tar.gz | tail -n +11 | xargs rm -f 2>/dev/null || true
BACKUP_COUNT=$(ls -1 sage-reports-backup-*.tar.gz 2>/dev/null | wc -l)
echo -e "${GREEN}Keeping ${BACKUP_COUNT} most recent backups${NC}"
