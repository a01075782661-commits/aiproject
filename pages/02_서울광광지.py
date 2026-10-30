
import streamlit as st
import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(
    page_title="Seoul Tourism Map",
    page_icon="🗺️",
    layout="wide"
)

# 제목
st.title("🗺️ Discover Seoul")
st.subheader("서울의 인기 관광지 TOP 10")
st.write(
    "서울을 방문하는 외국인 관광객을 위한 주요 관광지를 소개합니다."
)

# 관광지 데이터
places = [
    {
        "name": "명동",
        "english": "Myeongdong",
        "lat": 37.5636,
        "lon": 126.9869,
        "description": "쇼핑과 K-뷰티, 길거리 음식으로 유명한 서울의 대표 관광지입니다.",
        "category": "쇼핑"
    },
    {
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "description": "서울의 아름다운 전경을 감상할 수 있는 대표적인 전망 명소입니다.",
        "category": "전망"
    },
    {
        "name": "코엑스",
        "english": "COEX",
        "lat": 37.5125,
        "lon": 127.0588,
        "description": "대형 쇼핑몰과 별마당도서관이 있는 복합문화공간입니다.",
        "category": "쇼핑·문화"
    },
    {
        "name": "강남역",
        "english": "Gangnam Station",
        "lat": 37.4979,
        "lon": 127.0276,
        "description": "다양한 상점과 음식점, 카페가 모여 있는 활기찬 거리입니다.",
        "category": "쇼핑·문화"
    },
    {
        "name": "홍대",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "description": "거리 공연과 음악, 패션, 예술을 즐길 수 있는 젊음의 거리입니다.",
        "category": "문화·예술"
    },
    {
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "description": "조선 왕조의 대표 궁궐로 한국의 전통문화를 경험할 수 있습니다.",
        "category": "역사·문화"
    },
    {
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "description": "전통 한옥이 모여 있는 아름다운 마을입니다. 주민들을 배려해 방문해야 합니다.",
        "category": "전통·문화"
    },
    {
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5701,
        "lon": 126.9997,
        "description": "빈대떡과 마약김밥 등 다양한 한국 전통 음식을 맛볼 수 있습니다.",
        "category": "음식"
    },
    {
        "name": "동대문디자인플라자",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5674,
        "lon": 127.0095,
        "description": "독특한 건축물과 전시, 디자인 행사를 즐길 수 있는 공간입니다.",
        "category": "건축·문화"
    },
    {
        "name": "남대문시장",
        "english": "Namdaemun Market",
        "lat": 37.5592,
        "lon": 126.9777,
        "description": "다양한 상품과 먹거리를 판매하는 서울의 대표 전통시장입니다.",
        "category": "쇼핑·음식"
    }
]

# 사이드바
st.sidebar.header("🔎 관광지 검색")

place_names = [place["name"] for place in places]

selected_name = st.sidebar.selectbox(
    "관광지를 선택하세요",
    place_names
)

selected_place = next(
    place for place in places
    if place["name"] == selected_name
)

# 선택한 관광지 정보
st.sidebar.markdown("---")
st.sidebar.subheader("📍 선택한 관광지")
st.sidebar.write(f"**이름:** {selected_place['name']}")
st.sidebar.write(f"**영문명:** {selected_place['english']}")
st.sidebar.write(f"**종류:** {selected_place['category']}")
st.sidebar.write(selected_place["description"])

# Google 지도 링크
google_map_url = (
    "https://www.google.com/maps/search/?api=1&query="
    f"{selected_place['lat']},{selected_place['lon']}"
)

st.sidebar.link_button(
    "Google 지도에서 보기",
    google_map_url
)

# 지도 생성
seoul_map = folium.Map(
    location=[
        selected_place["lat"],
        selected_place["lon"]
    ],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# 관광지 마커 추가
for place in places:

    # 선택한 관광지는 빨간색, 나머지는 파란색
    if place["name"] == selected_name:
        marker_color = "red"
    else:
        marker_color = "blue"

    # 마커 팝업 내용
    popup_html = f"""
    <div style="width:220px;">
        <h4>{place['name']}</h4>
        <p><b>{place['english']}</b></p>
        <p>{place['description']}</p>
        <p>분류: {place['category']}</p>
    </div>
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=place["name"],
        icon=folium.Icon(
            color=marker_color,
            icon="info-sign"
        )
    ).add_to(seoul_map)

# 지도 표시
st.markdown("### 📌 서울 주요 관광지 지도")

st_folium(
    seoul_map,
    width=None,
    height=600,
    use_container_width=True
)

# 관광지 목록
st.markdown("---")
st.markdown("### 🏙️ 서울 관광지 TOP 10")

# 2열로 관광지 정보 표시
col1, col2 = st.columns(2)

for index, place in enumerate(places):

    target_col = col1 if index % 2 == 0 else col2

    with target_col:
        with st.container(border=True):
            st.markdown(
                f"**{index + 1}. {place['name']}**"
            )
            st.caption(place["english"])
            st.write(place["description"])
            st.caption(f"분류: {place['category']}")

# 안내
st.markdown("---")
st.caption(
    "※ 관광지 목록은 서울의 대표적인 명소를 소개하기 위한 편집 목록이며, "
    "공식적인 외국인 방문객 순위는 아닙니다."
)
