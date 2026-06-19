import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# =========================
# 📌 한글 폰트 설정
# =========================
# Windows / Mac 환경 모두 대응하기 위한 기본 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic' if plt.rcParams['font.family'] == ['sans-serif'] else 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False


class ElectricityVisualizer:
    """
    전기 사용량 데이터를 시각화하는 클래스

    - 월별 사용량 비교
    - 요일별 소비 패턴 분석
    - 전기요금 구성 시각화
    """

    def __init__(self, data: pd.DataFrame):
        """
        Args:
            data (pd.DataFrame): 전처리된 전력 사용량 데이터
        """

        # 원본 데이터 보호를 위해 복사본 생성
        self.data = data.copy()

        # 날짜 기반 분석을 위해 요일 컬럼 생성
        if 'Date' in self.data.columns:
            self.data['weekday'] = self.data['Date'].dt.day_name()

        # seaborn 스타일 적용 (그래프 시각적 품질 향상)
        sns.set_style("whitegrid")

    # ==========================================================
    # 📊 1. 월별 사용량 / 요금 비교 그래프
    # ==========================================================
    def plot_monthly_comparison(self, monthly_df: pd.DataFrame):
        """
        월별 전력 사용량과 요금을 비교하는 막대 그래프

        Args:
            monthly_df (pd.DataFrame): aggregate_monthly 결과 데이터
        """

        # subplot 생성 (2개 그래프)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # =========================
        # 월별 사용량 그래프
        # =========================
        ax1.bar(
            monthly_df['Month'].astype(str),
            monthly_df['Total_Usage_kWh'],
            color='steelblue',
            alpha=0.7
        )
        ax1.set_title('월별 전기 사용량', fontsize=12, fontweight='bold')
        ax1.set_xlabel('월')
        ax1.set_ylabel('kWh')

        # =========================
        # 월별 요금 그래프
        # =========================
        # analyzer 결과 컬럼 기준 (Calculated_Bill)
        if 'Calculated_Bill' in monthly_df.columns:
            bill_col = 'Calculated_Bill'
        else:
            # fallback (안전장치)
            bill_col = monthly_df.columns[-1]

        ax2.bar(
            monthly_df['Month'].astype(str),
            monthly_df[bill_col],
            color='coral',
            alpha=0.7
        )
        ax2.set_title('월별 전기 요금', fontsize=12, fontweight='bold')
        ax2.set_xlabel('월')
        ax2.set_ylabel('원')

        plt.tight_layout()
        return fig

    # ==========================================================
    # 📊 2. 요일별 사용 패턴 그래프
    # ==========================================================
    def plot_weekday_pattern(self, weekly_df: pd.DataFrame):
        """
        요일별 평균 전력 사용량을 시각화

        Args:
            weekly_df (pd.DataFrame): aggregate_weekly 결과
        """

        # 요일 순서 고정 (분석 정확도 + 시각 정렬)
        weekday_order = [
            'Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday', 'Sunday'
        ]

        # 주말/평일 색상 구분
        colors = [
            '#FF6B6B' if day in ['Saturday', 'Sunday'] else '#4ECDC4'
            for day in weekly_df['Day']
        ]

        fig, ax = plt.subplots(figsize=(8, 5))

        ax.bar(
            weekly_df['Day'],
            weekly_df['Usage_kWh'],
            color=colors,
            alpha=0.7
        )

        ax.set_title('요일별 평균 전기 사용량', fontsize=14, fontweight='bold')

        # 한글 요일 표시
        ax.set_xticks(range(7))
        ax.set_xticklabels(['월', '화', '수', '목', '금', '토', '일'])

        ax.set_ylabel('kWh')
        ax.grid(axis='y', alpha=0.3)

        return fig

    # ==========================================================
    # 📊 3. 요금 구성 파이차트
    # ==========================================================
    def plot_bill_breakdown(self, bill_info: dict):
        """
        전기요금 구성 요소를 파이차트로 시각화

        Args:
            bill_info (dict): calculate_bill 결과
        """

        labels = ['전력량 요금', 'VAT', '전력기금', '기본요금']

        sizes = [
            bill_info['energy_price'],
            bill_info['vat'],
            bill_info['fund'],
            bill_info['base_price']
        ]

        fig, ax = plt.subplots(figsize=(7, 7))

        ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            shadow=True,
            startangle=90,
            colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'],
            explode=(0.1, 0, 0, 0)
        )

        ax.set_title(
            f'전기요금 상세 구성 (총 {bill_info["total_bill"]:,}원)',
            fontsize=14,
            fontweight='bold'
        )

        return fig