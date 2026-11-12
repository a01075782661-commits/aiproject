
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor

# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="기온 분석 및 AI 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 분석 및 예측")
st.write("3가지 회귀 알고리즘을 활용한 과거 기온 분석 및 미래 예측")

st.divider()


# =====================================
# 2. CSV 데이터 불러오기
# =====================================

@st.cache_data
def load_data():

    # pages 폴더의 상위 폴더에 있는 CSV
    file_path = Path(__file__).resolve().parent.parent / "temperature.csv"

    if not file_path.exists():
        st.error("temperature.csv 파일을 찾을 수 없습니다.")
        st.stop()

    try:
        try:
            data = pd.read_csv(file_path, encoding="cp949")
        except UnicodeDecodeError:
            data = pd.read_csv(file_path, encoding="utf-8-sig")

        # 연도 변환
        # Oct-07 = 1907년
        # Jan-08 = 1908년
        # Jan-00 = 2000년
        # 연도 숫자가 99에서 00으로 바뀌면 세기를 변경

        years = []
        months = []

        century = 1900
        previous_year = None

        for value in data["일시"]:

            try:
                month_text, year_text = str(value).strip().split("-")

                yy = int(year_text)

                if previous_year is not None and yy < previous_year:
                    century += 100

                full_year = century + yy

                from datetime import datetime

                month = datetime.strptime(
                    month_text.title(), "%b"
                ).month

                years.append(full_year)
                months.append(month)

                previous_year = yy

            except Exception:
                years.append(None)
                months.append(None)

        data["연도"] = years
        data["월"] = months

        data["연도"] = pd.to_numeric(
            data["연도"], errors="coerce"
        )

        data["월"] = pd.to_numeric(
            data["월"], errors="coerce"
        )

        data["평균기온(℃)"] = pd.to_numeric(
            data["평균기온(℃)"], errors="coerce"
        )

        data = data.dropna(
            subset=["연도", "월", "평균기온(℃)"]
        )

        data["연도"] = data["연도"].astype(int)
        data["월"] = data["월"].astype(int)

        # 같은 연도와 월의 데이터가 여러 개라면 평균 계산
        data = (
            data.groupby(["연도", "월"], as_index=False)
            ["평균기온(℃)"].mean()
        )

        return data

    except Exception as e:
        st.error(f"데이터 처리 오류: {e}")
        st.stop()


df = load_data()


# =====================================
# 3. 데이터 정보
# =====================================

st.subheader("📁 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("전체 데이터", f"{len(df):,}개")

with col2:
    st.metric("시작 연도", f"{df['연도'].min()}년")

with col3:
    st.metric("마지막 연도", f"{df['연도'].max()}년")


# =====================================
# 4. 사용자 입력
# =====================================

st.divider()
st.subheader("📌 분석 조건 선택")

col1, col2 = st.columns(2)

with col1:

    selected_month = st.selectbox(
        "분석할 월 선택",
        range(1, 13),
        format_func=lambda x: f"{x}월"
    )

with col2:

    selected_year = st.number_input(
        "예측할 연도 입력",
        min_value=1900,
        max_value=2100,
        value=int(df["연도"].max()) + 5,
        step=1
    )


# =====================================
# 5. 회귀 알고리즘 선택
# =====================================

st.divider()
st.subheader("🤖 회귀 알고리즘 선택")

algorithm_options = {
    "선형회귀 (Linear Regression)": "linear",
    "랜덤 포레스트 회귀 (Random Forest)": "random_forest",
    "그래디언트 부스팅 회귀 (Gradient Boosting)": "gradient_boosting"
}

selected_algorithm_name = st.selectbox(
    "사용할 회귀 알고리즘을 선택하세요",
    list(algorithm_options.keys())
)

selected_algorithm = algorithm_options[
    selected_algorithm_name
]


# =====================================
# 6. 선택한 월 데이터 추출
# =====================================

month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")

if len(month_df) < 2:
    st.warning("분석할 데이터가 부족합니다.")
    st.stop()

X = month_df[["연도"]]
y = month_df["평균기온(℃)"]


# =====================================
# 7. 세 가지 회귀 모델 생성
# =====================================

models = {

    "선형회귀 (Linear Regression)": LinearRegression(),

    "랜덤 포레스트 회귀 (Random Forest)": RandomForestRegressor(
        n_estimators=300,
        max_depth=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    ),

    "그래디언트 부스팅 회귀 (Gradient Boosting)": GradientBoostingRegressor(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=2,
        random_state=42
    )

}


# =====================================
# 8. 모델 학습 및 예측
# =====================================

start_year = int(month_df["연도"].min())
last_year = int(month_df["연도"].max())

end_year = max(
    last_year,
    int(selected_year)
)

trend_years = np.arange(
    start_year,
    end_year + 1
)

trend_X = pd.DataFrame({
    "연도": trend_years
})

prediction_X = pd.DataFrame({
    "연도": [int(selected_year)]
})

results = {}
prediction_values = {}
r2_values = {}

for name, model in models.items():

    # 모델 학습
    model.fit(X, y)

    # 전체 연도 추세 예측
    trend_values = model.predict(trend_X)

    # 미래 기온 예측
    future_value = model.predict(prediction_X)[0]

    # 학습 데이터 결정계수
    r2 = model.score(X, y)

    results[name] = {
        "model": model,
        "trend": trend_values,
        "prediction": future_value,
        "r2": r2
    }

    prediction_values[name] = future_value
    r2_values[name] = r2


# =====================================
# 9. 선택한 알고리즘 결과
# =====================================

selected_result = results[
    selected_algorithm_name
]

prediction = selected_result["prediction"]

st.divider()
st.subheader("📊 선택한 알고리즘의 예측 결과")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "선택한 알고리즘",
        selected_algorithm_name
    )

