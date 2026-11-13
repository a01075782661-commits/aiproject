
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from pathlib import Path

from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from sklearn.inspection import permutation_importance

# --------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------

st.set_page_config(
    page_title="Iris 붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 Iris 붓꽃 품종 예측 AI")
st.write(
    "꽃잎의 길이와 너비를 입력하고 "
    "3가지 머신러닝 알고리즘으로 붓꽃 품종을 예측해 보세요."
)

st.divider()

# --------------------------------------------------
# 2. 데이터 불러오기
# --------------------------------------------------

current_dir = Path(__file__).resolve().parent

csv_candidates = [
    current_dir.parent / "Iris.csv",
    current_dir / "Iris.csv"
]

csv_path = next(
    (p for p in csv_candidates if p.exists()),
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
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()

# 필요한 컬럼 확인

required_columns = [
    "꽃잎 길이",
    "꽃잎 너비",
    "품종"
]

if not all(col in df.columns for col in required_columns):
    st.error(
        "CSV 파일의 컬럼 이름을 확인해주세요.\n\n"
        "필요한 컬럼: 꽃잎 길이, 꽃잎 너비, 품종"
    )
    st.stop()

df = df[required_columns].copy()

df["꽃잎 길이"] = pd.to_numeric(
    df["꽃잎 길이"], errors="coerce"
)

df["꽃잎 너비"] = pd.to_numeric(
    df["꽃잎 너비"], errors="coerce"
)

df = df.dropna().reset_index(drop=True)

df["품종"] = df["품종"].astype(str)

if len(df) < 5 or df["품종"].nunique() < 2:
    st.error("분류 학습에 필요한 데이터가 부족합니다.")
    st.stop()

X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

species_list = sorted(y.unique())

# --------------------------------------------------
# 3. 데이터 기본 정보
# --------------------------------------------------

st.subheader("📊 데이터 기본 정보")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("전체 데이터", f"{len(df)}개")

with col2:
    st.metric("붓꽃 품종", f"{len(species_list)}종")

with col3:
    st.metric("분석 변수", "2개")

with col4:
    st.metric("분류 알고리즘", "3개")

with st.expander("데이터 미리보기"):
    st.dataframe(df.head(10), use_container_width=True)

st.divider()

# --------------------------------------------------
# 4. 알고리즘 설명
# --------------------------------------------------

st.subheader("🧠 머신러닝 분류 알고리즘")

algorithm_info = {
    "KNN (K-최근접 이웃)": """
    **작동 원리**

    1. 입력한 꽃잎 크기와 기존 데이터의 거리를 계산합니다.
    2. 가장 가까운 데이터 5개를 찾습니다.
    3. 가장 많이 등장한 품종을 최종 결과로 선택합니다.

    특징: 주변 데이터의 품종을 참고하는 방식입니다.
    """,

    "Random Forest (랜덤 포레스트)": """
    **작동 원리**

    1. 여러 개의 의사결정나무를 만듭니다.
    2. 각 나무가 입력한 꽃잎 크기를 분석합니다.
    3. 여러 나무의 예측 결과를 종합하여 품종을 결정합니다.

    특징: 여러 의사결정나무의 결과를 결합하는 앙상블 알고리즘입니다.
    """,

    "SVM (서포트 벡터 머신)": """
    **작동 원리**

    1. 품종별 데이터를 분석합니다.
    2. 품종을 구분하는 결정 경계를 학습합니다.
    3. 입력값이 어느 영역에 속하는지 판단합니다.

    특징: 데이터 사이의 경계를 찾아 분류하는 알고리즘입니다.
    """
}

selected_algorithm = st.selectbox(
    "사용할 분류 알고리즘 선택",
    list(algorithm_info.keys())
)

st.info(algorithm_info[selected_algorithm])

# --------------------------------------------------
# 5. 모델 생성
# --------------------------------------------------

models = {

    "KNN (K-최근접 이웃)": Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", KNeighborsClassifier(
            n_neighbors=min(5, len(df))
        ))
    ]),

    "Random Forest (랜덤 포레스트)": RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced"
    ),

    "SVM (서포트 벡터 머신)": Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", SVC(
            kernel="rbf",
            C=1.0,
            gamma="scale",
            probability=True,
            random_state=42
        ))
    ])
}

# 모든 알고리즘 학습
for model in models.values():
    model.fit(X, y)

model = models[selected_algorithm]

# --------------------------------------------------
# 6. 꽃잎 입력 범위
# --------------------------------------------------

st.divider()
st.subheader("✏️ 꽃잎 크기 입력")

min_length = float(X["꽃잎 길이"].min())
max_length = float(X["꽃잎 길이"].max())

min_width = float(X["꽃잎 너비"].min())
max_width = float(X["꽃잎 너비"].max())

