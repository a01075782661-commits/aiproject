
import streamlit as st
import pandas as pd
from urllib.parse import quote

st.set_page_config(
    page_title="Seoul Explorer",
    page_icon="🗺️",
    layout="wide"
)

# 서울 관광지 데이터
places = [
    {
        "rank": 1, "name": "명동", "english": "Myeong-dong",
        "lat": 37.5636, "lon": 126.9850,
        "category": "쇼핑 · K-뷰티",
        "description": "화장품 매장, 패션 숍, 길거리 음식과 다양한 쇼핑을 즐길 수 있는 서울 대표 관광 거리예요.",
        "why": "외국인 방문객이 많이 찾는 대표 쇼핑 지역이에요.",
        "visitors": "일평균 약 100,910명"
    },
    {
        "rank": 2, "name": "N서울타워", "english": "N Seoul Tower",
        "lat": 37.5512, "lon": 126.9882,
        "category": "전망 · 랜드마크",
        "description": "남산 정상 부근에 있는 서울의 대표 전망 명소예요.",
        "why": "서울의 상징적인 랜드마크예요.",
        "visitors": "일평균 약 57,370명"
    },
    {
        "rank": 3, "name": "삼성역 · 코엑스", "english": "Samseong Station · COEX",
        "lat": 37.5125, "lon": 127.0590,
        "category": "쇼핑 · 문화",
        "description": "별마당도서관, 쇼핑몰, 아쿠아리움 등이 모여 있는 복합 문화 공간이에요.",
        "why": "쇼핑과 문화 체험을 한 번에 즐길 수 있어요.",
        "visitors": "일평균 약 46,813명"
    },
    {
        "rank": 4, "name": "강남역 일대", "english": "Gangnam Station",
        "lat": 37.4979, "lon": 127.0276,
        "category": "쇼핑 · 트렌드",
        "description": "패션 매장, 음식점, 카페가 모여 있는 활기찬 거리예요.",
        "why": "서울의 현대적인 도시 분위기를 경험하기 좋아요.",
        "visitors": "일평균 약 41,210명"
    },
    {
        "rank": 5, "name": "홍대", "english": "Hongdae",
        "lat": 37.5563, "lon": 126.9236,
        "category": "문화 · 공연",
        "description": "거리 공연, 음악, 예술과 개성 있는 상점이 있는 지역이에요.",
        "why": "한국의 대중문화와 거리 예술을 경험하기 좋아요.",
        "visitors": "일평균 약 40,213명"
    },
    {
        "rank": 6, "name": "경복궁", "english": "Gyeongbokgung Palace",
        "lat": 37.5796, "lon": 126.9770,
        "category": "역사 · 전통문화",
        "description": "조선 왕조의 대표 궁궐로 아름다운 전통 건축을 볼 수 있어요.",
        "why": "한국의 역사와 전통문화를 체험하기 좋아요."
    },
    {
        "rank": 7, "name": "북촌한옥마을", "english": "Bukchon Hanok Village",
        "lat": 37.5826, "lon": 126.9830,
        "category": "전통 · 거리 풍경",
        "description": "전통 한옥이 모여 있어 서울의 옛 골목 풍경을 느낄 수 있어요.",
        "why": "한국의 전통 주거 문화를 경험할 수 있어요.",
        "notice": "주민이 거주하는 공간이므로 조용히 관람해 주세요."
    },
    {
        "rank": 8, "name": "광장시장", "english": "Gwangjang Market",
        "lat": 37.5701, "lon": 126.9997,
        "category": "전통시장 · 음식",
        "description": "빈대떡, 김밥 등 다양한 한국 음식을 즐길 수 있는 전통시장이에요.",
        "why": "한국의 시장 문화와 먹거리를 경험하기 좋아요."
    },
    {
        "rank": 9, "name": "동대문디자인플라자", "english": "Dongdaemun Design Plaza",
        "lat": 37.5671, "lon": 127.0095,
        "category": "건축 · 디자인",
        "description": "독특한 건축물과 전시, 디자인 행사가 열리는 문화 공간이에요.",
        "why": "현대적인 건축과 디자인을 즐길 수 있어요."
    },
    {
        "rank": 10, "name": "남대문시장", "english": "Namdaemun Market",
        "lat": 37.5592, "lon": 126.9777,
        "category": "전통시장 · 쇼핑",
        "description": "오랜 역사를 가진 전통시장으로 다양한 상품과 먹거리가 있어요.",
        "why": "한국의 전통시장과 쇼핑 문화를 경험할 수 있어요."
    }
]

