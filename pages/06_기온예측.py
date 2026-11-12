
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from datetime import datetime
from pathlib import Path

# -----------------------------
# 1. 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="기온 분석 및 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 분석 및 예측")
st.caption("과거 기온 데이터를 활용한 선형회귀 기온 예측 프로그램")

st.divider()

# -----------------------------
# 2. CSV 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "temperature.csv"

    try:
        try:
            data = pd.read_csv(file_path, encoding="cp949")
        except UnicodeDecodeError:
            data = pd.read_csv(file_path, encoding="utf-8-sig")

        # 날짜 데이터 처리
        data["일시"] = pd.to_datetime(
            data["일시"],
            format="%b-%y",
            errors="coerce"
        )

        data = data.dropna(subset=["일시"])

        data["연도"] = data["일시"].dt.year
        data["월"] = data["일시"].dt.month

        data["평균기온(℃)"] = pd.to_numeric(
            data["평균기온(℃)"],
            errors="coerce"
        )

        data = data.dropna(subset=["평균기온(℃)"])

        # 같은 월과 연도에 여러 데이터가 있으면 평균 계산
        monthly_data = (
            data.groupby(["연도", "월"], as_index=False)
            ["평균기온(℃)"].mean()
        )

        return monthly_data

    except FileNotFoundError:
        st.error("temperature.csv 파일을 찾을 수 없습니다.")
        st.stop()

    except Exception as e:
        st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")
        st.stop()


df = load_data()

# -----------------------------
# 3. 사용자 입력
# -----------------------------
st.subheader("📌 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "분석할 월을 선택하세요",
        options=list(range(1, 13)),
        format_func=lambda x: f"{x}월"
    )

with col2:
    selected_year = st.number_input(
        "예측할 연도를 입력하세요",
        min_value=1900,
        max_value=2100,
        value=int(df["연도"].max()) + 5,
        step=1
    )

# -----------------------------
# 4. 선택한 월 데이터 추출
# -----------------------------
month_df = df[df["월"] == selected_month].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.warning("선형회귀 분석을 위해서는 최소 2개 이상의 데이터가 필요합니다.")
    st.stop()

X = month_df[["연도"]]
y = month_df["평균기온(℃)"]

# -----------------------------
# 5. 선형회귀 모델 학습
# -----------------------------
model = LinearRegression()

model.fit(X, y)

# 실제 데이터의 예측값
month_df["회귀예측값"] = model.predict(X)

# 사용자가 선택한 연도의 기온 예측
prediction = model.predict(
    pd.DataFrame({"연도": [selected_year]})
)[0]

# 회귀식 정보
slope = model.coef_[0]
intercept = model.intercept_
r2 = model.score(X, y)

# -----------------------------
# 6. 그래프용 데이터 생성
# -----------------------------
start_year = int(month_df["연도"].min())
end_year = max(int(month_df["연도"].max()), int(selected_year))

trend_years = np.arange(start_year, end_year + 1)

trend_predictions = model.predict(
    pd.DataFrame({"연도": trend_years})
)

# -----------------------------
# 7. 주요 결과 표시
# -----------------------------
st.divider()
st.subheader(f"📊 {selected_month}월 평균기온 분석 결과")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "예측 연도",
        f"{selected_year}년"
    )

with col2:
    st.metric(
        "예측 평균기온",
        f"{prediction:.2f} ℃"
    )

with col3:
    st.metric(
        "결정계수 (R²)",
        f"{r2:.3f}"
    )

# -----------------------------
# 8. 그래프 생성
# -----------------------------
fig = go.Figure()

# 실제 평균기온
fig.add_trace(go.Scatter(
    x=month_df["연도"],
    y=month_df["평균기온(℃)"],
    mode="markers",
    name="실제 평균기온",
    marker=dict(
        color="#FF1493",
        size=10,
        line=dict(width=1, color="white")
    ),
    hovertemplate=
    "%{x}년<br>실제 기온: %{y:.2f}℃<extra></extra>"
))

# 잔차 표시: 실제 기온과 회귀선 사이의 거리
residual_x = []
residual_y = []

for _, row in month_df.iterrows():
    residual_x.extend([
        row["연도"],
        row["연도"],
        None
    ])

    residual_y.extend([
        row["평균기온(℃)"],
        row["회귀예측값"],
        None
    ])

fig.add_trace(go.Scatter(
    x=residual_x,
    y=residual_y,
    mode="lines",
    name="잔차 (실제값과 예측값의 차이)",
    line=dict(
        color="gray",
        width=1.5,
        dash="dot"
    ),
    hoverinfo="skip"
))

