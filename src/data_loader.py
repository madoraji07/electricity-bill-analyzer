import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta


def generate_sample_data(file_path: str, start_date: str = '2025-01-01', days: int = 365) -> str:
    """
    가정(Residential) 및 사업장(Commercial)의 전력 사용량 샘플 CSV 데이터를 생성합니다.
    
    계절별 사용량 패턴(여름/겨울 냉난방 증가)과 주중/주말 패턴을 반영하여
    현실적인 전력 소비 데이터를 생성합니다.
    
    Args:
        file_path (str): 생성된 CSV 파일이 저장될 경로
        start_date (str): 데이터 생성 시작 날짜 (YYYY-MM-DD 형식)
        days (int): 생성할 데이터 일수
    
    Returns:
        str: 생성된 CSV 파일 경로
    """

    # 시작 날짜를 datetime 객체로 변환
    start = datetime.strptime(start_date, '%Y-%m-%d')

    # 날짜 리스트 생성 (start_date부터 days만큼)
    date_list = [start + timedelta(days=x) for x in range(days)]

    data = []

    # 난수 고정 (항상 같은 데이터 생성되도록 설정)
    np.random.seed(42)

    for dt in date_list:

        # 현재 날짜 정보 추출
        month = dt.month
        day_of_week = dt.weekday()  # 0: 월요일 ~ 6: 일요일
        is_weekend = day_of_week >= 5

        # =========================
        # 계절별 가중치 설정
        # =========================
        # 여름(7~8월): 냉방 증가 → 사용량 증가
        # 겨울(12~2월): 난방 증가 → 사용량 증가
        if month in [7, 8]:
            season_mult = 1.5
        elif month in [12, 1, 2]:
            season_mult = 1.3
        else:
            season_mult = 1.0

        # =========================
        # 1. 가정용 전력 사용량 생성
        # =========================
        # 기본 사용량 (일 평균)
        base_res = 10.0

        # 주말에는 집에 있는 시간이 많아 사용량 증가
        weekend_mult_res = 1.2 if is_weekend else 1.0

        # 랜덤 변동성 추가 (현실적인 데이터 생성)
        noise_res = np.random.normal(0, 1.5)

        # 최종 가정용 사용량 계산
        usage_res = round(
            max(3.0, base_res * season_mult * weekend_mult_res + noise_res),
            2
        )

        data.append({
            'Date': dt.strftime('%Y-%m-%d'),
            'Type': 'Residential',
            'Usage_kWh': usage_res
        })

        # =========================
        # 2. 사업장 전력 사용량 생성
        # =========================
        base_com = 45.0

        # 사업장은 주말에 영업 감소
        weekend_mult_com = 0.4 if is_weekend else 1.0

        noise_com = np.random.normal(0, 5.0)

        usage_com = round(
            max(10.0, base_com * season_mult * weekend_mult_com + noise_com),
            2
        )

        data.append({
            'Date': dt.strftime('%Y-%m-%d'),
            'Type': 'Commercial',
            'Usage_kWh': usage_com
        })

    # DataFrame 생성
    df = pd.DataFrame(data)

    # 저장 디렉토리 자동 생성
    dir_name = os.path.dirname(file_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # CSV 저장
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

    print(f"[Success] 샘플 데이터 생성 완료: {file_path}")

    return file_path


def load_data(file_path: str) -> pd.DataFrame:
    """
    CSV 전력 사용량 데이터를 로딩하여 DataFrame으로 반환합니다.
    
    데이터 인코딩 문제(utf-8 / cp949)를 자동으로 처리합니다.
    
    Args:
        file_path (str): CSV 파일 경로
    
    Returns:
        pd.DataFrame: 전처리된 데이터
    """

    # 파일 존재 여부 확인
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

    # CSV 로딩 (utf-8-sig 우선)
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except Exception:
        df = pd.read_csv(file_path, encoding='cp949')

    # 필수 컬럼 검증
    required_cols = {'Date', 'Type', 'Usage_kWh'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"필수 컬럼이 누락되었습니다: {required_cols}")

    # 날짜 형식 변환
    df['Date'] = pd.to_datetime(df['Date'])

    # 날짜 기준 정렬 (분석 안정성 확보)
    df = df.sort_values(by=['Type', 'Date']).reset_index(drop=True)

    return df


def aggregate_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """
    전력 사용량 데이터를 월별 및 사용자 타입별로 집계합니다.
    
    (가정용 / 사업장용 소비 패턴 비교 분석용 데이터 생성)
    
    Args:
        df (pd.DataFrame): load_data()로 불러온 데이터
    
    Returns:
        pd.DataFrame: 월별 집계 결과
    """

    temp_df = df.copy()

    # 연도 / 월 파생 변수 생성
    temp_df['Year'] = temp_df['Date'].dt.year
    temp_df['Month'] = temp_df['Date'].dt.month

    # 월별 + 타입별 집계
    summary = temp_df.groupby(['Year', 'Month', 'Type']).agg(
        Total_Usage_kWh=('Usage_kWh', 'sum'),
        Daily_Average_kWh=('Usage_kWh', 'mean'),
        Max_Usage_kWh=('Usage_kWh', 'max'),
        Days_Count=('Usage_kWh', 'count')
    ).reset_index()

    # 소수점 정리
    summary['Total_Usage_kWh'] = summary['Total_Usage_kWh'].round(2)
    summary['Daily_Average_kWh'] = summary['Daily_Average_kWh'].round(2)
    summary['Max_Usage_kWh'] = summary['Max_Usage_kWh'].round(2)

    return summary


def aggregate_weekly(df: pd.DataFrame) -> pd.DataFrame:
    """
    전력 사용량 데이터를 요일별 + 타입별로 집계합니다.
    
    요일별 소비 패턴 분석 (주중 vs 주말 소비 차이 분석)
    
    Args:
        df (pd.DataFrame): load_data()로 불러온 데이터
    
    Returns:
        pd.DataFrame: 요일별 평균 사용량 데이터
    """

    temp_df = df.copy()

    # 요일 생성 (Monday ~ Sunday)
    temp_df['Day'] = temp_df['Date'].dt.day_name()

    # 타입 + 요일 기준 평균 사용량 계산
    weekly = temp_df.groupby(['Type', 'Day'])['Usage_kWh'].mean().reset_index()

    # 요일 순서 고정 (분석 시 시각적 정렬 목적)
    day_order = [
        'Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday', 'Saturday', 'Sunday'
    ]

    weekly['Day'] = pd.Categorical(weekly['Day'], categories=day_order, ordered=True)

    # 정렬 후 반환
    return weekly.sort_values('Day').reset_index(drop=True).round(2)


# =========================
# 테스트 실행 코드
# =========================
if __name__ == '__main__':

    test_file = 'electricity_usage_test.csv'

    try:
        print("1. 샘플 데이터 생성 중...")
        generate_sample_data(test_file, days=30)

        print("2. 데이터 로딩 중...")
        df = load_data(test_file)

        print("3. 데이터 샘플 확인")
        print(df.head())

        print("\n4. 월별 집계 수행")
        print(aggregate_monthly(df))

    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
            print("\n테스트 파일 삭제 완료")