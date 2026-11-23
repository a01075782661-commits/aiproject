
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
st.title("🏆 발롱도르 역대 기록 분석")
st.caption("Ballon d'Or Nominees & Winners")

st.markdown("""
원하는 연도를 입력하면 해당 연도의 후보 선수와 수상자를 확인하고,
입력한 연도부터 5년 동안 TOP 5에 가장 많이 진입한 선수도 분석합니다.
""")

# CSV 파일 경로
current_dir = Path(__file__).resolve().parent

possible_paths = [
    current_dir / "nominees.csv",
    current_dir.parent / "nominees.csv"
]

csv_path = next(
    (path for path in possible_paths if path.exists()),
    None
)

if csv_path is None:
    st.error("nominees.csv 파일을 찾을 수 없습니다.")
    st.stop()

# 데이터 불러오기
try:
    df = pd.read_csv(csv_path)
except Exception as e:
    st.error(f"CSV 파일 오류: {e}")
    st.stop()

# 필요한 열 확인
required_columns = [
    "Year", "Order", "Player",
    "Nationality", "Club", "Points"
]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해주세요.")
    st.stop()

# 데이터 정리
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Order"] = pd.to_numeric(df["Order"], errors="coerce")
df["Points"] = pd.to_numeric(df["Points"], errors="coerce")

df = df.dropna(subset=["Year", "Order", "Player"])

# 1956~2018년 데이터의 국적과 소속팀 열 교정
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

# 사용 가능한 연도
available_years = sorted(
    df["Year"].unique().astype(int)
)

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

    # ==================================
    # 1. 해당 연도 수상자 및 후보 조회
    # ==================================

    if selected_year.empty:
        st.warning(
            f"{year}년의 후보 데이터가 없습니다."
        )

    else:
        selected_year = selected_year.sort_values("Order")

        st.divider()
        st.header(f"🏆 {year}년 발롱도르 결과")

        # 수상자
        winner = selected_year[
            selected_year["Order"] == 1
        ]

        if not winner.empty:
            winner = winner.iloc[0]

            st.success(
                f"🥇 발롱도르 수상자: {winner['Player']}"
            )

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
        st.subheader(f"⚽ {year}년 후보 선수")

        st.write(
            f"총 **{len(selected_year)}명**의 후보가 있습니다."
        )

        display_df = selected_year[
            ["Order", "Player", "Club",
             "Nationality", "Points"]
        ].copy()

        display_df.columns = [
            "순위", "선수 이름", "소속팀",
            "국적", "득표수"
        ]

        display_df["득표수"] = display_df["득표수"].apply(
            lambda x: f"{x:,.0f}"
            if pd.notna(x) else "-"
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        # ==================================
        # 2. 상위 3명
        # ==================================

        st.subheader("🥇 해당 연도 TOP 3")

        top3 = selected_year.head(3)

        cols = st.columns(3)
        medals = ["🥇", "🥈", "🥉"]

        for i, (_, player) in enumerate(top3.iterrows()):
            with cols[i]:
                st.markdown(
                    f"### {medals[i]} {int(player['Order'])}위"
                )
                st.markdown(f"**{player['Player']}**")
                st.caption(f"소속팀: {player['Club']}")
                st.caption(f"국적: {player['Nationality']}")

    # ==================================
    # 3. 입력 연도부터 5년간 TOP 5 분석
    # ==================================

    st.divider()
    st.header("📊 5년간 TOP 5 진입 횟수 분석")

    start_year = int(year)
    end_year = start_year + 4

    st.info(
        f"분석 기간: **{start_year}년 ~ {end_year}년**"
    )

    # 5년간 데이터 추출
    five_year_df = df[
        (df["Year"] >= start_year) &
        (df["Year"] <= end_year) &
        (df["Order"] <= 5)
    ].copy()

    if five_year_df.empty:
        st.warning(
            "해당 기간에 TOP 5 진입 기록이 없습니다."
        )

    else:
        # 선수별 TOP 5 진입 횟수 계산
        player_stats = (
            five_year_df.groupby("Player")
            .agg(
                진입횟수=("Year", "count"),
                진입연도=(
                    "Year",
                    lambda x: ", ".join(
                        str(int(y))
                        for y in sorted(x.unique())
                    )
                ),
                소속팀=(
                    "Club",
                    lambda x: ", ".join(
                        sorted(set(x))
                    )
                )
            )
            .reset_index()
        )

        # 진입 횟수 순으로 정렬
        player_stats = player_stats.sort_values(
            ["진입횟수", "Player"],
            ascending=[False, True]
        ).reset_index(drop=True)

        # 최다 진입 횟수
        max_count = player_stats["진입횟수"].max()

        # 공동 1위 선수
        best_players = player_stats[
            player_stats["진입횟수"] == max_count
        ]

        st.subheader("👑 5년간 TOP 5 최다 진입 선수")

        st.write(
            f"**{start_year}~{end_year}년** 동안 "
            f"TOP 5에 가장 많이 진입한 선수입니다."
        )

        # 공동 1위 모두 표시
        cols = st.columns(min(len(best_players), 3))

        for i, (_, player) in enumerate(
            best_players.iterrows()
        ):
            with cols[i % len(cols)]:
                st.success(
                    f"🏆 {player['Player']}\n\n"
                    f"TOP 5 진입: {int(player['진입횟수'])}회"
                )

                st.caption(
                    f"진입 연도: {player['진입연도']}"
                )

                st.caption(
                    f"소속팀: {player['소속팀']}"
                )

        # ==================================
        # 4. 전체 선수별 진입 횟수
        # ==================================

        st.divider()
        st.subheader("📈 선수별 TOP 5 진입 기록")

        result_df = player_stats.copy()

        result_df.insert(
            0,
            "순위",
            result_df["진입횟수"].rank(
                method="min",
                ascending=False
            ).astype(int)
        )

        result_df.columns = [
            "순위",
            "선수 이름",
            "TOP 5 진입 횟수",
            "진입 연도",
            "소속팀"
        ]

        st.dataframe(
            result_df,
            use_container_width=True,
            hide_index=True
        )

        # ==================================
        # 5. 분석 정보
        # ==================================

        st.divider()
        st.subheader("📌 분석 정보")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "분석 기간",
                f"{start_year}~{end_year}"
            )

        with col2:
            st.metric(
                "분석된 선수 수",
                f"{len(player_stats)}명"
            )

        with col3:
            st.metric(
                "최다 진입 횟수",
                f"{max_count}회"
            )

        actual_years = sorted(
            five_year_df["Year"].unique().astype(int)
        )

        missing_years = [
            y for y in range(start_year, end_year + 1)
            if y not in actual_years
        ]

        st.caption(
            f"실제 데이터가 존재하는 연도: "
            f"{', '.join(map(str, actual_years))}"
        )

        if missing_years:
            st.warning(
                "다음 연도는 CSV에 기록이 없어 "
                f"분석에서 제외되었습니다: {', '.join(map(str, missing_years))}"
            )

# 하단
st.divider()

st.caption(
    "자료 출처: nominees.csv | "
    "TOP 5 기준: 발롱도르 순위 1~5위"
)
