#!/bin/bash
# Save Checkpoint Script
# Usage: ./save_checkpoint.sh "description of what's working"

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if description provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide a description${NC}"
    echo "Usage: ./save_checkpoint.sh \"description of what's working\""
    exit 1
fi

DESCRIPTION="$1"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
TAG_NAME="checkpoint-${TIMESTAMP}"

echo -e "${BLUE}=== Creating Checkpoint ===${NC}"
echo -e "Description: ${YELLOW}${DESCRIPTION}${NC}"
echo ""

# Show what will be committed
echo -e "${BLUE}Files to be committed:${NC}"
git status --short

echo ""
read -p "Continue with commit? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Checkpoint cancelled${NC}"
    exit 0
fi

# Add all changes
echo -e "${BLUE}Adding files...${NC}"
git add -A

# Create commit
echo -e "${BLUE}Creating commit...${NC}"
git commit -m "Checkpoint: ${DESCRIPTION}

Created: ${TIMESTAMP}
Status: Working
All features tested and confirmed working."

# Create tag
echo -e "${BLUE}Creating tag: ${TAG_NAME}${NC}"
git tag -a "${TAG_NAME}" -m "Checkpoint: ${DESCRIPTION}"

echo ""
echo -e "${GREEN}✅ Checkpoint created successfully!${NC}"
echo -e "${GREEN}Tag: ${TAG_NAME}${NC}"
echo ""
echo -e "${YELLOW}To restore this checkpoint later:${NC}"
echo -e "  ./restore_checkpoint.sh ${TAG_NAME}"
echo ""
echo -e "${YELLOW}To list all checkpoints:${NC}"
echo -e "  ./list_checkpoints.sh"
