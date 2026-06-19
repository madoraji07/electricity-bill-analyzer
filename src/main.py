import streamlit as st
import data_loader as dl      # 초한(홍길동)님 모듈
import analyzer as az        # 분석 모듈
from visualizer import ElectricityVisualizer  # 시각화 모듈
import os

# 1. 페이지 레이아웃 및 디자인 설정
st.set_page_config(
    page_title="전기요금 분석 시스템",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ AI 전기요금 분석 및 인터랙티브 절약 대시보드")
st.markdown("본 웹 어플리케이션은 파이썬 백엔드 모듈을 기반으로 유기적으로 동작하는 종합 데이터 분석 시스템입니다.")
st.divider()

# 2. 데이터 로드 내장
@st.cache_data
def get_system_data():
    csv_file = 'electricity_usage_data.csv'
    if not os.path.exists(csv_file):
        dl.generate_sample_data(csv_file, days=365)
    return dl.load_data(csv_file)

try:
    raw_data = get_system_data()
    
    # ⚙️ 왼쪽 사이드바 컨트롤러 설정
    st.sidebar.header("⚙️ 시스템 대시보드 제어판")
    
    # 기존 한글 셀렉트박스 유지
    user_type_kor = st.sidebar.selectbox("🎯 분석할 사용자 타입 선택", ["가정용", "사업장용"])
    user_type = "Residential" if user_type_kor == "가정용" else "Commercial"
    
    st.sidebar.divider()
    
    # 💡 [핵심] 사용자가 직접 숫자를 조절할 수 있는 실시간 요금 입력창 배치!
    st.sidebar.subheader("🔢 실시간 요금 시뮬레이터")
    data = raw_data[raw_data['Type'] == user_type].copy()
    current_month = data['Date'].dt.month.iloc[-1]
    default_usage = float(round(data[data['Date'].dt.month == current_month]['Usage_kWh'].sum(), 2))
    
    user_input_usage = st.sidebar.number_input(
        "이번 달 전력 사용량 입력(kWh)", 
        min_value=0.0, 
        max_value=2000.0, 
        value=350.0,  # 영상 찍기 딱 좋은 기본값 세팅
        step=10.0
    )
    
    # 팀원들 클래스 정상 연결
    analyzer_instance = az.ElectricityAnalyzer(data)
    visualizer_instance = ElectricityVisualizer(data)

    # 3. 상단 핵심 지표 (Metrics) - 캡처화면 양식 그대로 유지
    st.header(f"📊 {user_type_kor} 데이터 탑라인 분석")
    stats = analyzer_instance.get_statistics()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("최고 전력 소비월", f"{stats['max_monthly_month']}월" if 'max_monthly_month' in stats else "8월")
    with col2:
        st.metric("연간 누적 전력량", f"{stats['total_yearly']:,} kWh")
    with col3:
        st.metric("연간 누적 예상 요금", f"{int(stats['total_yearly'] * 249):,} 원") # 샘플 요금 지표

    st.divider()

    # 4. 🔥 [여기가 빠졌었습니다!] 실시간 입력에 따라 실시간으로 변하는 요금 청구서 내역서
    st.header("💰 실시간 사용자 입력 요금 시뮬레이션 결과")
    
    bill_info = az.calculate_single_bill(user_input_usage)
    raw_breakdown = analyzer_instance.calculate_bill(user_input_usage)
    
    left_col, right_col = st.columns(2)
    with left_col:
        st.subheader(f"현재 입력 사용량 요금: 총 {int(bill_info['total_bill']):,} 원")
        st.caption(f"실시간 설정값: {user_input_usage:,.1f} kWh (주택용 고압 누진제 기준)")
        
        with st.expander("🔍 누진제 구간별 상세 내역서 펼치기"):
            st.write(f"• 기본 요금: {int(bill_info['base_price']):,}원")
            st.write(f"• 전력량 요금(구간 합산): {int(bill_info['energy_price']):,}원")
            if 'breakdown' in raw_breakdown:
                for item in raw_breakdown['breakdown']:
                    st.write(f"  - {item['tier']}: {item['usage']}kWh × {item['rate']}원 = {int(item['bill']):,}원")
            st.write(f"• 부가가치세 (10%): {int(bill_info['vat']):,}원")
            st.write(f"• 전력산업기반기금 (3.7%): {int(bill_info['fund']):,}원")

    with right_col:
        st.subheader("💡 실시간 인공지능 절약 팁")
        st.info(bill_info['tip'])
        if bill_info['saved_money'] > 0:
            st.success(f"⚠️ 사용량을 조금만 줄여 아래 구간 진입 시: 월 약 {bill_info['saved_money']:,}원 절약 가능!")

    st.divider()

    # 5. 하단 데이터 시각화 결과 (기존 그래프 출력 코드)
    graph_col1, graph_col2 = st.columns(2)
    
    with graph_col1:
        st.subheader("📊 전력 사용 실실태 분석 결과")
        monthly_bill_df = analyzer_instance.analyze_monthly_bills()
        st.pyplot(visualizer_instance.plot_monthly_comparison(monthly_bill_df))

    with graph_col2:
        st.subheader("💸 누진 요금 청구 시뮬레이션")
        # 요금 세부 차트 혹은 요일별 차트 바인딩
        st.pyplot(visualizer_instance.plot_bill_breakdown(bill_info))

except Exception as e:
    st.error(f"대시보드 구동 중 에러가 발생했습니다: {e}")