import streamlit as st

FORZY_CSS = """
<style>
/* ─── Google Fonts ─── */
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;600;700;900&family=Barlow+Condensed:wght@700;900&family=Inter:wght@300;400;500&display=swap');

/* ─── Root Variables (Forzy Brand) ─── */
:root {
    --orange:   #FF6B00;
    --orange-l: #FF8C33;
    --purple:   #3D1A6E;
    --purple-l: #5B2DA0;
    --yellow:   #F5C400;
    --black:    #111111;
    --white:    #FFFFFF;
    --gray-bg:  #F4F4F6;
    --gray-mid: #CCCCCC;
    --gray-dk:  #555555;
    --success:  #28A745;
    --warning:  #FFC107;
    --danger:   #DC3545;
    --card-bg:  #FFFFFF;
    --border:   #E0E0E0;
    --shadow:   0 4px 24px rgba(0,0,0,0.08);
    --radius:   12px;
}

/* ─── Global Reset ─── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--black);
    background-color: var(--gray-bg);
}

/* ─── Sidebar ─── */
[data-testid="stSidebar"] {
    background: var(--purple) !important;
    border-right: 3px solid var(--orange) !important;
}

[data-testid="stSidebar"] * {
    color: var(--white) !important;
}

.sidebar-logo {
    padding: 8px 0 4px 0;
    text-align: left;
}
.logo-forzy {
    display: block;
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 42px;
    color: var(--orange) !important;
    line-height: 1;
    letter-spacing: -1px;
    font-style: italic;
}
.logo-sub {
    display: block;
    font-size: 11px;
    font-weight: 400;
    color: rgba(255,255,255,0.6) !important;
    letter-spacing: 0.5px;
    margin-top: 2px;
}

/* ─── Sidebar Nav Buttons ─── */
[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    color: rgba(255,255,255,0.8) !important;
    border: none !important;
    border-radius: 8px !important;
    text-align: left !important;
    font-family: 'Barlow', sans-serif !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    margin: 2px 0 !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,107,0,0.25) !important;
    color: var(--white) !important;
    transform: translateX(4px) !important;
}

/* ─── Main Content Area ─── */
.main .block-container {
    padding: 2rem 2.5rem 4rem 2.5rem !important;
    max-width: 1400px;
}

/* ─── Page Headers ─── */
.page-header {
    border-left: 5px solid var(--orange);
    padding-left: 16px;
    margin-bottom: 28px;
}
.page-header h1 {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 36px;
    color: var(--purple);
    line-height: 1.1;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.page-header p {
    color: var(--gray-dk);
    font-size: 14px;
    margin: 6px 0 0 0;
}

/* ─── KPI Cards ─── */
.kpi-card {
    background: var(--card-bg);
    border-radius: var(--radius);
    padding: 20px 24px;
    box-shadow: var(--shadow);
    border-top: 4px solid var(--orange);
    position: relative;
    overflow: hidden;
}
.kpi-card.purple  { border-top-color: var(--purple); }
.kpi-card.yellow  { border-top-color: var(--yellow); }
.kpi-card.success { border-top-color: var(--success); }
.kpi-card .kpi-value {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 42px;
    font-weight: 900;
    color: var(--orange);
    line-height: 1;
}
.kpi-card.purple .kpi-value  { color: var(--purple); }
.kpi-card.yellow .kpi-value  { color: #C89A00; }
.kpi-card.success .kpi-value { color: var(--success); }
.kpi-card .kpi-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--gray-dk);
    margin-top: 4px;
}
.kpi-card .kpi-icon {
    position: absolute;
    top: 16px;
    right: 20px;
    font-size: 28px;
    opacity: 0.15;
}

/* ─── Data Table ─── */
.forzy-table {
    width: 100%;
    border-collapse: collapse;
    background: var(--card-bg);
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow);
    font-size: 13px;
}
.forzy-table thead tr {
    background: var(--purple);
    color: var(--white);
}
.forzy-table thead th {
    padding: 14px 16px;
    text-align: left;
    font-family: 'Barlow', sans-serif;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.forzy-table tbody tr {
    border-bottom: 1px solid var(--border);
    transition: background 0.15s;
}
.forzy-table tbody tr:hover {
    background: #FFF5EE;
}
.forzy-table tbody td {
    padding: 12px 16px;
    color: var(--black);
}
.tag-badge {
    display: inline-block;
    background: var(--orange);
    color: white;
    padding: 3px 10px;
    border-radius: 50px;
    font-size: 11px;
    font-weight: 700;
    font-family: 'Barlow', monospace;
    letter-spacing: 1px;
}
.status-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 50px;
    font-size: 11px;
    font-weight: 600;
}
.status-active   { background: #E6F9ED; color: #1A7A35; }
.status-inactive { background: #FEE; color: #C0392B; }
.status-maint    { background: #FFF3CD; color: #856404; }

/* ─── Cards / Panels ─── */
.forzy-card {
    background: var(--card-bg);
    border-radius: var(--radius);
    padding: 24px;
    box-shadow: var(--shadow);
    margin-bottom: 20px;
}
.forzy-card h3 {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 20px;
    color: var(--purple);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 0 16px 0;
    border-bottom: 2px solid var(--orange);
    padding-bottom: 10px;
}

/* ─── Section Divider ─── */
.section-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 24px 0 16px 0;
}
.section-divider span {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 14px;
    color: var(--purple);
    text-transform: uppercase;
    letter-spacing: 2px;
    white-space: nowrap;
}
.section-divider::after {
    content: '';
    flex: 1;
    height: 2px;
    background: linear-gradient(to right, var(--orange), transparent);
}

/* ─── Streamlit native overrides ─── */
.stButton > button {
    background: var(--orange) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Barlow', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 24px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: var(--orange-l) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(255,107,0,0.4) !important;
}

/* Secondary button via container class */
.btn-secondary .stButton > button {
    background: var(--purple) !important;
}
.btn-secondary .stButton > button:hover {
    background: var(--purple-l) !important;
    box-shadow: 0 4px 12px rgba(61,26,110,0.4) !important;
}

.stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
    border: 1.5px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.2s !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: var(--orange) !important;
    box-shadow: 0 0 0 2px rgba(255,107,0,0.15) !important;
}

label {
    font-weight: 600 !important;
    font-size: 13px !important;
    color: var(--gray-dk) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

.stSuccess {
    background: #E6F9ED !important;
    border-left: 4px solid var(--success) !important;
    border-radius: 8px !important;
}
.stWarning {
    background: #FFF8E6 !important;
    border-left: 4px solid var(--warning) !important;
}
.stError {
    background: #FEE !important;
    border-left: 4px solid var(--danger) !important;
}

/* ─── Raw Data Gauge-like cards ─── */
.sensor-card {
    background: var(--black);
    border-radius: var(--radius);
    padding: 20px;
    text-align: center;
    border: 1px solid #333;
    position: relative;
}
.sensor-card .sensor-value {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 38px;
    font-weight: 900;
    color: var(--orange);
    line-height: 1;
}
.sensor-card .sensor-unit {
    font-size: 14px;
    color: var(--gray-mid);
    margin-top: 4px;
}
.sensor-card .sensor-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #888;
    margin-top: 8px;
}
.sensor-card .sensor-status {
    position: absolute;
    top: 12px;
    right: 12px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 6px var(--success);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* ─── Topbar accent strip ─── */
.topbar-strip {
    display: flex;
    gap: 4px;
    margin-bottom: 24px;
}
.strip-seg {
    height: 4px;
    border-radius: 2px;
    flex: 1;
}
.s1 { background: var(--orange); }
.s2 { background: var(--purple); }
.s3 { background: var(--yellow); }
.s4 { background: var(--orange); flex: 0.5; }

/* ─── Metric delta ─── */
[data-testid="stMetricDelta"] { font-size: 12px !important; }
</style>
"""


def inject_css():
    st.markdown(FORZY_CSS, unsafe_allow_html=True)
