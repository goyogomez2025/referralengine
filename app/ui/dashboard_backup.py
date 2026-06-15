import sys
import sqlite3
import subprocess
from pathlib import Path

import pandas as pd
import streamlit as st

# ── Make sure project root is in sys.path ─────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from app.config import settings  # noqa: E402

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Yirra Care · Referral Engine",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*, body, [class*="css"] { font-family: 'Inter', sans-serif; }

[data-testid="stAppViewContainer"]  { background: #F4F7F5; }
[data-testid="stSidebar"]           { background: #1B4332 !important; }
[data-testid="stSidebar"] *         { color: #D8F3DC !important; }
[data-testid="stSidebar"] hr        { border-color: #2D6A4F !important; }

section[data-testid="stSidebar"] .stRadio label {
    background: #2D6A4F;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    margin: 0.15rem 0;
    display: block;
    font-weight: 500;
    cursor: pointer;
}
section[data-testid="stSidebar"] .stRadio label:hover { background: #40916C; }

.stButton > button {
    background: #2D6A4F !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: .55rem 1.4rem !important;
    font-weight: 600 !important;
    width: 100%;
    transition: background .2s;
}
.stButton > button:hover { background: #1B4332 !important; }

.card {
    background: #fff;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 1px 6px rgba(0,0,0,.07);
    text-align: center;
    margin-bottom: .4rem;
}
.card-num   { font-size: 2.6rem; font-weight: 700; color: #2D6A4F; line-height:1; }
.card-label { font-size: .78rem; color: #6B7280; margin-top:.45rem; font-weight:500; text-transform:uppercase; letter-spacing:.05em; }

.section-title { font-size:1.1rem; font-weight:700; color:#1B4332; margin:1.4rem 0 .6rem; }

.badge-qualified   { background:#D1FAE5; color:#065F46; padding:2px 10px; border-radius:20px; font-size:.75rem; font-weight:600; }
.badge-rejected    { background:#FEE2E2; color:#991B1B; padding:2px 10px; border-radius:20px; font-size:.75rem; font-weight:600; }
.badge-new         { background:#E0F2FE; color:#075985; padding:2px 10px; border-radius:20px; font-size:.75rem; font-weight:600; }
.badge-email_ready { background:#FEF9C3; color:#92400E; padding:2px 10px; border-radius:20px; font-size:.75rem; font-weight:600; }
.badge-draft       { background:#EDE9FE; color:#5B21B6; padding:2px 10px; border-radius:20px; font-size:.75rem; font-weight:600; }

h1 { color: #1B4332 !important; }
h2, h3 { color: #2D6A4F !important; }
</style>
""", unsafe_allow_html=True)


# ── DB helpers ────────────────────────────────────────────────────────────────
def db_query(sql: str, params: tuple = ()) -> pd.DataFrame:
    conn = sqlite3.connect(str(ROOT / settings.database_path))
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


def get_stats() -> dict:
    return {
        "prospects": int(db_query("SELECT COUNT(*) n FROM prospects").iloc[0]["n"]),
        "contacts":  int(db_query("SELECT COUNT(*) n FROM contacts").iloc[0]["n"]),
        "qualified": int(db_query("SELECT COUNT(*) n FROM contacts WHERE status='qualified'").iloc[0]["n"]),
        "emails":    int(db_query("SELECT COUNT(*) n FROM emails").iloc[0]["n"]),
        "drafts":    int(db_query("SELECT COUNT(*) n FROM emails WHERE status='gmail_draft_created'").iloc[0]["n"]),
    }


def run_step(args: list[str]) -> tuple[str, bool]:
    result = subprocess.run(
        [sys.executable, "-m", "app.main"] + args,
        capture_output=True, text=True, cwd=str(ROOT),
    )
    return (result.stdout + result.stderr).strip(), result.returncode == 0


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 Yirra Care")
    st.markdown("**Referral Engine**")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["🏠  Dashboard", "⚡  Pipeline", "👥  Contacts", "✉️  Emails"],
        label_visibility="hidden",
    )
    st.markdown("---")
    st.markdown(f"👤 **{settings.sender_name}**")
    st.caption(settings.sender_email)
    st.caption("📍 Brisbane North · Moreton Bay")


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠  Dashboard":
    st.title("🌿 Yirra Care — Referral Engine")
    st.caption("Automated NDIS outreach pipeline")
    st.markdown("---")

    stats = get_stats()
    labels = [
        ("🔍", "prospects", "Prospects Found"),
        ("👤", "contacts",  "Contacts Extracted"),
        ("✅", "qualified", "Qualified Contacts"),
        ("✍️", "emails",    "Emails Written"),
        ("📬", "drafts",    "Gmail Drafts"),
    ]
    cols = st.columns(5)
    for col, (icon, key, label) in zip(cols, labels):
        col.markdown(f"""
        <div class="card">
            <div style="font-size:1.6rem">{icon}</div>
            <div class="card-num">{stats[key]}</div>
            <div class="card-label">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    left, right = st.columns([3, 2])

    with left:
        st.markdown('<div class="section-title">🕐 Recent Contacts</div>', unsafe_allow_html=True)
        recent = db_query("""
            SELECT organisation, email, contact_type, qualification_score AS score, status
            FROM contacts ORDER BY created_at DESC LIMIT 8
        """)
        if not recent.empty:
            st.dataframe(recent, use_container_width=True, hide_index=True, height=280)
        else:
            st.info("No contacts yet — run the pipeline.")

    with right:
        st.markdown('<div class="section-title">📊 Contacts by Type</div>', unsafe_allow_html=True)
        by_type = db_query("""
            SELECT contact_type AS type, COUNT(*) AS count
            FROM contacts WHERE contact_type IS NOT NULL
            GROUP BY contact_type ORDER BY count DESC
        """)
        if not by_type.empty:
            st.bar_chart(by_type.set_index("type")["count"], color="#2D6A4F")
        else:
            st.info("No data yet.")

    st.markdown('<div class="section-title">📬 Pipeline Progress</div>', unsafe_allow_html=True)
    progress = [
        ("Find",          stats["prospects"], 60),
        ("Scrape",        stats["contacts"],  60),
        ("Qualify",       stats["qualified"], 30),
        ("Write Emails",  stats["emails"],    30),
        ("Gmail Drafts",  stats["drafts"],    30),
    ]
    for label, val, target in progress:
        pct = min(val / target, 1.0) if target else 0
        c1, c2, c3 = st.columns([2, 5, 1])
        c1.caption(label)
        c2.progress(pct)
        c3.caption(f"{val}")


# ══════════════════════════════════════════════════════════════════════════════
#  PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚡  Pipeline":
    st.title("⚡ Pipeline Runner")
    st.caption("Run individual steps or the full pipeline at once")
    st.markdown("---")

    # ── Full pipeline ─────────────────────────────────────────────────────────
    st.markdown("### 🚀 Full Pipeline")
    c1, c2, c3 = st.columns([3, 2, 2])
    campaign_full = c1.text_input("Campaign", "cleaning_sc_brisbane", key="fp_camp")
    limit_full    = c2.slider("Limit per step", 10, 100, 30, key="fp_limit")

    if c3.button("▶ Run Full Pipeline", key="run_all"):
        steps = [
            (["find",          f"--limit={limit_full}"],                             "🔍 Finding prospects"),
            (["scrape",        f"--limit={limit_full}"],                             "📧 Scraping emails"),
            (["qualify",       f"--limit={limit_full * 3}"],                         "✅ Qualifying contacts"),
            (["write-emails",  f"--campaign={campaign_full}", f"--limit={limit_full}"], "✍️ Writing emails"),
            (["create-drafts", f"--limit={limit_full}"],                             "📬 Creating Gmail drafts"),
        ]
        progress_bar = st.progress(0)
        for i, (args, label) in enumerate(steps):
            with st.spinner(f"Step {i+1}/5 — {label}"):
                out, ok = run_step(args)
            progress_bar.progress((i + 1) / len(steps))
            if ok:
                st.success(f"✅ {label} — {out}")
            else:
                st.error(f"❌ Failed: {label}")
                st.code(out)
                break
        else:
            st.balloons()
            st.success("🎉 Pipeline complete! Check Gmail Drafts.")

    st.markdown("---")

    # ── Individual steps ──────────────────────────────────────────────────────
    st.markdown("### 🔧 Individual Steps")
    left, right = st.columns(2)

    with left:
        with st.expander("1 · 🔍 Find Prospects", expanded=True):
            l1 = st.slider("Limit", 10, 100, 30, key="l1")
            if st.button("Run Find", key="b1"):
                with st.spinner("Searching..."):
                    out, ok = run_step(["find", f"--limit={l1}"])
                st.success(out) if ok else st.error(out)

        with st.expander("2 · 📧 Scrape Emails"):
            l2 = st.slider("Limit", 10, 100, 30, key="l2")
            if st.button("Run Scrape", key="b2"):
                with st.spinner("Scraping websites..."):
                    out, ok = run_step(["scrape", f"--limit={l2}"])
                st.success(out) if ok else st.error(out)

        with st.expander("3 · ✅ Qualify Contacts"):
            l3 = st.slider("Limit", 10, 200, 50, key="l3")
            if st.button("Run Qualify", key="b3"):
                with st.spinner("Qualifying..."):
                    out, ok = run_step(["qualify", f"--limit={l3}"])
                st.success(out) if ok else st.error(out)

    with right:
        with st.expander("4 · ✍️ Write Emails with AI", expanded=True):
            camp4 = st.text_input("Campaign", "cleaning_sc_brisbane", key="c4")
            l4    = st.slider("Limit", 5, 100, 20, key="l4")
            if st.button("Run Write Emails", key="b4"):
                with st.spinner("GPT is writing emails..."):
                    out, ok = run_step(["write-emails", f"--campaign={camp4}", f"--limit={l4}"])
                st.success(out) if ok else st.error(out)

        with st.expander("5 · 📬 Create Gmail Drafts"):
            l5 = st.slider("Limit", 5, 50, 20, key="l5")
            if st.button("Run Create Drafts", key="b5"):
                with st.spinner("Pushing to Gmail..."):
                    out, ok = run_step(["create-drafts", f"--limit={l5}"])
                st.success(out) if ok else st.error(out)

        with st.expander("📥 Import Contacts from CSV"):
            uploaded = st.file_uploader("Upload CSV", type="csv")
            if uploaded and st.button("Import", key="b6"):
                import_path = ROOT / "data" / "import_tmp.csv"
                import_path.write_bytes(uploaded.getvalue())
                with st.spinner("Importing..."):
                    out, ok = run_step(["import-contacts", f"--path={import_path}"])
                st.success(out) if ok else st.error(out)

        with st.expander("⬇️ Export to CSV"):
            if st.button("Export Contacts", key="b7"):
                out, ok = run_step(["export-contacts"])
                st.success(out) if ok else st.error(out)
            if st.button("Export Emails", key="b8"):
                out, ok = run_step(["export-emails"])
                st.success(out) if ok else st.error(out)


# ══════════════════════════════════════════════════════════════════════════════
#  CONTACTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👥  Contacts":
    st.title("👥 Contacts")
    st.markdown("---")

    f1, f2, f3 = st.columns([3, 2, 2])
    search  = f1.text_input("🔍 Search", placeholder="organisation, email, location...")
    status  = f2.selectbox("Status", ["all", "new", "enriched", "qualified", "low_priority", "email_ready", "rejected"])
    ctype   = f3.selectbox("Type", ["all", "Support Coordinator", "Recovery Coach",
                                     "Occupational Therapist", "Plan Manager",
                                     "Community Organisation", "Other"])

    sql    = """SELECT id, organisation, email, location, contact_type,
                       qualification_score AS score, status, created_at
                FROM contacts WHERE 1=1"""
    params: list = []

    if search:
        sql += " AND (organisation LIKE ? OR email LIKE ? OR location LIKE ?)"
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]
    if status != "all":
        sql += " AND status = ?"
        params.append(status)
    if ctype != "all":
        sql += " AND contact_type = ?"
        params.append(ctype)

    sql += " ORDER BY score DESC, created_at DESC"
    df = db_query(sql, tuple(params))

    st.caption(f"**{len(df)}** contacts")

    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True, height=420)
        st.download_button(
            "⬇️ Download CSV", df.to_csv(index=False),
            file_name="contacts.csv", mime="text/csv",
        )
    else:
        st.info("No contacts match your filters.")


# ══════════════════════════════════════════════════════════════════════════════
#  EMAILS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "✉️  Emails":
    st.title("✉️ Emails")
    st.markdown("---")

    f1, f2 = st.columns([3, 2])
    search = f1.text_input("🔍 Search", placeholder="subject, organisation, campaign...")
    status = f2.selectbox("Status", ["all", "draft_ready", "gmail_draft_created", "sent"])

    sql = """
        SELECT e.id, c.organisation, c.email AS recipient,
               e.campaign, e.subject, e.status, e.created_at
        FROM emails e
        LEFT JOIN contacts c ON e.contact_id = c.id
        WHERE 1=1
    """
    params: list = []
    if search:
        sql += " AND (e.subject LIKE ? OR c.organisation LIKE ? OR e.campaign LIKE ?)"
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]
    if status != "all":
        sql += " AND e.status = ?"
        params.append(status)
    sql += " ORDER BY e.created_at DESC"

    df = db_query(sql, tuple(params))
    st.caption(f"**{len(df)}** emails")

    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True, height=280)

        st.markdown("---")
        st.markdown("### 👁️ Preview Email")
        selected_id = st.selectbox(
            "Select email to preview",
            df["id"].tolist(),
            format_func=lambda i: (
                f"{df[df.id == i]['organisation'].values[0]}  —  "
                f"{df[df.id == i]['subject'].values[0][:55]}..."
            ),
        )
        if selected_id:
            row = db_query("""
                SELECT e.subject, e.body, e.status, e.campaign,
                       c.organisation, c.email AS recipient
                FROM emails e
                LEFT JOIN contacts c ON e.contact_id = c.id
                WHERE e.id = ?
            """, (selected_id,)).iloc[0]

            c1, c2, c3 = st.columns(3)
            c1.metric("To", row.recipient or "—")
            c2.metric("Organisation", row.organisation or "—")
            c3.metric("Status", row.status)

            st.markdown(f"**Subject:** {row.subject}")
            st.markdown("---")
            st.text_area("Email body", value=row.body, height=280, disabled=True, label_visibility="collapsed")

        st.markdown("---")
        st.download_button(
            "⬇️ Download CSV", df.to_csv(index=False),
            file_name="emails.csv", mime="text/csv",
        )
    else:
        st.info("No emails match your filters.")
