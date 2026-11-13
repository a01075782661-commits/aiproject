
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from pathlib import Path
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# --------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------

st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 Iris 붓꽃 품종 예측 프로그램")
st.write(
    "꽃잎의 길이와 너비를 입력하면 "
    "머신러닝 KNN 알고리즘으로 붓꽃 품종을 예측합니다."
)

st.divider()

# --------------------------------------------------
# 2. CSV 파일 불러오기
# --------------------------------------------------

current_dir = Path(__file__).resolve().parent

file_candidates = [
    current_dir.parent / "Iris.csv",
    current_dir / "Iris.csv"
]

csv_path = next(
    (p for p in file_candidates if p.exists()),
    None
)

if csv_path is None:
    st.error("Iris.csv 파일을 찾을 수 없습니다.")
    st.stop()

try:
    try:
        df = pd.read_csv(csv_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")

except Exception as e:
    st.error(f"CSV 파일을 불러오는 중 오류 발생: {e}")
    st.stop()

# --------------------------------------------------
# 3. 데이터 확인
# --------------------------------------------------

required_columns = ["꽃잎 길이", "꽃잎 너비", "품종"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 컬럼 이름을 확인해주세요.")
    st.stop()

df = df.dropna(subset=required_columns).copy()

X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

st.subheader("📊 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("전체 데이터", f"{len(df)}개")

with col2:
    st.metric("붓꽃 품종", f"{y.nunique()}종")

with col3:
    st.metric("사용 알고리즘", "KNN")

# --------------------------------------------------
# 4. KNN 모델 생성
# --------------------------------------------------

model = Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsClassifier(n_neighbors=5))
])

model.fit(X, y)

# --------------------------------------------------
# 5. 입력 범위 안내
# --------------------------------------------------

st.divider()
st.subheader("✏️ 붓꽃 크기 입력")

min_length = float(X["꽃잎 길이"].min())
max_length = float(X["꽃잎 길이"].max())

min_width = float(X["꽃잎 너비"].min())
max_width = float(X["꽃잎 너비"].max())

st.info(
    f"""
    📌 입력 가능한 범위

    - 꽃잎 길이: {min_length} ~ {max_length} cm
    - 꽃잎 너비: {min_width} ~ {max_width} cm

    입력 범위는 업로드된 Iris.csv 데이터의
    최솟값과 최댓값을 기준으로 합니다.
    """
)

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "🌸 꽃잎 길이 (cm)",
        min_value=min_length,
        max_value=max_length,
        value=3.0,
        step=0.1,
        format="%.1f"
    )

with col2:
    petal_width = st.number_input(
        "🌸 꽃잎 너비 (cm)",
        min_value=min_width,
        max_value=max_width,
        value=1.0,
        step=0.1,
        format="%.1f"
    )

# --------------------------------------------------
# 6. 품종 예측
# --------------------------------------------------

