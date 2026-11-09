
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

st.write(
    "원하는 월을 선택하면 1907년부터 2026년까지 "
    "해당 월의 최고기온과 최저기온을 비교할 수 있습니다."
)

# ==========================================
# 2. CSV 파일 불러오기
# ==========================================
@st.cache_data
def load_data():

    # 한글 인코딩 처리
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

    # --------------------------------------
    # 날짜 데이터 처리
    # --------------------------------------

    # 날짜 형식 예시: Oct-07, Nov-07, Jan-08
    date_parts = df["일시"].astype(str).str.split(
        "-",
        expand=True
    )

    # 월 이름을 숫자로 변환
    month_dict = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    }

    df["월"] = date_parts[0].map(month_dict)

    # --------------------------------------
    # 연도 계산
    # --------------------------------------

    # 데이터의 첫 연도는 1907년
    start_year = 1907

    # 월 정보가 정상적으로 변환된 행만 사용
    df = df.dropna(subset=["월"]).copy()

    # 월 숫자형 변환
    df["월"] = df["월"].astype(int)

    # 월이 이전 달보다 작아지는 순간
    # 새로운 연도가 시작된 것으로 판단
    month_change = df["월"].diff()

    year_change = (
        month_change < 0
    ).fillna(False)

    # 연도 변경 누적 계산
    year_count = year_change.cumsum()

    # 1907년부터 순서대로 연도 생성
    df["연도"] = start_year + year_count

    # 날짜 생성
    df["일시"] = pd.to_datetime(
        dict(
            year=df["연도"],
            month=df["월"],
            day=1
        ),
        errors="coerce"
    )

    # --------------------------------------
    # 기온 데이터 숫자형 변환
    # --------------------------------------

    temperature_columns = [
        "평균기온(℃)",
        "평균최고기온(℃)",
        "최고기온(℃)",
        "평균최저기온(℃)",
        "최저기온(℃)"
    ]

    for col in temperature_columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # 날짜 오류 제거
    df = df.dropna(
        subset=["일시"]
    )

    # 연도순 정렬
    df = df.sort_values(
        ["연도", "월"]
    )

    return df


# 데이터 불러오기
df = load_data()

# ==========================================
# 3. 데이터 기간 확인
# ==========================================
min_year = int(df["연도"].min())
max_year = int(df["연도"].max())

st.caption(
    f"분석 데이터 기간: {min_year}년 ~ {max_year}년"
)

# ==========================================
# 4. 월 선택
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
    format_func=lambda x: month_names[x],
    index=0
)

# ==========================================
# 5. 선택한 월 데이터 추출
# ==========================================
monthly_df = df[
    df["월"] == selected_month
].copy()

# 연도순 정렬
monthly_df = monthly_df.sort_values(
    "연도"
)

# ==========================================
# 6. 그래프 생성
# ==========================================
if monthly_df.empty:

    st.warning(
        "선택한 월의 데이터가 없습니다."
    )

else:

    fig = go.Figure()

    # --------------------------------------
    # 최고기온 그래프 - 핫핑크
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
                size=6
            ),

            connectgaps=False,

            hovertemplate=(
                "연도: %{x}년<br>"
                "최고기온: %{y:.1f}℃"
                "<extra></extra>"
            )
        )
    )

    # --------------------------------------
    # 최저기온 그래프 - 연핑크
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
                size=6
            ),

            connectgaps=False,

            hovertemplate=(
                "연도: %{x}년<br>"
                "최저기온: %{y:.1f}℃"
                "<extra></extra>"
            )
        )
    )

    # ======================================
    # 7. 그래프 디자인
    # ======================================
    fig.update_layout(

        # 그래프 제목
        title=dict(
            text="연별 기온분석",
            x=0.5,
            xanchor="center"
        ),

        # 축 제목
        xaxis_title="연도",
        yaxis_title="온도(℃)",

        # 그래프 배경
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

        # 마우스를 올렸을 때 정보 표시
        hovermode="x unified",

        # 그래프 높이
        height=550,

        # 글꼴
        font=dict(
            family="Malgun Gothic, Arial",
            size=14
        ),

        # 여백
        margin=dict(
            l=60,
            r=30,
            t=100,
            b=60
        )
    )

    # --------------------------------------
    # 가로축 설정
    # --------------------------------------
    fig.update_xaxes(

        title="연도",

        # 5년 간격으로 표시
        dtick=5,

        tickformat="d",

        showgrid=True,

        # 시작과 끝 연도 설정
        range=[
            min_year,
            max_year
        ]
    )

    # --------------------------------------
    # 세로축 설정
    # --------------------------------------
    fig.update_yaxes(

        title="온도(℃)",

        showgrid=True,

        zeroline=True
    )

    # ======================================
    # 8. 그래프 출력
    # ======================================
    st.subheader(
        f"📊 {month_names[selected_month]} 기온 변화"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================
    # 9. 연도별 기온 데이터 표
    # ======================================
    st.subheader(
        "📋 연도별 기온 데이터"
    )

    result_df = monthly_df[
        [
            "연도",
            "최고기온(℃)",
            "최저기온(℃)"
        ]
    ].copy()

    result_df["연도"] = (
        result_df["연도"].astype(int)
    )

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
    # 10. CSV 다운로드
    # ======================================
    csv_data = result_df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        label="📥 분석 결과 CSV 다운로드",

        data=csv_data,

        file_name=(
            f"{selected_month}월_연별_기온분석.csv"
        ),

        mime="text/csv"
    )

# ==========================================
# 11. 데이터 출처
# ==========================================
st.divider()

st.caption(
    "데이터 출처: temperature.csv | "
    "분석 도구: Pandas, Plotly, Streamlit"
)
