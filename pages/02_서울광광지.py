
import streamlit as st
import folium
from streamlit_folium import st_folium
from urllib.parse import quote

# -----------------------------------
# 1. 페이지 설정
# -----------------------------------
st.set_page_config(
    page_title="Seoul 1 Night 2 Days Tour",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Discover Seoul")
st.subheader("서울 주요 관광지 1박 2일 여행 코스")
st.write(
    "외국인 관광객을 위한 서울 대표 관광지 10곳과 "
    "식당, 호텔을 함께 소개하는 여행 일정입니다."
)

st.info(
    "여행 시간: 1일 차 09:00~19:00 / 2일 차 09:00~19:00  "
    "이동 시간은 교통 상황에 따라 달라질 수 있습니다."
)

# -----------------------------------
# 2. 링크 생성 함수
# -----------------------------------
def google_maps_link(place_name):
    query = quote(place_name + " Seoul")
    return (
        "https://www.google.com/maps/search/"
        "?api=1&query=" + query
    )


# -----------------------------------
# 3. 관광지 데이터
# -----------------------------------
places = [
    {
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "day": 1,
        "description": "조선 왕조의 대표 궁궐로 한국의 역사와 전통문화를 경험할 수 있습니다."
    },
    {
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "day": 1,
        "description": "전통 한옥이 모여 있는 마을로 한국의 옛 주거문화를 볼 수 있습니다."
    },
    {
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5701,
        "lon": 126.9997,
        "day": 1,
        "description": "빈대떡, 김밥 등 한국의 다양한 시장 음식을 즐길 수 있습니다."
    },
    {
        "name": "동대문디자인플라자",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5674,
        "lon": 127.0095,
        "day": 1,
        "description": "독특한 건축 디자인과 전시, 문화행사를 즐길 수 있는 공간입니다."
    },
    {
        "name": "남대문시장",
        "english": "Namdaemun Market",
        "lat": 37.5592,
        "lon": 126.9777,
        "day": 1,
        "description": "다양한 상품과 먹거리를 판매하는 서울의 대표 전통시장입니다."
    },
    {
        "name": "명동",
        "english": "Myeongdong",
        "lat": 37.5636,
        "lon": 126.9869,
        "day": 1,
        "description": "쇼핑과 K-뷰티, 길거리 음식으로 유명한 서울의 대표 관광지입니다."
    },
    {
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "day": 2,
        "description": "남산 정상에서 서울의 전경을 감상할 수 있는 대표 전망 명소입니다."
    },
    {
        "name": "홍대",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "day": 2,
        "description": "거리 공연과 음악, 패션, 예술을 즐길 수 있는 젊음의 거리입니다."
    },
    {
        "name": "강남역",
        "english": "Gangnam Station",
        "lat": 37.4979,
        "lon": 127.0276,
        "day": 2,
        "description": "다양한 상점과 카페, 음식점이 모여 있는 서울의 대표 번화가입니다."
    },
    {
        "name": "코엑스",
        "english": "COEX",
        "lat": 37.5125,
        "lon": 127.0588,
        "day": 2,
        "description": "별마당도서관과 쇼핑몰, 전시시설을 즐길 수 있는 복합문화공간입니다."
    }
]


# -----------------------------------
# 4. 식당 데이터
# -----------------------------------
restaurants = [
    {
        "name": "미성옥",
        "english": "Miseong-og",
        "meal": "아침",
        "day": 1,
        "lat": 37.5630,
        "lon": 126.9855,
        "description": "맑고 진한 설렁탕을 맛볼 수 있는 명동의 오래된 한식 식당입니다."
    },
    {
        "name": "광장시장 먹거리",
        "english": "Gwangjang Market Food",
        "meal": "점심",
        "day": 1,
        "lat": 37.5701,
        "lon": 126.9997,
        "description": "빈대떡, 마약김밥 등 다양한 한국 시장 음식을 맛볼 수 있습니다."
    },
    {
        "name": "왕비집 명동본점",
        "english": "Wangbijip Myeongdong",
        "meal": "저녁",
        "day": 1,
        "lat": 37.5630,
        "lon": 126.9850,
        "description": "갈비와 다양한 고기 메뉴를 즐길 수 있는 한국식 고깃집입니다."
    },
    {
        "name": "미성옥",
        "english": "Miseong-og",
        "meal": "아침",
        "day": 2,
        "lat": 37.5630,
        "lon": 126.9855,
        "description": "둘째 날에도 이용하기 좋은 명동의 설렁탕 식당입니다."
    },
    {
        "name": "신미경 홍대닭갈비",
        "english": "Shin Mi Kyung Hongdae Dakgalbi",
        "meal": "점심",
        "day": 2,
        "lat": 37.5560,
        "lon": 126.9250,
        "description": "치즈 닭갈비와 볶음밥을 즐길 수 있는 홍대의 닭갈비 전문점입니다."
    },
    {
        "name": "솥내음 코엑스점",
        "english": "Sotnaeum COEX",
        "meal": "저녁",
        "day": 2,
        "lat": 37.5125,
        "lon": 127.0588,
        "description": "다양한 재료를 올린 솥밥을 맛볼 수 있는 코엑스몰 안의 식당입니다."
    }
]


# -----------------------------------
# 5. 호텔 데이터
# -----------------------------------
hotels = [
    {
        "name": "솔라리아 니시테츠 호텔 서울 명동",
        "english": "Solaria Nishitetsu Hotel Seoul Myeongdong",
        "lat": 37.5635,
        "lon": 126.9858,
        "description": "명동 중심부에 위치해 쇼핑과 관광, 대중교통 이용에 편리한 호텔입니다."
    },
    {
        "name": "호텔28 명동",
        "english": "Hotel 28 Myeongdong",
        "lat": 37.5643,
        "lon": 126.9845,
        "description": "명동 쇼핑거리와 가까운 부티크 호텔입니다."
    },
    {
        "name": "스탠포드 호텔 명동",
        "english": "Stanford Hotel Myeongdong",
        "lat": 37.5640,
        "lon": 126.9805,
        "description": "명동과 남대문 일대 이동에 편리한 도심형 호텔입니다."
    }
]


# -----------------------------------
# 6. 관광 일정 데이터
# -----------------------------------
day1_schedule = [
    {
        "시간": "09:00~09:45",
        "일정": "아침 식사",
        "장소": "미성옥",
        "활동": "설렁탕으로 아침 식사",
        "이동": "도보"
    },
    {
        "시간": "09:45~10:15",
        "일정": "이동",
        "장소": "경복궁",
        "활동": "명동에서 경복궁으로 이동",
        "이동": "지하철 또는 버스"
    },
    {
        "시간": "10:15~11:30",
        "일정": "관광 1",
        "장소": "경복궁",
        "활동": "궁궐 관람 및 사진 촬영",
        "이동": "도보"
    },
    {
        "시간": "11:30~12:15",
        "일정": "관광 2",
        "장소": "북촌한옥마을",
        "활동": "한옥 거리 산책",
        "이동": "도보"
    },
    {
        "시간": "12:15~12:45",
        "일정": "이동",
        "장소": "광장시장",
        "활동": "시장으로 이동",
        "이동": "대중교통"
    },
    {
        "시간": "12:45~13:45",
        "일정": "점심 식사",
        "장소": "광장시장",
        "활동": "빈대떡, 김밥 등 시장 음식",
        "이동": "도보"
    },
    {
        "시간": "13:45~14:15",
        "일정": "이동",
        "장소": "동대문디자인플라자",
        "활동": "DDP로 이동",
        "이동": "도보 또는 대중교통"
    },
    {
        "시간": "14:15~15:15",
        "일정": "관광 3",
        "장소": "동대문디자인플라자",
        "활동": "건축물 관람 및 사진 촬영",
        "이동": "도보"
    },
    {
        "시간": "15:15~15:45",
        "일정": "이동",
        "장소": "남대문시장",
        "활동": "남대문시장으로 이동",
        "이동": "지하철"
    },
    {
        "시간": "15:45~16:30",
        "일정": "관광 4",
        "장소": "남대문시장",
        "활동": "전통시장 구경",
        "이동": "도보"
    },
    {
        "시간": "16:30~17:00",
        "일정": "이동",
        "장소": "명동",
        "활동": "명동으로 이동",
        "이동": "도보 또는 대중교통"
    },
    {
        "시간": "17:00~18:00",
        "일정": "관광 5",
        "장소": "명동",
        "활동": "쇼핑 및 거리 구경",
        "이동": "도보"
    },
    {
        "시간": "18:00~19:00",
        "일정": "저녁 식사",
        "장소": "왕비집 명동본점",
        "활동": "한국식 고기 요리",
        "이동": "도보"
    }
]


day2_schedule = [
    {
        "시간": "09:00~09:40",
        "일정": "아침 식사",
        "장소": "미성옥",
        "활동": "설렁탕으로 아침 식사",
        "이동": "도보"
    },
    {
        "시간": "09:40~10:20",
        "일정": "이동",
        "장소": "N서울타워",
        "활동": "남산으로 이동",
        "이동": "버스 또는 케이블카"
    },
    {
        "시간": "10:20~11:20",
        "일정": "관광 6",
        "장소": "N서울타워",
        "활동": "전망대와 남산 주변 관람",
        "이동": "도보"
    },
    {
        "시간": "11:20~12:10",
        "일정": "이동",
        "장소": "홍대",
        "활동": "홍대입구역으로 이동",
        "이동": "지하철"
    },
    {
        "시간": "12:10~13:10",
        "일정": "점심 식사",
        "장소": "신미경 홍대닭갈비",
        "활동": "닭갈비와 볶음밥",
        "이동": "도보"
    },
    {
        "시간": "13:10~14:10",
        "일정": "관광 7",
        "장소": "홍대",
        "활동": "거리 구경 및 쇼핑",
        "이동": "도보"
    },
    {
        "시간": "14:10~15:00",
        "일정": "이동",
        "장소": "강남역",
        "활동": "강남으로 이동",
        "이동": "지하철"
    },
    {
        "시간": "15:00~16:00",
        "일정": "관광 8",
        "장소": "강남역",
        "활동": "강남 거리와 상점 구경",
        "이동": "도보"
    },
    {
        "시간": "16:00~16:30",
        "일정": "이동",
        "장소": "코엑스",
        "활동": "삼성역으로 이동",
        "이동": "지하철"
    },
    {
        "시간": "16:30~18:00",
        "일정": "관광 9",
        "장소": "코엑스",
        "활동": "별마당도서관 및 쇼핑몰 관람",
        "이동": "도보"
    },
    {
        "시간": "18:00~19:00",
        "일정": "저녁 식사",
        "장소": "솥내음 코엑스점",
        "활동": "한국식 솥밥 식사",
        "이동": "도보"
    }
]

# 일정에 10개 관광지가 모두 포함되도록 표시
# 강남역과 코엑스는 별도 관광지로 계산


# -----------------------------------
# 7. Folium 지도 생성
# -----------------------------------
st.markdown("---")
st.header("📍 서울 관광 코스 지도")

seoul_map = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=11,
    tiles="OpenStreetMap"
)

