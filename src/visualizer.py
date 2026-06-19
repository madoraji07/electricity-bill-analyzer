import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# 한글 폰트 설정 (Windows/Mac 공통 최적화)
plt.rcParams['font.family'] = 'Malgun Gothic' if plt.rcParams['font.family'] == ['sans-serif'] else 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

class ElectricityVisualizer:
    """전기 사용량 데이터 시각화 클래스"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        # 시각화를 위해 날짜/요일 데이터 처리 (초한 님의 data_loader 규격 반영)
        if 'Date' in self.data.columns:
            self.data['weekday'] = self.data['Date'].dt.day_name()
        sns.set_style("whitegrid")
    
    def plot_monthly_comparison(self, monthly_df: pd.DataFrame):
        """월별 사용량 및 요금 비교 그래프 반환"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 월별 사용량
        ax1.bar(monthly_df['Month'].astype(str), monthly_df['Total_Usage_kWh'], color='steelblue', alpha=0.7)
        ax1.set_title('월별 전기 사용량', fontsize=12, fontweight='bold')
        
        # 월별 요금
        ax2.bar(monthly_df['Month'].astype(str), monthly_df['Calculated_Bill'], color='coral', alpha=0.7)
        ax2.set_title('월별 전기 요금', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        return fig # plt.show() 대신 fig를 반환해야 Streamlit에서 보입니다!
    
    def plot_weekday_pattern(self, weekly_df: pd.DataFrame):
        """요일별 사용 패턴 시각화"""
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig = plt.figure(figsize=(8, 5))
        colors = ['#FF6B6B' if day in ['Saturday', 'Sunday'] else '#4ECDC4' for day in weekly_order]
        plt.bar(weekly_df['Day'], weekly_df['Usage_kWh'], color=colors, alpha=0.7)
        
        plt.title('요일별 평균 전기 사용량', fontsize=14, fontweight='bold')
        plt.xticks(range(7), ['월', '화', '수', '목', '금', '토', '일'])
        plt.grid(axis='y', alpha=0.3)
        return fig
    
    def plot_bill_breakdown(self, bill_info: dict):
        """요금 구성 파이 차트 반환"""
        labels = ['전력량 요금', 'VAT', '전력기금', '기본요금']
        sizes = [bill_info['energy_price'], bill_info['vat'], bill_info['fund'], bill_info['base_price']]
        
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90, 
               colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'], explode=(0.1, 0, 0, 0))
        ax.set_title(f'전기요금 상세 구성 (총 {bill_info["total_bill"]:,}원)', fontsize=14, fontweight='bold')
        return fig