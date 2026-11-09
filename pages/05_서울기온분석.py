# 날짜 문자열 분리
date_parts = df["일시"].str.split("-", expand=True)

# 월 이름을 숫자로 변환
month_dict = {
    "Jan": 1, "Feb": 2, "Mar": 3,
    "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9,
    "Oct": 10, "Nov": 11, "Dec": 12
}

# 월 추출
df["월"] = date_parts[0].map(month_dict)

# 두 자리 연도를 숫자로 변환
year_2digit = pd.to_numeric(
    date_parts[1],
    errors="coerce"
)

# 00~26은 2000년대, 27~99는 1900년대로 변환
df["연도"] = year_2digit.apply(
    lambda y: int(y) + 2000 if y <= 26
    else int(y) + 1900
)

# 날짜 생성
df["일시"] = pd.to_datetime(
    dict(
        year=df["연도"],
        month=df["월"],
        day=1
    ),
    errors="coerce"
)

df = df.dropna(subset=["일시"])
