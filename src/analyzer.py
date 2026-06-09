"""
전기요금 계산 및 분석 모듈
담당자: 팀원2
"""

import pandas as pd
import numpy as np

class ElectricityAnalyzer:
    """전기요금 계산 및 분석 클래스"""
    
    # 한국전력 주택용 누진제 요금표 (2024년 기준 가정)
    RATE_TABLE = [
        {'min': 0, 'max': 200, 'rate': 112.0, 'base': 910},
        {'min': 200, 'max': 400, 'rate': 206.6, 'base': 1600},
        {'min': 400, 'max': float('inf'), 'rate': 299.3, 'base': 7300}
    ]
    
    def __init__(self, data):
        """
        Args:
            data (pd.DataFrame): 전기 사용량 데이터
        """
        self.data = data
    
    def calculate_bill(self, usage_kwh):
        """
        누진제 기반 전기요금 계산
        
        Args:
            usage_kwh (float): 월간 전기 사용량 (kWh)
            
        Returns:
            dict: 요금 계산 결과
        """
        total_bill = 0
        usage_remaining = usage_kwh
        breakdown = []
        
        for tier in self.RATE_TABLE:
            if usage_remaining <= 0:
                break
            
            # 해당 구간 사용량 계산
            tier_range = tier['max'] - tier['min']
            tier_usage = min(usage_remaining, tier_range)
            
            # 구간별 요금 계산
            tier_bill = tier_usage * tier['rate']
            total_bill += tier_bill
            
            breakdown.append({
                'tier': f"{tier['min']}-{tier['max']}kWh",
                'usage': round(tier_usage, 2),
                'rate': tier['rate'],
                'bill': round(tier_bill, 0)
            })
            
            usage_remaining -= tier_usage
        
        # 기본요금 추가
        base_charge = self._get_base_charge(usage_kwh)
        total_bill += base_charge
        
        # 부가세(10%) 및 전력기금(3.7%) 추가
        vat = total_bill * 0.1
        fund = total_bill * 0.037
        final_bill = total_bill + vat + fund
        
        return {
            'usage_kwh': round(usage_kwh, 2),
            'base_charge': round(base_charge, 0),
            'usage_charge': round(total_bill, 0),
            'vat': round(vat, 0),
            'fund': round(fund, 0),
            'total': round(final_bill, 0),
            'breakdown': breakdown
        }
    
    def _get_base_charge(self, usage_kwh):
        """기본요금 산정"""
        for tier in self.RATE_TABLE:
            if usage_kwh <= tier['max']:
                return tier['base']
        return self.RATE_TABLE[-1]['base']
    
    def analyze_monthly_bills(self):
        """
        월별 전기요금 분석
        
        Returns:
            pd.DataFrame: 월별 요금 분석 결과
        """
        monthly_data = self.data.groupby(['year', 'month'])['usage_kwh'].sum()
        
        results = []
        for (year, month), usage in monthly_data.items():
            bill_info = self.calculate_bill(usage)
            results.append({
                'year': year,
                'month': month,
                'usage_kwh': bill_info['usage_kwh'],
                'total_bill': bill_info['total']
            })
        
        return pd.DataFrame(results)
    
    def get_statistics(self):
        """
        사용량 통계 분석
        
        Returns:
            dict: 통계 정보
        """
        monthly_usage = self.data.groupby(['year', 'month'])['usage_kwh'].sum()
        
        return {
            'avg_monthly': round(monthly_usage.mean(), 2),
            'max_monthly': round(monthly_usage.max(), 2),
            'min_monthly': round(monthly_usage.min(), 2),
            'std_monthly': round(monthly_usage.std(), 2),
            'total_yearly': round(self.data['usage_kwh'].sum(), 2)
        }
    
    def get_saving_tips(self, current_usage):
        """
        절약 팁 제공
        
        Args:
            current_usage (float): 현재 월 사용량
            
        Returns:
            list: 절약 팁 리스트
        """
        tips = []
        
        if current_usage > 400:
            tips.append("⚠️ 누진 3구간입니다. 사용량을 400kWh 이하로 줄이면 큰 절약이 가능합니다.")
            potential_saving = self.calculate_bill(current_usage)['total'] - \
                             self.calculate_bill(400)['total']
            tips.append(f"💰 400kWh로 줄이면 약 {potential_saving:,.0f}원 절약 가능")
        elif current_usage > 200:
            tips.append("⚠️ 누진 2구간입니다. 200kWh 이하로 유지하면 요금을 크게 절감할 수 있습니다.")
        else:
            tips.append("✅ 누진 1구간입니다. 현재 사용 패턴을 유지하세요!")
        
        tips.append("💡 대기전력 차단으로 월 10-15% 절약 가능")
        tips.append("🌡️ 냉난방 온도 1도 조절로 월 5% 절약 가능")
        tips.append("💡 LED 조명 교체로 조명 전력 80% 절감")
        
        return tips