# 관광지 레이어
tourist_layer = folium.FeatureGroup(
    name="관광지 10곳",
    show=True
)

for index, place in enumerate(places, start=1):

    popup_text = f"""
    <div style="width:220px;">
        <h4>{index}. {place['name']}</h4>
        <p>{place['english']}</p>
        <p>{place['description']}</p>
        <p><b>{place['day']}일 차 일정</b></p>
    </div>
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=place["name"],
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(
            color="blue" if place["day"] == 1 else "purple",
            icon="camera",
            prefix="fa"
        )
    ).add_to(tourist_layer)

tourist_layer.add_to(seoul_map)


# 식당 레이어
restaurant_layer = folium.FeatureGroup(
    name="추천 식당",
    show=True
)

for restaurant in restaurants:

    popup_text = f"""
    <div style="width:220px;">
        <h4>{restaurant['name']}</h4>
        <p>{restaurant['english']}</p>
        <p>{restaurant['day']}일 차 {restaurant['meal']} 식사</p>
        <p>{restaurant['description']}</p>
    </div>
    """

    folium.Marker(
        location=[restaurant["lat"], restaurant["lon"]],
        tooltip=restaurant["name"],
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(
            color="green",
            icon="cutlery",
            prefix="fa"
        )
    ).add_to(restaurant_layer)

restaurant_layer.add_to(seoul_map)


# 호텔 레이어
hotel_layer = folium.FeatureGroup(
    name="추천 호텔",
    show=True
)

for hotel in hotels:

    popup_text = f"""
    <div style="width:230px;">
        <h4>{hotel['name']}</h4>
        <p>{hotel['english']}</p>
        <p>{hotel['description']}</p>
    </div>
    """

    folium.Marker(
        location=[hotel["lat"], hotel["lon"]],
        tooltip=hotel["name"],
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(
            color="orange",
            icon="bed",
            prefix="fa"
        )
    ).add_to(hotel_layer)

hotel_layer.add_to(seoul_map)


# 1일 차 관광 동선
day1_places = [p for p in places if p["day"] == 1]

folium.PolyLine(
    locations=[
        [p["lat"], p["lon"]]
        for p in day1_places
    ],
    color="blue",
    weight=4,
    opacity=0.8,
    tooltip="1일 차 관광 동선"
).add_to(seoul_map)


# 2일 차 관광 동선
day2_places = [p for p in places if p["day"] == 2]

folium.PolyLine(
    locations=[
        [p["lat"], p["lon"]]
        for p in day2_places
    ],
    color="purple",
    weight=4,
    opacity=0.8,
    tooltip="2일 차 관광 동선"
).add_to(seoul_map)


# 지도 레이어 선택
folium.LayerControl().add_to(seoul_map)

# 지도 출력
st_folium(
    seoul_map,
    width=None,
    height=620,
    use_container_width=True
)

st.caption(
    "파란색 선은 1일 차, 보라색 선은 2일 차 관광지 순서입니다. "
    "초록색 마커는 식당, 주황색 마커는 호텔입니다."
)


# -----------------------------------
# 8. 일정표 표시
# -----------------------------------
st.markdown("---")
st.header("📅 1박 2일 상세 여행 일정")

st.subheader("DAY 1 | 서울의 역사와 전통시장")

st.dataframe(
    day1_schedule,
    use_container_width=True,
    hide_index=True
)

st.subheader("DAY 2 | 서울의 현대적인 명소")

st.dataframe(
    day2_schedule,
    use_container_width=True,
    hide_index=True
)


# -----------------------------------
# 9. 식당 추천 및 링크
# -----------------------------------
st.markdown("---")
st.header("🍽️ 추천 식당")

st.write(
    "관광 동선에 맞춰 아침, 점심, 저녁 식당을 추천합니다. "
    "링크를 누르면 지도에서 위치와 길찾기를 확인할 수 있습니다."
)

for day in [1, 2]:

    st.subheader(f"DAY {day} 식당")

    day_restaurants = [
        r for r in restaurants
        if r["day"] == day
    ]

    cols = st.columns(3)

    for index, restaurant in enumerate(day_restaurants):

        with cols[index]:
            with st.container(border=True):
                st.markdown(
                    f"**{restaurant['meal']} | {restaurant['name']}**"
                )
                st.caption(restaurant["english"])
                st.write(restaurant["description"])

                st.link_button(
                    "식당 위치 및 길찾기",
                    google_maps_link(restaurant["name"])
                )


# -----------------------------------
# 10. 호텔 추천 및 링크
# -----------------------------------
st.markdown("---")
st.header("🏨 추천 호텔")

st.write(
    "1박 숙박을 위한 호텔입니다. "
    "관광지 이동과 명동 쇼핑을 고려해 도심 호텔을 추천합니다."
)

hotel_cols = st.columns(3)

for index, hotel in enumerate(hotels):

    with hotel_cols[index]:
        with st.container(border=True):

            st.markdown(f"**{hotel['name']}**")
            st.caption(hotel["english"])
            st.write(hotel["description"])

            st.link_button(
                "호텔 위치 및 정보 확인",
                google_maps_link(hotel["name"])
            )

st.warning(
    "호텔 가격과 객실 상황은 숙박 날짜에 따라 달라집니다. "
    "예약 전 공식 숙박 조건과 취소 규정을 확인하세요. "
    "미성년자는 보호자와 숙박 및 예약 가능 여부를 확인해야 합니다."
)


# -----------------------------------
# 11. 여행 안내
# -----------------------------------
st.markdown("---")
st.header("💡 여행 안내")

st.markdown("""
- 이동 시간은 교통 상황과 대기 시간에 따라 달라질 수 있습니다.
- 경복궁은 휴궁일이 있으므로 방문 날짜에 운영 여부를 확인하세요.
- 북촌한옥마을은 주민이 거주하는 곳이므로 조용히 관람해 주세요.
- N서울타워는 날씨가 좋을 때 방문하면 더 좋은 전망을 볼 수 있습니다.
- 관광지와 식당의 영업시간 및 휴무일은 방문 전에 확인하세요.
""")

st.markdown(
    "[서울 공식 관광 안내 사이트](https://english.visitseoul.net/) "
    "| [서울시 관광 가이드](https://english.seoul.go.kr/)"
)

st.caption(
    "Seoul 1 Night 2 Days Travel Planner"
)