# 선형회귀 추세선
fig.add_trace(go.Scatter(
    x=trend_years,
    y=trend_predictions,
    mode="lines",
    name="선형회귀 추세선",
    line=dict(
        color="#4169E1",
        width=3
    ),
    hovertemplate=
    "%{x}년<br>회귀 기온: %{y:.2f}℃<extra></extra>"
))

# 미래 예측 지점
fig.add_trace(go.Scatter(
    x=[selected_year],
    y=[prediction],
    mode="markers+text",
    name="예측 평균기온",
    marker=dict(
        color="#00BFFF",
        size=17,
        symbol="star",
        line=dict(width=2, color="white")
    ),
    text=[f"{prediction:.2f}℃"],
    textposition="top center",
    textfont=dict(size=14, color="#00BFFF"),
    hovertemplate=
    "%{x}년<br>예측 기온: %{y:.2f}℃<extra></extra>"
))

fig.update_layout(
    title=dict(
        text=f"{selected_month}월 연도별 평균기온 및 미래 예측",
        x=0.5
    ),
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    template="plotly_white",
    hovermode="x unified",
    height=600,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),
    margin=dict(l=30, r=30, t=100, b=50)
)

fig.update_xaxes(
    dtick=1,
    showgrid=True
)

fig.update_yaxes(
    showgrid=True,
    zeroline=True
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 9. 선형회귀 알고리즘 설명
# -----------------------------
st.divider()

st.subheader("🧠 선형회귀 알고리즘은 어떻게 작동할까?")

st.markdown("""
### ① 실제 데이터 수집
선택한 월에 해당하는 모든 연도의 평균기온 데이터를 가져옵니다.

예를 들어 7월을 선택하면 2008년 7월, 2009년 7월,
2010년 7월 등의 평균기온을 분석합니다.

### ② 가장 적합한 직선 찾기

선형회귀는 과거 연도와 평균기온의 관계를 분석하여
실제 데이터와 가장 잘 맞는 직선을 찾는 알고리즘입니다.

직선은 다음과 같은 수식으로 표현됩니다.
""")

st.latex(r"\hat{y} = ax+b")

st.markdown("""
- x : 연도
- ŷ : 예측 평균기온
- a : 기온의 연도별 변화량(기울기)
- b : 직선의 y절편

### ③ 오차를 최소화하기

그래프의 회색 점선은 실제 기온과 회귀선 사이의 차이를 나타냅니다.

이 차이를 잔차라고 합니다.

선형회귀는 각 데이터의 잔차를 제곱한 값의 합이
최소가 되도록 직선의 기울기와 절편을 계산합니다.
""")

st.latex(
    r"\min \sum_{i=1}^{n}(y_i-\hat{y}_i)^2"
)

st.markdown("""
### ④ 미래 기온 예측

과거 데이터로 직선을 완성하면 새로운 연도를 입력했을 때
그 직선 위의 값을 계산하여 미래 평균기온을 예측합니다.

따라서 파란색 별표가 사용자가 선택한 연도의 예측 기온입니다.
""")

# -----------------------------
# 10. 분석 결과 및 회귀식
# -----------------------------
st.divider()

st.subheader("📈 선형회귀 분석 상세 결과")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**회귀식**")
    st.latex(
        rf"\hat{{y}} = {slope:.4f}x + ({intercept:.2f})"
    )

    st.write(f"기울기: {slope:.4f} ℃/년")

    if slope > 0:
        st.success("장기적으로 기온이 상승하는 경향이 있습니다.")
    elif slope < 0:
        st.info("장기적으로 기온이 하락하는 경향이 있습니다.")
    else:
        st.info("기온에 뚜렷한 선형 변화가 없습니다.")

with col2:
    st.markdown("**모델 평가**")
    st.write(f"결정계수 R²: {r2:.4f}")
    st.write(f"학습 데이터 개수: {len(month_df)}개")
    st.write(f"분석 기간: {start_year}년 ~ {month_df['연도'].max()}년")

    if r2 >= 0.7:
        st.success("선형 추세가 데이터에 비교적 잘 맞습니다.")
    elif r2 >= 0.4:
        st.warning("선형 추세와 실제 데이터 사이에 차이가 있습니다.")
    else:
        st.info("선형 모델의 설명력이 낮습니다. 예측값에 주의하세요.")

# -----------------------------
# 11. 실제 데이터 표
# -----------------------------
with st.expander("📋 실제 기온 데이터 확인하기"):
    result_table = month_df[
        ["연도", "평균기온(℃)", "회귀예측값"]
    ].copy()

    result_table.columns = [
        "연도",
        "실제 평균기온(℃)",
        "회귀선 예측값(℃)"
    ]

    st.dataframe(
        result_table.round(2),
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "※ 이 프로그램은 과거 평균기온의 선형적인 추세를 바탕으로 "
    "예측합니다. 실제 미래 기온과 다를 수 있습니다."
)

