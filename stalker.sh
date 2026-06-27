#!/bin/bash
# Stalker - OSINT Investigation Tool (Termux / Linux)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  Stalker - OSINT Investigation Tool"
echo "========================================"
echo ""

# Find Python
PYTHON=""
if command -v python3 &>/dev/null; then PYTHON="python3"
elif command -v python &>/dev/null; then PYTHON="python"
else
    echo "[ERROR] Python not found!"
    echo "  Termux: pkg install python"
    echo "  Linux:  sudo apt install python3 python3-pip"
    read -p "Press Enter to exit..."
    exit 1
fi
echo "[OK] Python: $($PYTHON --version)"
echo ""

# Detect Termux
IS_TERMUX=false
[ -d /data/data/com.termux ] && IS_TERMUX=true

# Step 1: install base dependencies (ADDED: python-whois & aiohttp)
echo "[SETUP] Installing base dependencies..."
$PYTHON -m pip install httpx click rich python-dotenv jinja2 googlesearch-python pyvis networkx phonenumbers python-whois aiohttp --quiet
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install base dependencies!"
    echo "  Try: pip install httpx click rich python-dotenv jinja2 googlesearch-python python-whois aiohttp"
    read -p "Press Enter to exit..."
    exit 1
fi
echo "[OK] Base dependencies installed"

# Step 2: install maigret — minimal deps for fast Termux install
echo "[SETUP] Installing Maigret (core search only)..."
INSTALL_OK=false
if $IS_TERMUX; then
    # On Termux: avoid C-compilation-heavy packages we don't use
    echo "       Termux: installing maigret with minimal dependencies..."
    $PYTHON -m pip install aiohttp aiohttp-socks certifi colorama html5lib Jinja2 \
        MarkupSafe PySocks requests socid-extractor soupsieve alive_progress \
        typing-extensions yarl platformdirs pycountry python-socks python-dateutil --quiet
    if [ $? -eq 0 ]; then
        $PYTHON -m pip install -e maigret/ --no-deps --quiet && INSTALL_OK=true
    fi
else
    # Linux: full install (faster with proper build tools)
    $PYTHON -m pip install -e maigret/ --quiet && INSTALL_OK=true
fi

if ! $INSTALL_OK; then
    if $IS_TERMUX; then
        echo "[WARN] Minimal install failed, trying with aiodns stripped..."
        sed -i '/aiodns/d' maigret/pyproject.toml
        $PYTHON -m pip install aiohttp aiohttp-socks certifi colorama html5lib Jinja2 \
            MarkupSafe PySocks requests socid-extractor soupsieve alive_progress \
            typing-extensions yarl platformdirs pycountry --quiet
        if [ $? -eq 0 ]; then
            $PYTHON -m pip install -e maigret/ --no-deps --quiet && INSTALL_OK=true
        fi
        git checkout maigret/pyproject.toml 2>/dev/null
    else
        echo "[WARN] Full install failed, retrying with aiodns stripped..."
        sed -i '/aiodns/d' maigret/pyproject.toml
        $PYTHON -m pip install -e maigret/ --quiet && INSTALL_OK=true
        git checkout maigret/pyproject.toml 2>/dev/null
    fi
fi

if ! $INSTALL_OK; then
    echo "[ERROR] Maigret install still failed."
    if $IS_TERMUX; then
        echo "  Make sure build tools are installed:"
        echo "    pkg install binutils clang build-essential python-static"
    else
        echo "  Install build tools first:"
        echo "    sudo apt install python3-dev build-essential"
    fi
    echo "  Then re-run: bash stalker.sh"
    read -p "Press Enter to exit..."
    exit 1
fi
echo "[OK] Maigret installed"

# Create dirs
mkdir -p output/images

# Load .env (dotenv for Termux)
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
elif [ -f ".env.example" ]; then
    cp .env.example .env
    set -a
    source .env
    set +a
fi

# Launch menu
$PYTHON -m stalker.menu
