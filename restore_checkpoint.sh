#!/bin/bash
# Restore Checkpoint Script
# Usage: ./restore_checkpoint.sh <checkpoint-tag-name>
# IMPORTANT: This requires EXPLICIT user confirmation

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if tag name provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide a checkpoint tag name${NC}"
    echo "Usage: ./restore_checkpoint.sh <checkpoint-tag-name>"
    echo ""
    echo "Available checkpoints:"
    ./list_checkpoints.sh
    exit 1
fi

TAG_NAME="$1"

# Verify tag exists
if ! git tag -l | grep -q "^${TAG_NAME}$"; then
    echo -e "${RED}Error: Checkpoint '${TAG_NAME}' not found${NC}"
    echo ""
    echo "Available checkpoints:"
    ./list_checkpoints.sh
    exit 1
fi

echo -e "${RED}⚠️  WARNING: CHECKPOINT RESTORE ⚠️${NC}"
echo -e "${RED}This will DISCARD all uncommitted changes!${NC}"
echo ""
echo -e "${BLUE}Current state:${NC}"
git status --short
echo ""
echo -e "${BLUE}Checkpoint to restore:${NC}"
echo -e "${GREEN}${TAG_NAME}${NC}"
git tag -l --format='%(contents:subject)' "$TAG_NAME" | sed 's/^/  /'
git log -1 --format="  Date: %ai" "$TAG_NAME"
echo ""
echo -e "${YELLOW}You are about to:${NC}"
echo "  1. Discard ALL uncommitted changes"
echo "  2. Reset the code to the checkpoint: ${TAG_NAME}"
echo ""
echo -e "${RED}THIS CANNOT BE UNDONE!${NC}"
echo ""
read -p "Are you ABSOLUTELY SURE you want to restore this checkpoint? (yes/no) " -r
echo ""

if [[ ! $REPLY == "yes" ]]; then
    echo -e "${YELLOW}Restore cancelled - no changes made${NC}"
    exit 0
fi

# Extra confirmation
read -p "Type 'RESTORE' in all caps to confirm: " -r
echo ""

if [[ ! $REPLY == "RESTORE" ]]; then
    echo -e "${YELLOW}Restore cancelled - no changes made${NC}"
    exit 0
fi

# Create a safety backup before restore
BACKUP_TAG="pre-restore-backup-$(date +%Y%m%d-%H%M%S)"
echo -e "${BLUE}Creating safety backup: ${BACKUP_TAG}${NC}"
git add -A
git commit -m "Safety backup before restore to ${TAG_NAME}" || true
git tag "${BACKUP_TAG}" || true

# Restore to checkpoint
echo -e "${BLUE}Restoring to checkpoint...${NC}"
git reset --hard "${TAG_NAME}"

echo ""
echo -e "${GREEN}✅ Checkpoint restored successfully!${NC}"
echo ""
echo -e "${YELLOW}Note: A safety backup was created at: ${BACKUP_TAG}${NC}"
echo -e "${YELLOW}If you need to undo this restore, run:${NC}"
echo -e "  git reset --hard ${BACKUP_TAG}"
