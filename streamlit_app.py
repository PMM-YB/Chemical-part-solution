# -*- coding: utf-8 -*-
"""
Chemical Part Solution - 화학물질 수입요령 검색 시스템
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
    page_title="화학물질 수입요령 검색",
    page_icon="🧪",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Global CSS - Mercedes-Benz Star Truck Korea branding
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* Remove Streamlit default top padding */
.block-container {
    padding-top: 0rem !important;
}
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 2.5rem !important;
}

/* Page background */
.stApp {
    background-color: #f0f2f5;
}

/* Header bar */
.header-bar {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 1.2rem 2rem;
    border-radius: 0 0 16px 16px;
    margin: -1rem -1rem 1.5rem -1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.header-bar h1 {
    color: #ffffff;
    font-size: 1.6rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: 0.5px;
}
.header-bar .subtitle {
    color: #8ebbff;
    font-size: 0.9rem;
    margin: 0;
}
.header-logo {
    font-size: 2.2rem;
    margin-right: 0.5rem;
}

/* Section cards */
.section-card {
    background: #ffffff;
    border-radius: 10px;
    padding: 1.5rem 2rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 6px rgba(0,0,0,0.08);
    border: 1px solid #e0e4e8;
}

/* Search box styling */
[data-testid="stTextInput"] > div > div > input {
    font-size: 1.1rem !important;
    padding: 0.7rem 1rem !important;
    border-radius: 10px !important;
    border: 2px solid #0f3460 !important;
}
[data-testid="stTextInput"] > div > div > input:focus {
    border-color: #00adef !important;
    box-shadow: 0 0 0 3px rgba(0,173,239,0.15) !important;
}

/* Result card */
.result-card {
    background: #ffffff;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    border-left: 4px solid #0f3460;
}

/* Law highlight */
.law-badge {
    display: inline-block;
    background: #e74c3c;
    color: #fff;
    padding: 0.25rem 0.7rem;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    margin: 0.15rem 0.15rem;
}
.law-badge-blue {
    background: #0f3460;
}

/* Regulation tags */
.reg-tag {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 5px;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 0.1rem;
}
.reg-tag-red { background: #fde8e8; color: #c0392b; border: 1px solid #e74c3c; }
.reg-tag-orange { background: #fef3e2; color: #e67e22; border: 1px solid #f0ad4e; }
.reg-tag-yellow { background: #fef9e7; color: #b7950b; border: 1px solid #f1c40f; }
.reg-tag-green { background: #eafaf1; color: #1e8449; border: 1px solid #2ecc71; }
.reg-tag-blue { background: #eaf2f8; color: #1a5276; border: 1px solid #3498db; }
.reg-tag-purple { background: #f4ecf7; color: #6c3483; border: 1px solid #9b59b6; }

/* Stats cards */
.stat-card {
    background: #ffffff;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    border: 1px solid #e0e4e8;
}
.stat-number {
    font-size: 1.8rem;
    font-weight: 800;
    color: #0f3460;
    margin: 0;
}
.stat-label {
    font-size: 0.85rem;
    color: #666;
    margin: 0;
}

/* Dataframe styling */
[data-testid="stDataFrame"] div[role="columnheader"],
[data-testid="stDataFrame"] div[role="columnheader"] *,
[data-testid="stDataFrame"] th {
    color: #000000 !important;
    opacity: 1 !important;
    font-weight: 800 !important;
}

/* Info text in import requirements */
.import-req-box {
    background: #f8f9fa;
    border: 1px solid #e0e4e8;
    border-radius: 8px;
    padding: 1rem;
    font-size: 0.9rem;
    line-height: 1.6;
    white-space: pre-wrap;
    max-height: 300px;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Data loading and processing
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent

CAS_FILE = "화학물질_20260325(CAS no).xlsx"
HS_FILE = "(수정) [별표2] 수입요령.xlsx"


@st.cache_data(show_spinner="데이터 로딩 중...")
def load_cas_data():
    """Load the CAS number reference file (47K+ chemicals)."""
    fp = DATA_DIR / CAS_FILE
    df = pd.read_excel(fp, dtype=str)
    df.columns = [
        "NO", "CAS번호", "영문명", "국문명", "기존",
        "급성/만성/생태", "사고대비", "제한/금지/허가",
        "중점", "잔류", "유해특성분류 및 혼합물 함량기준(%)",
        "등록대상기존화학물질", "기존물질여부",
    ]
    # Clean up CAS numbers
    df["CAS번호"] = df["CAS번호"].fillna("").str.strip()
    df["영문명"] = df["영문명"].fillna("").str.strip()
    df["국문명"] = df["국문명"].fillna("").str.strip()
    return df


@st.cache_data(show_spinner="수입요령 데이터 처리 중...")
def load_hs_data():
    """Load the HS code / import requirements file."""
    fp = DATA_DIR / HS_FILE
    df = pd.read_excel(fp, dtype=str)
    # Rename columns by position for reliability
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
    """
    Extract CAS numbers from 수입요령 text, match with CAS reference file,
    and build a unified searchable database.
    """
    cas_df = load_cas_data()
    hs_df = load_hs_data()

    # Build CAS lookup dictionary: CAS번호 -> row index
    cas_lookup = {}
    for idx, row in cas_df.iterrows():
        cas_num = row["CAS번호"]
        if cas_num:
            # Handle multiple CAS numbers (comma / semicolon separated)
            for cn in re.split(r"[,;/]\s*", cas_num):
                cn = cn.strip()
                if cn:
                    cas_lookup[cn] = idx

    # Build English name lookup (lowercase -> row index)
    eng_lookup = {}
    for idx, row in cas_df.iterrows():
        eng = row["영문명"].lower().strip()
        if eng:
            eng_lookup[eng] = idx

    # Pattern to extract [EnglishName; CAS-number] from 수입요령
    bracket_pattern = re.compile(r"\[([^\]]+)\]")
    cas_num_pattern = re.compile(r"\b(\d{2,7}-\d{2}-\d)\b")

    records = []

    for _, hs_row in hs_df.iterrows():
        text = hs_row["수입요령"]
        if not text:
            continue

        # Find all bracketed sections that contain CAS-like numbers
        brackets = bracket_pattern.findall(text)

        extracted_items = []
        for bracket_text in brackets:
            cas_matches = cas_num_pattern.findall(bracket_text)
            if cas_matches:
                # Extract English name: everything before the first semicolon or CAS number
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
            # No CAS numbers found in brackets - still include the HS row
            # as a standalone entry (for HS code / product name search)
            records.append({
                "세번": hs_row["세번"],
                "품명": hs_row["품명"],
                "수입요령": text,
                "관련법령": hs_row["관련법령"],
                "CAS번호": "",
                "영문명": "",
                "국문명": "",
                "급성/만성/생태": "",
                "사고대비": "",
                "제한/금지/허가": "",
                "중점": "",
                "잔류": "",
                "유해특성분류": "",
                "기존물질여부": "",
                "_matched": False,
            })
            continue

        # For each extracted CAS, try to match with the CAS reference
        for eng_name, cas_num in extracted_items:
            cas_info = {}
            matched = False

            # Primary: exact CAS match
            if cas_num in cas_lookup:
                cas_row = cas_df.iloc[cas_lookup[cas_num]]
                cas_info = {
                    "CAS번호": cas_num,
                    "영문명": cas_row["영문명"] if cas_row["영문명"] else eng_name,
                    "국문명": cas_row["국문명"],
                    "급성/만성/생태": cas_row["급성/만성/생태"],
                    "사고대비": cas_row["사고대비"],
                    "제한/금지/허가": cas_row["제한/금지/허가"],
                    "중점": cas_row["중점"],
                    "잔류": cas_row["잔류"],
                    "유해특성분류": cas_row["유해특성분류 및 혼합물 함량기준(%)"],
                    "기존물질여부": cas_row["기존물질여부"],
                }
                matched = True
            else:
                # Fallback: English name fuzzy match
                eng_lower = eng_name.lower().strip()
                if eng_lower and eng_lower in eng_lookup:
                    cas_row = cas_df.iloc[eng_lookup[eng_lower]]
                    cas_info = {
                        "CAS번호": cas_num,
                        "영문명": cas_row["영문명"],
                        "국문명": cas_row["국문명"],
                        "급성/만성/생태": cas_row["급성/만성/생태"],
                        "사고대비": cas_row["사고대비"],
                        "제한/금지/허가": cas_row["제한/금지/허가"],
                        "중점": cas_row["중점"],
                        "잔류": cas_row["잔류"],
                        "유해특성분류": cas_row["유해특성분류 및 혼합물 함량기준(%)"],
                        "기존물질여부": cas_row["기존물질여부"],
                    }
                    matched = True

            if not matched:
                cas_info = {
                    "CAS번호": cas_num,
                    "영문명": eng_name,
                    "국문명": "",
                    "급성/만성/생태": "",
                    "사고대비": "",
                    "제한/금지/허가": "",
                    "중점": "",
                    "잔류": "",
                    "유해특성분류": "",
                    "기존물질여부": "",
                }

            records.append({
                "세번": hs_row["세번"],
                "품명": hs_row["품명"],
                "수입요령": text,
                "관련법령": hs_row["관련법령"],
                **cas_info,
                "_matched": matched,
            })

    result = pd.DataFrame(records)

    # ── Fuzzy matching for CAS-only entries ──────────────────────────
    # Build HS품명 lookup for fuzzy matching (품명 -> list of hs rows)
    hs_product_names = {}
    for _, hs_row in hs_df.iterrows():
        pname = hs_row["품명"].strip()
        if pname:
            hs_product_names[pname] = hs_row

    # Build list of HS 수입요령 English names for fuzzy matching
    hs_eng_names = {}  # english name -> hs_row
    for _, hs_row in hs_df.iterrows():
        text = hs_row["수입요령"]
        if not text:
            continue
        # Extract all English names from brackets
        for bracket_text in bracket_pattern.findall(text):
            parts = re.split(r";\s*", bracket_text)
            for part in parts:
                part = part.strip()
                if part and not cas_num_pattern.match(part) and re.search(r"[a-zA-Z]", part):
                    hs_eng_names[part.lower()] = hs_row

    hs_eng_keys = list(hs_eng_names.keys())

    # Also include CAS-only entries (chemicals not in HS file)
    # Try fuzzy matching by English name to find related HS entries
    cas_only_records = []
    matched_cas_set = set(result["CAS번호"].dropna().unique())
    fuzzy_matched = 0

    for _, cas_row in cas_df.iterrows():
        cas_num = cas_row["CAS번호"]
        if cas_num and cas_num not in matched_cas_set:
            eng_name = cas_row["영문명"].strip()
            hs_info = {"세번": "", "품명": "", "수입요령": "", "관련법령": ""}
            is_matched = False

            # Try fuzzy match with English names in HS data
            if eng_name and hs_eng_keys:
                eng_lower = eng_name.lower()
                # First try exact substring match
                for hs_eng, hs_row in hs_eng_names.items():
                    if eng_lower == hs_eng or eng_lower in hs_eng or hs_eng in eng_lower:
                        hs_info = {
                            "세번": hs_row["세번"],
                            "품명": hs_row["품명"],
                            "수입요령": hs_row["수입요령"],
                            "관련법령": hs_row["관련법령"],
                        }
                        is_matched = True
                        fuzzy_matched += 1
                        break

                # If no substring match, try fuzzy matching (score >= 85)
                if not is_matched:
                    match = process.extractOne(
                        eng_lower, hs_eng_keys,
                        scorer=fuzz.token_sort_ratio,
                        score_cutoff=85,
                    )
                    if match:
                        best_name, score, _ = match
                        hs_row = hs_eng_names[best_name]
                        hs_info = {
                            "세번": hs_row["세번"],
                            "품명": hs_row["품명"],
                            "수입요령": hs_row["수입요령"],
                            "관련법령": hs_row["관련법령"],
                        }
                        is_matched = True
                        fuzzy_matched += 1

            cas_only_records.append({
                **hs_info,
                "CAS번호": cas_num,
                "영문명": cas_row["영문명"],
                "국문명": cas_row["국문명"],
                "급성/만성/생태": cas_row["급성/만성/생태"],
                "사고대비": cas_row["사고대비"],
                "제한/금지/허가": cas_row["제한/금지/허가"],
                "중점": cas_row["중점"],
                "잔류": cas_row["잔류"],
                "유해특성분류": cas_row["유해특성분류 및 혼합물 함량기준(%)"],
                "기존물질여부": cas_row["기존물질여부"],
                "_matched": is_matched,
            })

    cas_only_df = pd.DataFrame(cas_only_records)
    result = pd.concat([result, cas_only_df], ignore_index=True)

    # Fill NaN with empty string for consistent searching
    result = result.fillna("")

    return result


def search_database(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """Search across multiple columns with case-insensitive partial matching."""
    if not query or not query.strip():
        return pd.DataFrame()

    query = query.strip().lower()
    # Split multi-word queries for AND-matching
    terms = query.split()

    mask = pd.Series([True] * len(df), index=df.index)

    # Build a combined searchable text column for efficiency
    search_cols = ["품명", "영문명", "국문명", "CAS번호", "세번", "관련법령"]
    combined = df[search_cols].apply(
        lambda row: " ".join(str(v).lower() for v in row), axis=1
    )

    for term in terms:
        mask &= combined.str.contains(re.escape(term), case=False, na=False)

    return df[mask]


def render_regulation_tags(row):
    """Generate HTML for regulation status tags."""
    tags = []
    if row.get("급성/만성/생태") and str(row["급성/만성/생태"]).strip():
        tags.append(f'<span class="reg-tag reg-tag-red">급성/만성/생태: {row["급성/만성/생태"]}</span>')
    if row.get("사고대비") and str(row["사고대비"]).strip():
        tags.append(f'<span class="reg-tag reg-tag-orange">사고대비: {row["사고대비"]}</span>')
    if row.get("제한/금지/허가") and str(row["제한/금지/허가"]).strip():
        tags.append(f'<span class="reg-tag reg-tag-red">제한/금지/허가: {row["제한/금지/허가"]}</span>')
    if row.get("중점") and str(row["중점"]).strip():
        tags.append(f'<span class="reg-tag reg-tag-purple">중점관리: {row["중점"]}</span>')
    if row.get("잔류") and str(row["잔류"]).strip():
        tags.append(f'<span class="reg-tag reg-tag-yellow">잔류: {row["잔류"]}</span>')
    if row.get("기존물질여부") and str(row["기존물질여부"]).strip():
        tags.append(f'<span class="reg-tag reg-tag-green">기존물질: {row["기존물질여부"]}</span>')
    return " ".join(tags)


def render_law_badges(law_text):
    """Generate HTML for related law badges."""
    if not law_text or not str(law_text).strip():
        return ""
    # Split by common delimiters
    laws = re.split(r"[,\n/]", str(law_text))
    badges = []
    for law in laws:
        law = law.strip()
        if law:
            badges.append(f'<span class="law-badge">{law}</span>')
    return " ".join(badges)


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------
def main():
    # ── Header ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="header-bar">
        <span class="header-logo">&#9883;</span>
        <div>
            <h1>화학물질 수입요령 검색 시스템</h1>
            <p class="subtitle">Chemical Import Requirements Search &mdash; Star Truck Korea</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Load data ─────────────────────────────────────────────────────────
    try:
        db = build_unified_db()
    except Exception as e:
        st.error(f"데이터 로딩 중 오류가 발생했습니다: {e}")
        st.stop()

    # ── Statistics ─────────────────────────────────────────────────────────
    total_chemicals = db[db["CAS번호"] != ""].shape[0]
    total_hs = db[db["세번"] != ""]["세번"].nunique()
    matched_count = db[db["_matched"]].shape[0]

    cols = st.columns(4)
    with cols[0]:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-number">{len(db):,}</p>
            <p class="stat-label">전체 레코드</p>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-number">{total_chemicals:,}</p>
            <p class="stat-label">화학물질 (CAS)</p>
        </div>
        """, unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-number">{total_hs:,}</p>
            <p class="stat-label">HS 코드</p>
        </div>
        """, unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f"""
        <div class="stat-card">
            <p class="stat-number">{matched_count:,}</p>
            <p class="stat-label">CAS-HS 매칭</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Search ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    query = st.text_input(
        "검색어를 입력하세요",
        placeholder="품명, 영문명, 국문명, CAS 번호, HS 코드 검색...",
        label_visibility="collapsed",
        key="search_input",
    )

    # Search mode options
    col_a, col_b = st.columns([3, 1])
    with col_b:
        search_scope = st.selectbox(
            "검색 범위",
            ["전체 (통합 DB)", "수입요령 있는 항목만", "CAS 화학물질만"],
            index=0,
            label_visibility="collapsed",
        )
    st.markdown('</div>', unsafe_allow_html=True)

    if not query:
        st.info("검색어를 입력하면 화학물질 정보와 수입요령을 조회할 수 있습니다.")
        st.markdown("---")
        st.markdown("""
        **검색 예시:**
        - CAS 번호: `64-19-7` (아세트산)
        - 영문명: `Nicotine`, `Acetic acid`
        - 국문명: `니코틴`, `아세트산`
        - HS 코드: `2209`, `2804`
        - 품명: `식초`, `질소`
        """)
        return

    # Filter by scope
    search_df = db.copy()
    if search_scope == "수입요령 있는 항목만":
        search_df = search_df[search_df["수입요령"] != ""]
    elif search_scope == "CAS 화학물질만":
        search_df = search_df[search_df["CAS번호"] != ""]

    results = search_database(search_df, query)

    if results.empty:
        st.warning(f"'{query}'에 대한 검색 결과가 없습니다.")
        return

    # ── Results summary ───────────────────────────────────────────────────
    st.markdown(f"### 검색 결과: **{len(results):,}건**")

    # ── Results table (summary view) ──────────────────────────────────────
    display_cols = ["CAS번호", "영문명", "국문명", "세번", "품명", "관련법령"]
    summary = results[display_cols].copy()
    summary = summary.reset_index(drop=True)

    # Limit display to prevent performance issues
    MAX_DISPLAY = 200
    if len(summary) > MAX_DISPLAY:
        st.info(f"검색 결과가 {len(results):,}건입니다. 상위 {MAX_DISPLAY}건만 표시합니다. 검색어를 더 구체적으로 입력해주세요.")
        display_results = results.head(MAX_DISPLAY)
    else:
        display_results = results

    st.dataframe(
        display_results[display_cols].reset_index(drop=True),
        use_container_width=True,
        height=min(400, 35 * len(display_results) + 38),
    )

    # ── Detailed cards ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 상세 정보")

    # Paginate detailed results
    CARDS_PER_PAGE = 20
    total_pages = max(1, (len(display_results) + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE)

    if total_pages > 1:
        page = st.number_input(
            "페이지", min_value=1, max_value=total_pages,
            value=1, step=1, format="%d",
        )
    else:
        page = 1

    start_idx = (page - 1) * CARDS_PER_PAGE
    end_idx = min(start_idx + CARDS_PER_PAGE, len(display_results))
    page_results = display_results.iloc[start_idx:end_idx]

    if total_pages > 1:
        st.caption(f"페이지 {page}/{total_pages} (전체 {len(display_results)}건 중 {start_idx+1}-{end_idx}건)")

    for i, (_, row) in enumerate(page_results.iterrows()):
        cas = row.get("CAS번호", "")
        eng = row.get("영문명", "")
        kor = row.get("국문명", "")
        hs = row.get("세번", "")
        product = row.get("품명", "")
        import_req = row.get("수입요령", "")
        law = row.get("관련법령", "")

        # Card title
        title_parts = []
        if cas:
            title_parts.append(f"[{cas}]")
        if eng:
            title_parts.append(eng)
        if kor:
            title_parts.append(f"({kor})")
        if not title_parts and product:
            title_parts.append(product)
        title = " ".join(title_parts) if title_parts else f"항목 {start_idx + i + 1}"

        with st.expander(title, expanded=(len(page_results) <= 5)):
            # Basic info row
            info_cols = st.columns([1, 1, 1])
            with info_cols[0]:
                st.markdown(f"**CAS 번호:** `{cas}`" if cas else "**CAS 번호:** -")
                st.markdown(f"**영문명:** {eng}" if eng else "**영문명:** -")
            with info_cols[1]:
                st.markdown(f"**국문명:** {kor}" if kor else "**국문명:** -")
                st.markdown(f"**품명:** {product}" if product else "**품명:** -")
            with info_cols[2]:
                st.markdown(f"**HS 코드 (세번):** `{hs}`" if hs else "**HS 코드:** -")

            # Related laws - prominently displayed
            if law:
                st.markdown("**관련법령:**")
                st.markdown(render_law_badges(law), unsafe_allow_html=True)

            # Regulation tags
            reg_html = render_regulation_tags(row)
            if reg_html:
                st.markdown("**규제정보:**")
                st.markdown(reg_html, unsafe_allow_html=True)

            # Hazard classification
            hazard = row.get("유해특성분류", "")
            if hazard:
                st.markdown(f"**유해특성분류 및 혼합물 함량기준:**")
                st.caption(hazard)

            # Import requirements - full text in scrollable box
            if import_req:
                st.markdown("**수입요령:**")
                st.markdown(
                    f'<div class="import-req-box">{import_req}</div>',
                    unsafe_allow_html=True,
                )


if __name__ == "__main__":
    main()
