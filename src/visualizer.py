"""
데이터 시각화 모듈
담당자: 팀원3
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows
# plt.rcParams['font.family'] = 'AppleGothic'  # Mac
plt.rcParams['axes.unicode_minus'] = False

class ElectricityVisualizer:
    """전기 사용량 데이터 시각화 클래스"""
    
    def __init__(self, data):
        """
        Args:
            data (pd.DataFrame): 전기 사용량 데이터
        """
        self.data = data
        sns.set_style("whitegrid")
    
    def plot_daily_usage(self, days=30):
        """
        일별 사용량 그래프
        
        Args:
            days (int): 표시할 일수
        """
        recent_data = self.data.tail(days)
        
        plt.figure(figsize=(12, 6))
        plt.plot(recent_data['date'], recent_data['usage_kwh'], 
                marker='o', linewidth=2, markersize=6)
        plt.title(f'최근 {days}일 전기 사용량', fontsize=16, fontweight='bold')
        plt.xlabel('날짜', fontsize=12)
        plt.ylabel('사용량 (kWh)', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def plot_monthly_comparison(self, analyzer):
        """
        월별 사용량 및 요금 비교
        
        Args:
            analyzer (ElectricityAnalyzer): 분석기 객체
        """
        monthly_bills = analyzer.analyze_monthly_bills()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 월별 사용량
        months = [f"{row['year']}-{row['month']:02d}" for _, row in monthly_bills.iterrows()]
        ax1.bar(months, monthly_bills['usage_kwh'], color='steelblue', alpha=0.7)
        ax1.set_title('월별 전기 사용량', fontsize=14, fontweight='bold')
        ax1.set_xlabel('월', fontsize=12)
        ax1.set_ylabel('사용량 (kWh)', fontsize=12)
        ax1.tick_params(axis='x', rotation=45)
        
        # 월별 요금
        ax2.bar(months, monthly_bills['total_bill'], color='coral', alpha=0.7)
        ax2.set_title('월별 전기 요금', fontsize=14, fontweight='bold')
        ax2.set_xlabel('월', fontsize=12)
        ax2.set_ylabel('요금 (원)', fontsize=12)
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    def plot_weekday_pattern(self):
        """요일별 사용 패턴"""
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                        'Friday', 'Saturday', 'Sunday']
        weekday_avg = self.data.groupby('weekday')['usage_kwh'].mean()
        weekday_avg = weekday_avg.reindex(weekday_order)
        
        plt.figure(figsize=(10, 6))
        colors = ['#FF6B6B' if day in ['Saturday', 'Sunday'] else '#4ECDC4' 
                 for day in weekday_order]
        plt.bar(range(7), weekday_avg.values, color=colors, alpha=0.7)
        plt.title('요일별 평균 전기 사용량', fontsize=16, fontweight='bold')
        plt.xlabel('요일', fontsize=12)
        plt.ylabel('평균 사용량 (kWh)', fontsize=12)
        plt.xticks(range(7), ['월', '화', '수', '목', '금', '토', '일'])
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def plot_bill_breakdown(self, bill_info):
        """
        요금 구성 파이 차트
        
        Args:
            bill_info (dict): 요금 계산 결과
        """
        labels = ['전력량 요금', 'VAT', '전력기금', '기본요금']
        sizes = [
            bill_info['usage_charge'],
            bill_info['vat'],
            bill_info['fund'],
            bill_info['base_charge']
        ]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
        explode = (0.1, 0, 0, 0)
        
        plt.figure(figsize=(10, 8))
        plt.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=90)
        plt.title(f'전기요금 구성 (총 {bill_info["total"]:,.0f}원)', 
                 fontsize=16, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()