#!/bin/bash
# List All Checkpoints Script

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== All Checkpoints ===${NC}"
echo ""

# Check if there are any checkpoints
if ! git tag -l "checkpoint-*" | grep -q .; then
    echo -e "${YELLOW}No checkpoints found yet.${NC}"
    echo "Create your first checkpoint with: ./save_checkpoint.sh \"description\""
    exit 0
fi

# List all checkpoint tags with their messages
git tag -l "checkpoint-*" --sort=-creatordate | while read tag; do
    echo -e "${GREEN}${tag}${NC}"
    git tag -l --format='%(contents:subject)' "$tag" | sed 's/^/  /'
    git log -1 --format="  Date: %ai" "$tag"
    echo ""
done

echo -e "${YELLOW}To restore a checkpoint:${NC}"
echo -e "  ./restore_checkpoint.sh <tag-name>"
echo ""
echo -e "${YELLOW}Current branch status:${NC}"
git log -1 --oneline
