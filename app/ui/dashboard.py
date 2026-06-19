"""
Referral Engine v1.1.0 — Yirra Care
Professional NDIS Outreach Automation Platform.
"""
import os, sys, subprocess, re, platform, time
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from app.config import settings
from app.services import campaign_service
from app.version import APP_VERSION

st.set_page_config(
    page_title=f"Referral Engine  v{APP_VERSION}",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
*,*::before,*::after{
  font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Inter","Segoe UI",system-ui,sans-serif!important;
  -webkit-font-smoothing:antialiased;box-sizing:border-box}

/* ─── App shell ─── */
:root{
  --bg:#F0F4F8;--card:#FFFFFF;--accent:#1B7A47;--accent-lite:#E8F5EE;
  --text-1:#111827;--text-2:#374151;--text-3:#6B7280;
  --sep:rgba(0,0,0,.09);
  --r-sm:10px;--r-md:14px;--r-lg:20px;
  --shadow-sm:0 1px 4px rgba(0,0,0,.08);
  --shadow-md:0 4px 18px rgba(0,0,0,.12)}
[data-testid="stAppViewContainer"]{background:var(--bg)!important}
.block-container{padding-top:1.2rem!important;padding-bottom:3rem!important;max-width:1400px!important}

/* ─── Sidebar ─── */
[data-testid="stSidebar"]{
  background:#1A4731!important;
  border-right:2px solid rgba(255,255,255,.12)!important}
/* Only colour the actual text/label nodes — NOT buttons/icons */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-baseweb="radio"] p {
  color:#FFFFFF!important}
[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.18)!important}
[data-testid="stSidebar"] [data-baseweb="radio"]{
  border-radius:8px;padding:.6rem 1rem!important;
  margin:.1rem 0!important;transition:background .15s}
[data-testid="stSidebar"] [data-baseweb="radio"]:hover{
  background:rgba(255,255,255,.10)!important}
[data-testid="stSidebar"] [data-baseweb="radio"][aria-checked="true"]{
  background:rgba(74,222,128,.18)!important}
[data-testid="stSidebar"] [data-baseweb="radio"][aria-checked="true"] p{
  color:#86EFAC!important;font-weight:700!important}

/* ─── Sidebar collapse/expand buttons ─── */
/* Collapse button (arrow left, inside sidebar when open) */
[data-testid="stSidebarCollapseButton"] button{
  background:rgba(255,255,255,.12)!important;
  border-radius:8px!important;border:none!important;cursor:pointer!important}
[data-testid="stSidebarCollapseButton"] button:hover{
  background:rgba(255,255,255,.22)!important}
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]{
  color:#FFFFFF!important;fill:#FFFFFF!important;
  font-family:'Material Icons'!important}
/* Expand button (tab on left edge when sidebar is collapsed) */
[data-testid="stSidebarCollapsedControl"]{
  background:#1A4731!important;
  border-radius:0 10px 10px 0!important;
  border:2px solid rgba(255,255,255,.15)!important;
  border-left:none!important;
  box-shadow:3px 0 10px rgba(0,0,0,.18)!important}
[data-testid="stSidebarCollapsedControl"] button{
  background:transparent!important;border:none!important;cursor:pointer!important;
  padding:.5rem .3rem!important}
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] [data-testid="stIconMaterial"]{
  color:#FFFFFF!important;fill:#FFFFFF!important;
  font-family:'Material Icons'!important}

/* ─── Hide Streamlit chrome (toolbar/footer only — NOT the header) ─── */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu,footer{display:none!important}

/* ─── All buttons — green across the board ─── */
.stButton > button,
div[data-testid="stFormSubmitButton"] > button,
div[data-testid="stDownloadButton"] > button {
  background:#1B7A47!important;
  color:#FFFFFF!important;
  border:none!important;
  border-radius:var(--r-md)!important;
  padding:.5rem 1.1rem!important;
  font-weight:600!important;
  font-size:.86rem!important;
  width:100%!important;
  box-shadow:0 2px 8px rgba(27,122,71,.30)!important;
  transition:all .18s ease!important}
.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
  background:#145e36!important;
  transform:translateY(-1px)!important;
  box-shadow:0 4px 14px rgba(27,122,71,.38)!important}
.stButton > button:disabled,
div[data-testid="stFormSubmitButton"] > button:disabled,
div[data-testid="stDownloadButton"] > button:disabled {
  background:#D1D5DB!important;
  color:#9CA3AF!important;
  box-shadow:none!important;
  transform:none!important}

/* ─── Metric cards ─── */
.ios-card{
  background:var(--card);border-radius:11px;padding:.8rem .9rem .75rem;
  box-shadow:var(--shadow-sm);border:1px solid var(--sep);text-align:center;
  transition:transform .18s,box-shadow .18s}
