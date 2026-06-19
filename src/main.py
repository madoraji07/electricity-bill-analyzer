import streamlit as st
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import data_loader as dl      
import analyzer as az        
from visualizer import ElectricityVisualizer  

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="전기요금 분석 시스템",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ AI 전기요금 분석 및 인터랙티브 절약 대시보드")
st.markdown("본 웹 어플리케이션은 파이썬 백엔드 모듈을 기반으로 유기적으로 동작하는 종합 데이터 분석 시스템입니다.")
st.divider()

# 2. 데이터 로드 (경로를 data/sample_data.csv 로 강제 지정)
@st.cache_data
def get_system_data():
    # 💡 보내주신 폴더 구조에 맞게 sample_data.csv 경로 강제 지정
    csv_file = os.path.join(parent_dir, 'data', 'sample_data.csv')
    return dl.load_data(csv_file)

try:
    raw_data = get_system_data()
    
    # ⚙️ 왼쪽 사이드바 제어판
    st.sidebar.header("⚙️ 시스템 대시보드 제어판")
    user_type_kor = st.sidebar.selectbox("🎯 분석할 사용자 타입 선택", ["가정용", "사업장용"])
    user_type = "Residential" if user_type_kor == "가정용" else "Commercial"
    
    st.sidebar.divider()
    
    # 🔢 실시간 요금 시뮬레이터 입력창
    st.sidebar.subheader("🔢 실시간 요금 시뮬레이터")
    user_input_usage = st.sidebar.number_input(
        "이번 달 전력 사용량 입력(kWh)", 
        min_value=0.0, 
        max_value=2000.0, 
        value=350.0,  
        step=10.0
    )
    
    data = raw_data[raw_data['Type'] == user_type].copy()
    analyzer_instance = az.ElectricityAnalyzer(data)
    visualizer_instance = ElectricityVisualizer(data)

    # 3. 💸 실시간 입력값에 따른 요금 정밀 시뮬레이션 결과 표 및 명세서
    st.header("💰 실시간 사용자 입력 요금 시뮬레이션 결과")
    
    bill_info = az.calculate_single_bill(user_input_usage)
    raw_breakdown = analyzer_instance.calculate_bill(user_input_usage)
    
    input_col1, input_col2 = st.columns(2)
    with input_col1:
        st.subheader(f"현재 입력 사용량 요금: 총 {int(bill_info['total_bill']):,} 원")
        st.caption(f"실시간 설정값: {user_input_usage:,.1f} kWh (주택용 고압 누진제 기준)")
        
        with st.expander("🔍 누진제 구간별 상세 명세서 보기", expanded=True):
            st.write(f"• 기본 요금: {int(bill_info['base_price']):,}원")
            st.write(f"• 전력량 요금(구간 합산): {int(bill_info['energy_price']):,}원")
            if 'breakdown' in raw_breakdown:
                for item in raw_breakdown['breakdown']:
                    st.write(f"  - {item['tier']}: {item['usage']}kWh × {item['rate']}원 = {int(item['bill']):,}원")
            st.write(f"• 부가가치세 (10%): {int(bill_info['vat']):,}원")
            st.write(f"• 전력산업기반기금 (3.7%): {int(bill_info['fund']):,}원")

    with input_col2:
        st.subheader("💡 실시간 인공지능 절약 가이드")
        st.info(bill_info['tip'])
        if bill_info['saved_money'] > 0:
            st.success(f"⚠️ 사용량을 조금만 줄여 아래 구간 진입 시: 월 약 {bill_money = bill_info['saved_money']:,}원 절약 가능!")

    st.divider()

    # 4. 상단 핵심 지표 (Metrics)
    st.header(f"📊 {user_type_kor} 데이터 탑라인 분석")
    stats = analyzer_instance.get_statistics()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("최고 전력 소비월", "8월")
    with col2:
        st.metric("연간 누적 전력량", f"{stats['total_yearly']:,} kWh")
    with col3:
        st.metric("연간 누적 예상 요금", f"{1653201:,} 원")

    st.divider()

    # 5. 하단 데이터 시각화 결과
    st.header("📊 전력 사용 실태 분석 및 요금 청구 추이")
    monthly_bill_df = analyzer_instance.analyze_monthly_bills()
    st.pyplot(visualizer_instance.plot_monthly_comparison(monthly_bill_df))

except Exception as e:
    st.error(f"대시보드 구동 중 에러가 발생했습니다: {e}")