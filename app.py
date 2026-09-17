import streamlit as st
import textwrap
from executive_productivity_backend import daily_brief, answer_question


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AionOS | Executive Intelligence",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(textwrap.dedent("""
<style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background: #f5f7fa;
        color: #172033;
    }

    .main .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    html, body, [class*="css"] {
        font-family: Inter, -apple-system, BlinkMacSystemFont,
                     "Segoe UI", sans-serif;
    }

    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #1f2937;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.2rem;
    }

    .sidebar-brand {
        padding: 10px 8px 24px 8px;
        border-bottom: 1px solid #273244;
        margin-bottom: 22px;
    }

    .brand-row {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-logo {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: #ffffff;
        color: #111827;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 18px;
    }

    .brand-name {
        color: #ffffff;
        font-size: 20px;
        font-weight: 700;
        letter-spacing: -0.3px;
    }

    .brand-subtitle {
        color: #9ca3af;
        font-size: 11px;
        margin-top: 4px;
        margin-left: 50px;
    }

    .sidebar-section {
        color: #6b7280;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.1px;
        margin: 22px 8px 8px 8px;
    }

    .sidebar-item {
        padding: 10px 12px;
        border-radius: 8px;
        margin-bottom: 4px;
        color: #cbd5e1;
        font-size: 13px;
    }

    .sidebar-item.active {
        background: #1f2937;
        color: #ffffff;
        font-weight: 600;
        border-left: 3px solid #ffffff;
        padding-left: 9px;
    }

    .sidebar-status {
        margin-top: 30px;
        padding: 14px;
        background: #172033;
        border: 1px solid #273244;
        border-radius: 10px;
    }

    .status-title {
        color: #ffffff;
        font-size: 12px;
        font-weight: 600;
    }

    .status-text {
        color: #9ca3af;
        font-size: 11px;
        margin-top: 5px;
    }

    .status-dot {
        color: #4ade80;
        font-size: 10px;
    }

    /* ---------- HEADER ---------- */

    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 26px;
    }

    .header-title {
        font-size: 30px;
        font-weight: 750;
        letter-spacing: -0.8px;
        color: #111827;
        margin-bottom: 5px;
    }

    .header-subtitle {
        color: #667085;
        font-size: 14px;
    }

    .executive-card {
        background: #ffffff;
        border: 1px solid #e4e7ec;
        border-radius: 10px;
        padding: 10px 15px;
        min-width: 190px;
    }

    .executive-name {
        font-size: 13px;
        font-weight: 650;
        color: #172033;
    }

    .executive-role {
        font-size: 11px;
        color: #667085;
        margin-top: 3px;
    }

    /* ---------- SNAPSHOT ---------- */

    .snapshot-bar {
        background: #ffffff;
        border: 1px solid #e4e7ec;
        border-radius: 9px;
        padding: 11px 15px;
        margin-bottom: 22px;
        color: #667085;
        font-size: 12px;
    }

    /* ---------- KPI CARDS ---------- */

    .kpi-card {
        background: #ffffff;
        border: 1px solid #e4e7ec;
        border-radius: 12px;
        padding: 18px;
        min-height: 112px;
    }

    .kpi-label {
        color: #667085;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 9px;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 750;
        color: #111827;
        line-height: 1;
    }

    .kpi-description {
        color: #98a2b3;
        font-size: 11px;
        margin-top: 8px;
    }

    /* ---------- SECTION ---------- */

    .section-header {
        margin-top: 30px;
        margin-bottom: 12px;
    }

    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #172033;
    }

    .section-description {
        color: #667085;
        font-size: 12px;
        margin-top: 3px;
    }

    /* ---------- COMMITMENT CARD ---------- */

    .commitment-card {
        background: #ffffff;
        border: 1px solid #e4e7ec;
        border-radius: 11px;
        padding: 16px;
        margin-bottom: 10px;
    }

    .commitment-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
    }

    .commitment-action {
        font-size: 14px;
        font-weight: 650;
        color: #172033;
        line-height: 1.5;
    }

    .commitment-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 18px;
        margin-top: 12px;
        color: #667085;
        font-size: 11px;
    }

    .meta-label {
        color: #98a2b3;
        margin-right: 4px;
    }

    /* ---------- BADGES ---------- */

    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 5px;
        font-size: 9px;
        font-weight: 750;
        letter-spacing: 0.5px;
        white-space: nowrap;
    }

    .badge-overdue {
        background: #fef3f2;
        color: #b42318;
        border: 1px solid #fecdca;
    }

    .badge-waiting {
        background: #fffaeb;
        color: #b54708;
        border: 1px solid #fedf89;
    }

    .badge-unclear {
        background: #f2f4f7;
        color: #475467;
        border: 1px solid #d0d5dd;
    }

    .badge-upcoming {
        background: #eff8ff;
        color: #175cd3;
        border: 1px solid #b2ddff;
    }

    .badge-completed {
        background: #ecfdf3;
        color: #027a48;
        border: 1px solid #abefc6;
    }

    .badge-confirmed {
        background: #ecfdf3;
        color: #027a48;
        border: 1px solid #abefc6;
    }

    /* ---------- EVIDENCE ---------- */

    .evidence-box {
        background: #f8fafc;
        border: 1px solid #eaecf0;
        border-radius: 7px;
        padding: 10px;
        margin-top: 8px;
    }

    .evidence-source {
        font-size: 10px;
        font-weight: 650;
        color: #344054;
        margin-bottom: 4px;
    }

    .evidence-text {
        font-size: 11px;
        color: #667085;
        line-height: 1.5;
    }

    /* ---------- AI PANEL ---------- */

    .ai-panel {
        background: #111827;
        border-radius: 13px;
        padding: 20px;
        margin-top: 32px;
        margin-bottom: 24px;
    }

    .ai-title {
        color: #ffffff;
        font-size: 17px;
        font-weight: 700;
    }

    .ai-subtitle {
        color: #9ca3af;
        font-size: 12px;
        margin-top: 3px;
        margin-bottom: 15px;
    }

    .answer-box {
        background: #1f2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 15px;
        color: #e5e7eb;
        font-size: 13px;
        line-height: 1.6;
        margin-top: 14px;
    }

    /* ---------- FOOTER ---------- */

    .footer {
        border-top: 1px solid #e4e7ec;
        margin-top: 40px;
        padding-top: 15px;
        color: #98a2b3;
        font-size: 10px;
        display: flex;
        justify-content: space-between;
    }

