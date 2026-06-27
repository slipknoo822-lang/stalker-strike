#!/data/data/com.termux/files/usr/bin/bash
# =============================================================
#  Stalker Strike — One-Click Termux Installer
#  Run once: bash install_termux.sh
# =============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; }
info() { echo -e "${CYAN}[INFO]${NC} $1"; }
head() { echo -e "\n${BOLD}$1${NC}"; echo "$(printf '─%.0s' {1..50})"; }

clear
echo -e "${BOLD}"
cat << 'BANNER'
  _____ _______       _      _  ________ _____
 / ____|__   __|/\   | |    | |/ /  ____|  __ \
| (___    | |  /  \  | |    | ' /| |__  | |__) |
 \___ \   | | / /\ \ | |    |  < |  __| |  _  /
 ____) |  | |/ ____ \| |____| . \| |____| | \ \
|_____/   |_/_/    \_\______|_|\_\______|_|  \_\

     All-in-One OSINT Tool — Termux Installer
BANNER
echo -e "${NC}"

# ── 0. Verify Termux ──────────────────────────────────────────
if [ ! -d "/data/data/com.termux" ]; then
    err "This installer is for Termux only!"
    err "On Linux/Mac, run: bash stalker.sh"
    exit 1
fi
ok "Running inside Termux"

# ── 1. Update pkg repos ───────────────────────────────────────
head "Step 1: Update package repositories"
pkg update -y -o Dpkg::Options::="--force-confnew" 2>/dev/null || warn "pkg update had issues, continuing..."
ok "Repos updated"

# ── 2. Install system packages ────────────────────────────────
head "Step 2: Install system packages"
PKGS="python git curl wget binutils clang libxml2 libxslt openssl libjpeg-turbo"
info "Installing: $PKGS"
pkg install -y $PKGS 2>/dev/null
ok "System packages installed"

# ── 3. Install Termux:API (optional) ─────────────────────────
head "Step 3: Termux:API (optional — for notifications)"
if command -v termux-notification &>/dev/null; then
    ok "termux-api already installed"
else
    info "Installing termux-api (enables push notifications, vibration, clipboard)..."
    pkg install -y termux-api 2>/dev/null
    if command -v termux-notification &>/dev/null; then
        ok "termux-api installed — also install Termux:API companion app from F-Droid!"
    else
        warn "termux-api not found — notifications will be disabled (non-critical)"
    fi
fi

# ── 4. Upgrade pip ────────────────────────────────────────────
head "Step 4: Upgrade pip"
pip install --upgrade pip --quiet
ok "pip upgraded"

# ── 5. Install Python base deps ───────────────────────────────
head "Step 5: Install Python dependencies"
info "Installing base packages..."
pip install --quiet \
    httpx \
    click \
    rich \
    python-dotenv \
    jinja2 \
    googlesearch-python \
    pyvis \
    networkx \
    phonenumbers \
    python-whois \
    aiohttp \
    aiofiles \
    Pillow

if [ $? -ne 0 ]; then
    err "Base package install failed!"
    info "Try manually: pip install httpx click rich python-dotenv jinja2"
    exit 1
fi
ok "Base Python packages installed"

# ── 6. Install Maigret ────────────────────────────────────────
head "Step 6: Install Maigret (OSINT search engine)"
info "Installing Maigret minimal deps for Termux..."

# Maigret extra deps (no C-compilation)
pip install --quiet \
    aiohttp-socks \
    certifi \
    colorama \
    html5lib \
    MarkupSafe \
    PySocks \
    socid-extractor \
    soupsieve \
    alive_progress \
    typing-extensions \
    yarl \
    platformdirs \
    pycountry \
    python-socks \
    python-dateutil

# Install maigret from local clone
if pip install -e maigret/ --no-deps --quiet 2>/dev/null; then
    ok "Maigret installed (minimal, no-deps)"
else
    warn "Maigret minimal install failed, trying full install..."
    pip install -e maigret/ --quiet 2>/dev/null || {
        warn "Maigret install had issues — username search may be limited"
    }
fi

# ── 7. Create .env config ─────────────────────────────────────
head "Step 7: Configure .env"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        ok ".env created from .env.example"
    else
        cat > .env << 'ENVEOF'
# Stalker Strike Configuration
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
EXIFTOOLS_API_KEY=
NUMVERIFY_API_KEY=
VERIPHONE_API_KEY=
MAIGRET_TIMEOUT=60
MAIGRET_MAX_SITES=300
OUTPUT_DIR=output
STEALTH_MODE=false
STEALTH_RANDOM_UA=true
REQUEST_DELAY=0.5
FACE_SEARCH_MAX_AVATARS=3
ENVEOF
        ok ".env created with defaults"
    fi
else
    ok ".env already exists"
fi

# ── 8. Create output dirs ─────────────────────────────────────
mkdir -p output/images
ok "Output directories created"

# ── 9. Make scripts executable ────────────────────────────────
chmod +x stalker.sh install_termux.sh 2>/dev/null
ok "Scripts made executable"

# ── 10. Verify installation ───────────────────────────────────
head "Step 10: Verify installation"
PYTHON=$(command -v python3 || command -v python)
echo -n "  Python: "
$PYTHON --version

echo -n "  Stalker modules: "
if $PYTHON -c "import stalker" 2>/dev/null; then
    echo "OK"
else
    echo "WARNING — may need to run from project root"
fi

echo -n "  Maigret: "
if $PYTHON -c "import maigret" 2>/dev/null; then
    echo "OK"
else
    echo "PARTIAL (re-run if username search fails)"
fi

echo -n "  Termux:API: "
command -v termux-notification &>/dev/null && echo "OK" || echo "Not installed (optional)"

# ── Done ──────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${GREEN}║   Installation complete! 🎉              ║${NC}"
echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}Quick Start:${NC}"
echo -e "  ${CYAN}bash stalker.sh${NC}              # Interactive menu"
echo -e "  ${CYAN}python -m stalker.cli --help${NC}  # CLI commands"
echo ""
echo -e "  ${BOLD}CLI Examples:${NC}"
echo -e "  ${CYAN}python -m stalker.cli search johndoe${NC}"
echo -e "  ${CYAN}python -m stalker.cli email test@gmail.com${NC}"
echo -e "  ${CYAN}python -m stalker.cli phone +62812345678${NC}"
echo -e "  ${CYAN}python -m stalker.cli ip 8.8.8.8${NC}"
echo ""
echo -e "  ${BOLD}Optional — Telegram Bot (auto-send reports):${NC}"
echo -e "  Edit ${CYAN}.env${NC} → set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID"
echo ""
