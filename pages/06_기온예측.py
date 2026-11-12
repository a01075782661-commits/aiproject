
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from pathlib import Path
from datetime import datetime

# =====================================
# 1. 페이지 설정
# =====================================
st.set_page_config(
    page_title="월별 평균기온 분석 및 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 분석 및 예측")
st.write("과거 기온 데이터를 활용한 선형회귀 미래 기온 예측")

st.divider()

# =====================================
# 2. CSV 파일 불러오기
# =====================================
@st.cache_data
def load_data():

    # pages 폴더의 상위 폴더에서 CSV 찾기
    file_path = Path(__file__).resolve().parent.parent / "temperature.csv"

    if not file_path.exists():
        st.error("temperature.csv 파일을 찾을 수 없습니다.")
        st.stop()

    try:
        try:
            data = pd.read_csv(file_path, encoding="cp949")
        except UnicodeDecodeError:
            data = pd.read_csv(file_path, encoding="utf-8-sig")

        # 날짜 처리
        # 1907~1999년은 1900년대
        # 2000~2026년은 2000년대
        def convert_date(value):
            try:
                month_text, year_text = str(value).strip().split("-")
                yy = int(year_text)

                if yy >= 7:
                    year = 1900 + yy
                else:
                    year = 2000 + yy

                month = datetime.strptime(
                    month_text.title(), "%b"
                ).month

                return pd.Timestamp(year, month, 1)

            except Exception:
                return pd.NaT

        data["날짜"] = data["일시"].apply(convert_date)

        data = data.dropna(subset=["날짜"])

        data["연도"] = data["날짜"].dt.year
        data["월"] = data["날짜"].dt.month

        data["평균기온(℃)"] = pd.to_numeric(
            data["평균기온(℃)"],
            errors="coerce"
        )

        data = data.dropna(subset=["평균기온(℃)"])

        return data

    except Exception as e:
        st.error(f"데이터 처리 오류: {e}")
        st.stop()


df = load_data()

# =====================================
# 3. 데이터 확인
# =====================================
st.subheader("📁 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("전체 데이터 개수", f"{len(df):,}개")

with col2:
    st.metric("시작 연도", f"{df['연도'].min()}년")

with col3:
    st.metric("마지막 연도", f"{df['연도'].max()}년")

# =====================================
# 4. 월 및 예측 연도 선택
# =====================================
st.divider()
st.subheader("📌 분석 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "분석할 월을 선택하세요",
        range(1, 13),
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

# =====================================
# 5. 선택 월의 데이터 추출
# =====================================
month_df = df[df["월"] == selected_month].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.warning("분석할 데이터가 부족합니다.")
    st.stop()

X = month_df[["연도"]]
y = month_df["평균기온(℃)"]

# =====================================
# 6. 선형회귀 모델 학습
# =====================================
model = LinearRegression()

model.fit(X, y)

# 기존 데이터의 회귀 예측값
month_df["회귀예측값"] = model.predict(X)

# 미래 연도 예측
prediction = model.predict(
    pd.DataFrame({"연도": [int(selected_year)]})
)[0]

# 회귀식 정보
slope = model.coef_[0]
intercept = model.intercept_
r2 = model.score(X, y)

# =====================================
# 7. 그래프 데이터 생성
# =====================================
start_year = int(month_df["연도"].min())
end_year = max(
    int(month_df["연도"].max()),
    int(selected_year)
)

trend_years = np.arange(start_year, end_year + 1)

trend_predictions = model.predict(
    pd.DataFrame({"연도": trend_years})
)

# =====================================
# 8. 예측 결과
# =====================================
st.divider()
st.subheader(f"📊 {selected_month}월 기온 분석 결과")

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
        "결정계수 R²",
        f"{r2:.3f}"
    )

# =====================================
# 9. 그래프 생성
# =====================================
fig = go.Figure()

# 실제 평균기온
fig.add_trace(go.Scatter(
    x=month_df["연도"],
    y=month_df["평균기온(℃)"],
    mode="markers",
    name="실제 평균기온",
    marker=dict(
        color="#FF1493",
        size=8
    ),
    hovertemplate="%{x}년<br>실제 기온: %{y:.2f}℃<extra></extra>"
))

# 잔차 표시
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
    name="잔차",
    line=dict(
        color="gray",
        width=1,
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
    )
))

