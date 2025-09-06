"""
brion_plot.py

BRION 유방암 모델용 병기(Stage)별 약제 수 시각화 스크립트

- CSV 파일(nccn_breast_stage_drug_map_final_500plus.csv)을 기반으로 병기별 약제 수를 계산
- 컬러맵(Blues) 기반 수직 막대그래프 생성 + 수치 라벨 표시
- 결과 이미지는 stage_drug_count_gradient_labeled.png로 저장됨
- matplotlib, numpy, pandas 사용

CSV 파일은 이 스크립트와 동일한 폴더에 위치해야 정상 작동합니다.
""" 

"""
BRION_EDA.py

BRION 유방암 모델용 시각화 코드

- CSV 파일(nccn_breast_stage_drug_map_final_500plus.csv)을 기반으로 병기(Stage)별 약제 개수를 분석
- 컬러맵 및 수치 표시 포함된 막대그래프 생성
- 출력 그래프는 stage_drug_count_gradient_labeled.png로 저장됨
"""

import os
import pandas as pd

# CSV 불러오기
base_dir = os.path.dirname(__file__)
# 예시입니다: 필요 시 다른 CSV 파일명을 아래에 입력하세요
csv_path = os.path.join(base_dir, "nccn_breast_stage_drug_map_final_500plus.csv")
df = pd.read_csv(csv_path, encoding='cp949')

# 기본 구조 확인
print(df.columns)
print(df.head())

# 병기(Stage)별 약제 수 분포
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colormaps
from matplotlib import rcParams

# 병기별 약제 수 계산
stage_counts = df['Stage'].value_counts().sort_index()
stages = stage_counts.index
counts = stage_counts.values

# 컬러맵 설정
cmap = colormaps["Blues"]
norm = plt.Normalize(counts.min(), counts.max())
colors = [cmap(norm(value)) for value in counts]

# 스타일 설정
plt.style.use('ggplot')
rcParams['font.family'] = 'Malgun Gothic'
rcParams['axes.unicode_minus'] = False

# 시각화
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(stages, counts, color=colors)

# 수치 표시
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, height + 1, f'{int(height)}',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# 기타 설정
ax.set_title("병기(Stage)별 약제 수 분포", fontsize=14, fontweight='bold')
ax.set_xlabel("병기(Stage)", fontsize=12)
ax.set_ylabel("약제 수", fontsize=12)
ax.tick_params(axis='x', labelrotation=0)
plt.tight_layout()
output_path = os.path.join(base_dir, "stage_drug_count_gradient_labeled.png")
plt.savefig(output_path)
plt.show()