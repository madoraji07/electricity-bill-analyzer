import streamlit as st
import os
import sys

# ==========================================================
# 📌 경로 설정 (모듈 import 오류 방지)
# ==========================================================
# 현재 main.py 위치를 기준으로 상대경로 import가 가능하도록 설정
# data_loader / analyzer / visualizer 모듈을 정상적으로 불러오기 위함
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import data_loader as dl
import analyzer as az
from visualizer import ElectricityVisualizer


# ==========================================================
# 📌 Streamlit 기본 설정
# ==========================================================
# 웹 앱 제목 / 아이콘 / 레이아웃 설정
st.set_page_config(
    page_title="전기요금 분석 시스템",
    page_icon="⚡",
    layout="wide"
)

# 메인 타이틀
st.title("⚡ AI 전기요금 분석 및 전력 소비 대시보드")

# 시스템 설명
st.markdown("""
본 시스템은 전력 사용량 데이터를 기반으로
전기요금 계산 및 소비 패턴 분석을 수행하는 데이터 분석 대시보드입니다.
""")


# ==========================================================
# 📌 사이드바 (페이지 네비게이션)
# ==========================================================
# Streamlit은 기본적으로 SPA 구조이므로 radio로 페이지 분리 구현
st.sidebar.header("📌 메뉴 선택")

page = st.sidebar.radio(
    "이동할 페이지 선택",
    ["🏠 홈 (요금 계산기)", "🏡 가정용 분석", "🏢 사업장 분석"]
)


# ==========================================================
# 🏠 1. 홈 (전력량 입력 기반 요금 계산기)
# ==========================================================
if page == "🏠 홈 (요금 계산기)":

    st.header("🔢 실시간 전기요금 계산기")

    # 사용자 입력 (kWh 단위)
    # 실제 한전 구조를 단순화한 교육용 입력값
    usage = st.number_input(
        "이번 달 전력 사용량 입력 (kWh)",
        min_value=0.0,
        max_value=2000.0,
        value=300.0,
        step=10.0
    )

    # ======================================================
    # 📌 단순화된 전기요금 계산 함수
    # ======================================================
    # 실제 누진제를 단순 모델로 구현하여 이해를 돕는 구조
    def calculate_bill(u):
        """
        전력 사용량 기반 단순 요금 계산 함수
        (교육용 모델: 기본요금 + 단가 기반 계산)
        """

        # 누진 구간별 기본요금 및 단가 설정
        if u <= 200:
            base = 910
            rate = 120
        elif u <= 400:
            base = 1600
            rate = 214
        else:
            base = 7300
            rate = 307

        # 전력량 요금 계산
        energy = u * rate

        # 총 요금 계산 (세금 제외 단순 모델)
        total = base + energy

        return base, energy, total


    # 요금 계산 실행
    base, energy, total = calculate_bill(usage)

    # 결과 출력
    st.subheader(f"💰 예상 전기요금: {int(total):,}원")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### 📌 요금 상세 내역")
        st.write(f"- 기본요금: {base:,}원")
        st.write(f"- 전력량요금: {energy:,}원")

    with col2:
        st.write("### 📌 누진 구간 분석")

        # 사용량 기반 구간 판정
        if usage > 400:
            st.error("🚨 3구간 (고사용량)")
            st.write("전력 사용량이 많아 요금 부담이 가장 높은 구간입니다.")
        elif usage > 200:
            st.warning("⚠️ 2구간 (중간 사용량)")
            st.write("절약 시 1구간 진입 가능")
        else:
            st.success("✅ 1구간 (저사용량)")
            st.write("최적의 전력 사용 상태입니다.")


# ==========================================================
# 🏡 2. 가정용 데이터 분석 페이지
# ==========================================================
elif page == "🏡 가정용 분석":

    st.header("🏡 가정용 전력 소비 분석")

    # ======================================================
    # 📌 CSV 데이터 로딩
    # ======================================================
    # sample_data.csv를 기반으로 Residential 데이터만 분석
    csv_path = os.path.join(current_dir, "../data/sample_data.csv")

    df = dl.load_data(csv_path)

    # 가정용 데이터 필터링
    df = df[df["Type"] == "Residential"]

    # 분석 클래스 초기화
    analyzer = az.ElectricityAnalyzer(df)

    # 시각화 클래스 초기화
    visualizer = ElectricityVisualizer(df)

    # 월별 분석 실행
    monthly_df = analyzer.analyze_monthly_bills()

    # 결과 출력
    st.subheader("📊 월별 소비 분석 결과")
    st.dataframe(monthly_df)

    # 그래프 출력
    st.pyplot(visualizer.plot_monthly_comparison(monthly_df))


# ==========================================================
# 🏢 3. 사업장 데이터 분석 페이지
# ==========================================================
elif page == "🏢 사업장 분석":

    st.header("🏢 사업장 전력 소비 분석")

    # CSV 데이터 로딩
    csv_path = os.path.join(current_dir, "../data/sample_data.csv")

    df = dl.load_data(csv_path)

    # 사업장 데이터 필터링
    df = df[df["Type"] == "Commercial"]

    analyzer = az.ElectricityAnalyzer(df)
    visualizer = ElectricityVisualizer(df)

    monthly_df = analyzer.analyze_monthly_bills()

    st.subheader("📊 사업장 월별 분석 결과")
    st.dataframe(monthly_df)

    st.pyplot(visualizer.plot_monthly_comparison(monthly_df))


# ==========================================================
# 📌 Footer (제출 필수 요소)
# ==========================================================
st.markdown(
    """
    <div style='text-align:center; color:gray; font-size:14px; margin-top:50px;'>
    ⚡ Electricity Bill Analyzer System v1.0.0 |
    개발자: 이초한, 마연희, 조민서
    </div>
    """,
    unsafe_allow_html=True
)