# 예측 기온
fig.add_trace(go.Scatter(
    x=[int(selected_year)],
    y=[prediction],
    mode="markers+text",
    name="예측 평균기온",
    marker=dict(
        color="#00BFFF",
        size=16,
        symbol="star"
    ),
    text=[f"{prediction:.2f}℃"],
    textposition="top center"
))

fig.update_layout(
    title=f"{selected_month}월 연도별 평균기온 및 미래 예측",
    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",
    template="plotly_white",
    height=600,
    hovermode="x unified",
    legend=dict(
        orientation="h",
        y=1.12,
        x=0.5,
        xanchor="center"
    )
)

fig.update_xaxes(
    dtick=5,
    showgrid=True
)

fig.update_yaxes(
    showgrid=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================
# 10. 선형회귀 알고리즘 설명
# =====================================
st.divider()

st.subheader("🧠 선형회귀 알고리즘 설명")

st.markdown("""
### ① 실제 데이터 수집

선택한 월에 해당하는 모든 연도의 평균기온 데이터를 수집합니다.

예를 들어 7월을 선택하면 1907년 7월부터
데이터에 존재하는 마지막 연도까지의 평균기온을 가져옵니다.

### ② 가장 적합한 직선 찾기

선형회귀는 과거 연도와 평균기온의 관계를 분석하여
실제 데이터와 가장 잘 맞는 직선을 찾습니다.
""")

st.latex(r"\hat{y} = ax+b")

st.markdown("""
- x : 연도
- ŷ : 예측 평균기온
- a : 기울기 (연간 기온 변화량)
- b : y절편

### ③ 오차 최소화

그래프의 회색 점선은 실제 기온과 회귀선의 차이를 나타냅니다.

이를 잔차라고 합니다.

선형회귀는 잔차를 제곱한 값들의 합이
최소가 되는 직선을 계산합니다.
""")

st.latex(
    r"\min \sum_{i=1}^{n}(y_i-\hat{y}_i)^2"
)

st.markdown("""
### ④ 미래 기온 예측

과거 데이터를 통해 계산한 직선에
사용자가 입력한 미래 연도를 대입합니다.

그 결과로 나온 값이 미래 평균기온 예측값입니다.

즉, 파란색 별표가 미래 기온 예측 결과입니다.
""")

# =====================================
# 11. 회귀 분석 상세 정보
# =====================================
st.divider()

st.subheader("📈 선형회귀 분석 상세 결과")

col1, col2 = st.columns(2)

with col1:

    st.markdown("**선형회귀 공식**")

    st.latex(
        rf"\hat{{y}} = {slope:.4f}x + ({intercept:.2f})"
    )

    st.write(f"기울기: {slope:.4f} ℃/년")

    if slope > 0:
        st.success("장기적인 기온 상승 경향")
    elif slope < 0:
        st.info("장기적인 기온 하락 경향")
    else:
        st.info("기온의 선형적인 변화가 거의 없음")

with col2:

    st.markdown("**모델 평가**")

    st.write(f"결정계수 R²: {r2:.4f}")

    st.write(f"학습 데이터: {len(month_df)}개")

    st.write(
        f"분석 기간: {start_year}년 ~ {month_df['연도'].max()}년"
    )

    if r2 >= 0.7:
        st.success("회귀선이 데이터의 경향을 비교적 잘 설명합니다.")
    elif r2 >= 0.4:
        st.warning("회귀선과 실제 데이터 사이에 차이가 있습니다.")
    else:
        st.info("선형회귀의 설명력이 낮습니다.")

# =====================================
# 12. 실제 데이터 표
# =====================================
st.divider()

with st.expander("📋 실제 기온 데이터 확인"):

    result_table = month_df[
        ["연도", "평균기온(℃)", "회귀예측값"]
    ].copy()

    result_table.columns = [
        "연도",
        "실제 평균기온(℃)",
        "회귀 예측기온(℃)"
    ]

    st.dataframe(
        result_table.round(2),
        use_container_width=True,
        hide_index=True
    )

# =====================================
# 13. 마무리
# =====================================
st.caption(
    "본 프로그램은 과거 평균기온을 바탕으로 "
    "선형회귀 알고리즘을 이용해 미래 기온을 예측합니다. "
    "실제 기상예보와는 차이가 발생할 수 있습니다."
)
