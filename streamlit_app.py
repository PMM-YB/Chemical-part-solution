# -*- coding: utf-8 -*-
"""
화학물질 관리시스템 - Chemical Substance Management System
Star Truck Korea
"""

import streamlit as st
import pandas as pd
import re
import io
from pathlib import Path
from rapidfuzz import fuzz, process

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="화학물질 관리시스템",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif !important; }
.block-container { padding-top: 0rem !important; padding-bottom: 1rem !important; }
header[data-testid="stHeader"] { background: transparent !important; height: 2rem !important; }
.stApp { background-color: #f4f6f9; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #001845 0%, #002060 40%, #003080 100%);
    min-width: 230px !important; max-width: 230px !important;
}
section[data-testid="stSidebar"] * { color: #ffffff !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }
/* Hide sidebar collapse button text */
button[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* Header */
.top-header {
    background: linear-gradient(135deg, #001845 0%, #002060 60%, #003894 100%);
    padding: 1rem 2rem; border-radius: 0 0 12px 12px;
    margin: -1rem -1rem 1.2rem -1rem;
    display: flex; align-items: center; gap: 1rem;
    box-shadow: 0 2px 12px rgba(0,32,96,0.25);
}
.top-header h1 { color: #fff; font-size: 1.4rem; font-weight: 700; margin: 0; }
.top-header .sub { color: #8cb4ff; font-size: 0.8rem; margin: 0; }

/* Stats */
.stats-row { display: flex; gap: 1rem; margin-bottom: 1rem; }
.stat-box {
    flex: 1; background: #fff; border-radius: 10px; padding: 0.8rem 1rem;
    text-align: center; border: 1px solid #dde3ea; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.stat-box .num { font-size: 1.5rem; font-weight: 800; color: #002060; margin: 0; }
.stat-box .lbl { font-size: 0.75rem; color: #5a6a7a; margin: 0; }

/* Page title */
.page-title {
    color: #002060; font-size: 1.15rem; font-weight: 700;
    padding-bottom: 0.5rem; border-bottom: 2px solid #002060; margin-bottom: 1rem;
}

/* Detail rows */
.detail-section-title {
    color: #002060; font-size: 0.9rem; font-weight: 700;
    padding: 0.4rem 0; border-bottom: 1.5px solid #002060; margin-bottom: 0.6rem;
}
.detail-row {
    display: flex; border-bottom: 1px solid #f0f2f5; padding: 0.35rem 0; font-size: 0.85rem;
}
.detail-label { width: 160px; min-width: 160px; color: #002060; font-weight: 600; }
.detail-value { color: #333; flex: 1; }

/* Law badges */
.law-badge {
    display: inline-block; background: #002060; color: #fff;
    padding: 0.2rem 0.6rem; border-radius: 5px; font-size: 0.78rem; font-weight: 600; margin: 0.1rem;
}
.law-badge-red { background: #c0392b; }

/* Reg tags */
.reg-tag {
    display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px;
    font-size: 0.75rem; font-weight: 600; margin: 0.1rem;
}
.reg-tag-red { background: #fde8e8; color: #c0392b; border: 1px solid #e74c3c; }
.reg-tag-orange { background: #fef3e2; color: #d35400; border: 1px solid #f0ad4e; }
.reg-tag-yellow { background: #fef9e7; color: #b7950b; border: 1px solid #f1c40f; }
.reg-tag-green { background: #eafaf1; color: #1e8449; border: 1px solid #27ae60; }
.reg-tag-blue { background: #eaf2f8; color: #1a5276; border: 1px solid #3498db; }
.reg-tag-purple { background: #f4ecf7; color: #6c3483; border: 1px solid #9b59b6; }

/* Import Req */
.import-req-box {
    background: #f8f9fb; border: 1px solid #dde3ea; border-radius: 8px;
    padding: 0.8rem; font-size: 0.82rem; line-height: 1.7;
    white-space: pre-wrap; max-height: 250px; overflow-y: auto; color: #333;
}

/* Table headers */
[data-testid="stDataFrame"] div[role="columnheader"],
[data-testid="stDataFrame"] div[role="columnheader"] *,
[data-testid="stDataFrame"] th {
    background: #002060 !important; color: #ffffff !important;
    font-weight: 700 !important; font-size: 0.8rem !important;
}

/* Substance table */
.substance-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; margin-top: 0.3rem; }
.substance-table th {
    background: #002060; color: #fff; padding: 0.4rem 0.6rem;
    text-align: left; font-weight: 600; font-size: 0.75rem;
}
.substance-table td { padding: 0.35rem 0.6rem; border-bottom: 1px solid #eee; color: #333; }
.substance-table tr:hover td { background: #f0f4ff; }

/* Search box */
[data-testid="stTextInput"] > div > div > input {
    font-size: 0.95rem !important; padding: 0.6rem 1rem !important;
    border-radius: 8px !important; border: 2px solid #002060 !important;
}
[data-testid="stTextInput"] > div > div > input:focus {
    border-color: #0066cc !important; box-shadow: 0 0 0 3px rgba(0,102,204,0.12) !important;
}

/* Buttons */
.stButton > button {
    background: #002060 !important; color: #fff !important;
    border: none !important; border-radius: 6px !important; font-weight: 600 !important;
}
.stButton > button:hover { background: #003894 !important; }
.stDownloadButton > button {
    background: #1a8754 !important; color: #fff !important;
    border: none !important; border-radius: 6px !important; font-weight: 600 !important;
}
.stDownloadButton > button:hover { background: #15713f !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 0; }
.stTabs [data-baseweb="tab"] {
    background: #e8ecf1; border-radius: 8px 8px 0 0; padding: 0.5rem 1.5rem;
    font-weight: 600; font-size: 0.85rem; color: #002060;
}
.stTabs [aria-selected="true"] {
    background: #002060 !important; color: #fff !important;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent
CAS_FILE = "화학물질_20260325(CAS no).xlsx"
HS_FILE = "(수정) [별표2] 수입요령.xlsx"
KREACH_FILE = "K-REACH list in DTK.xlsx"


@st.cache_data(show_spinner="K-REACH 데이터 로딩 중...")
def load_kreach():
    """Load K-REACH main data (Component sheet + HS sheet)."""
    fp = DATA_DIR / KREACH_FILE

    # Component sheet - main matched data
    comp = pd.read_excel(fp, sheet_name="Component", dtype=str)
    comp.columns = [
        "No", "Part number", "Description", "CAS No", "Check DTK CAS",
        "min", "max", "%", "Weight (kg)", "HS Code", "Demand", "_blank",
        "Inside weight", "New material", "PM", "Subjected PM",
        "Toxic", "Restriction", "Prohibition", "Accident",
        "관리대상", "중점관리대상", "기존 살생물질", "col21", "암 돌연변이성",
        "Exemption", "Delivery prohibition", "LoC", "SDS",
        "Application date / No.", "check", "Confirm", "Report",
        "Registration", "Declaration", "Safety&Label", "Pre-registration",
        "remarks", "O or X", "Remark", "Contact point",
    ]
    # Forward-fill Part number and Description for grouped rows
    comp["Part number"] = comp["Part number"].fillna(method="ffill")
    comp["Description"] = comp["Description"].fillna(method="ffill")
    comp = comp.fillna("")

    # HS sheet - law mapping
    hs = pd.read_excel(fp, sheet_name="HS", dtype=str)
    hs.columns = ["HS Code", "관련법령", "관련항목"]
    hs = hs.fillna("")

    # Part list sheet
    parts = pd.read_excel(fp, sheet_name="Part list", dtype=str)
    parts = parts.fillna("")

    return comp, hs, parts


@st.cache_data(show_spinner="수입요령 데이터 로딩 중...")
def load_hs_import():
    """Load HS import requirements."""
    fp = DATA_DIR / HS_FILE
    df = pd.read_excel(fp, dtype=str)
    col_map = {
        df.columns[5]: "세번",
        df.columns[6]: "품명",
        df.columns[7]: "수입요령",
        df.columns[8]: "관련법령_수입",
    }
    df = df.rename(columns=col_map)
    df = df.fillna("")
    return df[["세번", "품명", "수입요령", "관련법령_수입"]]


@st.cache_data(show_spinner="CAS 데이터 로딩 중...")
def load_cas_ref():
    """Load full CAS reference."""
    fp = DATA_DIR / CAS_FILE
    df = pd.read_excel(fp, dtype=str)
    df.columns = [
        "NO", "CAS번호", "영문명", "국문명", "기존",
        "급성/만성/생태", "사고대비", "제한/금지/허가",
        "중점", "잔류", "유해특성분류",
        "등록대상기존화학물질", "기존물질여부",
    ]
    df = df.fillna("")
    return df


@st.cache_data(show_spinner="통합 데이터베이스 구축 중...")
def build_master_db():
    """Build the master database merging K-REACH + HS imports + CAS ref."""
    comp, hs_law, parts = load_kreach()
    hs_import = load_hs_import()
    cas_ref = load_cas_ref()

    # Build HS law lookup
    hs_law_dict = {}
    hs_item_dict = {}
    for _, r in hs_law.iterrows():
        code = r["HS Code"].strip()
        if code:
            hs_law_dict[code] = r["관련법령"]
            hs_item_dict[code] = r["관련항목"]

    # Build HS import lookup (세번 -> row)
    hs_import_dict = {}
    for _, r in hs_import.iterrows():
        code = r["세번"].strip()
        if code:
            hs_import_dict[code] = r

    # Build CAS ref lookup
    cas_dict = {}
    for _, r in cas_ref.iterrows():
        c = r["CAS번호"].strip()
        if c:
            cas_dict[c] = r

    # Build master records from Component sheet
    records = []
    for _, row in comp.iterrows():
        cas = row["CAS No"].strip()
        hs_code = row["HS Code"].strip()
        hs_4 = hs_code[:4] if len(hs_code) >= 4 else hs_code

        # Get law from HS sheet
        law = hs_law_dict.get(hs_4, "")
        hs_item = hs_item_dict.get(hs_4, "")

        # Get import requirements
        import_info = hs_import_dict.get(hs_code, None)
        품명 = import_info["품명"] if import_info is not None else ""
        수입요령 = import_info["수입요령"] if import_info is not None else ""
        관련법령_수입 = import_info["관련법령_수입"] if import_info is not None else ""

        # Get CAS reference info
        cas_info = cas_dict.get(cas, None)
        영문명 = cas_info["영문명"] if cas_info is not None else ""
        국문명 = cas_info["국문명"] if cas_info is not None else ""
        급성만성 = cas_info["급성/만성/생태"] if cas_info is not None else ""
        기존물질 = cas_info["기존물질여부"] if cas_info is not None else ""

        # Combine laws
        all_laws = set()
        if law:
            for l in re.split(r"[/,]", law):
                l = l.strip()
                if l:
                    all_laws.add(l)
        if 관련법령_수입:
            for l in re.split(r"[/,\n]", 관련법령_수입):
                l = l.strip()
                if l:
                    all_laws.add(l)

        records.append({
            "No": row["No"],
            "Part number": row["Part number"],
            "Description": row["Description"],
            "CAS No": cas,
            "CAS 영문명": 영문명,
            "CAS 국문명": 국문명,
            "Check DTK CAS": row["Check DTK CAS"],
            "min%": row["min"],
            "max%": row["max"],
            "함량%": row["%"],
            "Weight (kg)": row["Weight (kg)"],
            "HS Code": hs_code,
            "HS 4자리": hs_4,
            "품명": 품명,
            "관련항목": hs_item,
            "관련법령": " / ".join(sorted(all_laws)) if all_laws else "",
            "수입요령": 수입요령,
            "PM": row["PM"],
            "Toxic": row["Toxic"],
            "Restriction": row["Restriction"],
            "Prohibition": row["Prohibition"],
            "Accident": row["Accident"],
            "관리대상": row["관리대상"],
            "중점관리대상": row["중점관리대상"],
            "기존 살생물질": row["기존 살생물질"],
            "암 돌연변이성": row["암 돌연변이성"],
            "Exemption": row["Exemption"],
            "급성/만성/생태": 급성만성,
            "기존물질여부": 기존물질,
            "SDS": row["SDS"],
            "Application date": row["Application date / No."],
            "Confirm": row["Confirm"],
            "Report": row["Report"],
            "Registration": row["Registration"],
            "Declaration": row["Declaration"],
            "Safety&Label": row["Safety&Label"],
        })

    master = pd.DataFrame(records)
    master = master.fillna("")
    return master


def search_df(df, query, columns):
    """Search across given columns."""
    if not query or not query.strip():
        return df
    q = query.strip().lower()
    terms = q.split()
    combined = df[columns].apply(lambda row: " ".join(str(v).lower() for v in row), axis=1)
    mask = pd.Series(True, index=df.index)
    for t in terms:
        mask &= combined.str.contains(re.escape(t), case=False, na=False)
    return df[mask]


def to_excel_download(df, filename="data.xlsx"):
    """Convert df to Excel bytes for download."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    return buf.getvalue()


def render_detail(row):
    """Render detail card for a single row."""
    cas = row.get("CAS No", "")
    eng = row.get("CAS 영문명", "")
    kor = row.get("CAS 국문명", "")
    hs = row.get("HS Code", "")
    part = row.get("Part number", "")
    desc = row.get("Description", "")
    product = row.get("품명", "")
    law = row.get("관련법령", "")
    import_req = row.get("수입요령", "")

    title = f"[{cas}] {eng}" if cas else (desc or product or "항목")
    if kor:
        title += f" ({kor})"

    with st.expander(title, expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="detail-row"><div class="detail-label">Part Number</div><div class="detail-value">{part or '-'}</div></div>
            <div class="detail-row"><div class="detail-label">Description</div><div class="detail-value">{desc or '-'}</div></div>
            <div class="detail-row"><div class="detail-label">CAS No.</div><div class="detail-value">{cas or '-'}</div></div>
            <div class="detail-row"><div class="detail-label">영문명</div><div class="detail-value">{eng or '-'}</div></div>
            <div class="detail-row"><div class="detail-label">국문명</div><div class="detail-value">{kor or '-'}</div></div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="detail-row"><div class="detail-label">HS Code</div><div class="detail-value">{hs or '-'}</div></div>
            <div class="detail-row"><div class="detail-label">품명</div><div class="detail-value">{product or '-'}</div></div>
            <div class="detail-row"><div class="detail-label">함량 (min-max)</div><div class="detail-value">{row.get('min%','')} ~ {row.get('max%','')} ({row.get('함량%','')}%)</div></div>
            <div class="detail-row"><div class="detail-label">Weight</div><div class="detail-value">{row.get('Weight (kg)','')} kg</div></div>
            <div class="detail-row"><div class="detail-label">PM</div><div class="detail-value">{row.get('PM','') or '-'}</div></div>
            """, unsafe_allow_html=True)

        # Laws
        if law:
            st.markdown('<div class="detail-section-title">관련법령</div>', unsafe_allow_html=True)
            badges = " ".join(f'<span class="law-badge">{l.strip()}</span>' for l in re.split(r"[/]", law) if l.strip())
            st.markdown(badges, unsafe_allow_html=True)

        # Regulation info
        reg_items = [
            ("Toxic", "reg-tag-red"), ("Restriction", "reg-tag-red"),
            ("Prohibition", "reg-tag-red"), ("Accident", "reg-tag-orange"),
            ("관리대상", "reg-tag-purple"), ("중점관리대상", "reg-tag-purple"),
            ("기존 살생물질", "reg-tag-yellow"), ("암 돌연변이성", "reg-tag-red"),
            ("Exemption", "reg-tag-green"), ("급성/만성/생태", "reg-tag-orange"),
        ]
        tags = []
        for field, cls in reg_items:
            val = str(row.get(field, "")).strip()
            if val:
                tags.append(f'<span class="reg-tag {cls}">{field}: {val}</span>')
        if tags:
            st.markdown('<div class="detail-section-title">규제물질 정보</div>', unsafe_allow_html=True)
            st.markdown(" ".join(tags), unsafe_allow_html=True)

        # Import requirements
        if import_req:
            st.markdown('<div class="detail-section-title">수입요령</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="import-req-box">{import_req}</div>', unsafe_allow_html=True)

        # Status
        status_items = [
            ("SDS", row.get("SDS", "")), ("Confirm", row.get("Confirm", "")),
            ("Report", row.get("Report", "")), ("Registration", row.get("Registration", "")),
            ("Declaration", row.get("Declaration", "")), ("Safety&Label", row.get("Safety&Label", "")),
        ]
        status_tags = [f'<span class="reg-tag reg-tag-green">{k}: {v}</span>' for k, v in status_items if v.strip()]
        if status_tags:
            st.markdown('<div class="detail-section-title">신고/등록 현황</div>', unsafe_allow_html=True)
            st.markdown(" ".join(status_tags), unsafe_allow_html=True)


def show_results(results, tab_key):
    """Show results table + detail + download."""
    if results.empty:
        st.warning("검색 결과가 없습니다.")
        return

    st.markdown(f'총 **{len(results):,}** 건', unsafe_allow_html=True)

    # Download button
    dl_cols = [
        "No", "Part number", "Description", "CAS No", "CAS 영문명", "CAS 국문명",
        "Check DTK CAS", "min%", "max%", "함량%", "Weight (kg)",
        "HS Code", "품명", "관련항목", "관련법령", "PM",
        "Toxic", "Restriction", "Prohibition", "Accident",
        "관리대상", "중점관리대상", "기존 살생물질", "암 돌연변이성", "Exemption",
        "SDS", "Application date", "Confirm", "Report",
        "Registration", "Declaration", "Safety&Label",
    ]
    available = [c for c in dl_cols if c in results.columns]
    excel_data = to_excel_download(results[available], f"chemical_search_{tab_key}.xlsx")

    c1, c2 = st.columns([4, 1])
    with c2:
        st.download_button(
            "엑셀 다운로드",
            data=excel_data,
            file_name=f"chemical_search_{tab_key}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=f"dl_{tab_key}",
            use_container_width=True,
        )

    # Summary table
    table_cols = ["CAS No", "CAS 영문명", "CAS 국문명", "HS Code", "품명", "Description", "관련법령"]
    available_table = [c for c in table_cols if c in results.columns]

    MAX = 500
    show = results.head(MAX)
    if len(results) > MAX:
        st.info(f"상위 {MAX}건만 표시합니다.")

    st.dataframe(
        show[available_table].reset_index(drop=True),
        use_container_width=True,
        height=min(450, 35 * len(show) + 38),
    )

    # Detail cards
    st.markdown("---")
    st.markdown('<div class="page-title">상세 정보</div>', unsafe_allow_html=True)

    PER_PAGE = 15
    total_pages = max(1, (len(show) + PER_PAGE - 1) // PER_PAGE)
    page = 1
    if total_pages > 1:
        page = st.number_input("페이지", 1, total_pages, 1, key=f"page_{tab_key}")
        st.caption(f"페이지 {page}/{total_pages}")

    start = (page - 1) * PER_PAGE
    end = min(start + PER_PAGE, len(show))
    for _, row in show.iloc[start:end].iterrows():
        render_detail(row)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem 0;">
        <div style="font-size:1.8rem;">⚗️</div>
        <div style="font-size:1rem; font-weight:700;">화학물질 관리시스템</div>
        <div style="font-size:0.65rem; color:#8cb4ff; margin-top:0.2rem;">Chemical Substance Management</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Star Truck Korea")
    st.caption("Daimler Truck Korea")


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="top-header">
    <span style="font-size:1.8rem;">&#9883;</span>
    <div>
        <h1>화학물질 관리시스템</h1>
        <p class="sub">Chemical Substance Management System — Star Truck Korea</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
try:
    master = build_master_db()
except Exception as e:
    st.error(f"데이터 로딩 오류: {e}")
    st.stop()

# Stats
has_cas = master[master["CAS No"] != ""]
has_hs = master[master["HS Code"] != ""]
has_law = master[master["관련법령"] != ""]

st.markdown(f"""
<div class="stats-row">
    <div class="stat-box"><p class="num">{len(master):,}</p><p class="lbl">전체 성분 레코드</p></div>
    <div class="stat-box"><p class="num">{has_cas["CAS No"].nunique():,}</p><p class="lbl">CAS 물질</p></div>
    <div class="stat-box"><p class="num">{has_hs["HS Code"].nunique():,}</p><p class="lbl">HS 코드</p></div>
    <div class="stat-box"><p class="num">{len(has_law):,}</p><p class="lbl">법령 매칭</p></div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 4 Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 HS Code 검색",
    "🔬 CAS Number 검색",
    "⚖️ 법률 검색",
    "🔍 품목명 검색 (영문/한글)",
])


# ── Tab 1: HS Code 검색 ──
with tab1:
    st.markdown('<div class="page-title">HS Code 검색</div>', unsafe_allow_html=True)
    q1 = st.text_input("HS Code를 입력하세요", placeholder="예: 2710, 2909, 3208199000", key="q_hs")
    if q1:
        results = search_df(master, q1, ["HS Code", "HS 4자리"])
        show_results(results, "hs")
    else:
        st.info("HS Code를 입력하면 해당 코드의 모든 화학물질, 법령, 수입요령이 표시됩니다.")


# ── Tab 2: CAS Number 검색 ──
with tab2:
    st.markdown('<div class="page-title">CAS Number 검색</div>', unsafe_allow_html=True)
    q2 = st.text_input("CAS Number를 입력하세요", placeholder="예: 64-19-7, 67124-09-8", key="q_cas")
    if q2:
        results = search_df(master, q2, ["CAS No"])
        show_results(results, "cas")
    else:
        st.info("CAS Number를 입력하면 해당 물질의 모든 정보가 표시됩니다.")


# ── Tab 3: 법률 검색 ──
with tab3:
    st.markdown('<div class="page-title">법률 검색</div>', unsafe_allow_html=True)

    # Get unique laws for dropdown
    all_laws_set = set()
    for law_str in master["관련법령"].unique():
        if law_str:
            for l in re.split(r"[/]", law_str):
                l = l.strip()
                if l:
                    all_laws_set.add(l)
    sorted_laws = sorted(all_laws_set)

    c1, c2 = st.columns([2, 3])
    with c1:
        selected_law = st.selectbox("법령 선택", ["전체"] + sorted_laws, key="sel_law")
    with c2:
        q3 = st.text_input("또는 법률명 직접 입력", placeholder="예: 화평법, 산업안전", key="q_law")

    if q3:
        results = search_df(master, q3, ["관련법령"])
        show_results(results, "law")
    elif selected_law != "전체":
        results = master[master["관련법령"].str.contains(re.escape(selected_law), case=False, na=False)]
        show_results(results, "law")
    else:
        # Show law summary
        law_counts = []
        for l in sorted_laws:
            cnt = master["관련법령"].str.contains(re.escape(l), case=False, na=False).sum()
            law_counts.append({"법령명": l, "관련 성분 수": cnt})
        law_summary = pd.DataFrame(law_counts).sort_values("관련 성분 수", ascending=False)
        st.dataframe(law_summary.reset_index(drop=True), use_container_width=True, height=400)


# ── Tab 4: 품목명 검색 (영문/한글) ──
with tab4:
    st.markdown('<div class="page-title">품목명 검색 (영문/한글)</div>', unsafe_allow_html=True)
    q4 = st.text_input("품목명을 입력하세요", placeholder="예: GEAR OIL, 페인트, Acetic acid, 염소", key="q_name")
    if q4:
        results = search_df(master, q4, ["Description", "CAS 영문명", "CAS 국문명", "품명", "관련항목"])
        show_results(results, "name")
    else:
        st.info("영문 또는 한글 품목명을 입력하면 관련 화학물질 정보가 표시됩니다.")
