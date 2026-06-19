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

st.title("⚡ 전기요금 분석 시스템 대시보드")
st.markdown("가정 및 사업장의 전력 사용량 데이터를 기반으로 한전 누진제를 적용한 정밀 요금 분석 플랫폼입니다.")
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
    
    # ⚙️ 사이드바 컨트롤러 설정
    st.sidebar.header("⚙️ 시스템 컨트롤러")
    user_type = st.sidebar.selectbox("🏠 분석 대상 데이터 선택", ["Residential", "Commercial"])
    
    st.sidebar.divider()
    
    # 💡 [영상 촬영용 핵심 기능] 사용자가 직접 전력량을 입력해볼 수 있는 창 추가!
    st.sidebar.subheader("🔢 실시간 요금 계산기")
    data = raw_data[raw_data['Type'] == user_type].copy()
    current_month = data['Date'].dt.month.iloc[-1]
    default_usage = float(round(data[data['Date'].dt.month == current_month]['Usage_kWh'].sum(), 2))
    
    # 사용자가 직접 입력하거나 버튼으로 조절 가능 (기본값은 데이터의 당월 사용량)
    user_input_usage = st.sidebar.number_input(
        "월간 전력 사용량 입력(kWh)", 
        min_value=0.0, 
        max_value=2000.0, 
        value=default_usage, 
        step=10.0
    )
    
    # 팀원들 클래스 정상 연결
    analyzer_instance = az.ElectricityAnalyzer(data)
    visualizer_instance = ElectricityVisualizer(data)

    # 3. 상단 핵심 지표 (Metrics)
    st.header(f"📈 {user_type} 기본 소비 패턴 통계 (연간)")
    stats = analyzer_instance.get_statistics()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("월평균 사용량", f"{stats['avg_monthly']:,} kWh")
    with col2:
        st.metric("당해 최고 사용량", f"{stats['max_monthly']:,} kWh")
    with col3:
        st.metric("당해 최저 사용량", f"{stats['min_monthly']:,} kWh")
    with col4:
        st.metric("연간 총 사용량", f"{stats['total_yearly']:,} kWh")

    st.divider()

    # 4. 당월 요금 청구서 및 AI 절약 팁 (사용자가 입력한 값으로 실시간 연산!)
    left_col, right_col = st.columns(2)
    
    # 💡 사용자가 사이드바에서 바꾼 입력값(user_input_usage)을 넣어 실시간으로 계산하게 변경!
    bill_info = az.calculate_single_bill(user_input_usage)
    raw_breakdown = analyzer_instance.calculate_bill(user_input_usage)

    with left_col:
        st.header("💰 실시간 예상 청구 요금")
        st.subheader(f"최종 청구 금액: {int(bill_info['total_bill']):,} 원")
        st.caption(f"현재 설정된 사용량: {user_input_usage:,.2f} kWh (주택용 고압 누진제 기준)")
        
        with st.expander("🔍 누진제 요금 상세 내역서 확인"):
            st.write(f"• 기본 요금: {int(bill_info['base_price']):,}원")
            st.write(f"• 전력량 요금: {int(bill_info['energy_price']):,}원")
            for item in raw_breakdown['breakdown']:
                st.write(f"  - {item['tier']}: {item['usage']}kWh × {item['rate']}원 = {int(item['bill']):,}원")
            st.write(f"• 부가가치세 (10%): {int(bill_info['vat']):,}원")
            st.write(f"• 전력산업기반기금 (3.7%): {int(bill_info['fund']):,}원")

    with right_col:
        st.header("💡 맞춤형 에너지 가이드")
        st.info(bill_info['tip'])
        
        if bill_info['saved_money'] > 0:
            st.success(f"💰 하위 구간 진입 시 예상 절감액: 월 약 {bill_info['saved_money']:,}원 절약 가능")
            
        tips_list = analyzer_instance.get_saving_tips(user_input_usage)
        for extra_tip in tips_list[2:]:
            st.write(f"• {extra_tip}")

    st.divider()

    # 5. 하단 데이터 시각화 (탭 구조)
    st.header("📊 데이터 시각화 및 패턴 분석")
    tab1, tab2, tab3 = st.tabs(["📅 월별 분석", "📆 요일별 소비 성향", "🍕 요금 구성 비율"])

    with tab1:
        st.subheader("연간 월별 사용량 및 요금 추이")
        monthly_bill_df = analyzer_instance.analyze_monthly_bills()
        st.pyplot(visualizer_instance.plot_monthly_comparison(monthly_bill_df))

    with tab2:
        st.subheader("요일별 평균 전력 소비 패턴")
        weekly_usage_df = dl.aggregate_weekly(data)
        st.pyplot(visualizer_instance.plot_weekday_pattern(weekly_usage_df))

    with tab3:
        st.subheader("현재 입력한 사용량 기준 요금 항목별 지출 비중")
        col_center, _ = st.columns([2, 1])
        with col_center:
            st.pyplot(visualizer_instance.plot_bill_breakdown(bill_info))

except Exception as e:
    st.error(f"대시보드 구동 중 에러가 발생했습니다: {e}")