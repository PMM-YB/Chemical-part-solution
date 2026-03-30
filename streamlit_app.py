# -*- coding: utf-8 -*-
"""
화학물질 관리시스템 - Chemical Substance Management System
Star Truck Korea
"""

import streamlit as st
import pandas as pd
import re
from pathlib import Path
from rapidfuzz import fuzz, process

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="화학물질 관리시스템",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS - PPT 디자인 기반 (#002060 네이비, 맑은 고딕 스타일)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;800&display=swap');

/* Global */
* { font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif !important; }
.block-container { padding-top: 0rem !important; padding-bottom: 1rem !important; }
header[data-testid="stHeader"] { background: transparent !important; height: 2rem !important; }

/* Page background */
.stApp { background-color: #f4f6f9; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #001845 0%, #002060 40%, #003080 100%);
    min-width: 220px !important;
    max-width: 220px !important;
}
section[data-testid="stSidebar"] * { color: #ffffff !important; }
section[data-testid="stSidebar"] .stRadio label {
    padding: 0.4rem 0.8rem !important;
    border-radius: 6px !important;
    transition: background 0.2s;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.1) !important;
}
section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 0.9rem !important;
}
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }

/* ── Top Header Bar ── */
.top-header {
    background: linear-gradient(135deg, #001845 0%, #002060 60%, #003894 100%);
    padding: 1rem 2rem;
    border-radius: 0 0 12px 12px;
    margin: -1rem -1rem 1.2rem -1rem;
    display: flex; align-items: center; gap: 1rem;
    box-shadow: 0 2px 12px rgba(0,32,96,0.25);
}
.top-header h1 { color: #fff; font-size: 1.4rem; font-weight: 700; margin: 0; letter-spacing: 0.3px; }
.top-header .sub { color: #8cb4ff; font-size: 0.8rem; margin: 0; }
.top-header .logo { font-size: 1.8rem; }

/* ── Filter Section ── */
.filter-section {
    background: #fff;
    border: 1px solid #dde3ea;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.filter-label {
    color: #002060;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 0.2rem;
}

/* ── Stats Row ── */
.stats-row { display: flex; gap: 1rem; margin-bottom: 1rem; }
.stat-box {
    flex: 1;
    background: #fff;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    text-align: center;
    border: 1px solid #dde3ea;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.stat-box .num { font-size: 1.5rem; font-weight: 800; color: #002060; margin: 0; }
.stat-box .lbl { font-size: 0.75rem; color: #5a6a7a; margin: 0; }

/* ── Count badge ── */
.count-badge {
    display: inline-block;
    color: #002060;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.count-badge b { font-size: 1rem; }

/* ── Page Title ── */
.page-title {
    color: #002060;
    font-size: 1.15rem;
    font-weight: 700;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #002060;
    margin-bottom: 1rem;
}

/* ── Detail Card ── */
.detail-card {
    background: #fff;
    border: 1px solid #dde3ea;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.detail-section-title {
    color: #002060;
    font-size: 0.9rem;
    font-weight: 700;
    padding: 0.4rem 0;
    border-bottom: 1.5px solid #002060;
    margin-bottom: 0.6rem;
}
.detail-row {
    display: flex;
    border-bottom: 1px solid #f0f2f5;
    padding: 0.35rem 0;
    font-size: 0.85rem;
}
.detail-label {
    width: 140px;
    min-width: 140px;
    color: #002060;
    font-weight: 600;
}
.detail-value { color: #333; flex: 1; }

/* ── Law / Regulation Tags ── */
.law-badge {
    display: inline-block;
    background: #002060;
    color: #fff;
    padding: 0.2rem 0.6rem;
    border-radius: 5px;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 0.1rem;
}
.law-badge-red { background: #c0392b; }
.law-badge-orange { background: #e67e22; }

.reg-tag {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    margin: 0.1rem;
}
.reg-tag-red { background: #fde8e8; color: #c0392b; border: 1px solid #e74c3c; }
.reg-tag-orange { background: #fef3e2; color: #d35400; border: 1px solid #f0ad4e; }
.reg-tag-yellow { background: #fef9e7; color: #b7950b; border: 1px solid #f1c40f; }
.reg-tag-green { background: #eafaf1; color: #1e8449; border: 1px solid #27ae60; }
.reg-tag-blue { background: #eaf2f8; color: #1a5276; border: 1px solid #3498db; }
.reg-tag-purple { background: #f4ecf7; color: #6c3483; border: 1px solid #9b59b6; }

/* ── Import Req Box ── */
.import-req-box {
    background: #f8f9fb;
    border: 1px solid #dde3ea;
    border-radius: 8px;
    padding: 0.8rem;
    font-size: 0.82rem;
    line-height: 1.7;
    white-space: pre-wrap;
    max-height: 250px;
    overflow-y: auto;
    color: #333;
}

/* ── Table Header ── */
[data-testid="stDataFrame"] div[role="columnheader"],
[data-testid="stDataFrame"] div[role="columnheader"] *,
[data-testid="stDataFrame"] th {
    background: #002060 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
}

/* ── Substance Tables ── */
.substance-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8rem;
    margin-top: 0.3rem;
}
.substance-table th {
    background: #002060;
    color: #fff;
    padding: 0.4rem 0.6rem;
    text-align: left;
    font-weight: 600;
    font-size: 0.75rem;
}
.substance-table td {
    padding: 0.35rem 0.6rem;
    border-bottom: 1px solid #eee;
    color: #333;
}
.substance-table tr:hover td { background: #f0f4ff; }

/* ── Search Box ── */
[data-testid="stTextInput"] > div > div > input {
    font-size: 0.95rem !important;
    padding: 0.6rem 1rem !important;
    border-radius: 8px !important;
    border: 2px solid #002060 !important;
}
[data-testid="stTextInput"] > div > div > input:focus {
    border-color: #0066cc !important;
    box-shadow: 0 0 0 3px rgba(0,102,204,0.12) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #002060 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}
.stButton > button:hover {
    background: #003894 !important;
}

/* ── Sidebar menu selected ── */
section[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] {
    background: rgba(255,255,255,0.15) !important;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Data loading (unchanged logic)
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent
CAS_FILE = "화학물질_20260325(CAS no).xlsx"
HS_FILE = "(수정) [별표2] 수입요령.xlsx"


@st.cache_data(show_spinner="데이터 로딩 중...")
def load_cas_data():
    fp = DATA_DIR / CAS_FILE
    df = pd.read_excel(fp, dtype=str)
    df.columns = [
        "NO", "CAS번호", "영문명", "국문명", "기존",
        "급성/만성/생태", "사고대비", "제한/금지/허가",
        "중점", "잔류", "유해특성분류 및 혼합물 함량기준(%)",
        "등록대상기존화학물질", "기존물질여부",
    ]
    df["CAS번호"] = df["CAS번호"].fillna("").str.strip()
    df["영문명"] = df["영문명"].fillna("").str.strip()
    df["국문명"] = df["국문명"].fillna("").str.strip()
    return df


@st.cache_data(show_spinner="수입요령 데이터 처리 중...")
def load_hs_data():
    fp = DATA_DIR / HS_FILE
    df = pd.read_excel(fp, dtype=str)
    col_map = {
        df.columns[0]: "구분",
        df.columns[5]: "세번",
        df.columns[6]: "품명",
        df.columns[7]: "수입요령",
        df.columns[8]: "관련법령",
    }
    df = df.rename(columns=col_map)
    df["세번"] = df["세번"].fillna("").str.strip()
    df["품명"] = df["품명"].fillna("").str.strip()
    df["수입요령"] = df["수입요령"].fillna("").str.strip()
    df["관련법령"] = df["관련법령"].fillna("").str.strip()
    return df[["구분", "세번", "품명", "수입요령", "관련법령"]]


@st.cache_data(show_spinner="CAS 번호 매칭 및 데이터베이스 구축 중...")
def build_unified_db():
    cas_df = load_cas_data()
    hs_df = load_hs_data()

    cas_lookup = {}
    for idx, row in cas_df.iterrows():
        cas_num = row["CAS번호"]
        if cas_num:
            for cn in re.split(r"[,;/]\s*", cas_num):
                cn = cn.strip()
                if cn:
                    cas_lookup[cn] = idx

    eng_lookup = {}
    for idx, row in cas_df.iterrows():
        eng = row["영문명"].lower().strip()
        if eng:
            eng_lookup[eng] = idx

    bracket_pattern = re.compile(r"\[([^\]]+)\]")
    cas_num_pattern = re.compile(r"\b(\d{2,7}-\d{2}-\d)\b")
    records = []

    for _, hs_row in hs_df.iterrows():
        text = hs_row["수입요령"]
        if not text:
            continue
        brackets = bracket_pattern.findall(text)
        extracted_items = []
        for bracket_text in brackets:
            cas_matches = cas_num_pattern.findall(bracket_text)
            if cas_matches:
                parts = re.split(r";\s*", bracket_text)
                eng_name = ""
                cas_nums = []
                for part in parts:
                    part = part.strip()
                    if cas_num_pattern.match(part):
                        cas_nums.append(part)
                    elif not eng_name:
                        eng_name = part
                for cn in cas_nums:
                    extracted_items.append((eng_name, cn))

        if not extracted_items:
            records.append({
                "세번": hs_row["세번"], "품명": hs_row["품명"],
                "수입요령": text, "관련법령": hs_row["관련법령"],
                "CAS번호": "", "영문명": "", "국문명": "",
                "급성/만성/생태": "", "사고대비": "", "제한/금지/허가": "",
                "중점": "", "잔류": "", "유해특성분류": "", "기존물질여부": "",
                "_matched": False,
            })
            continue

        for eng_name, cas_num in extracted_items:
            cas_info = {}
            matched = False
            if cas_num in cas_lookup:
                cr = cas_df.iloc[cas_lookup[cas_num]]
                cas_info = {
                    "CAS번호": cas_num,
                    "영문명": cr["영문명"] if cr["영문명"] else eng_name,
                    "국문명": cr["국문명"],
                    "급성/만성/생태": cr["급성/만성/생태"],
                    "사고대비": cr["사고대비"],
                    "제한/금지/허가": cr["제한/금지/허가"],
                    "중점": cr["중점"], "잔류": cr["잔류"],
                    "유해특성분류": cr["유해특성분류 및 혼합물 함량기준(%)"],
                    "기존물질여부": cr["기존물질여부"],
                }
                matched = True
            else:
                eng_lower = eng_name.lower().strip()
                if eng_lower and eng_lower in eng_lookup:
                    cr = cas_df.iloc[eng_lookup[eng_lower]]
                    cas_info = {
                        "CAS번호": cas_num, "영문명": cr["영문명"], "국문명": cr["국문명"],
                        "급성/만성/생태": cr["급성/만성/생태"], "사고대비": cr["사고대비"],
                        "제한/금지/허가": cr["제한/금지/허가"], "중점": cr["중점"],
                        "잔류": cr["잔류"],
                        "유해특성분류": cr["유해특성분류 및 혼합물 함량기준(%)"],
                        "기존물질여부": cr["기존물질여부"],
                    }
                    matched = True
            if not matched:
                cas_info = {
                    "CAS번호": cas_num, "영문명": eng_name, "국문명": "",
                    "급성/만성/생태": "", "사고대비": "", "제한/금지/허가": "",
                    "중점": "", "잔류": "", "유해특성분류": "", "기존물질여부": "",
                }
            records.append({
                "세번": hs_row["세번"], "품명": hs_row["품명"],
                "수입요령": text, "관련법령": hs_row["관련법령"],
                **cas_info, "_matched": matched,
            })

    result = pd.DataFrame(records)

    # Fuzzy matching for CAS-only entries
    hs_eng_names = {}
    for _, hs_row in hs_df.iterrows():
        text = hs_row["수입요령"]
        if not text:
            continue
        for bracket_text in bracket_pattern.findall(text):
            parts = re.split(r";\s*", bracket_text)
            for part in parts:
                part = part.strip()
                if part and not cas_num_pattern.match(part) and re.search(r"[a-zA-Z]", part):
                    hs_eng_names[part.lower()] = hs_row

    hs_eng_keys = list(hs_eng_names.keys())
    cas_only_records = []
    matched_cas_set = set(result["CAS번호"].dropna().unique())

    for _, cas_row in cas_df.iterrows():
        cas_num = cas_row["CAS번호"]
        if cas_num and cas_num not in matched_cas_set:
            eng_name = cas_row["영문명"].strip()
            hs_info = {"세번": "", "품명": "", "수입요령": "", "관련법령": ""}
            is_matched = False

            if eng_name and hs_eng_keys:
                eng_lower = eng_name.lower()
                for hs_eng, hs_row in hs_eng_names.items():
                    if eng_lower == hs_eng or eng_lower in hs_eng or hs_eng in eng_lower:
                        hs_info = {"세번": hs_row["세번"], "품명": hs_row["품명"],
                                   "수입요령": hs_row["수입요령"], "관련법령": hs_row["관련법령"]}
                        is_matched = True
                        break
                if not is_matched:
                    match = process.extractOne(eng_lower, hs_eng_keys,
                                               scorer=fuzz.token_sort_ratio, score_cutoff=85)
                    if match:
                        hs_row = hs_eng_names[match[0]]
                        hs_info = {"세번": hs_row["세번"], "품명": hs_row["품명"],
                                   "수입요령": hs_row["수입요령"], "관련법령": hs_row["관련법령"]}
                        is_matched = True

            cas_only_records.append({
                **hs_info,
                "CAS번호": cas_num, "영문명": cas_row["영문명"], "국문명": cas_row["국문명"],
                "급성/만성/생태": cas_row["급성/만성/생태"], "사고대비": cas_row["사고대비"],
                "제한/금지/허가": cas_row["제한/금지/허가"], "중점": cas_row["중점"],
                "잔류": cas_row["잔류"],
                "유해특성분류": cas_row["유해특성분류 및 혼합물 함량기준(%)"],
                "기존물질여부": cas_row["기존물질여부"], "_matched": is_matched,
            })

    cas_only_df = pd.DataFrame(cas_only_records)
    result = pd.concat([result, cas_only_df], ignore_index=True)
    result = result.fillna("")
    return result


def search_database(df, query):
    if not query or not query.strip():
        return pd.DataFrame()
    query = query.strip().lower()
    terms = query.split()
    search_cols = ["품명", "영문명", "국문명", "CAS번호", "세번", "관련법령"]
    combined = df[search_cols].apply(lambda row: " ".join(str(v).lower() for v in row), axis=1)
    mask = pd.Series([True] * len(df), index=df.index)
    for term in terms:
        mask &= combined.str.contains(re.escape(term), case=False, na=False)
    return df[mask]


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem 0;">
        <div style="font-size:1.8rem;">⚗️</div>
        <div style="font-size:1rem; font-weight:700; letter-spacing:0.5px;">화학물질 관리시스템</div>
        <div style="font-size:0.65rem; color:#8cb4ff; margin-top:0.2rem;">Chemical Substance Management</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    menu = st.radio(
        "메뉴",
        ["제품목록", "법령관리", "화학물질 조회"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("Star Truck Korea")


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="top-header">
    <span class="logo">&#9883;</span>
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
    db = build_unified_db()
except Exception as e:
    st.error(f"데이터 로딩 오류: {e}")
    st.stop()

total_chemicals = db[db["CAS번호"] != ""].shape[0]
total_hs = db[db["세번"] != ""]["세번"].nunique()
matched_count = db[db["_matched"]].shape[0]


# ===========================================================================
# PAGE: 제품목록
# ===========================================================================
if menu == "제품목록":
    st.markdown('<div class="page-title">제품목록</div>', unsafe_allow_html=True)

    # Stats
    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-box"><p class="num">{len(db):,}</p><p class="lbl">전체 레코드</p></div>
        <div class="stat-box"><p class="num">{total_chemicals:,}</p><p class="lbl">화학물질 (CAS)</p></div>
        <div class="stat-box"><p class="num">{total_hs:,}</p><p class="lbl">HS 코드</p></div>
        <div class="stat-box"><p class="num">{matched_count:,}</p><p class="lbl">CAS-HS 매칭</p></div>
    </div>
    """, unsafe_allow_html=True)

    # Filter section
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    fc1, fc2, fc3, fc4 = st.columns([3, 2, 2, 1])
    with fc1:
        query = st.text_input("검색", placeholder="제품명 / 영문명 / CAS No. / HSK No.", label_visibility="collapsed")
    with fc2:
        scope = st.selectbox("범위", ["전체", "수입요령 있는 항목", "CAS 화학물질"], label_visibility="collapsed")
    with fc3:
        law_filter = st.selectbox("관련법령", ["전체"] + sorted(db[db["관련법령"] != ""]["관련법령"].unique().tolist()), label_visibility="collapsed")
    with fc4:
        st.button("검색", use_container_width=True, key="search_btn")
    st.markdown('</div>', unsafe_allow_html=True)

    # Apply filters
    filtered = db.copy()
    if scope == "수입요령 있는 항목":
        filtered = filtered[filtered["수입요령"] != ""]
    elif scope == "CAS 화학물질":
        filtered = filtered[filtered["CAS번호"] != ""]
    if law_filter != "전체":
        filtered = filtered[filtered["관련법령"].str.contains(re.escape(law_filter), case=False, na=False)]

    if query:
        filtered = search_database(filtered, query)

    if query or law_filter != "전체":
        st.markdown(f'<div class="count-badge">총 <b>{len(filtered):,}</b> 건</div>', unsafe_allow_html=True)

        if filtered.empty:
            st.warning("검색 결과가 없습니다.")
        else:
            MAX_DISPLAY = 300
            show = filtered.head(MAX_DISPLAY) if len(filtered) > MAX_DISPLAY else filtered
            if len(filtered) > MAX_DISPLAY:
                st.info(f"상위 {MAX_DISPLAY}건만 표시합니다.")

            display_cols = ["CAS번호", "영문명", "국문명", "세번", "품명", "관련법령"]
            st.dataframe(
                show[display_cols].reset_index(drop=True),
                use_container_width=True,
                height=min(450, 35 * len(show) + 38),
            )

            # Detail view on select
            st.markdown("---")
            st.markdown('<div class="page-title">제품상세</div>', unsafe_allow_html=True)

            CARDS_PER_PAGE = 15
            total_pages = max(1, (len(show) + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE)
            page = 1
            if total_pages > 1:
                page = st.number_input("페이지", 1, total_pages, 1, key="prod_page")
                st.caption(f"페이지 {page}/{total_pages}")

            start = (page - 1) * CARDS_PER_PAGE
            end = min(start + CARDS_PER_PAGE, len(show))

            for _, row in show.iloc[start:end].iterrows():
                cas = row.get("CAS번호", "")
                eng = row.get("영문명", "")
                kor = row.get("국문명", "")
                hs = row.get("세번", "")
                product = row.get("품명", "")
                law = row.get("관련법령", "")
                import_req = row.get("수입요령", "")

                title_parts = []
                if cas: title_parts.append(f"[{cas}]")
                if eng: title_parts.append(eng)
                if kor: title_parts.append(f"({kor})")
                if not title_parts and product: title_parts.append(product)
                title = " ".join(title_parts) or "항목"

                with st.expander(title, expanded=(len(show.iloc[start:end]) <= 3)):
                    # ── 기본정보 ──
                    st.markdown('<div class="detail-section-title">기본정보</div>', unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"""
                        <div class="detail-row"><div class="detail-label">제품명</div><div class="detail-value">{product or '-'}</div></div>
                        <div class="detail-row"><div class="detail-label">영문 제품명</div><div class="detail-value">{eng or '-'}</div></div>
                        <div class="detail-row"><div class="detail-label">국문명</div><div class="detail-value">{kor or '-'}</div></div>
                        """, unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"""
                        <div class="detail-row"><div class="detail-label">CAS No.</div><div class="detail-value">{cas or '-'}</div></div>
                        <div class="detail-row"><div class="detail-label">HSK No.</div><div class="detail-value">{hs or '-'}</div></div>
                        <div class="detail-row"><div class="detail-label">기존물질여부</div><div class="detail-value">{row.get('기존물질여부', '') or '-'}</div></div>
                        """, unsafe_allow_html=True)

                    # ── 관련법령 ──
                    if law:
                        st.markdown('<div class="detail-section-title">관련법령</div>', unsafe_allow_html=True)
                        laws = re.split(r"[,\n]", str(law))
                        badges = " ".join(f'<span class="law-badge">{l.strip()}</span>' for l in laws if l.strip())
                        st.markdown(badges, unsafe_allow_html=True)

                    # ── 규제물질 정보 ──
                    has_reg = any(str(row.get(k, "")).strip() for k in
                                 ["급성/만성/생태", "사고대비", "제한/금지/허가", "중점", "잔류", "유해특성분류"])
                    if has_reg:
                        st.markdown('<div class="detail-section-title">규제물질 정보</div>', unsafe_allow_html=True)
                        rows_html = ""
                        reg_items = [
                            ("급성/만성/생태", "reg-tag-red"),
                            ("사고대비", "reg-tag-orange"),
                            ("제한/금지/허가", "reg-tag-red"),
                            ("중점", "reg-tag-purple"),
                            ("잔류", "reg-tag-yellow"),
                        ]
                        for field, cls in reg_items:
                            val = str(row.get(field, "")).strip()
                            if val:
                                rows_html += f'<tr><td><span class="reg-tag {cls}">{field}</span></td><td>{val}</td></tr>'
                        hazard = str(row.get("유해특성분류", "")).strip()
                        if hazard:
                            rows_html += f'<tr><td><span class="reg-tag reg-tag-blue">유해특성분류</span></td><td>{hazard}</td></tr>'
                        if rows_html:
                            st.markdown(f'<table class="substance-table"><thead><tr><th>구분</th><th>내용</th></tr></thead><tbody>{rows_html}</tbody></table>', unsafe_allow_html=True)

                    # ── 수입요령 ──
                    if import_req:
                        st.markdown('<div class="detail-section-title">수입요령</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="import-req-box">{import_req}</div>', unsafe_allow_html=True)
    else:
        # No search yet - show guide
        st.markdown("""
        <div class="detail-card" style="text-align:center; padding:2rem;">
            <p style="color:#5a6a7a; font-size:0.95rem;">검색어를 입력하거나 법령 필터를 선택하면 결과가 표시됩니다.</p>
            <div style="margin-top:1rem; color:#999; font-size:0.85rem;">
                <b>검색 예시:</b> CAS No. <code>64-19-7</code> | 영문명 <code>Acetic acid</code> | HSK No. <code>2804</code> | 품명 <code>염소</code>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ===========================================================================
# PAGE: 법령관리
# ===========================================================================
elif menu == "법령관리":
    st.markdown('<div class="page-title">법령목록</div>', unsafe_allow_html=True)

    # Get unique laws
    all_laws = db[db["관련법령"] != ""]["관련법령"].unique().tolist()
    law_counts = db[db["관련법령"] != ""].groupby("관련법령").size().sort_values(ascending=False)

    st.markdown(f'<div class="count-badge">총 <b>{len(law_counts)}</b> 개 법령</div>', unsafe_allow_html=True)

    # Law list as table
    law_df = law_counts.reset_index()
    law_df.columns = ["관련법령", "관련 품목 수"]
    st.dataframe(law_df, use_container_width=True, height=400)

    st.markdown("---")
    st.markdown('<div class="page-title">법령별 품목 조회</div>', unsafe_allow_html=True)

    selected_law = st.selectbox("법령 선택", ["선택하세요..."] + sorted(all_laws))

    if selected_law and selected_law != "선택하세요...":
        law_items = db[db["관련법령"].str.contains(re.escape(selected_law), case=False, na=False)]
        st.markdown(f'<div class="count-badge">총 <b>{len(law_items):,}</b> 건</div>', unsafe_allow_html=True)

        display_cols = ["CAS번호", "영문명", "세번", "품명"]
        st.dataframe(
            law_items[display_cols].reset_index(drop=True),
            use_container_width=True,
            height=min(450, 35 * len(law_items) + 38),
        )


# ===========================================================================
# PAGE: 화학물질 조회
# ===========================================================================
elif menu == "화학물질 조회":
    st.markdown('<div class="page-title">화학물질 조회 (팝업)</div>', unsafe_allow_html=True)

    q = st.text_input("CAS No. 또는 물질명으로 검색", placeholder="예: 64-19-7, Acetic acid, 아세트산",
                       key="chem_search")

    if q:
        results = search_database(db, q)
        # Prioritize entries with regulation info
        if not results.empty:
            has_reg = results.apply(
                lambda r: any(str(r.get(k, "")).strip() for k in
                              ["급성/만성/생태", "사고대비", "제한/금지/허가", "중점", "잔류", "관련법령"]),
                axis=1,
            )
            results = pd.concat([results[has_reg], results[~has_reg]])

        st.markdown(f'<div class="count-badge">총 <b>{len(results):,}</b> 건</div>', unsafe_allow_html=True)

        if results.empty:
            st.warning("검색 결과가 없습니다.")
        else:
            MAX = 100
            show = results.head(MAX)

            for _, row in show.iterrows():
                cas = row.get("CAS번호", "")
                eng = row.get("영문명", "")
                kor = row.get("국문명", "")
                hs = row.get("세번", "")
                product = row.get("품명", "")
                law = row.get("관련법령", "")

                # Title
                parts = []
                if cas: parts.append(f"[{cas}]")
                if eng: parts.append(eng)
                if kor: parts.append(f"({kor})")
                title = " ".join(parts) or product or "항목"

                with st.expander(title, expanded=False):
                    # Basic info as detail rows
                    info_html = f"""
                    <div class="detail-row"><div class="detail-label">CAS No.</div><div class="detail-value">{cas or '-'}</div></div>
                    <div class="detail-row"><div class="detail-label">영문명</div><div class="detail-value">{eng or '-'}</div></div>
                    <div class="detail-row"><div class="detail-label">국문명</div><div class="detail-value">{kor or '-'}</div></div>
                    <div class="detail-row"><div class="detail-label">HSK No.</div><div class="detail-value">{hs or '-'}</div></div>
                    <div class="detail-row"><div class="detail-label">품명</div><div class="detail-value">{product or '-'}</div></div>
                    """
                    st.markdown(info_html, unsafe_allow_html=True)

                    if law:
                        laws = re.split(r"[,\n]", str(law))
                        badges = " ".join(f'<span class="law-badge">{l.strip()}</span>' for l in laws if l.strip())
                        st.markdown(f'<div class="detail-row"><div class="detail-label">관련법령</div><div class="detail-value">{badges}</div></div>', unsafe_allow_html=True)

                    # Regulation tags inline
                    reg_parts = []
                    for field, cls in [("급성/만성/생태", "reg-tag-red"), ("사고대비", "reg-tag-orange"),
                                       ("제한/금지/허가", "reg-tag-red"), ("중점", "reg-tag-purple"),
                                       ("잔류", "reg-tag-yellow")]:
                        val = str(row.get(field, "")).strip()
                        if val:
                            reg_parts.append(f'<span class="reg-tag {cls}">{field}: {val}</span>')
                    if reg_parts:
                        st.markdown(f'<div class="detail-row"><div class="detail-label">규제정보</div><div class="detail-value">{" ".join(reg_parts)}</div></div>', unsafe_allow_html=True)

                    hazard = str(row.get("유해특성분류", "")).strip()
                    if hazard:
                        st.markdown(f'<div class="detail-row"><div class="detail-label">유해특성분류</div><div class="detail-value" style="font-size:0.8rem">{hazard}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="detail-card" style="text-align:center; padding:2rem;">
            <p style="color:#5a6a7a;">CAS No. 또는 물질명을 입력하면 화학물질 정보를 조회할 수 있습니다.</p>
        </div>
        """, unsafe_allow_html=True)