if st.button("🔍 붓꽃 품종 예측하기", type="primary"):

    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=["꽃잎 길이", "꽃잎 너비"]
    )

    prediction = model.predict(input_data)[0]

    probabilities = model.predict_proba(input_data)[0]

    classes = model.named_steps["knn"].classes_

    st.divider()
    st.subheader("🎯 예측 결과")

    st.success(f"예측된 붓꽃 품종: {prediction}")

    result_col1, result_col2 = st.columns(2)

    with result_col1:
        st.metric(
            "예측 품종",
            prediction
        )

    with result_col2:
        predicted_probability = probabilities[
            list(classes).index(prediction)
        ]

        st.metric(
            "가장 가까운 5개 중 해당 품종 비율",
            f"{predicted_probability * 100:.1f}%"
        )

    st.caption(
        "위 비율은 KNN의 최근접 이웃 5개 중 "
        "해당 품종이 차지하는 비율입니다."
    )

    # --------------------------------------------------
    # 7. 최근접 이웃 찾기
    # --------------------------------------------------

    scaler = model.named_steps["scaler"]
    knn = model.named_steps["knn"]

    scaled_input = scaler.transform(input_data)

    distances, indices = knn.kneighbors(scaled_input)

    nearest_df = df.iloc[indices[0]].copy()

    nearest_df["거리"] = distances[0]
    nearest_df["순위"] = range(1, 6)

    st.subheader("🔎 예측 이유 알아보기")

    st.write(
        "입력한 꽃잎 크기와 가장 가까운 데이터 5개를 찾았습니다. "
        "이 데이터들의 품종을 투표하여 최종 결과를 결정합니다."
    )

    vote_counts = pd.Series(
        nearest_df["품종"]
    ).value_counts()

    vote_col1, vote_col2, vote_col3 = st.columns(3)

    for col, species in zip(
        [vote_col1, vote_col2, vote_col3],
        classes
    ):
        with col:
            st.metric(
                species,
                f"{vote_counts.get(species, 0)}표"
            )

    st.dataframe(
        nearest_df[
            [
                "순위",
                "꽃잎 길이",
                "꽃잎 너비",
                "품종",
                "거리"
            ]
        ].round(3),
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # 8. 시각화 - 품종 분류 영역
    # --------------------------------------------------

    st.divider()
    st.subheader("📈 붓꽃 품종 분류 시각화")

    st.write(
        """
        - 배경 색상: KNN 모델이 해당 위치를 예측하는 품종 영역
        - 원형 점: 실제 붓꽃 데이터
        - 검은 테두리 원: 입력값과 가까운 데이터 5개
        - ⭐ 초록색 별: 사용자가 입력한 꽃잎 크기
        - 점선: 입력값과 가까운 데이터의 거리
        """
    )

    # 그래프 범위
    x_min = min_length - 0.3
    x_max = max_length + 0.3

    y_min = min_width - 0.2
    y_max = max_width + 0.2

    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, 250),
        np.linspace(y_min, y_max, 250)
    )

    grid_data = pd.DataFrame({
        "꽃잎 길이": xx.ravel(),
        "꽃잎 너비": yy.ravel()
    })

    # 각 영역의 품종 예측
    Z = model.predict(grid_data)

    # 품종별 색상
    unique_classes = list(classes)

    color_list = [
        "#F6A6B2",
        "#A5C8F0",
        "#F8D77A"
    ]

    color_map = {
        species: color_list[i % len(color_list)]
        for i, species in enumerate(unique_classes)
    }

    class_to_num = {
        species: i
        for i, species in enumerate(unique_classes)
    }

    Z_num = np.array([
        class_to_num[v] for v in Z
    ]).reshape(xx.shape)

    fig, ax = plt.subplots(figsize=(11, 7))

    cmap = mcolors.ListedColormap([
        color_map[c] for c in unique_classes
    ])

    # 분류 영역 표시
    ax.contourf(
        xx,
        yy,
        Z_num,
        levels=np.arange(len(unique_classes) + 1) - 0.5,
        cmap=cmap,
        alpha=0.30
    )

    # 실제 데이터 표시
    for species in unique_classes:

        species_df = df[df["품종"] == species]

        ax.scatter(
            species_df["꽃잎 길이"],
            species_df["꽃잎 너비"],
            color=color_map[species],
            label=species,
            s=45,
            edgecolors="white",
            linewidths=0.6,
            alpha=0.85
        )

    # 최근접 이웃 5개 표시
    for _, row in nearest_df.iterrows():

        ax.scatter(
            row["꽃잎 길이"],
            row["꽃잎 너비"],
            facecolors="none",
            edgecolors="black",
            s=180,
            linewidths=1.8,
            zorder=5
        )

        # 입력값과 가까운 데이터 연결
        ax.plot(
            [petal_length, row["꽃잎 길이"]],
            [petal_width, row["꽃잎 너비"]],
            color="black",
            linestyle="--",
            alpha=0.5,
            linewidth=1
        )

    # 사용자 입력값 - 초록색 별
    ax.scatter(
        petal_length,
        petal_width,
        color="#00C853",
        marker="*",
        s=450,
        edgecolors="black",
        linewidths=1.2,
        label="Your Input",
        zorder=10
    )

    ax.set_xlabel(
        "Petal Length (cm)",
        fontsize=12
    )

    ax.set_ylabel(
        "Petal Width (cm)",
        fontsize=12
    )

    ax.set_title(
        "Iris KNN Classification Map",
        fontsize=16,
        fontweight="bold"
    )

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    ax.grid(alpha=0.2)
    ax.legend(loc="upper left")

    st.pyplot(fig)
    plt.close(fig)

    # --------------------------------------------------
    # 9. 최종 분석 설명
    # --------------------------------------------------

    st.subheader("💡 AI 분석 설명")

    winning_count = vote_counts.get(prediction, 0)

    st.write(
        f"""
        입력한 꽃잎 길이는 **{petal_length:.1f} cm**,
        꽃잎 너비는 **{petal_width:.1f} cm**입니다.

        KNN 알고리즘은 입력한 값과 가장 가까운
        붓꽃 데이터 5개를 비교했습니다.

        그 결과 **{prediction}** 품종이
        가장 많은 {winning_count}표를 얻었습니다.

        따라서 입력한 붓꽃은
        **{prediction}** 품종으로 예측되었습니다.
        """
    )

    st.info(
        "그래프의 배경 색상은 KNN이 학습한 품종별 예측 영역입니다. "
        "초록색 별이 위치한 영역과 주변 데이터의 분포를 "
        "함께 살펴보면 분류 이유를 이해할 수 있습니다."
    )

else:

    st.info(
        "꽃잎 길이와 너비를 입력한 다음 "
        "'붓꽃 품종 예측하기' 버튼을 눌러주세요."
    )
