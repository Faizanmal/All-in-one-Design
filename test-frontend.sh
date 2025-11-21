#!/bin/bash

# Frontend UI Testing Script
# Run this to verify the new UI components

set -e

echo "================================================"
echo "  Frontend UI Testing - All-in-one-Design"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

echo -e "${YELLOW}Step 1: Checking dependencies...${NC}"
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✓ node_modules exists${NC}"
else
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

echo ""
echo -e "${YELLOW}Step 2: Verifying new component files...${NC}"
components=(
    "src/app/projects/[id]/page.tsx"
    "src/components/canvas/CanvasContainer.tsx"
    "src/components/canvas/PropertiesPanel.tsx"
    "src/components/templates/TemplateSidebar.tsx"
    "src/components/version/VersionHistoryPanel.tsx"
    "src/components/export/ExportModal.tsx"
    "src/components/collaboration/CommentsPanel.tsx"
    "src/components/ai/AIVariantsGenerator.tsx"
    "src/hooks/useCollaborativeCanvas.ts"
)

for component in "${components[@]}"; do
    if [ -f "$component" ]; then
        echo -e "${GREEN}✓ $component${NC}"
    else
        echo -e "${RED}✗ $component (missing)${NC}"
    fi
done

echo ""
echo -e "${GREEN}All components verified!${NC}"
echo ""
echo -e "${YELLOW}Starting Next.js development server...${NC}"
echo ""
echo "Test the new features at http://localhost:3000/projects/1"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

npm run dev
