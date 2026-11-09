
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="연별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 연별 기온분석")
st.write("월을 선택하여 해당 월의 연도별 최고기온과 최저기온을 비교해 보세요.")

# ==========================================
# 2. CSV 파일 불러오기
# ==========================================
@st.cache_data
def load_data():

    # 한글 인코딩 자동 처리
    try:
        df = pd.read_csv(
            "temperature.csv",
            encoding="cp949"
        )
    except UnicodeDecodeError:
        df = pd.read_csv(
            "temperature.csv",
            encoding="utf-8-sig"
        )

    # 날짜 데이터 변환
    df["일시"] = pd.to_datetime(
        df["일시"],
        format="%b-%y",
        errors="coerce"
    )

    # 연도와 월 추출
    df["연도"] = df["일시"].dt.year
    df["월"] = df["일시"].dt.month

    # 기온 데이터 숫자형 변환
    df["최고기온(℃)"] = pd.to_numeric(
        df["최고기온(℃)"],
        errors="coerce"
    )

    df["최저기온(℃)"] = pd.to_numeric(
        df["최저기온(℃)"],
        errors="coerce"
    )

    # 날짜가 잘못된 데이터 제거
    df = df.dropna(subset=["일시"])

    return df


df = load_data()

# ==========================================
# 3. 월 선택
# ==========================================
month_names = {
    1: "1월",
    2: "2월",
    3: "3월",
    4: "4월",
    5: "5월",
    6: "6월",
    7: "7월",
    8: "8월",
    9: "9월",
    10: "10월",
    11: "11월",
    12: "12월"
}

selected_month = st.selectbox(
    "📅 분석할 월을 선택하세요",
    options=list(month_names.keys()),
    format_func=lambda x: month_names[x]
)

# ==========================================
# 4. 선택한 월의 데이터 추출
# ==========================================
monthly_df = df[
    df["월"] == selected_month
].copy()

# 연도순 정렬
monthly_df = monthly_df.sort_values("연도")

# ==========================================
# 5. 그래프 생성
# ==========================================
if monthly_df.empty:

    st.warning("선택한 월의 데이터가 없습니다.")

else:

    fig = go.Figure()

    # --------------------------------------
    # 최고기온 - 핫핑크
    # --------------------------------------
    fig.add_trace(
        go.Scatter(
            x=monthly_df["연도"],
            y=monthly_df["최고기온(℃)"],
            mode="lines+markers",
            name="최고기온",
            line=dict(
                color="#FF1493",
                width=3
            ),
            marker=dict(
                color="#FF1493",
                size=7
            ),
            connectgaps=False
        )
    )

    # --------------------------------------
    # 최저기온 - 연핑크
    # --------------------------------------
    fig.add_trace(
        go.Scatter(
            x=monthly_df["연도"],
            y=monthly_df["최저기온(℃)"],
            mode="lines+markers",
            name="최저기온",
            line=dict(
                color="#FFB6C1",
                width=3
            ),
            marker=dict(
                color="#FFB6C1",
                size=7
            ),
            connectgaps=False
        )
    )

    # ======================================
    # 6. 그래프 디자인
    # ======================================
    fig.update_layout(
        title={
            "text": "연별 기온분석",
            "x": 0.5,
            "xanchor": "center"
        },

        xaxis_title="연도",
        yaxis_title="온도(℃)",

        template="plotly_white",

        # 범례 표시
        showlegend=True,
        legend=dict(
            title="기온 구분",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),

        hovermode="x unified",
        height=550,

        font=dict(
            family="Malgun Gothic, Arial",
            size=14
        )
    )

    # 가로축: 연도
    fig.update_xaxes(
        title="연도",
        dtick=1,
        tickformat="d",
        showgrid=True
    )

    # 세로축: 온도
    fig.update_yaxes(
        title="온도(℃)",
        showgrid=True,
        zeroline=True
    )

    # ======================================
    # 7. 그래프 출력
    # ======================================
    st.subheader(
        f"📊 {month_names[selected_month]} 연도별 기온"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================
    # 8. 데이터 표 출력
    # ======================================
    st.subheader("📋 연도별 기온 데이터")

    result_df = monthly_df[
        ["연도", "최고기온(℃)", "최저기온(℃)"]
    ].copy()

    result_df["연도"] = result_df["연도"].astype(int)

    result_df = result_df.rename(
        columns={
            "최고기온(℃)": "최고기온 (℃)",
            "최저기온(℃)": "최저기온 (℃)"
        }
    )

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True
    )

    # ======================================
    # 9. CSV 다운로드
    # ======================================
    csv_data = result_df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        label="📥 분석 데이터 다운로드",
        data=csv_data,
        file_name=f"{selected_month}월_연별_기온분석.csv",
        mime="text/csv"
    )

# ==========================================
# 10. 데이터 출처
# ==========================================
st.divider()

st.caption(
    "데이터 출처: temperature.csv | "
    "분석 도구: Pandas, Plotly, Streamlit"
)
