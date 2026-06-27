# OMNI v2.0

All-in-one OSINT investigation CLI tool. Enter a username, email, or phone → auto-detect input type → run targeted investigation across 600+ social networks, 30+ email platforms, 6 phone carriers, dark web sources, and more.

```
   _____ ___  ______  __ __
  / __  // _ \|  _  \/  |  \
  \/ /_// | | || |_| / __|  |
  /  __/| |_| ||  _ < |  |  |
  \___\ \___/\_|_| \_\___/__|

INTELLIGENCE GATHERING SYSTEM v2.0
```

---

## Features

### Core Investigation
- **Username Search** — 600+ social platforms via Maigret engine (ids_data extraction, avatars, bios)
- **Custom API Enrichment** — Instagram, TikTok, Twitter/X, YouTube, GitHub via Xemoz API
- **Smart Dork** — Auto-generated Google + DuckDuckGo queries from all extracted data
- **Recursive Search** — Re-runs username search on newly discovered usernames/IDs (depth 2)
- **Social Graph** — Interactive network visualization of found accounts (pyvis)
- **Auto-detection** — Automatically detects username / email / phone from input
- **Stealth Mode** — Random User-Agent rotation, request jitter
- **HTML + JSON Reports** — Professional dark-themed reports, local avatar images

### Email & Breach Intelligence
- **Email Scanner** — Check registration on 30+ platforms
- **Breach Check** — Hudson Rock infostealer intelligence (free API)
- **Password Leak** — Pwned Passwords k-anonymity check (free, no key)

### Phone Intelligence
- **Phone Scanner** — Check registration on 6 platforms: Instagram, Snapchat, Amazon, WhatsApp, Telegram, Signal
- **Carrier & Geo Analysis** — Powered by Google libphonenumber + Veriphone/Numverify
- **Anti-Scam Toolkit** — Report to platforms + expose scammer

### 🆕 IP Tracking
- **IP Geolocation** — Country, region, city, ISP, ASN (ip-api.com, no key needed)
- **Shodan InternetDB** — Open ports, CVEs, tags (no API key needed)
- **Proxy/VPN Detection** — Identify if IP is a proxy, hosting, or mobile
- **Reverse DNS** — Hostname resolution
- **My IP** — Get your own public IP + info

### 🆕 Dark Web Checker
- **GhostProject** — Email breach database search (free)
- **Psbdmp** — Pastebin dump search (free, no key)
- **BreachDirectory** — Credential breach lookup (free public tier)
- **LeakCheck** — Email breach sources (free public tier)
- **IntelX** — Intelligence X public search

### 🆕 Username Variants
- **Permutation Generator** — 150+ variants: leet, separators, suffixes, prefixes
- **Bio Extractor** — Extract @handles and URLs from profile bios
- **Variant Search** — Optionally search top variants in Maigret

### Visual Intelligence
- **Face Search** — 5 engines in parallel: Yandex, Google Lens, Bing, TinEye, Search4Faces
- **Reverse Image** — Yandex image search on profile photos
- **EXIF Extraction** — Metadata analysis via ExifTools.com API

### Termux Android Integration
- **Native Notifications** — Push notification when investigation completes (requires Termux:API)
- **Vibration Feedback** — Haptic feedback on completion
- **Auto-open Report** — Automatically opens HTML report in browser
- **Share Report** — Android share sheet integration
- **Clipboard Copy** — Copy results to clipboard
- **Text-to-Speech** — Speak investigation summary
- **Telegram Bot Output** — Auto-send full investigation summary + HTML/JSON reports

---

## Quick Start

### Termux Android (Recommended)
```bash
pkg install git python
git clone https://github.com/slipknoo822-lang/stalker-strike
cd stalker-strike
bash install_termux.sh
```

### Linux / macOS
```bash
git clone https://github.com/slipknoo822-lang/stalker-strike
cd stalker-strike
bash stalker.sh
```

### Manual Install
```bash
pip install -r requirements.txt
pip install -e maigret/
python -m stalker.menu
```

---

## CLI Commands

```bash
# Full investigation
python -m stalker.cli search johndoe
python -m stalker.cli search johndoe --variants   # also search username variants

# Quick modes
python -m stalker.cli quick johndoe               # 100 sites, no EXIF/dork
python -m stalker.cli email test@gmail.com        # email scanner + breach + dark web
python -m stalker.cli phone +62812345678          # phone scanner + carrier/geo
python -m stalker.cli dork "John Doe"             # smart dork

# New v2.0 commands
python -m stalker.cli ip 8.8.8.8                 # IP geolocation + Shodan
python -m stalker.cli ip me                       # Your own IP info
python -m stalker.cli variants johndoe            # Generate 150+ username variants
python -m stalker.cli variants johndoe --search   # Generate + search top variants
python -m stalker.cli darkweb test@gmail.com      # Dark web / paste site check

# Other
python -m stalker.cli exif image.jpg              # EXIF from file
python -m stalker.cli menu                        # Interactive menu
```