st.info(
    f"""
    📌 입력 가능한 범위

    - 꽃잎 길이: {min_length} ~ {max_length} cm
    - 꽃잎 너비: {min_width} ~ {max_width} cm

    입력 범위는 CSV 데이터의 최솟값과 최댓값을 기준으로 합니다.
    """
)

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "🌸 꽃잎 길이 (cm)",
        min_value=min_length,
        max_value=max_length,
        value=float(np.clip(3.0, min_length, max_length)),
        step=0.1,
        format="%.1f"
    )

with col2:
    petal_width = st.number_input(
        "🌸 꽃잎 너비 (cm)",
        min_value=min_width,
        max_value=max_width,
        value=float(np.clip(1.0, min_width, max_width)),
        step=0.1,
        format="%.1f"
    )

# --------------------------------------------------
# 7. 예측 버튼
# --------------------------------------------------

predict_button = st.button(
    "🔍 품종 예측하기",
    type="primary",
    use_container_width=True
)

# --------------------------------------------------
# 8. 예측 결과
# --------------------------------------------------

if predict_button:

    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=["꽃잎 길이", "꽃잎 너비"]
    )

    prediction = model.predict(input_data)[0]

    probabilities = model.predict_proba(input_data)[0]

    classes = model.classes_ if hasattr(
        model, "classes_"
    ) else model.named_steps["classifier"].classes_

    st.divider()
    st.subheader("🎯 예측 결과")

    st.success(
        f"예측된 붓꽃 품종: {prediction}"
    )

    predicted_probability = probabilities[
        list(classes).index(prediction)
    ]

    result_col1, result_col2, result_col3 = st.columns(3)

    with result_col1:
        st.metric(
            "예측 품종",
            prediction
        )

    with result_col2:
        st.metric(
            "예측 점수",
            f"{predicted_probability * 100:.1f}%"
        )

    with result_col3:
        st.metric(
            "선택 알고리즘",
            selected_algorithm.split(" (")[0]
        )

    st.caption(
        "예측 점수는 모델의 predict_proba 결과입니다. "
        "모델별로 계산 방식이 달라 직접적인 성능 비교 지표로 "
        "사용해서는 안 됩니다."
    )

    # --------------------------------------------------
    # 9. 모든 알고리즘 예측 비교
    # --------------------------------------------------

    st.subheader("⚖️ 3가지 알고리즘 예측 비교")

    comparison_data = []

    for name, compare_model in models.items():

        compare_prediction = compare_model.predict(
            input_data
        )[0]

        compare_probabilities = compare_model.predict_proba(
            input_data
        )[0]

        compare_classes = (
            compare_model.classes_
            if hasattr(compare_model, "classes_")
            else compare_model.named_steps["classifier"].classes_
        )

        compare_score = compare_probabilities[
            list(compare_classes).index(compare_prediction)
        ]

        comparison_data.append({
            "알고리즘": name,
            "예측 품종": compare_prediction,
            "예측 점수(%)": round(
                compare_score * 100, 1
            )
        })

    comparison_df = pd.DataFrame(comparison_data)

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # 10. 품종별 예측 확률 그래프
    # --------------------------------------------------

    st.subheader("📊 선택한 알고리즘의 품종별 예측 점수")

    probability_df = pd.DataFrame({
        "품종": classes,
        "예측 점수": probabilities * 100
    })

    st.bar_chart(
        probability_df.set_index("품종"),
        color="#FF69B4"
    )

    # --------------------------------------------------
    # 11. 가장 가까운 데이터 5개
    # --------------------------------------------------

    st.divider()
    st.subheader("🔎 입력값과 가까운 실제 데이터")

    reference_scaler = StandardScaler()

    scaled_X = reference_scaler.fit_transform(X)

    scaled_input = reference_scaler.transform(input_data)

    distances = np.sqrt(
        np.sum(
            (scaled_X - scaled_input) ** 2,
            axis=1
        )
    )

    nearest_indices = np.argsort(distances)[:5]

    nearest_df = df.iloc[nearest_indices].copy()

    nearest_df["거리"] = distances[nearest_indices]

    nearest_df["순위"] = range(1, 6)

    st.write(
        "입력값과 가장 가까운 실제 데이터 5개입니다. "
        "이 데이터는 모든 알고리즘에서 공통적인 참고 자료로 사용합니다."
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

    # KNN 투표 결과
    if selected_algorithm.startswith("KNN"):

        st.write("**KNN의 실제 최근접 이웃 투표 결과**")

        vote_counts = nearest_df["품종"].value_counts()

        for species in species_list:

            count = vote_counts.get(species, 0)

            st.write(f"{species}: {count}표")

            st.progress(count / 5)

    else:

        st.info(
            "현재 선택한 알고리즘은 단순히 가까운 데이터 5개의 "
            "투표로 결정하지 않습니다. 위 표는 입력값 주변의 "
            "실제 데이터 분포를 이해하기 위한 참고 자료입니다."
        )

    # --------------------------------------------------
    # 12. 분류 영역 시각화
    # --------------------------------------------------

    st.divider()
    st.subheader("📈 머신러닝 분류 영역 시각화")

    st.write(
        """
        그래프 읽는 방법

        - 배경색: 선택한 알고리즘이 예측한 품종 영역
        - 원형 점: 실제 붓꽃 데이터
        - 검은 테두리 원: 입력값과 가까운 실제 데이터 5개
        - 초록색 별: 사용자가 입력한 꽃잎 크기
        - 검은 점선: 입력값과 가까운 데이터까지의 거리
        """
    )

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

    Z = model.predict(grid_data)

    class_to_num = {
        species: i
        for i, species in enumerate(species_list)
    }

    Z_num = np.array([
        class_to_num[v] for v in Z
    ]).reshape(xx.shape)

    color_list = [
        "#F4A6B7",
        "#A7C8F0",
        "#F5D77E",
        "#B9DDB9"
    ]

    color_map = {
        species: color_list[i % len(color_list)]
        for i, species in enumerate(species_list)
    }

    cmap = mcolors.ListedColormap([
        color_map[s] for s in species_list
    ])

    fig, ax = plt.subplots(figsize=(11, 7))

    ax.contourf(
        xx,
        yy,
        Z_num,
        levels=np.arange(
            len(species_list) + 1
        ) - 0.5,
        cmap=cmap,
        alpha=0.35
    )

    # 실제 데이터
    for species in species_list:

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

    # 최근접 데이터 5개 표시 및 연결선
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

        ax.plot(
            [petal_length, row["꽃잎 길이"]],
            [petal_width, row["꽃잎 너비"]],
            linestyle="--",
            color="black",
            alpha=0.45,
            linewidth=1
        )

    # 사용자 입력값 초록색 별
    ax.scatter(
        petal_length,
        petal_width,
        color="#00C853",
        marker="*",
        s=500,
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
        f"Iris Classification - {selected_algorithm}",
        fontsize=15,
        fontweight="bold"
    )

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    ax.grid(alpha=0.2)
    ax.legend(loc="upper left")

    st.pyplot(fig)
    plt.close(fig)

    # --------------------------------------------------
    # 13. 랜덤 포레스트 변수 중요도
    # --------------------------------------------------

    if selected_algorithm.startswith("Random Forest"):

        st.divider()
        st.subheader("🌳 랜덤 포레스트 변수 중요도")

        importance_model = model

        importance_df = pd.DataFrame({
            "변수": ["꽃잎 길이", "꽃잎 너비"],
            "중요도": importance_model.feature_importances_
        }).sort_values(
            "중요도",
            ascending=False
        )

        st.bar_chart(
            importance_df.set_index("변수"),
            color="#FF69B4"
        )

        st.write(
            "변수 중요도는 랜덤 포레스트가 품종을 구분할 때 "
            "각 변수를 얼마나 활용했는지 나타내는 지표입니다."
        )

    # --------------------------------------------------
    # 14. SVM 설명
    # --------------------------------------------------

    if selected_algorithm.startswith("SVM"):

        st.divider()
        st.subheader("📐 SVM 결정 경계 설명")

        st.write(
            """
            SVM은 꽃잎 길이와 너비를 이용해 품종별 영역을 구분하는
            결정 경계를 학습합니다.

            이번 프로그램에서는 RBF 커널을 사용했습니다.
            따라서 직선뿐만 아니라 곡선 형태의 경계도 학습할 수 있습니다.

            그래프의 배경색을 통해 입력값이 어느 품종 영역에
            포함되는지 확인할 수 있습니다.
            """
        )

        svm_classifier = model.named_steps["classifier"]

        st.write(
            f"학습에 사용된 서포트 벡터 수: "
            f"{int(np.sum(svm_classifier.n_support_))}개"
        )

    # --------------------------------------------------
    # 15. 최종 분석
    # --------------------------------------------------

    st.divider()
    st.subheader("💡 최종 AI 분석")

    st.write(
        f"""
        입력한 꽃잎 길이: **{petal_length:.1f} cm**

        입력한 꽃잎 너비: **{petal_width:.1f} cm**

        선택한 알고리즘: **{selected_algorithm}**

        예측된 품종: **{prediction}**

        예측 점수: **{predicted_probability * 100:.1f}%**
        """
    )

    st.success(
        f"최종 예측 결과는 {prediction}입니다."
    )

    st.caption(
        "주의: 이 프로그램은 Iris 데이터 전체를 학습한 교육용 모델입니다. "
        "별도의 테스트 데이터로 검증한 정확도와는 구분해야 합니다."
    )

else:

    st.info(
        "꽃잎 길이와 너비를 입력하고 "
        "'품종 예측하기' 버튼을 눌러주세요."
    )
