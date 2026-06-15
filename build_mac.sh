#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  Yirra Care Agents — macOS Build Script
#  Produces: dist/Yirra Care Agents.app  (double-clickable)
#
#  Requirements: run on macOS with Python 3.11 venv already set up.
#  Usage:  chmod +x build_mac.sh && ./build_mac.sh
# ═══════════════════════════════════════════════════════════════════
set -e
cd "$(dirname "$0")"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║      Yirra Care Agents — macOS Build             ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ── 1. Activate venv ──────────────────────────────────────────────
if [ ! -f ".venv/bin/activate" ]; then
    echo -e "${RED}❌  .venv not found.${NC}"
    echo "    Run:  python3.11 -m venv .venv && pip install -r requirements.txt"
    exit 1
fi
source .venv/bin/activate
echo -e "${GREEN}✓${NC}  Virtual environment activated"

# ── 2. Install PyInstaller ────────────────────────────────────────
echo "▸  Installing PyInstaller..."
pip install pyinstaller --quiet --upgrade
echo -e "${GREEN}✓${NC}  PyInstaller ready"

# ── 3. Make sure streamlit is in requirements ─────────────────────
pip install streamlit --quiet
echo -e "${GREEN}✓${NC}  Streamlit confirmed"

# ── 4. Clean previous builds ─────────────────────────────────────
echo "▸  Cleaning previous builds..."
rm -rf build dist __pycache__

# ── 5. Build the .app bundle ──────────────────────────────────────
echo ""
echo -e "${YELLOW}▸  Building macOS app bundle (this takes 5–10 min)...${NC}"
echo ""
pyinstaller yirra_care_mac.spec --noconfirm --clean

# ── 6. Copy user data into the app bundle ────────────────────────
#    The launcher looks for files next to the exe:
#    Yirra Care Agents.app/Contents/MacOS/
APP_MACOS="dist/Yirra Care Agents.app/Contents/MacOS"
echo ""
echo "▸  Copying data files into app bundle..."

mkdir -p "$APP_MACOS/data"
mkdir -p "$APP_MACOS/exports"

# .env (API keys — required)
if [ -f ".env" ]; then
    cp .env "$APP_MACOS/.env"
    echo -e "${GREEN}  ✓${NC}  .env"
else
    cp .env.template "$APP_MACOS/.env.template" 2>/dev/null || true
    echo -e "${YELLOW}  ⚠${NC}  No .env found — user must configure API keys after install"
fi

# Gmail OAuth credentials
if [ -f "client_secret.json" ]; then
    cp client_secret.json "$APP_MACOS/client_secret.json"
    echo -e "${GREEN}  ✓${NC}  client_secret.json"
fi

# Database (if exists — carries over contacts)
if [ -f "data/yirra_referrals.sqlite" ]; then
    cp data/yirra_referrals.sqlite "$APP_MACOS/data/"
    echo -e "${GREEN}  ✓${NC}  database"
fi

# Campaigns
if [ -f "data/campaigns.json" ]; then
    cp data/campaigns.json "$APP_MACOS/data/"
    echo -e "${GREEN}  ✓${NC}  campaigns.json"
fi

# ── 7. Final output ───────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo -e "║  ${GREEN}✅  Build complete!${NC}                              ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "  App:  dist/Yirra Care Agents.app"
APP_SIZE=$(du -sh "dist/Yirra Care Agents.app" 2>/dev/null | cut -f1)
echo "  Size: $APP_SIZE"
echo ""
echo "  To distribute:"
echo "    cd dist"
echo "    zip -r 'Yirra Care Agents.zip' 'Yirra Care Agents.app'"
echo ""
echo "  To test right now:"
echo "    open 'dist/Yirra Care Agents.app'"
echo ""
