
import streamlit as st
import pandas as pd
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="발롱도르 기록 조회",
    page_icon="🏆",
    layout="wide"
)

# 제목
st.title("🏆 발롱도르 역대 후보 및 수상자 조회")
st.caption("Ballon d'Or Nominees & Winners")

st.markdown("""
원하는 연도를 입력하면 해당 연도의 발롱도르 후보 선수와
수상자, 소속팀, 국적, 득표수를 확인할 수 있습니다.
""")

# CSV 파일 경로 찾기
current_dir = Path(__file__).resolve().parent

possible_paths = [
    current_dir / "nominees.csv",
    current_dir.parent / "nominees.csv"
]

csv_path = next(
    (path for path in possible_paths if path.exists()),
    None
)

# 데이터 불러오기
if csv_path is None:
    st.error("nominees.csv 파일을 찾을 수 없습니다.")
    st.info("app.py와 nominees.csv 파일의 위치를 확인하세요.")
    st.stop()

try:
    df = pd.read_csv(csv_path)
except Exception as e:
    st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

# 필요한 열 확인
required_columns = [
    "Year", "Order", "Player",
    "Nationality", "Club", "Points"
]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름이 올바르지 않습니다.")
    st.stop()

# 데이터 정리
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Order"] = pd.to_numeric(df["Order"], errors="coerce")
df["Points"] = pd.to_numeric(df["Points"], errors="coerce")

df = df.dropna(subset=["Year", "Order", "Player"])

# 업로드된 CSV의 1956~2018년은
# Nationality와 Club 열의 값이 서로 바뀌어 있어 보정
old_years = df["Year"] <= 2018

df.loc[old_years, ["Nationality", "Club"]] = (
    df.loc[old_years, ["Club", "Nationality"]].values
)

# 문자열 정리
for col in ["Player", "Nationality", "Club"]:
    df[col] = (
        df[col]
        .fillna("정보 없음")
        .astype(str)
        .str.replace("\n", " ", regex=False)
        .str.strip()
    )

# 데이터에 존재하는 연도
available_years = sorted(df["Year"].unique().astype(int))

# 연도 입력
st.divider()
st.subheader("📅 조회할 연도 선택")

year = st.number_input(
    "발롱도르 연도를 입력하세요.",
    min_value=min(available_years),
    max_value=max(available_years),
    value=max(available_years),
    step=1
)

# 조회 버튼
if st.button("🔍 선수 조회하기", type="primary"):

    selected_year = df[df["Year"] == year].copy()

    if selected_year.empty:
        st.warning(
            f"{year}년의 후보 데이터가 없습니다. "
            "다른 연도를 입력해 주세요."
        )

    else:
        selected_year = selected_year.sort_values("Order")

        # 수상자
        winner = selected_year[
            selected_year["Order"] == 1
        ]

        st.divider()

        if not winner.empty:
            winner = winner.iloc[0]

            st.subheader(f"🏆 {year}년 발롱도르 수상자")

            st.success(f"🥇 {winner['Player']}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("수상자", winner["Player"])

            with col2:
                st.metric("소속팀", winner["Club"])

            with col3:
                st.metric(
                    "득표수",
                    f"{winner['Points']:,.0f}"
                    if pd.notna(winner["Points"])
                    else "정보 없음"
                )

        # 전체 후보
        st.divider()
        st.subheader(f"⚽ {year}년 발롱도르 후보 명단")

        st.write(
            f"총 **{len(selected_year)}명**의 선수가 후보에 올랐습니다."
        )

        display_df = selected_year[
            ["Order", "Player", "Club", "Nationality", "Points"]
        ].copy()

        display_df.columns = [
            "순위",
            "선수 이름",
            "소속팀",
            "국적",
            "득표수"
        ]

        display_df["득표수"] = display_df["득표수"].apply(
            lambda x: f"{x:,.0f}" if pd.notna(x) else "-"
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        # 순위별 선수 표시
        st.divider()
        st.subheader("🥇 상위 3명")

        top3 = selected_year.head(3)

        cols = st.columns(3)

        medals = ["🥇", "🥈", "🥉"]

        for i, (_, player) in enumerate(top3.iterrows()):
            with cols[i]:
                st.markdown(f"### {medals[i]} {int(player['Order'])}위")
                st.markdown(f"**{player['Player']}**")
                st.caption(f"소속팀: {player['Club']}")
                st.caption(f"국적: {player['Nationality']}")

# 하단 안내
st.divider()

st.caption(
    "자료 출처: 업로드된 nominees.csv | "
    "데이터에 포함된 연도만 조회할 수 있습니다."
)

