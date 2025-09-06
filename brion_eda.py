"""
brion_eda.py

BRION 유방암 모델용 고급 EDA 자동 분석 스크립트

- `test_breast_data_varied.csv`를 기반으로 정밀 구조 분석
- 결측치, 변수 타입, 수치형/범주형 통계, 상관관계, 유사 변수명 탐지 포함
- 출력 결과는 eda_structure2.txt로 저장되며, 시각화 없이 구조 파악 중심
- 개인정보 없이 안전한 분석을 목표로 설계됨

CSV 파일은 같은 경로에 있어야 하며, 실행 시 eda_structure2.txt 파일로 출력됩니다.
""" 

import pandas as pd
import numpy as np
from difflib import SequenceMatcher
import io
import sys
import os

# 예시입니다: 필요 시 다른 CSV 파일명을 아래에 입력하세요.
file_path = os.path.join(os.getcwd(), "test_breast_data_varied.csv")

def full_safe_eda(df: pd.DataFrame):
    print("\U0001F4CC [1] 데이터 크기 및 컬럼 수")
    print(f"- 행(row) 수: {df.shape[0]:,}")
    print(f"- 열(column) 수: {df.shape[1]:,}")

    print("\n\U0001F4CC [2] 컬럼별 데이터 타입")
    dtype_df = df.dtypes.reset_index()
    dtype_df.columns = ['컬럼명', '데이터 타입']
    print(dtype_df.to_string(index=False))

    print("\n\U0001F4CC [3] 결측치 수 및 비율 (정밀) - null 비율 소수점 4자리")
    null_count = df.isnull().sum()
    null_percent = (null_count / len(df) * 100).round(4)
    null_df = pd.DataFrame({'null_count': null_count, 'null_percent(%)': null_percent})
    null_df = null_df.sort_values('null_percent(%)', ascending=False)
    print(null_df)

    print("\n\U0001F4CC [4] 수치형 변수 요약 통계 + 추가 지표")
    if not df.select_dtypes(include=[np.number]).empty:
        desc = df.describe(include=[np.number]).T
        desc['range'] = desc['max'] - desc['min']
        desc['iqr'] = desc['75%'] - desc['25%']
        desc['missing'] = df.isnull().sum()
        print(desc[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max', 'range', 'iqr', 'missing']].round(4))
    else:
        print("❗ 수치형 변수가 없습니다.")
        
    print("\n\U0001F4CC [5] 범주형 변수 분포 상위 5개")
    cat_cols = df.select_dtypes(include='object').columns
    if len(cat_cols) == 0:
        print("❗ 범주형 변수가 없습니다.")
    else:
        for col in cat_cols:
            print(f"\n- {col} (고유값 {df[col].nunique()}개 / 총 {len(df)}행 중)")
            print(df[col].value_counts(dropna=False).head(5))
            
    print("\n\U0001F4CC [6] 문자열 길이 통계 (min/max/mean/median/std/var)")
    for col in cat_cols:
        lengths = df[col].dropna().astype(str).apply(len)
        if not lengths.empty:
            print(f"- {col}: min={lengths.min()}, max={lengths.max()}, mean={lengths.mean():.2f}, median={lengths.median():.2f}, std={lengths.std():.2f}, var={lengths.var():.2f}")

    print("\n\U0001F4CC [7] 각 컬럼 고유값 5개 예시")
    for col in df.columns:
        unique_vals = df[col].dropna().unique()
        print(f"- {col} (고유값 {len(unique_vals)}개): {unique_vals[:5]}")

    print("\n\U0001F4CC [8] 변수 간 상관관계 (상위 10쌍 + 평균 + 강한 관계 분리)")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) < 2:
        print("❗ 상관계수 계산할 수 있는 수치형 변수가 부족합니다.")
    else:
        corr_matrix = df[numeric_cols].corr().round(4)
        corr_pairs = corr_matrix.unstack()
        corr_pairs = corr_pairs[corr_pairs.index.get_level_values(0) != corr_pairs.index.get_level_values(1)]
        corr_pairs = corr_pairs.dropna().sort_values(key=abs, ascending=False)
        unique_pairs = corr_pairs.groupby(lambda x: frozenset(x)).first()
        top_10 = unique_pairs.head(10)
        for (var1, var2), val in top_10.items():
            print(f"- {list(var1)[0]} ↔ {list(var1)[1]}: 상관계수 {val:.4f}")
        print(f"\n- 전체 변수 간 상관계수 평균: {unique_pairs.abs().mean():.4f}")
        print(f"- 총 변수 쌍 수: {len(unique_pairs)}")
        strong_pos = unique_pairs[unique_pairs > 0.8]
        strong_neg = unique_pairs[unique_pairs < -0.8]
        print(f"- 강한 양의 상관관계: {len(strong_pos)}쌍, 강한 음의 상관관계: {len(strong_neg)}쌍")

    print("\n\U0001F4CC [9] 컬럼명 패턴 자동 분류")
    for col in df.columns:
        col_lower = col.lower()
        if 'date' in col_lower:
            print(f"[DATE] {col}")
        elif 'code' in col_lower:
            print(f"[CODE] {col}")
        elif 'flag' in col_lower or 'yn' in col_lower:
            print(f"[FLAG] {col}")

    print("\n\U0001F4CC [10] 오염된 타입 탐지 (숫자형인데 object로 저장된 컬럼)")
    found_flag = False
    for col in cat_cols:
        try:
            df[col].astype(float)
            print(f"[가능] '{col}' → float 변환 가능 (숫자형 오염 가능성)")
            found_flag = True
        except:
            continue
    if not found_flag:
        print("❗ 숫자형 오염된 object 컬럼 없음")

    print("\n\U0001F4CC [11] 행 기준 결측치 통계 + 분포")
    df['nulls_per_row'] = df.isnull().sum(axis=1)
    print(df['nulls_per_row'].describe().round(2))
    bins = pd.cut(df['nulls_per_row'], bins=[-1, 0, 1, 3, 5, np.inf], labels=['0', '1', '2~3', '4~5', '6+'])
    print("\n- 결측치 개수별 행 분포:")
    print(bins.value_counts().sort_index())
    df.drop(columns=['nulls_per_row'], inplace=True)

    print("\n\U0001F4CC [12] 컬럼명 유사도 비교 (모든 쌍 유사도 점수 포함, cutoff=0.75 이상만 표시)")
    similarities = []
    cols = df.columns.tolist()
    for i in range(len(cols)):
        for j in range(i+1, len(cols)):
            ratio = SequenceMatcher(None, cols[i], cols[j]).ratio()
            if ratio >= 0.75:
                similarities.append((cols[i], cols[j], ratio))
    if similarities:
        similarities.sort(key=lambda x: x[2], reverse=True)
        for col1, col2, ratio in similarities:
            print(f"- '{col1}' ↔ '{col2}' : 유사도 {ratio:.4f}")
        print(f"\n- 유사한 컬럼 쌍 총 {len(similarities)}개")
        avg_ratio = np.mean([r[2] for r in similarities])
        print(f"- 평균 유사도: {avg_ratio:.4f}")
    else:
        print("❗ 유사한 컬럼 쌍이 존재하지 않습니다.")

    print("\n\U0001F4CC [13] 고유값 개수 많은 범주형 변수 (100개 이상)")
    found_many = False
    for col in cat_cols:
        nunique = df[col].nunique()
        if nunique >= 100:
            print(f"- {col}: 고유값 {nunique}개")
            found_many = True
        else:
            print(f"- {col}: 고유값 {nunique}개 (100 미만)")
    if not found_many:
        print("\n✅ 참고: 현재 고유값 100개 이상인 범주형 변수는 없습니다.")

    print("\n✅ 개인정보 없이 최대한의 구조 정보 정밀 분석 완료.")


buffer = io.StringIO()
sys.stdout = buffer

full_safe_eda(df)

sys.stdout = sys.__stdout__

# 예시입니다: 필요 시 다른 txt 파일명을 아래에 입력하세요.
with open("eda_structure2.txt", "w", encoding="utf-8") as f:
    f.write(buffer.getvalue())
    
with open("eda_structure2.txt", "r", encoding="utf-8") as f:
    print(f.read())
    
print(f"\n📁 저장 완료: {os.path.abspath('eda_structure2.txt')}")
