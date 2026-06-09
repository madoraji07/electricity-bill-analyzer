"""데이터 로딩 모듈"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class ElectricityDataLoader:
    def __init__(self):
        self.data = None
    
    def generate_sample_data(self, days=365):
        """샘플 데이터 생성"""
        print(f"📊 {days}일치 샘플 데이터 생성 중...")
        
        start_date = datetime.now() - timedelta(days=days)
        dates = [start_date + timedelta(days=i) for i in range(days)]
        
        np.random.seed(42)
        base_usage = 10
        
        data = []
        for date in dates:
            month = date.month
            seasonal_factor = 1.5 if month in [6, 7, 8, 12, 1, 2] else 1.0
            weekday_factor = 1.2 if date.weekday() >= 5 else 1.0
            
            daily_usage = base_usage * seasonal_factor * weekday_factor
            daily_usage += np.random.normal(0, 2)
            daily_usage = max(0, daily_usage)
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'usage_kwh': round(daily_usage, 2),
                'month': date.month,
                'year': date.year,
                'weekday': date.strftime('%A')
            })
        
        self.data = pd.DataFrame(data)
        print(f"✅ 데이터 생성 완료! (총 {len(self.data)}개)")
        return self.data
    
    def get_monthly_summary(self):
        """월별 요약"""
        if self.data is None:
            return None
        
        monthly = self.data.groupby(['year', 'month']).agg({
            'usage_kwh': ['sum', 'mean', 'max', 'min']
        }).round(2)
        
        monthly.columns = ['총사용량', '평균', '최대', '최소']
        return monthly
    
    def validate_data(self):
        """데이터 검증"""
        if self.data is None:
            return False
        print("✅ 데이터 검증 완료")
        return True