with col2:
    st.metric(
        "예측 연도",
        f"{selected_year}년"
    )

with col3:
    st.metric(
        "예측 평균기온",
        f"{prediction:.2f} ℃"
    )


# =====================================
# 10. 그래프 생성
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
    hovertemplate=
    "%{x}년<br>실제 기온: %{y:.2f}℃<extra></extra>"
))


# 알고리즘별 색상
model_colors = {
    "선형회귀 (Linear Regression)": "#2563EB",
    "랜덤 포레스트 회귀 (Random Forest)": "#16A34A",
    "그래디언트 부스팅 회귀 (Gradient Boosting)": "#EA580C"
}


# 세 알고리즘의 추세선
for name, result in results.items():

    is_selected = (name == selected_algorithm_name)

    fig.add_trace(go.Scatter(

        x=trend_years,
        y=result["trend"],

        mode="lines",

        name=(
            f"{name} ★ 선택"
            if is_selected
            else name
        ),

        line=dict(
            color=model_colors[name],
            width=4 if is_selected else 2,
            dash="solid" if is_selected else "dash"
        ),

        opacity=1 if is_selected else 0.7,

        hovertemplate=
        "%{x}년<br>예측 기온: %{y:.2f}℃<extra></extra>"

    ))


# 알고리즘별 미래 예측 지점
for name, result in results.items():

    is_selected = (name == selected_algorithm_name)

    fig.add_trace(go.Scatter(

        x=[int(selected_year)],
        y=[result["prediction"]],

        mode="markers+text" if is_selected else "markers",

        name=f"{name} 예측값",

        marker=dict(
            color=model_colors[name],
            size=16 if is_selected else 10,
            symbol="star" if is_selected else "circle"
        ),

        text=[
            f"{result['prediction']:.2f}℃"
        ] if is_selected else None,

        textposition="top center",

        hovertemplate=
        f"{name}<br>%{{x}}년<br>예측 기온: %{{y:.2f}}℃<extra></extra>"

    ))


