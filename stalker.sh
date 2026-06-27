#!/bin/bash
# OMNI v2.0 — OSINT + Cyber Intelligence Tool
# Termux Android / Linux / macOS

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

clear
echo -e "${BOLD}${CYAN}"
cat << 'BANNER'
   _____ ___  ______  __ __
  / __  // _ \|  _  \/  |  \
  \/ /_// | | || |_| / __|  |
  /  __/| |_| ||  _ < |  |  |
  \___\ \___/\_|_| \_\___/__|
BANNER
echo -e "${NC}"
echo -e "  ${BOLD}INTELLIGENCE GATHERING SYSTEM${NC}"
echo -e "  v2.0 — Cyber Intelligence Edition"
echo -e "  Maigret + GitHub Intel + Reddit + Gravatar + Wayback"
echo -e "  Correlation Engine + Timeline + Risk Score + Dark Web"
echo ""

# ── Find Python ───────────────────────────────────────────────
PYTHON=""
for cmd in python3 python python3.12 python3.11 python3.10; do
    if command -v "$cmd" &>/dev/null; then
        VER=$($cmd -c "import sys; print(sys.version_info.major*10+sys.version_info.minor)" 2>/dev/null)
        if [ "$VER" -ge 30 ] 2>/dev/null; then PYTHON="$cmd"; break; fi
    fi
done
[ -z "$PYTHON" ] && err "Python 3.10+ not found!\n  Termux: pkg install python\n  Linux: sudo apt install python3"
ok "Python: $($PYTHON --version)"

# ── Detect environment ────────────────────────────────────────
IS_TERMUX=false; IS_LINUX=false; IS_MAC=false
[ -d /data/data/com.termux ] && IS_TERMUX=true
[[ "$OSTYPE" == "linux-gnu"* ]] && ! $IS_TERMUX && IS_LINUX=true
[[ "$OSTYPE" == "darwin"* ]] && IS_MAC=true

if $IS_TERMUX; then
    echo -e "  ${CYAN}Environment: Termux Android${NC}"
elif $IS_MAC; then
    echo -e "  ${CYAN}Environment: macOS${NC}"
else
    echo -e "  ${CYAN}Environment: Linux${NC}"
fi

# ── Check if first run / deps missing ────────────────────────
NEEDS_SETUP=false
$PYTHON -c "import httpx, click, rich, maigret" 2>/dev/null || NEEDS_SETUP=true

if $NEEDS_SETUP; then
    echo ""
    echo -e "  ${YELLOW}[SETUP]${NC} First run detected — installing dependencies..."
    echo ""

    # Base deps
    if $IS_TERMUX; then
        echo -e "  ${CYAN}[SETUP]${NC} Termux: Installing minimal deps (no C compilation)..."
        $PYTHON -m pip install --quiet httpx click rich python-dotenv jinja2 \
            googlesearch-python pyvis networkx phonenumbers python-whois \
            aiohttp aiofiles 2>/dev/null
        # Maigret minimal for Termux
        $PYTHON -m pip install --quiet aiohttp-socks certifi colorama html5lib \
            MarkupSafe PySocks socid-extractor soupsieve alive_progress \
            typing-extensions yarl platformdirs pycountry python-socks python-dateutil 2>/dev/null
        $PYTHON -m pip install -e maigret/ --no-deps --quiet 2>/dev/null || \
            $PYTHON -m pip install -e maigret/ --quiet 2>/dev/null
    else
        $PYTHON -m pip install --quiet httpx click rich python-dotenv jinja2 \
            googlesearch-python pyvis networkx phonenumbers python-whois \
            aiohttp aiofiles 2>/dev/null
        $PYTHON -m pip install -e maigret/ --quiet 2>/dev/null
    fi

    if $PYTHON -c "import httpx, click, rich" 2>/dev/null; then
        ok "Dependencies installed"
    else
        err "Dependency install failed. Try running manually:\n  pip install httpx click rich python-dotenv jinja2 pyvis networkx phonenumbers aiohttp\n  pip install -e maigret/"
    fi
fi

# ── Create dirs + load .env ───────────────────────────────────
mkdir -p output/images databaselocal 2>/dev/null

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    ok ".env created from template — edit .env to configure Telegram bot etc."
fi

if [ -f ".env" ]; then
    set -a; source .env 2>/dev/null; set +a
fi

# ── Battery check (Termux) ─────────────────────────────────────
if $IS_TERMUX && command -v termux-battery-status &>/dev/null; then
    BATTERY=$(termux-battery-status 2>/dev/null | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{const b=JSON.parse(d);console.log(b.percentage+'% '+b.status)}catch(e){}});" 2>/dev/null)
    if [ -n "$BATTERY" ]; then
        BATT_NUM=$(echo "$BATTERY" | grep -o '[0-9]*' | head -1)
        if [ "$BATT_NUM" -lt 20 ] 2>/dev/null; then
            warn "Battery low: $BATTERY — long scans may be interrupted"
        else
            ok "Battery: $BATTERY"
        fi
    fi
fi

# ── Check for updates ─────────────────────────────────────────
if command -v git &>/dev/null && [ -d ".git" ]; then
    BEHIND=$(git fetch --dry-run 2>&1 | grep -c "origin/main" || echo 0)
    if [ "$BEHIND" -gt "0" ] 2>/dev/null; then
        warn "Updates available! Run: git pull && bash stalker.sh"
    fi
fi

echo ""
echo -e "  ${BOLD}Ready!${NC} Launching OMNI Intelligence System..."
echo ""

# ── Launch ────────────────────────────────────────────────────
$PYTHON -m stalker.menu
