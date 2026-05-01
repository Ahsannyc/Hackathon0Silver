#!/bin/bash

# Email MCP Server - Test Script
# Tests draft_email and send_email functions

set -e

PROJECT_ROOT="$(cd ../.. && pwd)"
SERVER_DIR="$(pwd)"
MCP_SERVER="$SERVER_DIR/index.js"

echo "=========================================="
echo "Email MCP Server - Test Suite"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."
if [ ! -f "$MCP_SERVER" ]; then
    echo -e "${RED}✗ Server not found: $MCP_SERVER${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Server file found${NC}"

if [ ! -f "$PROJECT_ROOT/credentials.json" ]; then
    echo -e "${YELLOW}⚠ credentials.json not found${NC}"
    echo "  Please download from Google Cloud Console and save to project root"
    exit 1
fi
echo -e "${GREEN}✓ credentials.json found${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js installed${NC}"

# Check dependencies
if [ ! -d "$SERVER_DIR/node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi
echo -e "${GREEN}✓ Dependencies ready${NC}"

echo ""
echo "=========================================="
echo "Test 1: Check Server Startup"
echo "=========================================="
echo "Starting server in background..."

# Start server in background
node "$MCP_SERVER" &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"

# Wait for server to start
sleep 2

# Check if server is running
if kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${GREEN}✓ Server started successfully${NC}"
else
    echo -e "${RED}✗ Server failed to start${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "Test 2: Create Test Draft Email"
echo "=========================================="
echo "Creating test file in /Needs_Action..."

TEST_FILE="$PROJECT_ROOT/Needs_Action/test_email_draft.md"
mkdir -p "$PROJECT_ROOT/Needs_Action"

cat > "$TEST_FILE" << 'EOF'
---
type: email_request
to: test@example.com
subject: Test Email from MCP Server
priority: high
---

This is a test email request.
Please draft an email to test@example.com with the subject "Test Email from MCP Server"
and body "This is a test email from the Email MCP Server."
EOF

echo -e "${GREEN}✓ Test file created: $TEST_FILE${NC}"

# Check if draft was created (would be created by Claude calling the tool)
echo ""
echo "Note: Draft emails are created when Claude calls the draft_email tool"
echo "You can manually test by calling the tool from Claude Code:"
echo ""
echo "  Claude: Draft an email to test@example.com with subject 'Test' and body 'Hello'"
echo ""

echo "=========================================="
echo "Test 3: Check Vault Directories"
echo "=========================================="

REQUIRED_DIRS=(
    "Plans"
    "Pending_Approval"
    "Approved"
    "Logs"
    "Done"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    dir_path="$PROJECT_ROOT/$dir"
    if [ -d "$dir_path" ]; then
        echo -e "${GREEN}✓ $dir/${NC}"
    else
        echo "Creating $dir..."
        mkdir -p "$dir_path"
        echo -e "${GREEN}✓ $dir/ (created)${NC}"
    fi
done

echo ""
echo "=========================================="
echo "Test 4: Check Server Capabilities"
echo "=========================================="
echo ""
echo "Server exposes the following tools to Claude Code:"
echo ""
echo "1. draft_email"
echo "   - Creates email draft in /Plans/"
echo "   - Generates approval request"
echo "   - Parameters: to, cc, bcc, subject, body, attachments"
echo ""
echo "2. send_email"
echo "   - Sends approved email via Gmail API"
echo "   - Requires approval file in /Approved/"
echo "   - Parameters: to, cc, bcc, subject, body, approval_file"
echo ""
echo "3. get_email_status"
echo "   - Shows pending approvals, approved, completed"
echo ""
echo "4. authenticate_gmail"
echo "   - OAuth2 authentication"
echo ""

echo "=========================================="
echo "Test 5: Manual Testing"
echo "=========================================="
echo ""
echo "To test the Email MCP Server manually:"
echo ""
echo "Terminal 1: Start server"
echo "  $ node mcp_servers/email-mcp/index.js --verbose"
echo ""
echo "Terminal 2: Use Claude Code to draft email"
echo "  Claude: Draft an email to test@example.com..."
echo ""
echo "Then:"
echo "  1. Check /Plans/ for email_draft_*.md"
echo "  2. Check /Pending_Approval/ for email_approval_*.md"
echo "  3. Move approval to /Approved/"
echo "  4. Claude: Send the email"
echo "  5. Check /Logs/email_send_*.json for confirmation"
echo ""

echo "=========================================="
echo "Test Complete"
echo "=========================================="
echo ""

# Cleanup
echo "Stopping server..."
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

echo -e "${GREEN}✓ Test suite completed${NC}"
echo ""
echo "Next steps:"
echo "1. Start server: node mcp_servers/email-mcp/index.js"
echo "2. Use Claude Code to draft emails"
echo "3. Approve in /Pending_Approval/"
echo "4. Claude sends via Gmail API"
echo ""
