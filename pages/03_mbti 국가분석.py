
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="세계 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)

# =====================================
# 2. 제목 및 설명
# =====================================

st.title("🌍 세계 국가별 MBTI 분석")
st.markdown(
    "국가를 선택하면 해당 국가의 16가지 MBTI 유형별 비율을 확인할 수 있습니다."
)

st.divider()

# =====================================
# 3. CSV 데이터 불러오기
# =====================================

@st.cache_data
def load_data():

    file_path = Path(__file__).parent / "countriesMBTI_16types.csv"

    if not file_path.exists():
        st.error(
            "CSV 파일을 찾을 수 없습니다. "
            "app.py와 같은 폴더에 countriesMBTI_16types.csv를 넣어주세요."
        )
        st.stop()

    data = pd.read_csv(file_path, encoding="utf-8-sig")

    if "Country" not in data.columns:
        st.error("CSV 파일에 Country 열이 없습니다.")
        st.stop()

    mbti_columns = [
        col for col in data.columns
        if col != "Country"
    ]

    if len(mbti_columns) != 16:
        st.error("MBTI 데이터가 16개인지 확인해주세요.")
        st.stop()

    data["Country"] = data["Country"].astype(str).str.strip()

    for col in mbti_columns:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    data = data.dropna(subset=["Country"])

    return data, mbti_columns


df, mbti_columns = load_data()

# =====================================
# 4. 국가 선택
# =====================================

countries = sorted(df["Country"].unique())

if len(countries) == 0:
    st.error("국가 데이터가 없습니다.")
    st.stop()

default_country = (
    "South Korea"
    if "South Korea" in countries
    else countries[0]
)

selected_country = st.selectbox(
    "🌎 국가를 선택하세요",
    countries,
    index=countries.index(default_country)
)

# =====================================
# 5. 선택 국가 데이터 분석
# =====================================

country_data = df[
    df["Country"] == selected_country
]

if country_data.empty:
    st.warning("해당 국가의 데이터가 없습니다.")
    st.stop()

country_data = country_data.iloc[0]

chart_data = pd.DataFrame({
    "MBTI": mbti_columns,
    "비율": [
        country_data[col]
        for col in mbti_columns
    ]
})

chart_data = chart_data.dropna()

if chart_data.empty:
    st.warning("분석할 MBTI 데이터가 없습니다.")
    st.stop()

# 데이터가 0~1 사이의 비율이면 백분율로 변환
if chart_data["비율"].max() <= 1.5:
    chart_data["비율"] = chart_data["비율"] * 100

# 높은 비율 순서대로 정렬
chart_data = chart_data.sort_values(
    by="비율",
    ascending=False
).reset_index(drop=True)

# =====================================
# 6. 최고 / 최저 MBTI 통계
# =====================================

highest = chart_data.iloc[0]
lowest = chart_data.iloc[-1]

st.subheader(f"📊 {selected_country} MBTI 분석")

col1, col2, col3 = st.columns(3)

col1.metric(
    "가장 높은 MBTI",
    highest["MBTI"],
    f'{highest["비율"]:.2f}%'
)

col2.metric(
    "가장 낮은 MBTI",
    lowest["MBTI"],
    f'{lowest["비율"]:.2f}%'
)

col3.metric(
    "MBTI 유형 개수",
    "16개"
)

st.divider()

# =====================================
# 7. 그래프 색상 설정
# =====================================

# 1위는 빨간색
colors = ["#E53935"]

# 나머지는 파란색 그라데이션
blue_gradient = [
    "#174EA6",
    "#2864B4",
    "#397AC2",
    "#4A90D0",
    "#5BA6DE",
    "#70B8E8",
    "#85C5ED",
    "#9AD2F2",
    "#AFE0F7",
    "#C4EAFB",
    "#D9F2FD",
    "#E5F6FE",
    "#CDEBFA",
    "#B5DFF6",
    "#9DD3F2"
]

colors.extend(
    blue_gradient[:len(chart_data) - 1]
)

# =====================================
# 8. 막대그래프 생성
# =====================================

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=chart_data["MBTI"],
        y=chart_data["비율"],
        marker=dict(
            color=colors
        ),
        text=[
            f"{value:.2f}%"
            for value in chart_data["비율"]
        ],
        textposition="outside",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "비율: %{y:.2f}%"
            "<extra></extra>"
        )
    )
)

fig.update_layout(
    title=f"{selected_country}의 MBTI 유형별 비율",
    xaxis_title="MBTI 유형",
    yaxis_title="비율 (%)",
    template="plotly_white",
    height=550,
    showlegend=False,
    margin=dict(
        l=30,
        r=30,
        t=70,
        b=40
    ),
    xaxis=dict(
        categoryorder="array",
        categoryarray=chart_data["MBTI"].tolist()
    ),
    yaxis=dict(
        rangemode="tozero",
        ticksuffix="%",
        range=[
            0,
            max(chart_data["비율"].max() * 1.2, 1)
        ]
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================
# 9. MBTI 상세 데이터 표
# =====================================

st.subheader("📋 MBTI 상세 비율")

display_data = chart_data.copy()

display_data["비율"] = display_data["비율"].map(
    lambda x: f"{x:.2f}%"
)

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)

# =====================================
# 10. 데이터 설명
# =====================================

with st.expander("📌 데이터 정보"):
    st.write(f"전체 국가 수: {len(countries)}개")
    st.write(f"MBTI 유형 수: {len(mbti_columns)}개")
    st.write(f"현재 선택 국가: {selected_country}")

st.caption(
    "본 결과는 제공된 CSV 데이터에 기반한 분석이며, "
    "각 국가 전체 인구의 실제 MBTI 분포를 의미하지는 않습니다."
)