# 그래프 디자인
fig.update_layout(

    title=dict(
        text=f"{selected_month}월 평균기온 및 알고리즘별 예측 비교",
        x=0.5
    ),

    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",

    template="plotly_white",

    height=650,

    hovermode="x unified",

    legend=dict(
        orientation="h",
        y=1.15,
        x=0.5,
        xanchor="center"
    ),

    margin=dict(
        l=30,
        r=30,
        t=120,
        b=50
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
# 11. 알고리즘별 예측값 비교
# =====================================

st.divider()

st.subheader("🔍 알고리즘별 예측값 비교")

comparison_df = pd.DataFrame({

    "회귀 알고리즘": list(prediction_values.keys()),

    "예측 평균기온(℃)": [
        round(value, 2)
        for value in prediction_values.values()
    ],

    "학습 데이터 R²": [
        round(value, 4)
        for value in r2_values.values()
    ]

})

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)

# 알고리즘별 예측 차이
max_prediction = max(prediction_values.values())
min_prediction = min(prediction_values.values())

st.metric(
    "알고리즘 간 예측값 최대 차이",
    f"{max_prediction - min_prediction:.2f} ℃"
)


# =====================================
# 12. 선택한 알고리즘의 상세 정보
# =====================================

st.divider()

st.subheader("🧠 회귀 알고리즘 작동 원리")

if selected_algorithm == "linear":

    st.markdown("""
    ### 선형회귀 (Linear Regression)

    선형회귀는 과거 연도와 평균기온 사이의 관계를 분석하여
    가장 적합한 직선을 찾는 알고리즘입니다.

    **작동 과정**

    1. 과거 연도별 평균기온 데이터를 수집합니다.
    2. 실제 데이터와 가장 가까운 직선을 계산합니다.
    3. 직선과 실제 기온 사이의 오차 제곱합을 최소화합니다.
    4. 미래 연도를 직선에 대입하여 기온을 예측합니다.
    """)

    st.latex(r"\hat{y}=ax+b")

    st.markdown("""
    - a : 기울기
    - b : y절편
    - x : 연도
    - ŷ : 예측 평균기온

    그래프에서는 파란색 실선으로 표시됩니다.
    """)

elif selected_algorithm == "random_forest":

    st.markdown("""
    ### 랜덤 포레스트 회귀 (Random Forest Regression)

    랜덤 포레스트는 여러 개의 의사결정나무를 만들어
    각각의 예측 결과를 결합하는 알고리즘입니다.

    **작동 과정**

    1. 원본 데이터에서 여러 학습용 표본을 만듭니다.
    2. 각 표본을 이용하여 여러 의사결정나무를 학습합니다.
    3. 각각의 나무가 평균기온을 예측합니다.
    4. 여러 나무의 예측 결과를 평균하여 최종 예측값을 만듭니다.

    **특징**

    - 데이터의 복잡한 패턴을 학습할 수 있습니다.
    - 여러 나무의 결과를 결합하여 예측합니다.
    - 직선이 아닌 구간별 형태의 예측 결과가 나올 수 있습니다.

    그래프에서는 초록색 점선으로 표시됩니다.
    """)

    st.latex(
        r"\hat{y}=\frac{1}{N}\sum_{i=1}^{N}T_i(x)"
    )

    st.caption(
        "T는 각각의 의사결정나무 예측값이며 N은 나무의 개수입니다."
    )

elif selected_algorithm == "gradient_boosting":

    st.markdown("""
    ### 그래디언트 부스팅 회귀 (Gradient Boosting Regression)

    그래디언트 부스팅은 여러 개의 약한 예측 모델을
    순차적으로 학습시키며 이전 모델의 오차를 보완하는 알고리즘입니다.

    **작동 과정**

    1. 첫 번째 모델이 평균기온을 예측합니다.
    2. 실제 기온과 예측 기온 사이의 오차를 계산합니다.
    3. 다음 모델이 이전 모델의 오차를 보완하도록 학습합니다.
    4. 여러 모델의 결과를 합쳐 최종 예측값을 만듭니다.

    **특징**

    - 이전 모델의 오차를 지속적으로 보완합니다.
    - 복잡한 데이터 패턴을 학습할 수 있습니다.
    - 학습 설정에 따라 예측 결과가 달라집니다.

    그래프에서는 주황색 점선으로 표시됩니다.
    """)

    st.latex(
        r"F_m(x)=F_{m-1}(x)+\eta h_m(x)"
    )

    st.caption(
        "F는 현재 예측 모델, h는 새롭게 학습한 모델, η는 학습률입니다."
    )


# =====================================
# 13. 모델 비교 시 주의사항
# =====================================

st.divider()

st.subheader("⚠️ 알고리즘별 예측 차이에 대한 설명")

st.markdown("""
세 알고리즘은 데이터를 학습하는 방법이 서로 다르기 때문에
동일한 연도를 입력해도 예측 결과가 달라질 수 있습니다.

특히 랜덤 포레스트와 그래디언트 부스팅은
의사결정나무 기반 알고리즘입니다.

이 두 알고리즘은 학습 데이터의 연도 범위를 벗어난 미래를
예측할 때 새로운 추세를 계속 연장하지 못하고
마지막 학습 구간의 예측값에 가까워지는 특성이 있습니다.

반면 선형회귀는 직선의 추세를 미래까지 연장합니다.

따라서 미래 예측값이 서로 다르다고 해서
무조건 어느 한 알고리즘이 더 정확하다는 의미는 아닙니다.
실제 예측 성능은 과거 데이터를 나누어 별도로 검증해야 합니다.
""")


# =====================================
# 14. 실제 데이터 확인
# =====================================

st.divider()

with st.expander("📋 선택한 월의 실제 기온 데이터"):

    st.dataframe(
        month_df[
            ["연도", "평균기온(℃)"]
        ],
        use_container_width=True,
        hide_index=True
    )


# =====================================
# 15. 마무리
# =====================================

st.caption(
    "본 프로그램은 과거 평균기온 데이터를 이용한 "
    "선형회귀, 랜덤 포레스트, 그래디언트 부스팅 "
    "모델의 예측 결과를 비교합니다. "
    "실제 미래 기온과 차이가 발생할 수 있습니다."
)
