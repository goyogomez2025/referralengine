# -*- mode: python ; coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#  Yirra Care Agents — PyInstaller spec  ·  Windows (.exe folder)
#  Build with:  pyinstaller yirra_care_windows.spec --noconfirm
#  ⚠  MUST be run on a Windows machine with Python 3.11 installed.
# ═══════════════════════════════════════════════════════════════════
from PyInstaller.utils.hooks import collect_all

st_datas,  st_binaries,  st_hidden  = collect_all("streamlit")
alt_datas, alt_binaries, alt_hidden = collect_all("altair")

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
        "streamlit",
        "streamlit.web",
        "streamlit.web.cli",
        "streamlit.runtime",
        "streamlit.runtime.scriptrunner",
        "streamlit.components.v1",
        "altair",
        "pandas",
        "pandas.core.arrays.masked",
        "sqlite3",
        "openai",
        "openai.resources",
        "httpx",
        "google.auth",
        "google.auth.transport",
        "google.oauth2",
        "google.oauth2.credentials",
        "google_auth_oauthlib",
        "google_auth_oauthlib.flow",
        "googleapiclient",
        "googleapiclient.discovery",
        "googleapiclient.http",
        "bs4",
        "requests",
        "tldextract",
        "ddgs",
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
    console=False,          # No black terminal window on Windows
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets\\icon.ico" if __import__("os").path.exists("assets\\icon.ico") else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="YirraCareAgents",
)
