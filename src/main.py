"""
전기요금 분석 시스템 메인 프로그램
담당자: 팀원3
"""

from data_loader import ElectricityDataLoader
from analyzer import ElectricityAnalyzer
from visualizer import ElectricityVisualizer
import sys

def print_header(title):
    """헤더 출력"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_bill_detail(bill_info):
    """요금 상세 출력"""
    print(f"\n📊 사용량: {bill_info['usage_kwh']} kWh")
    print(f"\n💰 요금 내역:")
    print(f"  - 기본요금: {bill_info['base_charge']:,}원")
    print(f"  - 전력량요금: {bill_info['usage_charge']:,}원")
    
    print(f"\n  구간별 상세:")
    for item in bill_info['breakdown']:
        print(f"    • {item['tier']}: {item['usage']}kWh × {item['rate']}원 = {item['bill']:,}원")
    
    print(f"\n  - 부가세 (10%): {bill_info['vat']:,}원")
    print(f"  - 전력기금 (3.7%): {bill_info['fund']:,}원")
    print(f"\n✨ 총 요금: {bill_info['total']:,}원")

def main():
    """메인 함수"""
    print_header("⚡ 전기요금 분석 시스템")
    
    # 1. 데이터 로딩
    print("\n1️⃣ 데이터 로딩 중...")
    loader = ElectricityDataLoader()
    data = loader.generate_sample_data(days=365)
    print(f"✅ {len(data)}일치 데이터 로딩 완료")
    
    # 2. 분석기 초기화
    analyzer = ElectricityAnalyzer(data)
    visualizer = ElectricityVisualizer(data)
    
    # 3. 통계 정보
    print_header("📈 사용량 통계")
    stats = analyzer.get_statistics()
    print(f"\n월평균 사용량: {stats['avg_monthly']} kWh")
    print(f"최대 사용량: {stats['max_monthly']} kWh")
    print(f"최소 사용량: {stats['min_monthly']} kWh")
    print(f"연간 총 사용량: {stats['total_yearly']} kWh")
    
    # 4. 최근 월 요금 계산
    print_header("💰 이번 달 예상 요금")
    current_month_usage = data[data['month'] == data['month'].iloc[-1]]['usage_kwh'].sum()
    bill_info = analyzer.calculate_bill(current_month_usage)
    print_bill_detail(bill_info)
    
    # 5. 절약 팁
    print_header("💡 절약 팁")
    tips = analyzer.get_saving_tips(current_month_usage)
    for tip in tips:
        print(f"  {tip}")
    
    # 6. 시각화
    print_header("📊 데이터 시각화")
    print("\n시각화를 시작합니다...")
    
    try:
        print("\n1) 최근 30일 사용량 그래프")
        visualizer.plot_daily_usage(days=30)
        
        print("\n2) 월별 사용량 및 요금 비교")
        visualizer.plot_monthly_comparison(analyzer)
        
        print("\n3) 요일별 사용 패턴")
        visualizer.plot_weekday_pattern()
        
        print("\n4) 요금 구성 차트")
        visualizer.plot_bill_breakdown(bill_info)
        
    except Exception as e:
        print(f"⚠️ 시각화 중 오류 발생: {e}")
    
    print_header("✅ 분석 완료")
    print("\n프로그램을 종료합니다.\n")

if __name__ == "__main__":
    main()