import streamlit as st
import os
import sys
import pandas as pd

# 경로 보정 (src 폴더 내부 실행 및 데이터 접근 완벽 대응)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

import data_loader as dl      
from visualizer import ElectricityVisualizer  

# 1. 페이지 레이아웃 및 제목 설정
st.set_page_config(page_title="전기요금 분석 시스템", page_icon="⚡", layout="wide")

st.title("⚡ AI 전기요금 분석 및 인터랙티브 절약 대시보드")
st.markdown("본 웹 어플리케이션은 파이썬 백엔드 모듈을 기반으로 유기적으로 동작하는 종합 데이터 분석 시스템입니다.")
st.divider()

# ⚙️ 왼쪽 사이드바 제어판 구성
st.sidebar.header("⚙️ 시스템 대시보드 제어판")
user_type_kor = st.sidebar.selectbox("🎯 분석할 사용자 타입 선택", ["가정용", "사업장용"])

st.sidebar.divider()
show_analysis = st.sidebar.checkbox("📊 1년 데이터 소비 패턴 분석 보기", value=True)


# 2. 🔢 메인 화면: 실시간 전기요금 시뮬레이터 (최상단 배치)
st.header("🔢 실시간 전기요금 시뮬레이터")
st.write("이번 달 예상 전력 사용량을 입력하시면 한전 누진제 규격에 맞게 실시간 청구서가 발급됩니다.")

# 입력창 강제 활성화
user_input_usage = st.number_input(
    "이번 달 전력 사용량 입력 (단위: kWh)", 
    min_value=0.0, 
    max_value=2000.0, 
    value=350.0,  
    step=10.0
)

# 간이 누진제 연산 로직 (파이 차트 규격 연동)
def emergency_calc(usage):
    if usage <= 200:
        base, rate = 910, 120.0
    elif usage <= 400:
        base, rate = 1600, 214.6
    else:
        base, rate = 7300, 307.3
    energy = usage * rate
    vat = (base + energy) * 0.1
    fund = (base + energy) * 0.037
    total = base + energy + vat + fund
    return {
        'base_price': int(base),
        'energy_price': int(energy),
        'vat': int(vat),
        'fund': int(fund),
        'total_bill': int(total)
    }

bill_info = emergency_calc(user_input_usage)

st.subheader(f"💵 당월 예상 청구 금액: 총 {bill_info['total_bill']:,} 원")

main_col1, main_col2 = st.columns(2)
with main_col1:
    with st.expander("🔍 누진제 구간별 명세서 세부 내역 펼치기", expanded=True):
        st.write(f"• **기본 요금:** {bill_info['base_price']:,} 원")
        st.write(f"• **전력량 요금:** {bill_info['energy_price']:,} 원")
        st.write(f"• **부가가치세 (10%):** {bill_info['vat']:,} 원")
        st.write(f"• **전력산업기반기금 (3.7%):** {bill_info['fund']:,} 원")
        st.divider()
        st.write(f"👉 **최종 합계 청구 금액:** {bill_info['total_bill']:,} 원")

with main_col2:
    st.markdown("### 💡 실시간 에코(Eco) 절약 조언")
    if user_input_usage > 400:
        st.error("🚨 **현재 최고 누진 3구간(폭탄 구간)입니다!** 사용량을 줄이셔야 합니다.")
        diff_3 = int(bill_info['total_bill'] - 70000)
        st.success(f"💡 사용량을 400kWh 이하로 줄이시면 다음 달 요금이 약 {diff_3:,}원 절감됩니다!")
    elif user_input_usage > 200:
        st.warning("⚠️ **현재 평이한 누진 2구간입니다.** 조금만 신경 쓰면 최저 구간 진입이 가능합니다.")
        diff_2 = int(bill_info['total_bill'] - 25000)
        st.success(f"💡 사용량을 200kWh 이하로 줄이시면 요금이 약 {diff_2:,}원 절감됩니다!")
    else:
        st.info("✅ **최저 누진 1구간입니다.** 아주 훌륭하게 에너지를 절약하고 계십니다!")

st.divider()


# 3. 📊 하단: 데이터 분석 결과 및 팀원 시각화 차트 연동
if show_analysis:
    st.header(f"📈 {user_type_kor} 연간 전력 사용 실태 분석 결과")
    
    try:
        csv_file = os.path.join(parent_dir, 'data', 'sample_data.csv')
        
        if not os.path.exists(csv_file):
            dl.generate_sample_data(csv_file, days=365)
            
        raw_data = dl.load_data(csv_file)
        user_type = "Residential" if user_type_kor == "가정용" else "Commercial"
        filtered_data = raw_data[raw_data['Type'] == user_type].copy()
        
        # 최신 모듈 규격 매핑
        monthly_summary = dl.aggregate_monthly(filtered_data)
        
        # visualizer 필수 컬럼 'Calculated_Bill' 매핑
        monthly_summary['Calculated_Bill'] = (monthly_summary['Total_Usage_kWh'] * 214.6).astype(int)
        
        visualizer_instance = ElectricityVisualizer(filtered_data)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("최고 전력 소비월", "8월")
        with col2:
            st.metric("연간 누적 전력량", f"{int(monthly_summary['Total_Usage_kWh'].sum()):,} kWh")
        with col3:
            st.metric("연간 누적 예상 요금", f"{int(monthly_summary['Calculated_Bill'].sum()):,} 원")

        st.write("")
        
        graph_col1, graph_col2 = st.columns(2)
        with graph_col1:
            st.subheader("📊 월별 전력 분석 (팀원 구현)")
            st.pyplot(visualizer_instance.plot_monthly_comparison(monthly_summary))
        with graph_col2:
            st.subheader("🍰 요금 상세 구성 파이차트 (팀원 구현)")
            st.pyplot(visualizer_instance.plot_bill_breakdown(bill_info))
            
    except Exception as e:
        st.error(f"데이터 연동 중 오류 발생: {e}")

st.divider()

# 4. 📝 하단 팀원 이름 고정 푸터 (이초한, 마연희, 조민서 반영 완료)
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 14px;'>"
    "⚡ Electricity Bill Analyzer System v1.0.0 | 개발자: 이초한, 마연희, 조민서"
    "</div>", 
    unsafe_allow_html=True
)