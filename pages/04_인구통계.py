import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="서울시 연령별 인구 분석",
    page_icon="📊",
    layout="wide",
)

st.title("서울시 행정구별 연령·성별 인구 분석")
st.caption("행정구, 성별, 연도를 선택해 인구 데이터를 확인합니다.")

# 이 파일은 pages 폴더 안에 있으므로 CSV는 상위 폴더에서 찾습니다.
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_FILE = BASE_DIR / "population.csv"


@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """한글 CSV 인코딩을 순서대로 시도해 읽습니다."""
    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]
    last_error = None

    for encoding in encodings:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError as error:
            last_error = error

    raise ValueError(
        "CSV 파일의 인코딩을 읽을 수 없습니다. "
        "CP949 또는 UTF-8 형식인지 확인해주세요."
    ) from last_error


try:
    df = load_data(str(CSV_FILE))
except FileNotFoundError:
    st.error(
        f"'{CSV_FILE.name}' 파일을 찾을 수 없습니다. "
        "population.csv가 app.py의 상위 폴더에 있는지 확인해주세요."
    )
    st.stop()
except Exception as error:
    st.error(f"CSV 파일을 불러오는 중 오류가 발생했습니다: {error}")
    st.stop()


# 행정구 이름 정리
# 예: '서울특별시 종로구 (1111000000)' -> '종로구'
def clean_district(value) -> str:
    value = str(value).strip()
    value = re.sub(r"\s*\(\d+\)\s*$", "", value)
    value = value.replace("서울특별시", "").strip()

    return value if value else "서울특별시"


if "행정구역" not in df.columns:
    st.error("CSV에서 '행정구역' 열을 찾을 수 없습니다.")
    st.stop()

df["행정구"] = df["행정구역"].apply(clean_district)

# 인구 열의 쉼표 제거 후 숫자로 변환
population_columns = [
    column
    for column in df.columns
    if column not in ["행정구역", "행정구"]
]

for column in population_columns:
    df[column] = (
        df[column]
        .astype(str)
        .str.replace(",", "", regex=False)
        .replace({"": None, "nan": None, "-": None})
    )
    df[column] = pd.to_numeric(df[column], errors="coerce")

# 서울시 전체 행은 제외하고 자치구만 선택지로 표시
districts = sorted(
    district
    for district in df["행정구"].dropna().unique()
    if district != "서울특별시"
)

if not districts:
    st.error("행정구 데이터를 찾을 수 없습니다.")
    st.stop()

# 열 이름에서 연도 추출
years = sorted(
    {
        int(match.group(1))
        for column in df.columns
        if (match := re.match(r"(\d{4})년_", column))
    }
)

if not years:
    st.error("연도 형식의 데이터 열을 찾을 수 없습니다.")
    st.stop()


# 선택 컨트롤
col1, col2, col3 = st.columns(3)

with col1:
    selected_district = st.selectbox("행정구 선택", districts)

with col2:
    selected_gender = st.selectbox("성별 선택", ["전체", "남성", "여성"])

with col3:
    selected_year = st.selectbox(
        "연도 선택",
        years,
        index=len(years) - 1,
    )


# CSV 열 이름의 성별 표기와 연결
if selected_gender == "전체":
    gender_key = "거주자"
elif selected_gender == "남성":
    gender_key = "남_거주자"
else:
    gender_key = "여_거주자"

prefix = f"{selected_year}년_{gender_key}_"

# 세부 연령대 열 찾기
age_columns = []

for column in df.columns:
    if not column.startswith(prefix):
        continue

    age_label = column[len(prefix):]

    # 0~9세, 10~19세 등의 연령대만 선택
    if re.search(r"\d+\s*~\s*\d+\s*세", age_label):
        age_columns.append((column, age_label))


district_data = df[df["행정구"] == selected_district]

if district_data.empty:
    st.error("선택한 행정구의 데이터를 찾을 수 없습니다.")
    st.stop()

selected_row = district_data.iloc[0]


# 이 파일에는 0~9세 항목만 있으므로 해당 사실을 안내
if not age_columns or len(age_columns) == 1:
    st.warning(
        "현재 CSV에는 선택한 성별·연도 기준으로 0~9세 연령대만 있습니다. "
        "따라서 그래프에는 해당 연령대의 한 점만 표시됩니다. "
        "10~19세, 20~29세 등 연령별 꺾은선 그래프를 만들려면 "
        "각 연령대가 포함된 CSV 파일이 필요합니다."
    )

    fallback_column = f"{selected_year}년_{gender_key}_0~9세"

    if fallback_column not in df.columns:
        st.error(f"열 '{fallback_column}'을(를) 찾을 수 없습니다.")
        st.stop()

    age_data = pd.DataFrame(
        {
            "연령대": ["0~9세"],
            "인구수": [selected_row[fallback_column]],
        }
    )
else:
    age_data = pd.DataFrame(
        [
            {
                "연령대": age_label,
                "인구수": selected_row[column],
            }
            for column, age_label in age_columns
        ]
    )


# 연령대 시작 나이 기준으로 정렬
def get_age_start(age_label) -> int:
    match = re.search(r"(\d+)\s*~", str(age_label))
    return int(match.group(1)) if match else 0


age_data["연령 시작"] = age_data["연령대"].apply(get_age_start)
age_data = age_data.sort_values("연령 시작")


# 핫핑크 꺾은선 그래프
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=age_data["연령 시작"],
        y=age_data["인구수"],
        mode="lines+markers",
        name="인구수",
        line=dict(color="#FF1493", width=3),
        marker=dict(color="#FF1493", size=8),
        customdata=age_data["연령대"],
        hovertemplate=(
            "%{customdata}<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        ),
    )
)

fig.update_layout(
    title=(
        f"{selected_district} · {selected_gender} · "
        f"{selected_year}년 연령대별 인구"
    ),
    xaxis_title="나이",
    yaxis_title="인구수(명)",
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Arial, sans-serif"),
    hovermode="x unified",
    margin=dict(l=20, r=20, t=60, b=20),
)

# 가로축 10살 단위 구분선
fig.update_xaxes(
    dtick=10,
    tick0=0,
    showgrid=True,
    gridcolor="#E6E6E6",
    zeroline=False,
)

# 세로축 10만 명 단위 구분선
fig.update_yaxes(
    dtick=100000,
    tickformat=",",
    rangemode="tozero",
    showgrid=True,
    gridcolor="#E6E6E6",
    zeroline=False,
)

st.plotly_chart(fig, use_container_width=True)


# 선택 데이터 표
st.subheader("선택한 데이터")

display_data = age_data[["연령대", "인구수"]].copy()
display_data["인구수"] = display_data["인구수"].apply(
    lambda value: f"{value:,.0f}" if pd.notna(value) else "결측치"
)

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True,
)


# 결측치 현황
missing_count = int(df[population_columns].isna().sum().sum())
st.caption(f"데이터 결측치 수: {missing_count:,}개")
