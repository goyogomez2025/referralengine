# -*- mode: python ; coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#  Yirra Care Agents — PyInstaller spec  ·  macOS (.app bundle)
#  Build with:  pyinstaller yirra_care_mac.spec --noconfirm
# ═══════════════════════════════════════════════════════════════════
from PyInstaller.utils.hooks import collect_all, collect_data_files

# ── Collect ALL Streamlit files (frontend React assets + Python) ──
st_datas, st_binaries, st_hidden = collect_all("streamlit")

# ── Altair (Vega schema JSONs are required at runtime) ────────────
alt_datas, alt_binaries, alt_hidden = collect_all("altair")

# ── pydeck (optional charts) ──────────────────────────────────────
try:
    pd_datas, pd_binaries, pd_hidden = collect_all("pydeck")
except Exception:
    pd_datas, pd_binaries, pd_hidden = [], [], []

a = Analysis(
    ["launcher.py"],
    pathex=["."],
    binaries=st_binaries + alt_binaries + pd_binaries,
    datas=[
        ("app",        "app"),
        (".streamlit", ".streamlit"),
        ("prompts",    "prompts"),
    ] + st_datas + alt_datas + pd_datas,
    hiddenimports=[
        # Streamlit internals
        "streamlit",
        "streamlit.web",
        "streamlit.web.cli",
        "streamlit.runtime",
        "streamlit.runtime.scriptrunner",
        "streamlit.components.v1",
        # Data / ML
        "altair",
        "pandas",
        "pandas.core.arrays.masked",
        "sqlite3",
        # OpenAI
        "openai",
        "openai.resources",
        "httpx",
        # Google / Gmail
        "google.auth",
        "google.auth.transport",
        "google.oauth2",
        "google.oauth2.credentials",
        "google_auth_oauthlib",
        "google_auth_oauthlib.flow",
        "googleapiclient",
        "googleapiclient.discovery",
        "googleapiclient.http",
        # Web scraping
        "bs4",
        "requests",
        "tldextract",
        "ddgs",
        # Misc
        "dotenv",
        "pydantic",
        "rich",
        "email.message",
        "logging.handlers",
    ] + st_hidden + alt_hidden + pd_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy", "notebook", "IPython"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="YirraCareAgents",
    debug=False,
    strip=False,
    upx=False,
    console=False,         # No terminal window
    argv_emulation=False,  # Don't process Apple Events (causes silent crash on double-click)
    target_arch=None,      # None = native arch (arm64 on M1/M2)
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="YirraCareAgents",
)

app = BUNDLE(
    coll,
    name="Yirra Care Agents.app",
    icon=None,                        # add path to .icns here if you have one
    bundle_identifier="au.yirracare.agents",
    version="1.1.0",
    info_plist={
        "CFBundleName":             "Yirra Care Agents",
        "CFBundleDisplayName":      "Yirra Care Agents",
        "CFBundleVersion":          "1.1.0",
        "CFBundleShortVersionString": "1.1.0",
        "NSHighResolutionCapable":  True,
        "LSUIElement":              True,   # background agent — won't be killed for having no window
        "LSApplicationCategoryType": "public.app-category.business",
        "NSRequiresAquaSystemAppearance": False,
    },
)
