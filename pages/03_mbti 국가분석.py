import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="세계 국가별 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 세계 국가별 MBTI 분석")
st.caption("국가를 선택하면 해당 국가의 16가지 MBTI 비율을 확인할 수 있습니다.")

# CSV 파일은 app.py와 같은 폴더에 있어야 합니다.
DATA_CANDIDATES = [
    Path(__file__).parent / "countriesMBTI_16types.csv",
    Path(__file__).parent / "countriesMBTI_16types (1).csv",
]

@st.cache_data
def load_data():
    csv_path = next((p for p in DATA_CANDIDATES if p.exists()), None)
    if csv_path is None:
        st.error(
            "CSV 파일을 찾을 수 없습니다. "
            "countriesMBTI_16types.csv 파일을 app.py와 같은 폴더에 업로드해 주세요."
        )
        st.stop()

    try:
        data = pd.read_csv(csv_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(csv_path, encoding="cp949")

    if "Country" not in data.columns:
        st.error("CSV에 'Country' 열이 없습니다. 데이터 파일의 열 이름을 확인해 주세요.")
        st.stop()

    mbti_cols = [col for col in data.columns if col != "Country"]
    if len(mbti_cols) != 16:
        st.warning(f"MBTI 열이 16개가 아닙니다. 현재 {len(mbti_cols)}개 열을 찾았습니다.")

    data["Country"] = data["Country"].astype(str).str.strip()
    for col in mbti_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=["Country"])
    return data, mbti_cols

df, mbti_columns = load_data()

if df.empty or not mbti_columns:
    st.error("표시할 데이터가 없습니다.")
    st.stop()

countries = sorted(df["Country"].dropna().unique().tolist())
default_index = countries.index("South Korea") if "South Korea" in countries else 0

selected_country = st.selectbox(
    "국가 선택",
    options=countries,
    index=default_index
)

country_row = df.loc[df["Country"] == selected_country].iloc[0]

# 비율을 내림차순으로 정렬하고, 데이터가 0~1 사이의 비율이면 %로 변환
chart_data = pd.DataFrame({
    "MBTI": mbti_columns,
    "비율": [country_row[col] for col in mbti_columns]
}).dropna()

if chart_data.empty:
    st.warning("선택한 국가의 MBTI 데이터가 없습니다.")
    st.stop()

if chart_data["비율"].max() <= 1.5:
    chart_data["비율"] = chart_data["비율"] * 100

chart_data = chart_data.sort_values("비율", ascending=False).reset_index(drop=True)

# 1위는 빨간색, 나머지는 진한 파랑에서 연한 파랑으로 그라데이션
blue_gradient = [
    "#174EA6", "#2864B4", "#397AC2", "#4A90D0",
    "#5BA6DE", "#70B8E8", "#8AC8EF", "#A4D7F5",
    "#BDE4FA", "#D2EEFC", "#E3F5FE", "#EDF9FF",
    "#DCEFFD", "#C9E5FA", "#B5DAF6"
]
bar_colors = ["#E53935"] + blue_gradient[: max(0, len(chart_data) - 1)]

st.subheader(f"{selected_country}의 MBTI 비율")

top_mbti = chart_data.iloc[0]
metric_col1, metric_col2 = st.columns(2)
metric_col1.metric("가장 높은 MBTI", top_mbti["MBTI"])
metric_col2.metric("가장 높은 비율", f'{top_mbti["비율"]:.2f}%')

fig = go.Figure(
    data=[
        go.Bar(
            x=chart_data["MBTI"],
            y=chart_data["비율"],
            marker_color=bar_colors,
            text=[f"{v:.2f}%" for v in chart_data["비율"]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{x}<br>비율: %{y:.2f}%<extra></extra>"
        )
    ]
)

fig.update_layout(
    template="plotly_white",
    height=520,
    margin=dict(l=25, r=25, t=35, b=25),
    xaxis_title="MBTI 유형",
    yaxis_title="비율(%)",
    yaxis=dict rangemode="tozero", ticksuffix="%",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

with st.expander("비율 데이터 표 보기"):
    display_data = chart_data.copy()
    display_data["비율"] = display_data["비율"].map(lambda x: f"{x:.2f}%")
    st.dataframe(display_data, use_container_width=True, hide_index=True)

st.caption(
    "참고: 이 자료는 제공된 CSV의 국가별 비율을 시각화한 것입니다. "
    "국가 전체 인구를 대표하는 공식 통계로 해석하지 않도록 주의해 주세요."
)