.ios-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-md)}
.ios-num{font-size:1.8rem;font-weight:800;color:#111827;letter-spacing:-.04em;line-height:1;margin-bottom:.2rem}
.ios-label{font-size:.74rem;color:#374151;font-weight:600;text-transform:uppercase;letter-spacing:.07em}
.ios-icon{font-size:1.1rem;margin-bottom:.3rem;display:block}

/* ─── Setup step rows ─── */
.step-row{
  display:flex;align-items:center;gap:1rem;background:var(--card);
  border-radius:var(--r-md);padding:1rem 1.2rem;margin-bottom:.6rem;
  border:1px solid var(--sep);box-shadow:var(--shadow-sm)}
.step-row.done{border-left:4px solid #22C55E}
.step-row.todo{border-left:4px solid #F59E0B}
.step-title{font-weight:600;font-size:1rem;color:#111827}
.step-sub{font-size:.86rem;color:#4B5563;margin-top:.12rem}

/* ─── Section headings ─── */
.sec-head{
  font-size:.72rem;font-weight:700;color:#1B7A47;
  text-transform:uppercase;letter-spacing:.08em;margin:1.1rem 0 .6rem;
  border-left:3px solid #1B7A47;padding-left:.5rem;display:block}

/* ─── Warning / info bars ─── */
.warn-bar{
  background:#FEF3C7;border:1px solid #FCD34D;border-radius:var(--r-md);
  padding:.6rem .9rem;margin-bottom:.6rem;color:#78350F;font-size:.84rem;font-weight:500}
.update-bar{
  background:linear-gradient(135deg,#1B7A47,#145e36);color:#fff;
  border-radius:var(--r-md);padding:.9rem 1.2rem;margin-bottom:1rem;
  display:flex;align-items:center;gap:.8rem;
  box-shadow:0 4px 16px rgba(27,122,71,.28)}
.info-card{
  background:var(--card);border-radius:var(--r-lg);border:1px solid var(--sep);
  padding:2.8rem;text-align:center;color:#374151;font-size:.94rem}

/* ─── Tabs ─── */
[data-baseweb="tab-list"]{
  background:rgba(0,0,0,.06)!important;
  border-radius:10px!important;padding:4px!important}
[data-baseweb="tab"]{border-radius:8px!important;font-weight:500!important;color:#374151!important;font-size:.92rem!important;padding:.5rem .9rem!important}
[aria-selected="true"][data-baseweb="tab"]{
  background:#FFFFFF!important;box-shadow:var(--shadow-sm)!important;
  color:#111827!important;font-weight:700!important}

/* ─── Form labels ─── */
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stSlider"] label,
[data-testid="stTextArea"] label,
[data-testid="stNumberInput"] label,
[data-testid="stFileUploader"] label,
[data-testid="stToggle"] label {
  font-size:.92rem!important;font-weight:600!important;color:#374151!important}

/* ─── Metric widgets ─── */
[data-testid="stMetric"] label{font-size:.86rem!important;font-weight:600!important;color:#6B7280!important}
[data-testid="stMetric"] [data-testid="stMetricValue"]{font-size:1.55rem!important;font-weight:800!important;color:#111827!important}

/* ─── Progress bar ─── */
[data-testid="stProgressBar"]>div>div{background:#1B7A47!important;border-radius:999px!important}
[data-testid="stProgressBar"]>div{background:#D1FAE5!important;border-radius:999px!important;height:8px!important}

/* ─── Expanders ─── */
[data-testid="stExpander"]{
  border-radius:var(--r-md)!important;
  border:1px solid var(--sep)!important;
  background:#FFFFFF!important}

/* ─── Alerts ─── */
[data-testid="stAlert"]{border-radius:var(--r-md)!important;font-size:.92rem!important}

/* ─── Dataframe readability ─── */
[data-testid="stDataFrame"]{border-radius:var(--r-md)!important;overflow:hidden!important}

/* ─── Caption / subtext ─── */
[data-testid="stCaptionContainer"] p{font-size:.88rem!important;color:#6B7280!important}

/* ─── Hide the 1-px sidebar-toggle iframe ─── */
iframe[height="1"]{display:none!important}

/* ─── Typography ─── */
h1{font-size:1.55rem!important;font-weight:800!important;letter-spacing:-.04em!important;color:#111827!important;margin-bottom:.15rem!important}
h2{font-size:1.2rem!important;font-weight:700!important;color:#111827!important}
h3{font-size:.98rem!important;font-weight:700!important;color:#111827!important}
h4{font-size:.9rem!important;font-weight:700!important;color:#111827!important}
</style>"""

st.markdown(CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def db_query(sql, params=()):
    db_path = ROOT / settings.database_path
    if not db_path.exists():
        return pd.DataFrame()
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    df   = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


def _live_env(key: str, fallback: str = "") -> str:
    """Read a value fresh from the .env file on every render so that
    changes made in the Settings page are reflected immediately in the
    sidebar / header without needing a server restart."""
    try:
        from dotenv import dotenv_values
        val = dotenv_values(str(ROOT / ".env")).get(key, "")
        return val if val else fallback
    except Exception:
        return fallback


def run_step(args: list) -> tuple:
    """
    Run a worker in-process (works in both dev and frozen .app).
    Avoids spawning sys.executable as a subprocess, which breaks in PyInstaller bundles.
    """
    import io, traceback
    from contextlib import redirect_stdout, redirect_stderr

    cmd  = args[0]
    rest = args[1:]

    # helpers to parse --key=value flags from the args list
    def _int(flag: str, default: int = 100) -> int:
        for a in rest:
            if a.startswith(f"{flag}="):
                try:
                    return int(a.split("=", 1)[1])
                except ValueError:
                    pass
        return default

    def _str(flag: str, default=None):
        for a in rest:
            if a.startswith(f"{flag}="):
                return a.split("=", 1)[1]
        return default

    buf = io.StringIO()
    try:
        from app.db import init_db
        init_db()

        with redirect_stdout(buf), redirect_stderr(buf):
            if cmd == "find":
                from app.workers import find_contacts
                n = find_contacts.run(
                    query=None,
                    limit=_int("--limit"),
                    campaign_id=_str("--campaign"),
                )
                buf.write(f"Prospects found/saved: {n}\n")

            elif cmd == "scrape":
                from app.workers import scrape_emails
                n = scrape_emails.run(limit=_int("--limit"), location=None)
                buf.write(f"Contacts extracted: {n}\n")

            elif cmd == "qualify":
                from app.workers import qualify_contacts
                n = qualify_contacts.run(limit=_int("--limit"))
                buf.write(f"Contacts qualified: {n}\n")

            elif cmd == "write-emails":
                from app.workers import write_emails
                n = write_emails.run(
                    campaign=_str("--campaign") or "",
                    limit=_int("--limit"),
                )
                buf.write(f"Emails written: {n}\n")

            elif cmd == "create-drafts":
                from app.workers import create_gmail_drafts
                n = create_gmail_drafts.run(limit=_int("--limit"))
                buf.write(f"Gmail drafts created: {n}\n")

            elif cmd == "export-contacts":
                from app.workers import export_data
                path = export_data.export_contacts(_str("--path") or "")
                buf.write(f"Contacts exported: {path}\n")

            elif cmd == "export-emails":
                from app.workers import export_data
                path = export_data.export_emails(_str("--path") or "")
                buf.write(f"Emails exported: {path}\n")

            elif cmd == "import-contacts":
                from app.workers import import_contacts
                n = import_contacts.run(_str("--path") or "")
                buf.write(f"Contacts imported: {n}\n")

            else:
                return f"Unknown command: {cmd}", False

        return buf.getvalue().strip(), True

    except Exception:
        return (buf.getvalue() + "\n" + traceback.format_exc()).strip(), False


def show_result(out: str, ok: bool):
    """Display run_step output — avoids Streamlit magic treating ternaries as widgets."""
    if ok:
        st.success(out or "Done.")
    else:
        st.error(out or "An error occurred. Check logs.")


def update_env_file(updates):
    env_path = ROOT / ".env"
    lines    = env_path.read_text().splitlines() if env_path.exists() else []
    new_lines, updated = [], set()
    for line in lines:
        s = line.strip()
        if "=" in s and not s.startswith("#"):
            key = s.split("=")[0].strip()
            if key in updates:
                new_lines.append(f"{key}={updates[key]}")
                updated.add(key)
                continue
        new_lines.append(line)
    for k, v in updates.items():
        if k not in updated:
            new_lines.append(f"{k}={v}")
    env_path.write_text("\n".join(new_lines) + "\n")


def gmail_status():
    return (
        (ROOT / settings.google_client_secret_file).exists(),
        (ROOT / settings.google_token_file).exists(),
    )


def get_stats():
    try:
        from app.db import get_all_stats
        return get_all_stats()
    except Exception:
        return {k: 0 for k in ["prospects","contacts","qualified","emails","drafts","sent","contacted"]}


def _installed_version() -> str:
    """
    Read the installed version from version.txt on disk.
    Tries multiple paths so it works in both dev and frozen .app,
    and correctly reflects git updates (not the compiled constant).
    """
    candidates = [
        ROOT / "version.txt",                                          # dev + frozen (via ROOT)
        Path(sys.executable).resolve().parent.parent / "Resources" / "version.txt",  # frozen .app MacOS/../../Resources
        Path(sys.executable).resolve().parent / "version.txt",        # frozen onedir
    ]
    for p in candidates:
        try:
            content = p.read_text().strip()
            if content:
                return content
        except Exception:
            pass
    return APP_VERSION  # last resort: compiled constant


def check_update():
    try:
        import urllib.request, json, base64
        from app.version import UPDATE_CHECK_URL
        req = urllib.request.Request(
            UPDATE_CHECK_URL,
            headers={"Accept": "application/vnd.github+json",
                     "User-Agent": "YirraCareAgents"}
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
        latest = base64.b64decode(data["content"]).decode().strip()
        return latest if latest != _installed_version() else None
    except Exception:
        return None


def perform_update():
    """
    Pull the latest code from GitHub and reinstall dependencies.
    Works whether or not the folder is already a git repo.
    Secrets (.env, token.json, client_secret.json) and data/ are
    protected by .gitignore and will never be touched.
    """
    from app.version import REPO_URL
    out = []
    try:
        # ── Ensure git is installed ──────────────────────────────────────
        r_git = subprocess.run(["git", "--version"], capture_output=True, text=True)
        if r_git.returncode != 0:
            out.append(("git", "git not found — install git from https://git-scm.com", False))
            return out

        # ── Ensure this is a git repo pointing at the right remote ───────
        r_check = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        if r_check.returncode != 0:
            # Not a git repo yet — initialise and set remote
            subprocess.run(["git", "init"], capture_output=True, cwd=str(ROOT))
            subprocess.run(
                ["git", "remote", "add", "origin", REPO_URL],
                capture_output=True, cwd=str(ROOT)
            )
            out.append(("git init", "Initialised local repository", True))
        else:
            # Already a repo — make sure remote URL is correct
            subprocess.run(
                ["git", "remote", "set-url", "origin", REPO_URL],
                capture_output=True, cwd=str(ROOT)
            )

        # ── Fetch + reset to latest main ─────────────────────────────────
        # reset --hard keeps untracked files (.env, data/, etc.) untouched
        r_fetch = subprocess.run(
            ["git", "fetch", "origin", "main"],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        out.append(("git fetch", r_fetch.stdout + r_fetch.stderr, r_fetch.returncode == 0))

        if r_fetch.returncode == 0:
            r_reset = subprocess.run(
                ["git", "reset", "--hard", "origin/main"],
                capture_output=True, text=True, cwd=str(ROOT)
            )
            out.append(("git reset", r_reset.stdout + r_reset.stderr, r_reset.returncode == 0))

            if r_reset.returncode == 0:
                # Force-write every indexed file to the working tree.
                r_ci = subprocess.run(
                    ["git", "checkout-index", "-a", "-f"],
                    capture_output=True, text=True, cwd=str(ROOT)
                )
                msg = r_ci.stdout + r_ci.stderr if (r_ci.stdout + r_ci.stderr).strip() else "All files updated"
                out.append(("git checkout-index", msg, r_ci.returncode == 0))

                # Explicitly overwrite version.txt using git's object store.
                # This guarantees the correct version is on disk regardless of
                # any OS-level file-write buffering from the subprocess above.
                r_ver = subprocess.run(
                    ["git", "show", "HEAD:version.txt"],
                    capture_output=True, text=True, cwd=str(ROOT)
                )
                if r_ver.returncode == 0 and r_ver.stdout.strip():
                    new_version_str = r_ver.stdout.strip()
                    (ROOT / "version.txt").write_text(new_version_str + "\n")
                    out.append(("version.txt", f"→ {new_version_str}", True))

        # ── Reinstall dependencies (dev / source installs only) ──────────
        if not getattr(sys, "frozen", False):
            r_pip = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"],
                capture_output=True, text=True, cwd=str(ROOT)
            )
            out.append(("pip install", r_pip.stdout + r_pip.stderr, r_pip.returncode == 0))
        else:
            out.append(("pip install", "Skipped (not needed in packaged app)", True))

    except Exception as e:
        out.append(("error", str(e), False))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

has_secret, has_token = gmail_status()
has_openai = bool(settings.openai_api_key)
is_ready   = has_openai and has_token

# ── Permanent sidebar toggle button injected via JS ──────────────────────────
# st.iframe runs real JS in an iframe that can access window.parent to inject
# a permanent floating hamburger button — works regardless of Streamlit version.
st.iframe("""
<script>
(function () {
  var BTN_ID = '__yirra_sb_toggle__';

  function makeBtn(p) {
    if (p.document.getElementById(BTN_ID)) return;
    var b = p.document.createElement('button');
    b.id          = BTN_ID;
    b.title       = 'Show / hide menu';
    b.textContent = '\u2630';           /* ☰ hamburger */
    b.style.cssText = [
      'position:fixed', 'left:10px', 'top:10px',
      'z-index:9999999',
      'width:40px', 'height:40px',
      'background:#1A4731', 'color:#fff',
      'font-size:1.25rem', 'line-height:1',
      'border:none', 'border-radius:10px',
      'cursor:pointer',
      'box-shadow:0 2px 10px rgba(0,0,0,.35)',
      'display:flex', 'align-items:center', 'justify-content:center'
    ].join(';');
    b.onmouseenter = function(){ b.style.background='#2D6A4F'; };
    b.onmouseleave = function(){ b.style.background='#1A4731'; };
    b.onclick = function () {
      /* Try every selector Streamlit has ever used for this button */
      var sels = [
        '[data-testid="stSidebarCollapseButton"] button',
        '[data-testid="stSidebarCollapsedControl"] button',
        '[data-testid="collapsedControl"] button',
        'button[aria-label="Close sidebar"]',
        'button[aria-label="Open sidebar"]'
      ];
      for (var i = 0; i < sels.length; i++) {
        var el = p.document.querySelector(sels[i]);
        if (el) { el.click(); return; }
      }
    };
    p.document.body.appendChild(b);
  }

  /* Run now and keep re-adding after Streamlit re-renders */
  function tryAdd() {
    try { makeBtn(window.parent); } catch(e) {}
  }
  tryAdd();
  setTimeout(tryAdd, 500);
  setTimeout(tryAdd, 1500);
  new MutationObserver(tryAdd).observe(
    document.body, { childList: true }
  );
})();
</script>
""", height=1)
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div style="padding:1.8rem 1.2rem 1.2rem">
      <div style="font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;
                  color:rgba(255,255,255,.65);margin-bottom:.3rem;font-weight:700">
        REFERRAL ENGINE
      </div>
      <div style="font-size:1.65rem;font-weight:800;color:#FFFFFF;letter-spacing:-.04em">
        v{_installed_version()}
      </div>
      <div style="font-size:.8rem;color:rgba(255,255,255,.75);margin-top:.25rem;font-weight:500">
        {_live_env("COMPANY_NAME", settings.company_name)}
      </div>
    </div>""", unsafe_allow_html=True)

    if not is_ready:
        st.markdown("""
        <div style="margin:0 .8rem .9rem;padding:.75rem 1rem;
            background:rgba(251,191,36,.18);border:1px solid rgba(251,191,36,.45);
            border-radius:10px;font-size:.83rem;color:#FEF3C7;font-weight:600;line-height:1.4">
          ⚠️ Setup required<br>
          <span style="font-weight:400;font-size:.78rem">Go to Settings to configure</span>
        </div>""", unsafe_allow_html=True)

    page = st.radio(
        "nav",
        ["  🏠   Dashboard","  ⚡   Pipeline","  🎯   Campaigns",
         "  👥   Contacts", "  ✉️   Emails",  "  ⚙️   Settings"],
        label_visibility="hidden",
    )

    st.markdown(
        '<div style="height:1px;background:rgba(255,255,255,.15);margin:.7rem .8rem 0"></div>',
        unsafe_allow_html=True
    )

    oi = "🟢" if has_openai else "🔴"
    gi = "🟢" if has_token   else "🔴"
    st.markdown(f"""
    <div style="padding:.9rem 1.2rem 1.4rem">
      <div style="font-weight:700;color:#FFFFFF;font-size:.92rem;margin-bottom:.15rem">
        {settings.sender_name}
      </div>
      <div style="color:rgba(255,255,255,.75);font-size:.79rem;margin-bottom:.45rem">
        {settings.sender_email}
      </div>
      <div style="font-size:.79rem;color:rgba(255,255,255,.7)">
        {oi} OpenAI &nbsp;&nbsp; {gi} Gmail
      </div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "  🏠   Dashboard":
    nv = check_update()
    if nv:
        st.markdown(f"""
        <div class="update-bar">
          <span style="font-size:1.5rem">🆕</span>
          <div>
            <div style="font-weight:700;font-size:.95rem">Update available — v{nv}</div>
            <div style="font-size:.82rem;opacity:.9">Go to Settings → Updates to install</div>
          </div>
        </div>""", unsafe_allow_html=True)

    # ── Page header ──────────────────────────────────────────────────────────
    ready_badge = (
        '<span style="background:#DCFCE7;color:#14532D;border-radius:20px;'
        'padding:.2rem .7rem;font-size:.74rem;font-weight:600;border:1px solid #BBF7D0">'
        '🟢 Ready</span>'
        if is_ready else
        '<span style="background:#FEF3C7;color:#92400E;border-radius:20px;'
        'padding:.2rem .7rem;font-size:.74rem;font-weight:600;border:1px solid #FCD34D">'
        '⚠️ Setup Needed</span>'
    )
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
                margin-bottom:1.1rem;padding-bottom:.85rem;border-bottom:1px solid #E5E7EB">
      <div>
        <h1 style="margin:0 0 .1rem;font-size:1.5rem;font-weight:800">Pipeline Dashboard</h1>
        <p style="color:#9CA3AF;font-size:.79rem;margin:0;font-weight:500">
          {_live_env("COMPANY_NAME", settings.company_name)} · Outreach Automation
        </p>
      </div>
      <div>{ready_badge}</div>
    </div>""", unsafe_allow_html=True)

    if not is_ready:
        st.markdown("""
        <div class="warn-bar">
          ⚠️ Complete API & Gmail setup in <b>Settings</b> before running the pipeline.
        </div>""", unsafe_allow_html=True)

    stats = get_stats()

    # ── KPI row ───────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    kpi_data = [
        (k1, "🔍", stats["prospects"], "Prospects",  "found",      "#1B7A47"),
        (k2, "👤", stats["contacts"],  "Contacts",   "with email", "#2563EB"),
        (k3, "✅", stats["qualified"], "Qualified",  "AI scored",  "#7C3AED"),
        (k4, "📤", stats["sent"],      "Sent",       "delivered",  "#DC2626"),
    ]
    for col, icon, val, label, sub, accent in kpi_data:
        col.markdown(f"""
        <div style="background:#FFFFFF;border-radius:10px;padding:.9rem 1.05rem .85rem;
                    border:1px solid #E5E7EB;border-left:3px solid {accent};
                    box-shadow:0 1px 4px rgba(0,0,0,.06)">
          <div style="display:flex;align-items:center;gap:.4rem;margin-bottom:.45rem">
            <span style="font-size:.9rem">{icon}</span>
            <span style="font-size:.66rem;font-weight:700;color:{accent};
                         text-transform:uppercase;letter-spacing:.07em">{label}</span>
          </div>
          <div style="font-size:1.85rem;font-weight:800;color:#111827;
                      letter-spacing:-.04em;line-height:1;margin-bottom:.18rem">{val}</div>
          <div style="font-size:.68rem;color:#9CA3AF;font-weight:500">{sub}</div>
        </div>""", unsafe_allow_html=True)

    # ── Secondary metrics strip ──────────────────────────────────────────
    st.markdown(f"""
    <div style="background:#FFFFFF;border-radius:9px;padding:.65rem 1.2rem;
                border:1px solid #E5E7EB;display:flex;align-items:center;
                margin-top:.5rem;margin-bottom:1.2rem;
                box-shadow:0 1px 3px rgba(0,0,0,.04)">
      <div style="display:flex;align-items:center;gap:.45rem;flex:1">
        <span style="font-size:.85rem">✍️</span>
        <span style="font-size:1.05rem;font-weight:800;color:#111827">{stats["emails"]}</span>
        <span style="font-size:.64rem;font-weight:600;color:#9CA3AF;text-transform:uppercase;letter-spacing:.05em">Written</span>
      </div>
      <div style="width:1px;height:20px;background:#E5E7EB"></div>
      <div style="display:flex;align-items:center;gap:.45rem;flex:1;padding-left:.75rem">
        <span style="font-size:.85rem">📬</span>
        <span style="font-size:1.05rem;font-weight:800;color:#111827">{stats["drafts"]}</span>
        <span style="font-size:.64rem;font-weight:600;color:#9CA3AF;text-transform:uppercase;letter-spacing:.05em">Drafts</span>
      </div>
      <div style="width:1px;height:20px;background:#E5E7EB"></div>
      <div style="display:flex;align-items:center;gap:.45rem;flex:1;padding-left:.75rem">
        <span style="font-size:.85rem">🤝</span>
        <span style="font-size:1.05rem;font-weight:800;color:#111827">{stats["contacted"]}</span>
        <span style="font-size:.64rem;font-weight:600;color:#9CA3AF;text-transform:uppercase;letter-spacing:.05em">Contacted</span>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── legacy cards array (not used in new layout) ──
    cards = [
        ("🔍", stats["prospects"],  "Prospects"),
        ("👤", stats["contacts"],   "Contacts"),
        ("✅", stats["qualified"],  "Qualified"),
        ("✍️", stats["emails"],     "Written"),
        ("📬", stats["drafts"],     "Drafts"),
        ("📤", stats["sent"],       "Sent"),
        ("��", stats["contacted"],  "Contacted"),
    ]
    # ── Charts side by side (full width) ────────────────────────────────
    col_f, col_p = st.columns([3, 2], gap="medium")

    with col_f:
        # ── FUNNEL CARD ───────────────────────────────────────────────────
        funnel_data = [
            ("Prospects",  stats["prospects"], "#1B7A47"),
            ("Contacts",   stats["contacts"],  "#2563EB"),
            ("Qualified",  stats["qualified"], "#7C3AED"),
            ("Emails",     stats["emails"],    "#D97706"),
            ("Sent",       stats["sent"],      "#DC2626"),
        ]
        top_f = max(funnel_data[0][1], 1)
        f_inner = ''
        for i, (lbl, val, color) in enumerate(funnel_data):
            pct  = val / top_f
            w    = 100 - i * 9
            pcts = f"{pct*100:.0f}%"
            if i > 0:
                prev = funnel_data[i-1][1]
                conv = (val / prev * 100) if prev > 0 else 0
                dc   = "#22C55E" if conv >= 50 else ("#F59E0B" if conv >= 20 else "#EF4444")
                f_inner += (
                    f'<div style="text-align:center;font-size:.65rem;color:{dc};'
                    f'font-weight:700;padding:.1rem 0">↓ {conv:.0f}% converted</div>'
                )
            f_inner += (
                f'<div style="display:flex;justify-content:center">'
                f'<div style="width:{w}%;background:{color};border-radius:6px;'
                f'padding:.5rem .9rem;display:flex;justify-content:space-between;align-items:center">'
                f'<span style="font-size:.8rem;font-weight:600;color:#fff">{lbl}</span>'
                f'<div><span style="font-size:.92rem;font-weight:800;color:#fff">{val}</span>'
                f'<span style="font-size:.65rem;color:rgba(255,255,255,.72);margin-left:.25rem">{pcts}</span>'
                f'</div></div></div>'
            )
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:12px;
                    padding:1rem 1.1rem">
          <p style="font-size:.66rem;font-weight:700;color:#6B7280;text-transform:uppercase;
                    letter-spacing:.09em;margin:0 0 .75rem;padding:0">Conversion Funnel</p>
          {f_inner}
        </div>""", unsafe_allow_html=True)

    with col_p:
        # ── CONTACT TYPE CARD ─────────────────────────────────────────────
        df_t = db_query(
            "SELECT contact_type type, COUNT(*) count FROM contacts "
            "WHERE contact_type IS NOT NULL GROUP BY contact_type ORDER BY count DESC"
        )
        if df_t.empty:
            st.markdown(
                '<div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:12px;'
                'padding:1rem 1.1rem;color:#9CA3AF;font-size:.79rem;text-align:center">'
                'No provider data yet</div>',
                unsafe_allow_html=True
            )
        else:
            type_colors = ["#1B7A47","#2563EB","#7C3AED","#D97706","#DC2626","#0891B2"]
            top_count = int(df_t["count"].max()) or 1
            bars_inner = ''
            for i, (_, row) in enumerate(df_t.iterrows()):
                lbl   = str(row["type"])
                cnt   = int(row["count"])
                pct   = cnt / top_count * 100
                color = type_colors[i % len(type_colors)]
                bars_inner += (
                    f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">'
                    f'<div style="width:130px;font-size:.76rem;color:#374151;font-weight:600;'
                    f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-align:right">'
                    f'{lbl}</div>'
                    f'<div style="flex:1;background:#F3F4F6;border-radius:5px;overflow:hidden">'
                    f'<div style="height:22px;width:{pct:.0f}%;background:{color};border-radius:5px;'
                    f'display:flex;align-items:center;padding-left:8px;'
                    f'font-size:.74rem;font-weight:700;color:#fff;min-width:22px">'
                    f'{cnt}</div></div></div>'
                )
            st.markdown(f"""
            <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:12px;
                        padding:1rem 1.1rem">
              <p style="font-size:.66rem;font-weight:700;color:#6B7280;text-transform:uppercase;
                        letter-spacing:.09em;margin:0 0 .75rem;padding:0">By Contact Type</p>
              {bars_inner}
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "  ⚡   Pipeline":
    st.markdown("# Pipeline")
    st.markdown(
        '<p style="color:#374151;font-size:.9rem;margin-top:-.4rem;margin-bottom:1.4rem">'
        'Run each step individually, or fire the full pipeline in one click.</p>',
        unsafe_allow_html=True
    )

    if not is_ready:
        st.error("Complete API + Gmail setup in **Settings** first.")
        st.stop()

    campaigns = campaign_service.all_campaigns()
    camp_map  = {c["id"]: c["name"] for c in campaigns} if campaigns else {}
    if not camp_map:
        st.warning("No campaigns yet. Create one in **Campaigns** first.")
        st.stop()

    # ════════════════════════════════════════════════════
    # FULL PIPELINE RUN — always-visible white card
    # ════════════════════════════════════════════════════
    st.markdown("""
    <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:16px;
                padding:1.4rem 1.6rem 1.2rem;margin-bottom:1.6rem;
                box-shadow:0 1px 4px rgba(0,0,0,.07)">
      <div style="font-size:.72rem;font-weight:700;color:#374151;text-transform:uppercase;
                  letter-spacing:.09em;margin-bottom:.9rem">⚡ Full Pipeline Run</div>
    """, unsafe_allow_html=True)

    fp1, fp2, fp3 = st.columns([3, 2, 2])
    camp_id = fp1.selectbox("Campaign", list(camp_map.keys()),
                            format_func=lambda x: camp_map.get(x, x), key="fp_camp")
    limit   = fp2.slider("Limit per step", 10, 100, 30, key="fp_limit")
    fp3.markdown("<br>", unsafe_allow_html=True)

    if fp3.button("▶  Run All Steps", key="fp_run"):
        steps = [
            (["find",          f"--limit={limit}",       f"--campaign={camp_id}"], "🔍 Finding prospects"),
            (["scrape",        f"--limit={limit}"],                                 "📧 Scraping websites"),
            (["qualify",       f"--limit={limit*3}"],                               "✅ Qualifying contacts"),
            (["write-emails",  f"--campaign={camp_id}",  f"--limit={limit}"],       "✍️ Writing AI emails"),
            (["create-drafts", f"--limit={limit}"],                                 "📬 Creating Gmail drafts"),
        ]
        bar    = st.progress(0, "Starting…")
        all_ok = True
        for i, (args, label) in enumerate(steps):
            bar.progress(i / len(steps), label)
            with st.spinner(label):
                out, ok = run_step(args)
            bar.progress((i + 1) / len(steps))
            if ok:
                st.success(f"✅ {label}")
                if out:
                    st.caption(out[:300])
            else:
                st.error(f"❌ {label}")
                st.code(out)
                all_ok = False
                break
        bar.progress(1.0, "Complete" if all_ok else "Stopped")
        if all_ok:
            st.balloons()
            st.success("🎉 Pipeline complete! Head to **Emails** to review and send.")

    st.markdown("</div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    # INDIVIDUAL STEPS — tabs (always visible, no expanders)
    # ════════════════════════════════════════════════════
    st.markdown(
        '<p style="font-size:.72rem;font-weight:700;color:#374151;text-transform:uppercase;'
        'letter-spacing:.09em;margin:0 0 .7rem">Individual Steps</p>',
        unsafe_allow_html=True
    )

    (t_find, t_scrape, t_qualify,
     t_write, t_drafts, t_import, t_export) = st.tabs([
        "🔍  Find", "📧  Scrape", "✅  Qualify",
        "✍️  Write Emails", "📬  Drafts", "📥  Import", "⬇️  Export",
    ])

    # ── 1 · Find ──
    with t_find:
        st.markdown("#### 1 · Find Prospects")
        st.caption("Search the web for prospects matching your campaign search queries.")
        fc1, fc2 = st.columns(2)
        l1     = fc1.slider("Max results", 10, 100, 25, key="l1")
        c_find = fc2.selectbox("Campaign", list(camp_map.keys()),
                               format_func=lambda x: camp_map.get(x, x), key="c_find")
        if st.button("🔍  Run Find", key="b1"):
            with st.spinner("Searching for NDIS providers…"):
                out, ok = run_step(["find", f"--limit={l1}", f"--campaign={c_find}"])
            show_result(out, ok)

    # ── 2 · Scrape ──
    with t_scrape:
        st.markdown("#### 2 · Scrape Websites")
        st.caption("Visit each prospect's website and extract contact email addresses.")
        l2 = st.slider("Max pages to scrape", 10, 100, 25, key="l2")
        if st.button("📧  Run Scrape", key="b2"):
            with st.spinner("Scraping contact emails…"):
                out, ok = run_step(["scrape", f"--limit={l2}"])
            show_result(out, ok)

    # ── 3 · Qualify ──
    with t_qualify:
        st.markdown("#### 3 · Qualify Contacts")
        st.caption("Score each contact 0–100 based on role relevance, email quality, and location.")
        l3 = st.slider("Max contacts to score", 10, 200, 50, key="l3")
        if st.button("✅  Run Qualify", key="b3"):
            with st.spinner("Scoring contacts…"):
                out, ok = run_step(["qualify", f"--limit={l3}"])
            show_result(out, ok)

    # ── 4 · Write Emails ──
    with t_write:
        st.markdown("#### 4 · Write Emails (AI)")
        st.caption("GPT-4.1 writes a personalised outreach email for each qualified contact.")
        wc1, wc2 = st.columns(2)
        c4 = wc1.selectbox("Campaign", list(camp_map.keys()),
                           format_func=lambda x: camp_map.get(x, x), key="c4")
        l4 = wc2.slider("Max emails to write", 5, 100, 20, key="l4")
        if st.button("✍️  Run Write Emails", key="b4"):
            with st.spinner("GPT-4.1 writing personalised emails…"):
                out, ok = run_step(["write-emails", f"--campaign={c4}", f"--limit={l4}"])
            show_result(out, ok)

    # ── 5 · Gmail Drafts ──
    with t_drafts:
        st.markdown("#### 5 · Create Gmail Drafts")
        st.caption("Push ready emails into your Gmail Drafts folder for review before sending.")
        l5 = st.slider("Max drafts to create", 5, 50, 20, key="l5")
        if st.button("📬  Run Create Drafts", key="b5"):
            with st.spinner("Creating drafts in Gmail…"):
                out, ok = run_step(["create-drafts", f"--limit={l5}"])
            show_result(out, ok)

    # ── Import ──
    with t_import:
        st.markdown("#### Import Contacts from CSV")
        st.caption("Upload a CSV file with existing contacts to add them directly to the pipeline.")
        up = st.file_uploader("Choose a CSV file", type=["csv"])
        if up:
            st.success(f"File ready: **{up.name}** ({len(up.getvalue()):,} bytes)")
            if st.button("📥  Import Now", key="bimp"):
                tmp = ROOT / "data" / "import_tmp.csv"
                tmp.write_bytes(up.getvalue())
                out, ok = run_step(["import-contacts", f"--path={tmp}"])
                show_result(out, ok)

    # ── Export ──
    with t_export:
        st.markdown("#### Export Data to CSV")
        st.caption("Download all contacts and emails as CSV files into the `exports/` folder.")
        ec1, ec2 = st.columns(2)
        if ec1.button("📋  Export Contacts", key="bexpc"):
            _, ok = run_step(["export-contacts"])
            if ok:
                st.success("Saved → exports/contacts.csv")
            else:
                st.error("Export failed")
        if ec2.button("✉️  Export Emails", key="bexpe"):
            _, ok = run_step(["export-emails"])
            if ok:
                st.success("Saved → exports/emails.csv")
            else:
                st.error("Export failed")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — CAMPAIGNS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "  🎯   Campaigns":
    st.markdown("# Campaigns")
    st.markdown(
        '<p style="color:#374151;font-size:.9rem;margin-top:-.4rem;margin-bottom:1.4rem">'
        'Define your industry, target niche, service offer and search queries for each outreach campaign.</p>',
        unsafe_allow_html=True
    )

    # ── Industry / Tone options (used in both cards and form) ──
    INDUSTRY_OPTS = [
        "NDIS / Disability Services",
        "Healthcare / Allied Health",
        "Aged Care",
        "Real Estate",
        "Legal Services",
        "Construction / Trades",
        "Hospitality / Events",
        "Education / Training",
        "Finance / Accounting",
        "Technology / Software",
        "Retail / E-commerce",
        "Marketing / Media",
        "Professional Services",
        "Other",
    ]
    TONE_OPTS = [
        "Warm & Professional",
        "Direct & Concise",
        "Friendly & Conversational",
        "Formal & Corporate",
        "Consultative",
    ]

    campaigns = campaign_service.all_campaigns()
    if campaigns:
        for c in campaigns:
            active  = c.get("active", True)
            status_badge = (
                '<span style="background:#DCFCE7;color:#14532D;border-radius:20px;'
                'padding:.15rem .55rem;font-size:.72rem;font-weight:700">Active</span>'
                if active else
                '<span style="background:#F3F4F6;color:#6B7280;border-radius:20px;'
                'padding:.15rem .55rem;font-size:.72rem;font-weight:700">Inactive</span>'
            )
            industry_badge = (
                f'<span style="background:#DBEAFE;color:#1E3A8A;border-radius:20px;'
                f'padding:.18rem .6rem;font-size:.78rem;font-weight:600">'
                f'{c.get("industry") or "NDIS / Disability Services"}</span>'
            )
            niche_badge = (
                f'<span style="background:#EDE9FE;color:#4C1D95;border-radius:20px;'
                f'padding:.18rem .6rem;font-size:.78rem;font-weight:600">'
                f'{c.get("niche","")}</span>'
            ) if c.get("niche") else ""
            tone_badge = (
                f'<span style="background:#FEF3C7;color:#78350F;border-radius:20px;'
                f'padding:.18rem .6rem;font-size:.78rem;font-weight:500">'
                f'✍️ {c.get("tone","")}</span>'
            ) if c.get("tone") else ""
            # Sender line
            sender_parts = [p for p in [
                c.get("sender_name"), c.get("sender_title"), c.get("sender_company")
            ] if p]
            sender_line = (
                f'<div style="font-size:.83rem;color:#6B7280;margin-bottom:.3rem">'
                f'👤 {" · ".join(sender_parts)}</div>'
            ) if sender_parts else ""
            # Value proposition
            vp = c.get("value_proposition", "")
            vp_line = (
                f'<div style="font-size:.86rem;color:#374151;margin-bottom:.25rem;'
                f'font-style:italic">"{vp}"</div>'
            ) if vp else ""
            locations_str = ", ".join(c.get("locations", [])) or "—"
            queries_list  = c.get("queries", [])

            query_tags = "".join(
                f'<span style="background:#F0FDF4;color:#14532D;border-radius:8px;'
                f'padding:.25rem .65rem;font-size:.82rem;border:1px solid #BBF7D0">{q}</span>'
                for q in queries_list
            )
            # Build card HTML as a flat string — no leading spaces so Markdown
            # doesn't treat it as a code block (4+ spaces = code block in CommonMark)
            card_html = (
                '<div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:16px;'
                'padding:1.3rem 1.5rem 1.1rem;margin-bottom:1rem;box-shadow:0 1px 4px rgba(0,0,0,.06)">'

                '<div style="display:flex;align-items:center;flex-wrap:wrap;gap:.5rem;margin-bottom:.6rem">'
                f'<span style="font-size:1.05rem;font-weight:800;color:#111827">{c.get("name", c["id"])}</span>'
                + industry_badge + niche_badge + tone_badge + status_badge +
                '</div>'

                + sender_line

                + f'<div style="font-size:.88rem;color:#374151;margin-bottom:.2rem">'
                  f'<b>Service:</b> {c.get("service","—")}</div>'

                + vp_line

                + f'<div style="font-size:.88rem;color:#374151;margin-bottom:.6rem">'
                  f'<b>Locations:</b> {locations_str}</div>'

                + f'<div style="font-size:.82rem;font-weight:700;color:#6B7280;text-transform:uppercase;'
                  f'letter-spacing:.06em;margin-bottom:.4rem">Search Queries ({len(queries_list)})</div>'

                + '<div style="display:flex;flex-wrap:wrap;gap:6px">'
                + query_tags
                + '</div></div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

            bc1, bc2, bc3 = st.columns([2, 2, 8])
            if bc1.button("✏️ Edit",   key=f"e_{c['id']}"):
                st.session_state["editing"] = c["id"]
                st.rerun()
            if bc2.button("🗑 Delete", key=f"d_{c['id']}"):
                campaign_service.delete(c["id"])
                st.rerun()
    else:
        st.markdown(
            '<div class="info-card">'
            '<div style="font-size:1.9rem;margin-bottom:.4rem">🎯</div>'
            '<div style="font-weight:600;font-size:.95rem;color:#111827;margin-bottom:.2rem">'
            'No campaigns yet</div>'
            '<div style="font-size:.85rem;color:#6B7280">'
            'Create your first campaign below to get started.</div>'
            '</div>',
            unsafe_allow_html=True
        )

    st.divider()

    eid = st.session_state.get("editing")
    ex  = (campaign_service.get(eid) or {}) if eid else {}

    st.markdown(
        f'<p style="font-size:.72rem;font-weight:700;color:#374151;text-transform:uppercase;'
        f'letter-spacing:.09em;margin-bottom:.8rem">{"✏️ Edit Campaign" if eid else "➕ New Campaign"}</p>',
        unsafe_allow_html=True
    )
    with st.form("cf"):
        # ── Section 1: Campaign Identity ──
        st.markdown('<span class="sec-head">🎯 Campaign Identity</span>', unsafe_allow_html=True)
        r1c1, r1c2 = st.columns(2)
        name = r1c1.text_input(
            "Campaign Name *",
            value=ex.get("name", ""),
            placeholder="e.g. Brisbane Support Coordinators",
        )
        industry_idx = INDUSTRY_OPTS.index(ex.get("industry", "NDIS / Disability Services")) \
                       if ex.get("industry") in INDUSTRY_OPTS else 0
        industry = r1c2.selectbox("Industry *", INDUSTRY_OPTS, index=industry_idx)

        r2c1, r2c2 = st.columns(2)
        niche = r2c1.text_input(
            "Target Role / Niche *",
            value=ex.get("niche", ""),
            placeholder="e.g. Support Coordinator, Solicitor, Real Estate Agent, GP…",
            help="The type of person or business you are reaching out to.",
        )
        tone_idx = TONE_OPTS.index(ex.get("tone", "Warm & Professional")) \
                   if ex.get("tone") in TONE_OPTS else 0
        tone = r2c2.selectbox("Email Tone", TONE_OPTS, index=tone_idx)

        # ── Section 2: Your Business ──
        st.markdown('<span class="sec-head">👤 Your Business</span>', unsafe_allow_html=True)
        s1c1, s1c2, s1c3 = st.columns(3)
        sender_name = s1c1.text_input(
            "Your Name",
            value=ex.get("sender_name", settings.sender_name),
            placeholder="e.g. Greg Gomez",
        )
        sender_title = s1c2.text_input(
            "Your Title",
            value=ex.get("sender_title", settings.sender_title),
            placeholder="e.g. CEO | Founder",
        )
        sender_company = s1c3.text_input(
            "Company Name",
            value=ex.get("sender_company", settings.company_name),
            placeholder="e.g. Yirra Care",
        )

        # ── Section 3: Campaign Details ──
        st.markdown('<span class="sec-head">📋 Campaign Details</span>', unsafe_allow_html=True)
        service = st.text_input(
            "Service / Offer Description *",
            value=ex.get("service", ""),
            placeholder="e.g. NDIS cleaning and domestic task support, Conveyancing services, Property management…",
        )
        value_prop = st.text_area(
            "Value Proposition",
            value=ex.get("value_proposition", ""),
            height=72,
            placeholder="What can you offer their clients? e.g. We have capacity for participants needing cleaning support and can onboard quickly.",
            help="Used by the AI when writing outreach emails — describe why you are valuable to their clients.",
        )

        # ── Section 4: Locations & Search ──
        st.markdown('<span class="sec-head">📍 Locations & Search Queries</span>', unsafe_allow_html=True)
        lc1, lc2 = st.columns([1, 2])
        locs = lc1.text_area(
            "Locations (one per line)",
            value="\n".join(ex.get("locations", [])),
            height=120,
            placeholder="e.g.\nBrisbane North\nMoreton Bay\nRedcliffe",
        )
        queries = lc2.text_area(
            "Search Queries (one per line) *",
            value="\n".join(ex.get("queries", [])),
            height=120,
            help="Each line = one Google/DuckDuckGo search. Be specific: include role + location + 'email' or 'contact'.",
            placeholder="e.g.\nsupport coordinator Brisbane email\nrecovery coach Moreton Bay contact\nsolicitor Sydney conveyancing email",
        )

        active = st.toggle("Active", value=ex.get("active", True))
        sb1, sb2 = st.columns(2)
        saved    = sb1.form_submit_button("💾  Save Campaign", use_container_width=True)
        canceled = sb2.form_submit_button("Cancel",            use_container_width=True)

        if saved:
            name_v    = (name    or "").strip()
            niche_v   = (niche   or "").strip()
            service_v = (service or "").strip()
            queries_v = (queries or "").strip()
            if not name_v or not queries_v:
                st.error("Campaign Name and at least one Search Query are required.")
            else:
                cid = eid or re.sub(r"[^a-z0-9]+", "_", name_v.lower()).strip("_")
                campaign_service.upsert({
                    "id":               cid,
                    "name":             name_v,
                    "industry":         industry,
                    "niche":            niche_v,
                    "tone":             tone,
                    "sender_name":      (sender_name    or "").strip() or settings.sender_name,
                    "sender_title":     (sender_title   or "").strip() or settings.sender_title,
                    "sender_company":   (sender_company or "").strip() or settings.company_name,
                    "service":          service_v,
                    "value_proposition": (value_prop or "").strip(),
                    "locations":        [l.strip() for l in (locs or "").splitlines() if l.strip()],
                    "queries":          [q.strip() for q in queries_v.splitlines()    if q.strip()],
                    "active":           active,
                })
                st.session_state.pop("editing", None)
                st.success("Campaign saved!")
                st.rerun()
        if canceled:
            st.session_state.pop("editing", None)
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — CONTACTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "  👥   Contacts":
    st.markdown("# Contacts")
    st.markdown(
        '<p style="color:#374151;font-size:.9rem;margin-top:-.4rem;margin-bottom:1.1rem">'
        'Contacts found and scored by the pipeline</p>',
        unsafe_allow_html=True
    )

    # ── Status summary pills ──
    df_status = db_query(
        "SELECT status, COUNT(*) cnt FROM contacts GROUP BY status ORDER BY cnt DESC"
    )
    if not df_status.empty:
        STATUS_STYLE = {
            "qualified":    ("#DCFCE7","#14532D"),
            "contacted":    ("#DBEAFE","#1E3A8A"),
            "email_ready":  ("#EDE9FE","#4C1D95"),
            "new":          ("#F3F4F6","#1F2937"),
            "enriched":     ("#E5E7EB","#1F2937"),
            "low_priority": ("#FEF3C7","#78350F"),
            "rejected":     ("#FEE2E2","#7F1D1D"),
        }
        pills = '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:1.2rem">'
        for _, row in df_status.iterrows():
            bg, fg = STATUS_STYLE.get(str(row["status"]), ("#F3F4F6","#1F2937"))
            label  = str(row["status"]).replace("_", " ").title()
            pills += (
                f'<span style="background:{bg};color:{fg};border-radius:20px;'
                f'padding:.32rem .85rem;font-size:.84rem;font-weight:600;'
                f'border:1px solid rgba(0,0,0,.08)">'
                f'{label} · {int(row["cnt"])}</span>'
            )
        pills += '</div>'
        st.markdown(pills, unsafe_allow_html=True)

    f1, f2, f3 = st.columns([3, 2, 2])
    search = f1.text_input("Search", placeholder="organisation, email, location…")
    status = f2.selectbox(
        "Status",
        ["all","new","enriched","qualified","low_priority","email_ready","contacted","rejected"]
    )
    ctype  = f3.selectbox(
        "Contact Type",
        ["all","Support Coordinator","Recovery Coach","Occupational Therapist",
         "Plan Manager","Community Organisation","Other"]
    )

    sql    = ("SELECT id, organisation, email, location, contact_type, "
              "qualification_score score, status, created_at "
              "FROM contacts WHERE 1=1")
    params = []
    if search:
        sql    += " AND (organisation LIKE ? OR email LIKE ? OR location LIKE ?)"
        params += [f"%{search}%"] * 3
    if status != "all":
        sql += " AND status = ?"
        params.append(status)
    if ctype  != "all":
        sql += " AND contact_type = ?"
        params.append(ctype)
    sql += " ORDER BY score DESC, created_at DESC"

    df = db_query(sql, tuple(params))
    st.caption(f"**{len(df)}** contacts")

    if df.empty:
        st.markdown(
            '<div class="info-card">'
            '<div style="font-size:1.9rem;margin-bottom:.4rem">🔍</div>'
            '<div style="font-weight:600;font-size:.95rem;color:#111827;margin-bottom:.2rem">'
            'No contacts match your search</div>'
            '<div style="font-size:.85rem;color:#6B7280">'
            'Try different filters, or run the pipeline to find new providers.</div>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        sel_df = df.copy()
        sel_df.insert(0, "select", False)
        edited_contacts = st.data_editor(
            sel_df,
            column_config={
                "select":       st.column_config.CheckboxColumn("✓",            default=False, width="small"),
                "id":           st.column_config.NumberColumn("ID",             width="small"),
                "organisation": st.column_config.TextColumn("Organisation",     width="large"),
                "email":        st.column_config.TextColumn("Email",            width="medium"),
                "location":     st.column_config.TextColumn("Location",         width="medium"),
                "contact_type": st.column_config.TextColumn("Contact Type",    width="medium"),
                "score":        st.column_config.NumberColumn("Score", format="%d ⭐", width="small"),
                "status":       st.column_config.TextColumn("Status",           width="small"),
                "created_at":   st.column_config.TextColumn("Added",            width="medium"),
            },
            use_container_width=True, hide_index=True, height=480,
            key="contacts_editor",
        )
        selected_contact_ids = df[edited_contacts["select"]]["id"].tolist()
        n_contacts_sel = len(selected_contact_ids)

        cd1, cd2, cd3 = st.columns([2, 2, 3])
        cd1.download_button(
            "⬇️ Download CSV", df.to_csv(index=False), "contacts.csv", "text/csv",
            use_container_width=True,
        )
        del_btn = cd2.button(
            f"🗑 Delete {n_contacts_sel} Contact{'s' if n_contacts_sel != 1 else ''}",
            disabled=n_contacts_sel == 0, use_container_width=True,
            key="del_contacts_btn",
        )
        if del_btn:
            st.session_state["confirm_del_contacts"] = selected_contact_ids

        if "confirm_del_contacts" in st.session_state:
            ids_to_del = st.session_state["confirm_del_contacts"]
            st.warning(
                f"⚠️ Delete **{len(ids_to_del)}** contact(s) and all their associated emails? "
                f"This cannot be undone."
            )
            y1, y2 = st.columns(2)
            if y1.button("✅ Yes, delete permanently", key="confirm_del_c_yes"):
                from app.db import delete_contacts
                n_del = delete_contacts(ids_to_del)
                st.session_state.pop("confirm_del_contacts", None)
                st.success(f"🗑 Deleted {n_del} contact(s).")
                st.rerun()
            if y2.button("Cancel", key="confirm_del_c_no"):
                st.session_state.pop("confirm_del_contacts", None)
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — EMAILS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "  ✉️   Emails":
    st.markdown("# Emails")
    st.markdown(
        '<p style="color:#374151;font-size:.9rem;margin-top:-.4rem;margin-bottom:1.1rem">'
        'Review and send outreach emails to NDIS providers</p>',
        unsafe_allow_html=True
    )

    if not has_token:
        st.error("Gmail not connected. Go to **Settings → API & Gmail** to set up.")
        st.stop()

    tab_send, tab_sent_t = st.tabs(["📤  Ready to Send", "✅  Sent"])

    with tab_send:
        from app.db import fetch_sendable_emails
        emails = fetch_sendable_emails(200)
        if not emails:
            st.markdown(
                '<div class="info-card">'
                '<div style="font-size:2rem;margin-bottom:.5rem">✉️</div>'
                '<div style="font-weight:600;font-size:.95rem;color:#111827;margin-bottom:.25rem">'
                'No emails ready to send</div>'
                '<div style="font-size:.85rem;color:#6B7280">'
                'Run the pipeline first to generate AI outreach emails.</div>'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            df_raw = pd.DataFrame(emails)
            df_raw.insert(0, "send", False)
            st.markdown(
                f'<div class="sec-head">{len(df_raw)} Emails Ready to Send</div>',
                unsafe_allow_html=True
            )
            edited = st.data_editor(
                df_raw[["send","organisation","recipient_email","subject","status","qualification_score"]],
                column_config={
                    "send":                st.column_config.CheckboxColumn("✓ Send",  default=False, width="small"),
                    "organisation":        st.column_config.TextColumn("Organisation",               width="medium"),
                    "recipient_email":     st.column_config.TextColumn("Email Address",              width="medium"),
                    "subject":             st.column_config.TextColumn("Email Subject",              width="large"),
                    "status":              st.column_config.TextColumn("Status",                     width="small"),
                    "qualification_score": st.column_config.NumberColumn("Score ⭐",                 width="small"),
                },
                hide_index=True,
                use_container_width=True,
                height=350,
                key="email_editor",
            )

            selected_ids = df_raw[edited["send"]]["id"].tolist()
            n_sel        = len(selected_ids)

            # ── Email preview (single selection) ──
            if n_sel == 1:
                row = next(e for e in emails if e["id"] == selected_ids[0])
                st.markdown('<div class="sec-head">Email Preview</div>', unsafe_allow_html=True)
                m1, m2, m3 = st.columns(3)
                m1.metric("To",    row["recipient_email"])
                m2.metric("Org",   row["organisation"] or "—")
                m3.metric("Score", row.get("qualification_score", "—"))
                st.markdown(f"**Subject:** {row['subject']}")
                st.text_area(
                    "Body", value=row["body"], height=220,
                    disabled=True, label_visibility="visible"
                )

            # ── Action buttons ──
            act1, act2, act3, act4 = st.columns([2, 2, 2, 2])
            act4.markdown(
                f'<p style="text-align:right;padding:.6rem 0;color:#374151;font-size:.86rem">'
                f'<b>{n_sel}</b> of {len(df_raw)} selected</p>',
                unsafe_allow_html=True
            )

            if act1.button("📬 Create Drafts", disabled=n_sel == 0):
                with st.spinner("Creating drafts in Gmail…"):
                    out, ok = run_step(["create-drafts", f"--limit={n_sel + 5}"])
                show_result(out, ok)
                st.rerun()

            send_label = f"📤 Send {n_sel}" if n_sel else "📤 Send"
            if act2.button(send_label, disabled=n_sel == 0):
                st.session_state["confirm_ids"] = selected_ids

            del_email_label = f"🗑 Delete {n_sel}" if n_sel else "🗑 Delete"
            if act3.button(del_email_label, disabled=n_sel == 0, key="del_emails_btn"):
                st.session_state["confirm_del_emails"] = selected_ids

            # ── Delete drafts confirmation ──
            if "confirm_del_emails" in st.session_state:
                ids_to_del_e = st.session_state["confirm_del_emails"]
                st.warning(
                    f"⚠️ Delete **{len(ids_to_del_e)}** email draft(s)? "
                    f"Gmail drafts will also be removed. This cannot be undone."
                )
                de1, de2 = st.columns(2)
                if de1.button("✅ Yes, delete", key="confirm_del_e_yes"):
                    from app.db import delete_emails, fetch_emails_by_ids
                    from app.services.gmail_service import delete_draft
                    rows_to_del = fetch_emails_by_ids(ids_to_del_e)
                    for row in rows_to_del:
                        if row.get("gmail_draft_id"):
                            try:
                                delete_draft(row["gmail_draft_id"])
                            except Exception:
                                pass
                    n_del_e = delete_emails(ids_to_del_e)
                    st.session_state.pop("confirm_del_emails", None)
                    st.success(f"🗑 Deleted {n_del_e} email draft(s).")
                    st.rerun()
                if de2.button("Cancel", key="confirm_del_e_no"):
                    st.session_state.pop("confirm_del_emails", None)
                    st.rerun()

            if "confirm_ids" in st.session_state:
                ids = st.session_state["confirm_ids"]
                st.markdown(
                    f'<div style="background:#FEF2F2;border:1px solid #FECACA;'
                    f'border-radius:var(--r-md);padding:1rem 1.2rem;margin:.6rem 0">'
                    f'<b style="color:#991B1B">⚠️ Confirm Send</b><br>'
                    f'<span style="color:#7F1D1D;font-size:.88rem">You are about to send '
                    f'<b>{len(ids)} real email(s)</b> from <b>{settings.sender_email}</b>. '
                    f'This cannot be undone.</span></div>',
                    unsafe_allow_html=True
                )
                yc, nc = st.columns(2)
                if yc.button("✅ Confirm — Send Now", key="yes_send"):
                    from app.workers.send_emails import run as do_send
                    with st.spinner(f"Sending {len(ids)} emails…"):
                        sc2, errs = do_send(email_ids=ids, limit=len(ids) + 5)
                    st.session_state.pop("confirm_ids", None)
                    if errs:
                        st.error(f"Sent {sc2} · Errors: {'; '.join(errs)}")
                    else:
                        st.success(f"🎉 {sc2} email(s) sent successfully!")
                    st.rerun()
                if nc.button("Cancel", key="no_send"):
                    st.session_state.pop("confirm_ids", None)
                    st.rerun()

    with tab_sent_t:
        df_s = db_query("""
            SELECT e.id, c.organisation, c.email recipient, e.subject, e.campaign,
                   c.qualification_score score, c.contact_type provider_type, e.sent_at
            FROM emails e
            JOIN contacts c ON c.id = e.contact_id
            WHERE e.status = 'sent'
            ORDER BY e.sent_at DESC
        """)
        if df_s.empty:
            st.markdown(
                '<div class="info-card">'
                '<div style="font-size:2rem;margin-bottom:.5rem">📤</div>'
                '<div style="font-weight:600;font-size:.95rem;color:#111827;margin-bottom:.25rem">'
                'No emails sent yet</div>'
                '<div style="font-size:.85rem;color:#6B7280">'
                'Tick emails in the Ready to Send tab, then click Send.</div>'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            st.caption(f"**{len(df_s)}** sent")
            st.dataframe(
                df_s,
                column_config={
                    "id":           st.column_config.NumberColumn("ID",           width="small"),
                    "organisation": st.column_config.TextColumn("Organisation",   width="large"),
                    "recipient":    st.column_config.TextColumn("Email",          width="medium"),
                    "subject":      st.column_config.TextColumn("Subject",        width="large"),
                    "campaign":     st.column_config.TextColumn("Campaign",       width="medium"),
                    "score":        st.column_config.NumberColumn("Score ⭐",     width="small"),
                    "provider_type":st.column_config.TextColumn("Provider Type",  width="medium"),
                    "sent_at":      st.column_config.TextColumn("Sent At",        width="medium"),
                },
                use_container_width=True, hide_index=True, height=450,
            )
            st.download_button(
                "⬇️ Download CSV", df_s.to_csv(index=False), "sent_emails.csv", "text/csv"
            )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "  ⚙️   Settings":
    st.markdown("# Settings")
    tab_api, tab_sndr, tab_cfg, tab_upd = st.tabs([
        "�� API & Gmail", "👤 Sender", "⚙️ Pipeline", "🔄 Updates"
    ])

    with tab_api:
        st.markdown("### OpenAI")
        oa1, oa2 = st.columns([4, 1])
        okey = oa1.text_input(
            "API Key", value=settings.openai_api_key or "",
            type="password", placeholder="sk-proj-…",
            help="Get your key at platform.openai.com/api-keys"
        )
        oa2.markdown("<br>", unsafe_allow_html=True)
        if oa2.button("Save", key="sv_oai"):
            if (okey or "").strip().startswith("sk-"):
                update_env_file({"OPENAI_API_KEY": (okey or "").strip()})
                st.success("OpenAI key saved.")
            else:
                st.error("Key must start with sk-")

        model_opts = ["gpt-4.1-mini", "gpt-4o-mini", "gpt-4o", "gpt-4.1"]
        cm         = settings.openai_model if settings.openai_model in model_opts else "gpt-4.1-mini"
        m1, m2     = st.columns([4, 1])
        chosen     = m1.selectbox("Model", model_opts, index=model_opts.index(cm))
        m2.markdown("<br>", unsafe_allow_html=True)
        if m2.button("Save", key="sv_mdl"):
            update_env_file({"OPENAI_MODEL": chosen})
            st.success("Model saved.")

        st.markdown("---")
        st.markdown("### Gmail Connection")
        st.caption("Connect the Gmail account you want to send outreach emails from.")

        hs, ht = gmail_status()

        if ht:
            # ── Already connected ──────────────────────────────────────────
            st.markdown("""
            <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:14px;
                        padding:1rem 1.2rem;margin:.5rem 0 .8rem">
              <div style="font-size:1.1rem;font-weight:700;color:#14532D;margin-bottom:.2rem">
                ✅ Gmail connected
              </div>
              <div style="font-size:.85rem;color:#166534">
                Your Gmail account is linked and ready to send emails.
              </div>
            </div>""", unsafe_allow_html=True)
            st.caption(f"Sending as: **{settings.sender_email}**  ·  "
                       "To switch accounts, disconnect and reconnect.")
            g1, g2 = st.columns(2)
            if g1.button("🔄 Switch Account"):
                (ROOT / "token.json").unlink(missing_ok=True)
                st.rerun()
            if g2.button("🔌 Disconnect"):
                (ROOT / "token.json").unlink(missing_ok=True)
                st.rerun()

        elif hs:
            # ── client_secret exists, not yet authenticated ────────────────
            st.markdown("""
            <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:14px;
                        padding:1rem 1.2rem;margin:.5rem 0 .8rem">
              <div style="font-size:.92rem;font-weight:600;color:#1E3A8A;margin-bottom:.2rem">
                Click below to sign in with your Google account
              </div>
              <div style="font-size:.83rem;color:#1E40AF">
                A browser window will open. Select the Gmail account you want
                to send from and click <b>Allow</b>.
              </div>
            </div>""", unsafe_allow_html=True)
            if st.button("🔗  Sign in with Gmail", use_container_width=False):
                with st.spinner("Opening browser for Gmail sign-in… (complete the login in the browser window)"):
                    try:
                        from google_auth_oauthlib.flow import InstalledAppFlow
                        _SCOPES = ["https://mail.google.com/"]
                        _flow = InstalledAppFlow.from_client_secrets_file(
                            str(ROOT / "client_secret.json"), _SCOPES
                        )
                        _creds = _flow.run_local_server(port=0, open_browser=True)
                        (ROOT / "token.json").write_text(_creds.to_json())
                        st.success("✅ Gmail connected successfully!")
                        st.rerun()
                    except Exception as _e:
                        st.error(f"Sign-in failed: {_e}")

        else:
            # ── No client_secret — admin setup needed ──────────────────────
            st.warning("Gmail is not configured yet. Ask your system administrator to complete the one-time setup.")
            with st.expander("⚙️ Admin: one-time setup instructions"):
                st.markdown("""
**1 ·** Go to [console.cloud.google.com](https://console.cloud.google.com/) → Create project

**2 ·** Enable the [Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com)

**3 ·** APIs & Services → OAuth Consent Screen → External → add test users

**4 ·** Credentials → Create OAuth client ID → Desktop app → Download JSON

**5 ·** Place the file as `client_secret.json` in the app root folder, then restart.
                """)
                ups = st.file_uploader("Or upload client_secret.json here", type=["json"])
                if ups:
                    (ROOT / "client_secret.json").write_bytes(ups.getvalue())
                    st.success("Saved. Restart the app, then return here to connect Gmail.")
                    st.rerun()

        st.markdown("---")
        st.markdown("### Google Custom Search *(optional)*")
        st.caption("Enables Google search results alongside DuckDuckGo for more NDIS provider prospects.")
        gs1, gs2 = st.columns(2)
        ga = gs1.text_input(
            "Google API Key", value=settings.google_api_key or "",
            type="password", placeholder="AIza…"
        )
        gc = gs2.text_input(
            "Custom Search Engine ID", value=settings.google_cse_id or "", placeholder="cx:…"
        )
        if st.button("Save Google Keys"):
            update_env_file({"GOOGLE_API_KEY": ga, "GOOGLE_CSE_ID": gc})
            st.success("Google search keys saved.")

    with tab_sndr:
        st.markdown("### Sender Information")
        st.caption("Used in outreach email signatures and AI personalisation.")
        with st.form("sf"):
            c1, c2 = st.columns(2)
            sn  = c1.text_input("Full Name",  value=settings.sender_name)
            st2 = c2.text_input("Title",      value=settings.sender_title)
            se  = c1.text_input("Email",      value=settings.sender_email)
            sp  = c2.text_input("Phone",      value=settings.sender_phone)
            sc_ = c1.text_input("Company",    value=settings.company_name)
            sw  = c2.text_input("Website",    value=settings.company_website)
            sl  = st.text_area("Default Locations", value=settings.default_locations, height=70)
            if st.form_submit_button("Save Sender Info"):
                update_env_file({
                    "SENDER_NAME": sn,   "SENDER_TITLE": st2,
                    "SENDER_EMAIL": se,  "SENDER_PHONE": sp,
                    "COMPANY_NAME": sc_, "COMPANY_WEBSITE": sw,
                    "DEFAULT_LOCATIONS": sl,
                })
                st.success("Saved. Restart the app to apply changes.")

    with tab_cfg:
        st.markdown("### Pipeline Limits")
        with st.form("pf"):
            p1, p2 = st.columns(2)
            mq = p1.number_input(
                "Max contacts per query", min_value=5, max_value=100,
                value=settings.max_contacts_per_query
            )
            dl = p2.number_input(
                "Request delay (s)", min_value=0.5, max_value=10.0,
                value=settings.request_delay_seconds, step=0.5
            )
            md = p1.number_input(
                "Max drafts per run", min_value=1, max_value=100,
                value=settings.max_drafts_per_run
            )
            if st.form_submit_button("Save Config"):
                update_env_file({
                    "MAX_CONTACTS_PER_QUERY": str(int(mq)),
                    "REQUEST_DELAY_SECONDS":  str(float(dl)),
                    "MAX_DRAFTS_PER_RUN":     str(int(md)),
                })
                st.success("Configuration saved.")

        st.markdown("---")
        st.markdown("### Database")
        stats  = get_stats()
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Total Contacts", stats["contacts"])
        d2.metric("Emails Written", stats["emails"])
        d3.metric("Gmail Drafts",   stats["drafts"])
        d4.metric("Sent",           stats["sent"])
        if st.button("Re-initialise DB"):
            from app.db import init_db
            init_db()
            st.success("Database tables verified and ready.")

    with tab_upd:
        from app.version import REPO_URL
        os_name = platform.system()

        # ── Current version card ─────────────────────────────────────────
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E5E7EB;border-radius:12px;
                    padding:1rem 1.2rem;margin-bottom:1rem">
          <div style="display:flex;align-items:center;justify-content:space-between">
            <div>
              <div style="font-size:.66rem;font-weight:700;color:#6B7280;
                          text-transform:uppercase;letter-spacing:.09em;margin-bottom:.3rem">
                Installed Version</div>
              <div style="font-size:1.4rem;font-weight:800;color:#111827">v{_installed_version()}</div>
              <div style="font-size:.78rem;color:#9CA3AF;margin-top:.1rem">{os_name} · {ROOT}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<span class="sec-head">Auto Update</span>', unsafe_allow_html=True)
        st.caption(
            "Pulls the latest code from GitHub (`main` branch) and reinstalls dependencies. "
            "Your data, API keys and Gmail credentials are **never** overwritten."
        )

        st.markdown("""
<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;
            padding:.9rem 1.1rem;color:#111827;font-size:.88rem;line-height:1.7;margin-bottom:1rem">
<div style="font-weight:700;color:#14532D;margin-bottom:.5rem">📋 What's new in v2.4.0</div>
<div>✅ <b>Multi-industry campaigns</b> — Industry selector (14 industries), free-text niche, tone, sender info, value proposition</div>
<div>✅ <b>AI emails use campaign context</b> — sender name, company, tone and value proposition all flow into GPT prompts</div>
<div>✅ <b>Generic contact qualifying</b> — non-NDIS contacts now qualify correctly for any industry</div>
<div>✅ <b>Update system restarts server</b> — all new code loads after Update Now without manual reopen</div>
<div>✅ <b>Delete Contacts &amp; Email Drafts</b> — remove from DB and Gmail in one click</div>
</div>
""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        if c1.button("🔍 Check for Updates", key="chk_upd", use_container_width=True):
            with st.spinner("Checking GitHub…"):
                nv3 = check_update()
            if nv3:
                st.success(f"🆕 Update available: **v{nv3}** — click Update Now to install.")
            else:
                st.info(f"✅ You are on the latest version (v{_installed_version()})")

        if c2.button("⬇️ Update Now", key="do_upd", use_container_width=True):
            with st.spinner("Pulling latest code from GitHub…"):
                steps_r = perform_update()
            all_ok = all(ok for _, _, ok in steps_r)
            for label, out_txt, ok in steps_r:
                if ok:
                    short = out_txt.strip().splitlines()[0][:120] if out_txt.strip() else "OK"
                    st.success(f"✅ **{label}** — {short}")
                else:
                    st.error(f"❌ **{label}**")
                    if out_txt.strip():
                        st.code(out_txt.strip()[:400])
            if all_ok:
                os.chdir(str(ROOT))
                try:
                    new_ver = (ROOT / "version.txt").read_text().strip()
                except Exception:
                    new_ver = "latest"
                st.success(f"🎉 **Update complete!** Now on **v{new_ver}**")
                st.info("⏳ The app will restart in 4 seconds to load the new code…")
                time.sleep(4)
                # Kill this Streamlit server process so the launcher restarts it
                # fresh — this is the only way to guarantee the new dashboard.py
                # (with updated changelog, new features, etc.) is fully loaded.
                # The launcher detects the server is gone and starts a new one.
                import signal
                PORT_FILE = Path.home() / ".yirracare.port"
                PORT_FILE.unlink(missing_ok=True)
                os.kill(os.getpid(), signal.SIGTERM)
            else:
                st.warning(
                    "⚠️ Update partially failed. "
                    "Make sure **git** is installed (`brew install git` on Mac) "
                    "and you have internet access."
                )