# 디자인
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #F1F5FF 0%, #FFFFFF 55%);
}
.hero {
    text-align: center;
    padding: 12px 0;
}
.hero h1 {
    color: #304A88;
    font-size: 38px;
    font-weight: 850;
}
.hero p {
    color: #5D6980;
    font-size: 17px;
}
.place-card {
    background: white;
    border: 1px solid #DCE4F2;
    border-radius: 15px;
    padding: 18px;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

# 메인 화면
st.markdown("""
<div class="hero">
<h1>🗺️ SEOUL EXPLORER 🇰🇷</h1>
<p>외국인 여행객을 위한 서울 인기 관광지 TOP 10</p>
</div>
""", unsafe_allow_html=True)

st.info("📍 지도에서 관광지 위치를 확인하고 원하는 장소를 선택해 보세요!")

df = pd.DataFrame(places)

map_col, info_col = st.columns([1.65, 1], gap="large")

# 지도
with map_col:
    st.subheader("📌 서울 관광 지도")

    st.map(
        df,
        latitude="lat",
        longitude="lon",
        color="#E4572E",
        size=100,
        zoom=11,
        use_container_width=True
    )

    st.caption("지도 위의 점을 눌러 위치를 확인할 수 있어요.")

# 관광지 정보
with info_col:
    st.subheader("🔎 관광지 자세히 보기")

    options = [
        f'{p["rank"]:02d}. {p["name"]} ({p["english"]})'
        for p in places
    ]

    selected = st.selectbox(
        "관광지를 선택하세요!",
        options
    )

    p = places[options.index(selected)]

    st.markdown('<div class="place-card">', unsafe_allow_html=True)

    st.subheader(f"⭐ {p['rank']}위 · {p['name']}")
    st.write(f"🌎 영어 이름: {p['english']}")
    st.write(f"🏷️ 테마: {p['category']}")

    st.markdown("### 📝 관광지 소개")
    st.write(p["description"])

    st.markdown("### 💡 추천 이유")
    st.write(p["why"])

    if p.get("visitors"):
        st.metric("2025년 일평균 외국인 유동인구", p["visitors"])

    if p.get("notice"):
        st.warning("🙏 관람 에티켓: " + p["notice"])

    st.markdown('</div>', unsafe_allow_html=True)

    query = quote(p["english"] + ", Seoul, South Korea")

    st.link_button(
        "🧭 Google Maps 길찾기",
        "https://www.google.com/maps/search/?api=1&query=" + query,
        use_container_width=True
    )

# 전체 관광지 목록
st.markdown("---")
st.subheader("🏙️ 서울 관광지 TOP 10")

for start in range(0, len(places), 2):
    cols = st.columns(2)

    for col, p in zip(cols, places[start:start + 2]):
        with col:
            st.markdown(f"""
            <div class="place-card">
                <b>#{p['rank']} · {p['name']}</b><br>
                <small>{p['english']} · {p['category']}</small><br><br>
                {p['description']}
            </div>
            """, unsafe_allow_html=True)

# 하단 설명
st.markdown("---")
st.subheader("📊 데이터 안내")

st.write("""
1~5위는 서울시의 2025년 외국인 일평균 유동인구 상위 지역 순서를 반영했어요.
6~10위는 서울의 대표적인 관광 명소를 추가한 추천 순위예요.
공식적인 전체 관광지 통합 순위는 아닙니다.
""")

st.markdown(
    "📚 참고 자료: [서울시 외국인 관광객 분석](https://english.seoul.go.kr/from-k-culture-to-k-hiking-foreign-tourists-venture-beyond-seouls-top-attractions/)"
)

st.caption("※ 방문객 수는 추정치이며 실시간 관광객 수가 아닙니다.")
