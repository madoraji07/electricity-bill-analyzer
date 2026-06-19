import pandas as pd
import numpy as np

class ElectricityAnalyzer:
    """전기요금 계산 및 데이터 분석을 수행하는 핵심 모듈 클래스"""
    
    # 한국전력 주택용 고압 누진제 요금표 표준화 규격 데이터
    RATE_TABLE = [
        {'min': 0, 'max': 200, 'rate': 120.0, 'base': 910},
        {'min': 200, 'max': 400, 'rate': 214.0, 'base': 1600},
        {'min': 400, 'max': float('inf'), 'rate': 307.0, 'base': 7300}
    ]
    
    def __init__(self, data: pd.DataFrame):
        """
        Args:
            data (pd.DataFrame): 전처리 완료된 전기 사용량 시계열 데이터
        """
        self.data = data.copy()
        # 데이터프레임 내 Date 컬럼 감지 시 연도 및 월 변수 자동 바인딩
        if 'Date' in self.data.columns:
            self.data['Year'] = self.data['Date'].dt.year
            self.data['Month'] = self.data['Date'].dt.month
    
    def calculate_bill(self, usage_kwh: float) -> dict:
        """
        누진 구간별 알고리즘을 적용하여 상세 전기요금을 정밀 계산합니다.
        
        Args:
            usage_kwh (float): 월간 총 전력 사용량
            
        Returns:
            dict: 기본요금, 전력량요금, 세금(부가세/기금) 및 청구 총액 명세
        """
        total_bill = 0
        usage_remaining = usage_kwh
        breakdown = []
        
        for tier in self.RATE_TABLE:
            if usage_remaining <= 0:
                break
            
            tier_range = tier['max'] - tier['min']
            tier_usage = min(usage_remaining, tier_range)
            
            tier_bill = tier_usage * tier['rate']
            total_bill += tier_bill
            
            breakdown.append({
                'tier': f"{tier['min']}-{tier['max']}kWh",
                'usage': round(tier_usage, 2),
                'rate': tier['rate'],
                'bill': round(tier_bill, 0)
            })
            
            usage_remaining -= tier_usage
        
        base_charge = self._get_base_charge(usage_kwh)
        pure_usage_charge = total_bill
        
        total_bill += base_charge
        
        # 부가세(10%) 및 전력기금(3.7%) 복합 연산
        vat = total_bill * 0.1
        fund = total_bill * 0.037
        final_bill = total_bill + vat + fund
        
        return {
            'usage_kwh': round(usage_kwh, 2),
            'base_charge': round(base_charge, 0),
            'usage_charge': round(pure_usage_charge, 0),
            'vat': round(vat, 0),
            'fund': round(fund, 0),
            'total': round(final_bill, 0),
            'breakdown': breakdown
        }
    
    def _get_base_charge(self, usage_kwh: float) -> int:
        """기본요금 구간 매핑 내부 메서드"""
        for tier in self.RATE_TABLE:
            if usage_kwh <= tier['max']:
                return tier['base']
        return self.RATE_TABLE[-1]['base']
    
    def analyze_monthly_bills(self) -> pd.DataFrame:
        """
        월별 누적 사용량을 집계하고 요금 분석 결과 데이터프레임을 생성합니다.
        
        Returns:
            pd.DataFrame: 연도, 월, 사용량, 청구 금액이 집계된 데이터프레임
        """
        monthly_data = self.data.groupby(['Year', 'Month'])['Usage_kWh'].sum()
        
        results = []
        for (year, month), usage in monthly_data.items():
            bill_info = self.calculate_bill(usage)
            results.append({
                'Year': year,
                'Month': month,
                'Total_Usage_kWh': bill_info['usage_kwh'],
                'Calculated_Bill': bill_info['total']
            })
        
        return pd.DataFrame(results)
    
    def get_statistics(self) -> dict:
        """월별 사용량에 대한 기술 통계 지표를 도출합니다."""
        monthly_usage = self.data.groupby(['Year', 'Month'])['Usage_kWh'].sum()
        
        return {
            'avg_monthly': round(monthly_usage.mean(), 2),
            'max_monthly': round(monthly_usage.max(), 2),
            'min_monthly': round(monthly_usage.min(), 2),
            'std_monthly': round(monthly_usage.std(), 2),
            'total_yearly': round(self.data['Usage_kWh'].sum(), 2)
        }
    
    def get_saving_tips(self, current_usage: float) -> list:
        """사용량 정량 분석에 기반한 에너지 절약 의사결정 가이드를 반환합니다."""
        tips = []
        bill_info = self.calculate_bill(current_usage)
        
        if current_usage > 400:
            tips.append("🚨 누진 3구간 초과 상태입니다. 가전제품 제어를 통한 400kWh 이하 저감이 시급합니다.")
            potential_saving = bill_info['total'] - self.calculate_bill(400)['total']
            tips.append(f"💰 사용량을 400kWh 이하로 조정 시, 다음 달 청구 금액 기준 약 {potential_saving:,.0f}원 절감 효과 발생.")
        elif current_usage > 200:
            tips.append("💡 누진 2구간 상태입니다. 200kWh 이하 저전력 구간 진입 시 기본요금 단가가 대폭 하향 조정됩니다.")
            potential_saving = bill_info['total'] - self.calculate_bill(200)['total']
            tips.append(f"💰 사용량을 200kWh 이하로 조정 시, 다음 달 청구 금액 기준 약 {potential_saving:,.0f}원 절감 효과 발생.")
        else:
            tips.append("🌱 현재 누진 1구간(최저 단가) 내에서 안정적인 소비 패턴을 유지하고 있습니다.")
        
        tips.append("🔌 대기전력 발생원 차단을 통해 월평균 소비 전력의 약 10-15% 추가 절감 가능.")
        tips.append("🌡️ 하절기 적정 실내 냉방 온도(26°C) 준수 시 전력비 변동 요인 통제 가능.")
        
        return tips

# -------------------------------------------------------------
# Streamlit 대시보드 연동을 위한 인터페이스 레이어 함수
# -------------------------------------------------------------
def calculate_single_bill(usage: float) -> dict:
    """단일 사용량 입력에 따른 요금 산정 인터페이스 함수"""
    analyzer = ElectricityAnalyzer(pd.DataFrame())
    res = analyzer.calculate_bill(usage)
    tips = analyzer.get_saving_tips(usage)
    
    target_tier = 200 if usage <= 400 else 400
    saved_money = int(res['total'] - analyzer.calculate_bill(target_tier)['total']) if usage > 200 else 0
    
    return {
        "base_price": res['base_charge'],
        "energy_price": res['usage_charge'],
        "vat": res['vat'],
        "fund": res['fund'],
        "total_bill": res['total'],
        "tip": tips[0],
        "saved_money": saved_money
    }

def calculate_bill(monthly_df: pd.DataFrame) -> pd.DataFrame:
    """월별 집계 데이터프레임 구조 연동 인터페이스 함수"""
    temp_df = monthly_df.copy()
    temp_df['Usage_kWh'] = temp_df['Total_Usage_kWh']
    
    analyzer = ElectricityAnalyzer(temp_df)
    return analyzer.analyze_monthly_bills()