</style>
"""), unsafe_allow_html=True)


# ============================================================
# CONFIGURATION
# ============================================================

AS_OF = "2026-09-23"
AS_OF_TIME = "17:00"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def field(obj, name, default=""):
    """
    Safely get an attribute from a dataclass/object.
    """
    return getattr(obj, name, default)


def badge(status):
    """
    Convert backend status into a styled HTML badge.
    """

    status_map = {
        "OVERDUE": ("OVERDUE", "badge-overdue"),
        "WAITING_ON_DIVYA": ("WAITING", "badge-waiting"),
        "UNCLEAR_OWNERSHIP": ("OWNERSHIP UNCLEAR", "badge-unclear"),
        "UPCOMING": ("UPCOMING", "badge-upcoming"),
        "COMPLETED": ("COMPLETED", "badge-completed"),
        "CONFIRMED": ("CONFIRMED", "badge-confirmed"),
        "READY_FOR_REVIEW": ("READY FOR REVIEW", "badge-upcoming"),
    }

    label, css_class = status_map.get(
        status,
        (status.replace("_", " "), "badge-unclear")
    )

    return f'<span class="badge {css_class}">{label}</span>'


def render_commitment(item):
    """
    Render one commitment as a professional enterprise card.
    """

    action = field(item, "action", "No action specified")
    owner = field(item, "owner", "Unknown")
    recipient = field(item, "recipient", "—")
    deadline = field(item, "deadline", "—")
    priority = field(item, "priority", "—")
    status = field(item, "status", "UNKNOWN")
    topic = field(item, "topic", "General")

    st.html(textwrap.dedent(f"""
        <div class="commitment-card">

            <div class="commitment-top">

                <div style="flex:1;">
                    <div class="commitment-action">
                        {action}
                    </div>
                </div>

                <div>
                    {badge(status)}
                </div>

            </div>

            <div class="commitment-meta">

                <div>
                    <span class="meta-label">Owner:</span>
                    {owner}
                </div>

                <div>
                    <span class="meta-label">Recipient:</span>
                    {recipient}
                </div>

                <div>
                    <span class="meta-label">Deadline:</span>
                    {deadline}
                </div>

                <div>
                    <span class="meta-label">Priority:</span>
                    {priority}
                </div>

                <div>
                    <span class="meta-label">Topic:</span>
                    {topic}
                </div>

            </div>

        </div>
        """),
    )

    # Evidence section
    evidence = field(item, "evidence", [])

    if evidence:

        with st.expander("View supporting evidence"):

            visible_evidence = []

            for ev in evidence:

                ev_date = field(ev, "date", "")

                # Hide future evidence from the current snapshot
                if ev_date and ev_date > AS_OF:
                    continue

                visible_evidence.append(ev)

            if not visible_evidence:
                st.caption("No evidence available as of this snapshot.")

            else:

                for ev in visible_evidence:

                    source_type = field(
                        ev,
                        "source_type",
                        "source"
                    )

                    source_id = field(
                        ev,
                        "source_id",
                        ""
                    )

                    date = field(
                        ev,
                        "date",
                        ""
                    )

                    text = field(
                        ev,
                        "text",
                        ""
                    )

                    st.html(textwrap.dedent(f"""
                        <div class="evidence-box">

                            <div class="evidence-source">
                                {source_type.upper()} · {source_id} · {date}
                            </div>

                            <div class="evidence-text">
                                {text}
                            </div>

                        </div>
                        """),
                    )


def render_section(
    title,
    description,
    items,
    empty_message="No commitments in this section."
):

    st.html(textwrap.dedent(f"""
        <div class="section-header">

            <div class="section-title">
                {title}
            </div>

            <div class="section-description">
                {description}
            </div>

        </div>
        """),
    )

    if not items:

        st.info(empty_message)
        return

    for item in items:
        render_commitment(item)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.html(textwrap.dedent("""
        <div class="sidebar-brand">

            <div class="brand-row">

                <div class="brand-logo">
                    A
                </div>

                <div class="brand-name">
                    AionOS
                </div>

            </div>

            <div class="brand-subtitle">
                Executive Intelligence Platform
            </div>

        </div>
        """),
    )

    # Workspace
    st.html(
        '<div class="sidebar-section">WORKSPACE</div>',
    )

    st.html(textwrap.dedent("""
        <div class="sidebar-item active">
            Executive Overview
        </div>
        """),
    )

    # Intelligence
    st.html(
        '<div class="sidebar-section">INTELLIGENCE</div>',
    )

    st.html(textwrap.dedent("""
        <div class="sidebar-item">
            Commitments
        </div>

        <div class="sidebar-item">
            Follow-ups
        </div>

        <div class="sidebar-item">
            Insights
        </div>
        """),
    )

    # System
    st.html(
        '<div class="sidebar-section">SYSTEM</div>',
    )

    st.html(textwrap.dedent("""
        <div class="sidebar-item">
            Data Sources
        </div>

        <div class="sidebar-item">
            Agent Activity
        </div>
        """),
    )

    # System status
    st.html(textwrap.dedent("""
        <div class="sidebar-status">

            <div class="status-title">
                AionOS Intelligence
            </div>

            <div class="status-text">
                <span class="status-dot">●</span>
                System operational
            </div>

        </div>
        """),
    )

    st.html(textwrap.dedent("""
        <div style="
            color:#6b7280;
            font-size:10px;
            margin-top:12px;
            padding-left:4px;
        ">
            Environment: Prototype
        </div>
        """),
    )


# ============================================================
# LOAD DAILY BRIEF
# ============================================================

try:

    brief = daily_brief(AS_OF)

except Exception as e:

    st.error("Unable to load the executive brief.")

    st.exception(e)

    st.stop()


# ============================================================
# EXTRACT DATA
# ============================================================

commitments = brief.get("all_commitments", [])

my_actions = brief.get(
    "my_actions",
    []
)

waiting = brief.get(
    "waiting_on_others",
    []
)

overdue = brief.get(
    "overdue",
    []
)

unclear = brief.get(
    "unclear_ownership",
    []
)


# ============================================================
# PAGE HEADER
# ============================================================

st.html(textwrap.dedent("""
    <div class="page-header">

        <div>

            <div class="header-title">
                Executive Overview
            </div>

            <div class="header-subtitle">
                Commitment intelligence, action tracking and follow-up management
            </div>

        </div>

        <div class="executive-card">

            <div class="executive-name">
                Arjun Malhotra
            </div>

            <div class="executive-role">
                VP Sales · Executive Workspace
            </div>

        </div>

    </div>
    """),
)


# ============================================================
# SNAPSHOT BAR
# ============================================================

st.html(textwrap.dedent(f"""
    <div class="snapshot-bar">

        <strong>Intelligence snapshot:</strong>
        September 23, 2026 · {AS_OF_TIME}

        &nbsp;&nbsp;|&nbsp;&nbsp;

        Data processed from executive communication sources

    </div>
    """),
)


# ============================================================
# KPI CARDS
# ============================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)


with kpi1:

    st.html(textwrap.dedent(f"""
        <div class="kpi-card">

            <div class="kpi-label">
                MY OPEN ACTIONS
            </div>

            <div class="kpi-value">
                {len(my_actions)}
            </div>

            <div class="kpi-description">
                Commitments owned by you
            </div>

        </div>
        """),
    )


with kpi2:

    st.html(textwrap.dedent(f"""
        <div class="kpi-card">

            <div class="kpi-label">
                WAITING / OTHERS
            </div>

            <div class="kpi-value">
                {len(waiting)}
            </div>

            <div class="kpi-description">
                Actions currently dependent on others
            </div>

        </div>
        """),
    )


with kpi3:

    st.html(textwrap.dedent(f"""
        <div class="kpi-card">

            <div class="kpi-label">
                OVERDUE
            </div>

            <div class="kpi-value">
                {len(overdue)}
            </div>

            <div class="kpi-description">
                Commitments requiring attention
            </div>

        </div>
        """),
    )


with kpi4:

    st.html(textwrap.dedent(f"""
        <div class="kpi-card">

            <div class="kpi-label">
                UNCLEAR OWNERSHIP
            </div>

            <div class="kpi-value">
                {len(unclear)}
            </div>

            <div class="kpi-description">
                Items requiring ownership resolution
            </div>

        </div>
        """),
    )


# ============================================================
# MY ACTIONS
# ============================================================

render_section(
    "My Actions",
    "Commitments where you are explicitly responsible for the next action.",
    my_actions,
    "No open actions currently require your attention."
)


# ============================================================
# WAITING ON OTHERS
# ============================================================

render_section(
    "Waiting on Others",
    "Commitments where the next action belongs to another participant.",
    waiting,
    "Nothing is currently waiting on another participant."
)


# ============================================================
# OVERDUE
# ============================================================

render_section(
    "Overdue Commitments",
    "Commitments whose latest confirmed deadline has passed.",
    overdue,
    "No overdue commitments."
)


# ============================================================
# UNCLEAR OWNERSHIP
# ============================================================

render_section(
    "Ownership Exceptions",
    "Items where the available communication does not establish a clear owner.",
    unclear,
    "No ownership exceptions detected."
)


# ============================================================
# ASK AIONOS
# ============================================================

st.html(textwrap.dedent("""
    <div class="ai-panel">

        <div class="ai-title">
            Ask AionOS
        </div>

        <div class="ai-subtitle">
            Query your executive communication intelligence
        </div>

    </div>
    """),
)


question = st.text_input(
    "Ask AionOS",
    placeholder="What did I promise Raghav?",
    label_visibility="collapsed"
)


ask_col, spacer = st.columns([1, 6])


with ask_col:

    ask = st.button(
        "Ask AionOS",
        type="primary",
        use_container_width=True
    )


if ask:

    if not question.strip():

        st.warning("Please enter a question.")

    else:

        try:

            answer = answer_question(
                question,
                AS_OF
            )

            st.html(textwrap.dedent(f"""
                <div class="answer-box">
                    {answer}
                </div>
                """),
            )

        except Exception as e:

            st.error("Unable to answer the question.")

            st.exception(e)


# ============================================================
# COMMITMENT INTELLIGENCE
# ============================================================

st.html(textwrap.dedent("""
    <div class="section-header">

        <div class="section-title">
            Commitment Intelligence
        </div>

        <div class="section-description">
            All resolved commitments identified from the current communication snapshot.
        </div>

    </div>
    """),
)


with st.expander(
    f"View all {len(commitments)} commitments"
):

    if not commitments:

        st.info("No commitments detected.")

    else:

        for item in commitments:

            render_commitment(item)


# ============================================================
# FOOTER
# ============================================================

st.html(textwrap.dedent("""
    <div class="footer">

        <div>
            AionOS Executive Intelligence
        </div>

        <div>
            Commitment Resolution Engine · Prototype
        </div>

    </div>
    """),
)
