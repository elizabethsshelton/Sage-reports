#!/bin/bash
# Quick Commit Script
# Usage: ./quick_commit.sh "what I changed"

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if description provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide a commit message${NC}"
    echo "Usage: ./quick_commit.sh \"what I changed\""
    echo ""
    echo "Example: ./quick_commit.sh \"Fixed auto-save bug\""
    exit 1
fi

MESSAGE="$1"

echo -e "${BLUE}=== Quick Commit ===${NC}"
echo -e "Message: ${YELLOW}${MESSAGE}${NC}"
echo ""

# Show what will be committed
echo -e "${BLUE}Files to be committed:${NC}"
git status --short

if ! git status --short | grep -q .; then
    echo -e "${YELLOW}No changes to commit!${NC}"
    exit 0
fi

echo ""

# Add all changes
echo -e "${BLUE}Adding files...${NC}"
git add -A

# Create commit
echo -e "${BLUE}Creating commit...${NC}"
git commit -m "${MESSAGE}"

echo ""
echo -e "${GREEN}✅ Changes committed successfully!${NC}"
echo ""
echo -e "${YELLOW}Tip: When this is a fully working state, create a checkpoint:${NC}"
echo -e "  ./save_checkpoint.sh \"${MESSAGE}\""
