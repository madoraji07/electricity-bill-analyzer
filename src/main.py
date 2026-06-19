import streamlit as st
import os
import sys

# 💡 Windows 콘솔 환경에서 이모지 등의 유니코드 출력 시 발생하는 UnicodeEncodeError 방지
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 💡 현재 main.py가 src 폴더 안에 있으므로, 상대 경로 참조를 위한 시스템 패스 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 같은 폴더(src) 내부의 모듈을 직접 가져옵니다.
from data_loader import load_data, aggregate_monthly, generate_sample_data
from analyzer import calculate_bill
from visualizer import plot_monthly_usage

# 1. 스트림릿 레이아웃 설정
st.set_page_config(page_title="전기요금 분석 시스템", page_icon="⚡", layout="wide")

st.title("⚡ AI 전기요금 분석 및 인터랙티브 절약 대시보드")
st.markdown("본 웹 어플리케이션은 파이썬 백엔드 모듈을 기반으로 유기적으로 동작하는 종합 데이터 분석 시스템입니다.")
st.sidebar.header("⚙️ 시스템 대시보드 제어판")

# ====== 🔢 [실시간 입력창 및 시뮬레이터 기능 추가] ======
st.sidebar.markdown("---")
st.sidebar.subheader("🔢 실시간 요금 시뮬레이터")
user_input_usage = st.sidebar.number_input(
    "당월 예상 사용량 입력 (kWh)", 
    min_value=0.0, max_value=2000.0, value=350.0, step=10.0
)

# 한전 규격 간이 연산 알고리즘
if user_input_usage <= 200:
    base, rate = 910, 120.0
elif user_input_usage <= 400:
    base, rate = 1600, 214.6
else:
    base, rate = 7300, 307.3

sim_bill = int((base + (user_input_usage * rate)) * 1.137)
st.sidebar.metric("💵 실시간 예상 요금", f"{sim_bill:,} 원")
st.sidebar.markdown("---")
# =======================================================

# 2. 데이터 파일 경로 설정
test_filename = "electricity_usage_test.csv"

if not os.path.exists(test_filename):
    generate_sample_data(test_filename)

raw_data = load_data(test_filename)
monthly_summary = aggregate_monthly(raw_data)
analyzed_data = calculate_bill(monthly_summary)

# 3. 사이드바 제어 설정
user_types = list(analyzed_data['Type'].unique())
selected_type = st.sidebar.selectbox("🎯 분석할 사용자 타입 선택", user_types)

filtered_data = analyzed_data[analyzed_data['Type'] == selected_type].reset_index(drop=True)

# 4. KPI 스코어보드
st.markdown(f"### 📊 {selected_type} 데이터 탑라인 분석")
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric("최고 전력 소비월", f"{int(filtered_data.loc[filtered_data['max'].idxmax(), 'Month'])}월")
with kpi2:
    st.metric("연간 누적 전력량", f"{filtered_data['sum'].sum():,.1f} kWh")
with kpi3:
    st.metric("연간 누적 예상 요금", f"{filtered_data['Calculated_Bill'].sum():,} 원")
st.markdown("---")

# 5. 메인 레이아웃 뷰 배치
left_column, right_column = st.columns([1, 1])
fig_usage, fig_bill = plot_monthly_usage(filtered_data)

with left_column:
    st.write("#### 📊 전력 사용 실태 분석 결과")
    st.pyplot(fig_usage)
    
    st.write("#### 📋 상세 원천 데이터 뷰어")
    display_df = filtered_data[['Year', 'Month', 'sum', 'Calculated_Bill']].copy()
    display_df.columns = ['연도', '월', '총사용량(kWh)', '청구액(원)']
    st.dataframe(display_df.style.format({'총사용량(kWh)': '{:.1f}', '청구액(원)': '{:,}'}), use_container_width=True)

with right_column:
    st.write("#### 💸 누진 요금 청구 시뮬레이션")
    st.pyplot(fig_bill)
    
    st.write("#### 💡 AI 인텔리전스 맞춤 절약 가이드")
    
    # ====== 🎯 [실시간 시뮬레이션 결과 연동 출력] ======
    st.success(f"🎯 현재 입력하신 **{user_input_usage} kWh** 기준 예상 요금은 **{sim_bill:,}원**입니다.")
    if user_input_usage > 400:
        st.error("🚨 누진세 최고 3구간(폭탄 구간)입니다! 사용량을 줄여보세요.")
    st.markdown("---")
    # ===================================================
    
    for idx, row in filtered_data.iterrows():
        icon = "🚨" if row['sum'] > 400 else "🌱"
        st.info(f"**[{int(row['Month'])}월 알림]** {icon} {row['Saving_Tip']}")

st.markdown("---")
# ====== 📝 [개발자 이름 마연희, 조민서 최종 업데이트] ======
st.caption("⚡ Electricity Bill Analyzer System v1.0.0 | 개발자: 이초한, 마연희, 조민서")