---

## Investigation Modes (Interactive Menu)

```
Enter username, email, or phone: johndoe
Detected: USERNAME

[1] Full Investigation     — All modules (comprehensive)
[2] Quick Profile          — Username + APIs + Breach + Telegram
[3] Deep Telegram          — Telegram profiler only
[4] Smart Dork Only        — Quick search → Dork → Report
[5] Face Search            — 5 engines on avatar
[6] Guided Mode            — Pick specific modules
[7] Linktree/Bio.site      — Check link aggregators
[8] Pastebin Leak Check    — Search pastebin/justpaste
[9] Username Variants      — Generate + search permutations

Enter username, email, or phone: test@gmail.com
Detected: EMAIL

[1] Full Investigation     — Email Scanner + Breach + Dark Web + Dork
[2] Email Scanner Only     — 30+ platforms
[3] Breach Check + Dork    — Hudson Rock + Smart Dork
[4] Dark Web Only          — Paste sites + breach DBs
[5] Domain WHOIS Check     — WHOIS lookup
[6] Guided Mode            — Pick specific modules

Enter username, email, or phone: +62812345678
Detected: PHONE

[1] Phone Investigation    — Phone Scanner (6 platforms) + Full Intel
[2] Phone Scanner Only     — Check 6 social platforms
[3] Anti-Scam Toolkit      — Report + expose scammer
[4] Guided Mode            — Pick specific modules
```

---

## Configuration

Copy `.env.example` to `.env` and configure:

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | — | Bot token for Telegram output |
| `TELEGRAM_CHAT_ID` | — | Chat ID for Telegram output |
| `EXIFTOOLS_API_KEY` | — | API key for ExifTools.com |
| `NUMVERIFY_API_KEY` | — | Numverify phone API (1000/mo free) |
| `VERIPHONE_API_KEY` | — | Veriphone phone API (1000/mo free, best for ID) |
| `MAIGRET_TIMEOUT` | 60 | Timeout per site check (seconds) |
| `MAIGRET_MAX_SITES` | 300 | Max sites to check (use 100-200 on Termux) |
| `OUTPUT_DIR` | output | Report output directory |
| `STEALTH_MODE` | false | Enable random delays + header rotation |
| `STEALTH_RANDOM_UA` | true | Rotate User-Agent per request |
| `REQUEST_DELAY` | 0.5 | Base delay between requests (seconds) |
| `FACE_SEARCH_MAX_AVATARS` | 3 | Max avatars to search |

---

## Modules

| Module | Source | Platforms / Data |
|--------|--------|-----------------|
| `maigret` | soxoj/maigret | 600+ social networks |
| `custom_apis` | Xemoz API | Instagram, TikTok, Twitter, YouTube, GitHub |
| `email_scanner` | megadose/holehe | 30+ platforms |
| `phone_scanner` | megadose/ignorant + cb-phonehunter | 6 social + carrier/geo |
| `ip_tracker` | ip-api.com + Shodan InternetDB | Geo, ports, vulns, proxy detect |
| `dark_web_checker` | GhostProject, Psbdmp, LeakCheck, BreachDirectory, IntelX | Paste/breach search |
| `username_variants` | Built-in | 150+ permutations: leet, separator, suffix |
| `face_search` | Yandex/Google/Bing/TinEye/S4F | 5 reverse image engines |
| `breach_check` | Hudson Rock | Infostealer intelligence |
| `password_leak` | Pwned Passwords | SHA-1 k-anonymity |
| `telegram_profiler` | t.me public data | Display name, numeric ID, group/channel |
| `text_profiler` | Regex extraction | Emails, phones, crypto, social handles |
| `google_dork` | Google + DuckDuckGo | Smart dork queries |
| `recursive_search` | Maigret recursion | Username discovery depth 2 |
| `reverse_image` | Yandex | Profile photo search |
| `social_graph` | pyvis + networkx | Interactive network visualization |
| `termux_tools` | Termux:API | Notifications, vibration, clipboard, share |

---

## Termux:API Setup (Optional)

For native Android notifications, vibration, and auto-open reports:

```bash
# 1. Install Termux:API app from F-Droid (NOT Google Play)
# 2. Install package in Termux:
pkg install termux-api

# 3. Grant permissions in Android → Apps → Termux:API → Permissions

# 4. Test it:
python -m stalker.cli termux
```

---

## Requirements

- Python 3.10+
- Windows, Linux, macOS, or **Termux Android**
- No Docker required

---

## License

MIT © OMNI Intelligence Project
