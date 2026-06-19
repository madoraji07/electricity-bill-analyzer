import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_sample_data(file_path: str, start_date: str = '2025-01-01', days: int = 365) -> str:
    """
    가정(Residential) 및 사업장(Commercial)의 전력 사용량 샘플 CSV 데이터를 생성합니다.
    계절별 사용량 패턴(여름/겨울 냉난방 증가)과 주중/주말 패턴을 반영합니다.
    
    Args:
        file_path (str): 저장할 CSV 파일 경로
        start_date (str): 시작 날짜 (YYYY-MM-DD)
        days (int): 생성할 날짜 수
        
    Returns:
        str: 생성된 파일 경로
    """
    start = datetime.strptime(start_date, '%Y-%m-%d')
    date_list = [start + timedelta(days=x) for x in range(days)]
    
    data = []
    
    # 난수 고정을 위해 시드 설정
    np.random.seed(42)
    
    for dt in date_list:
        month = dt.month
        day_of_week = dt.weekday()  # 0: 월요일, 6: 일요일
        is_weekend = day_of_week >= 5
        
        # 계절별 가중치 설정 (여름 7~8월, 겨울 12~2월에 사용량 증가)
        if month in [7, 8]:
            season_mult = 1.5
        elif month in [12, 1, 2]:
            season_mult = 1.3
        else:
            season_mult = 1.0
            
        # 1. 가정용 (Residential) 사용량 생성
        # 기본 사용량: 8 ~ 15 kWh/일 (누진세 구간을 고려해 월 200~400kWh 수준 타겟)
        base_res = 10.0
        # 주말에는 집에 머무는 시간이 많아 사용량 증가
        weekend_mult_res = 1.2 if is_weekend else 1.0
        # 랜덤 변동성 추가 (정규분포)
        noise_res = np.random.normal(0, 1.5)
        usage_res = round(max(3.0, (base_res * season_mult * weekend_mult_res) + noise_res), 2)
        
        data.append({
            'Date': dt.strftime('%Y-%m-%d'),
            'Type': 'Residential',
            'Usage_kWh': usage_res
        })
        
        # 2. 사업장용 (Commercial) 사용량 생성
        # 기본 사용량: 30 ~ 60 kWh/일
        base_com = 45.0
        # 주말에는 휴무 또는 단축 영업으로 사용량 감소
        weekend_mult_com = 0.4 if is_weekend else 1.0
        # 랜덤 변동성 추가
        noise_com = np.random.normal(0, 5.0)
        usage_com = round(max(10.0, (base_com * season_mult * weekend_mult_com) + noise_com), 2)
        
        data.append({
            'Date': dt.strftime('%Y-%m-%d'),
            'Type': 'Commercial',
            'Usage_kWh': usage_com
        })
        
    df = pd.DataFrame(data)
    
    # 디렉토리가 없으면 생성
    dir_name = os.path.dirname(file_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"[Success] 샘플 데이터가 성공적으로 생성되었습니다: {file_path}")
    return file_path

def load_data(file_path: str) -> pd.DataFrame:
    """
    CSV 데이터 파일을 로딩하여 pandas DataFrame으로 반환합니다.
    
    Args:
        file_path (str): 읽어올 CSV 파일 경로
        
    Returns:
        pd.DataFrame: 전처리된 데이터프레임
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
        
    try:
        # utf-8-sig로 읽어서 한글 깨짐 방지 및 BOM 제거
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except Exception as e:
        # 혹시 다른 인코딩인 경우 대응
        try:
            df = pd.read_csv(file_path, encoding='cp949')
        except Exception:
            raise ValueError(f"CSV 파일을 읽는 중 오류가 발생했습니다: {str(e)}")
            
    # 필수 컬럼 체크
    required_cols = {'Date', 'Type', 'Usage_kWh'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV 파일에 필수 컬럼이 누락되었습니다. 필요 컬럼: {required_cols}")
        
    # 날짜 데이터 처리 및 정렬
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by=['Type', 'Date']).reset_index(drop=True)
    
    return df
