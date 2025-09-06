"""
camelot.py

BRION 유방암 모델용 데이터 생성 스크립트

- NCCN breast PDF에서 Camelot을 통해 표 추출
- 관심 약제 필터링 후, 주요 정보를 메타정보(reimbursement_info)와 매핑
- 병기, 아형, Oncotype 등과 함께 임상시험 이름 및 치료 라인 조합 생성
- 최종 결과를 CSV로 저장 (final_brion_data.csv)

Ghostscript가 필요하며, 로컬 경로를 적절히 설정해야 함
""" 

import os
import camelot
import pandas as pd
import random

# 0. Ghostscript 경로 설정
gs_path = r"C:\Program Files\gs\gs10.05.1\bin"
os.environ["PATH"] = gs_path + os.pathsep + os.environ.get("PATH", "")

# 1. PDF에서 표 추출
base_dir = os.path.dirname(__file__)
pdf_path = os.path.join(base_dir, "NCNN_breast.pdf")  # 경로는 본인 환경에 맞게 수정

tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
df_all = pd.concat([table.df for table in tables], ignore_index=True)
df_all.columns = [f"Col{i+1}" for i in range(len(df_all.columns))]

# 2. 주요 약제명 리스트
target_drugs = [
    "Tamoxifen", "TCHP", "Olaparib", "Pembrolizumab", "Sacituzumab", "Trastuzumab", "CDK4/6", "Capecitabine"
]

# 3. 약제 메타정보 (심평원 기준)
reimbursement_info = {
    "Tamoxifen": {"정식_고시번호": "2021-150호", "급여여부": True, "권장용량_표시": "20mg/1일", "단가_표시": 100},
    "Olaparib": {"정식_고시번호": "2024-153호", "급여여부": True, "권장용량_표시": "300mg/2회", "단가_표시": 5000},
    "Sacituzumab": {"정식_고시번호": "2024-219호", "급여여부": True, "권장용량_표시": "10mg/kg", "단가_표시": 12000},
    "Pembrolizumab": {"정식_고시번호": "2023-338호", "급여여부": True, "권장용량_표시": "200mg/3주", "단가_표시": 8000},
    "TCHP": {"정식_고시번호": "2023-289호", "급여여부": True, "권장용량_표시": "복합요법", "단가_표시": 0},
    "Trastuzumab": {"정식_고시번호": "2023-289호", "급여여부": True, "권장용량_표시": "8mg/kg 초기 후 6mg/kg", "단가_표시": 7000},
    "CDK4/6": {"정식_고시번호": "2023-289호", "급여여부": True, "권장용량_표시": "125mg/1일", "단가_표시": 6000},
    "Capecitabine": {"정식_고시번호": "2022-151호", "급여여부": True, "권장용량_표시": "1250mg/m2", "단가_표시": 2000}
}

# 4. 약제명 필터링
filtered_df = df_all[df_all.apply(lambda row: any(drug in row.to_string() for drug in target_drugs), axis=1)]
unique_regimens = list(filtered_df.iloc[:, 0].dropna().unique())

# 5. 복수 약제 추출 함수
def extract_drug_info(regimen_text):
    drugs = [drug for drug in reimbursement_info if drug.lower() in regimen_text.lower()]
    if not drugs:
        return {
            "정식_고시번호": "N/A", "급여여부": False,
            "권장용량_표시": "N/A", "단가_표시": 0
        }
    # 복수 약제 병합
    return {
        "정식_고시번호": " / ".join([reimbursement_info[d]["정식_고시번호"] for d in drugs]),
        "급여여부": all(reimbursement_info[d]["급여여부"] for d in drugs),
        "권장용량_표시": " + ".join([reimbursement_info[d]["권장용량_표시"] for d in drugs]),
        "단가_표시": sum(reimbursement_info[d]["단가_표시"] for d in drugs)
    }

# 6. 병기/아형/기타 정의
stages = ["Stage 0", "Stage I", "Stage II", "Stage III", "Stage IV"]
subtypes = ["HR+/HER2-", "HR+/HER2+", "HR-/HER2+", "HER2-low", "TNBC"]
treatment_lines = ["Neoadjuvant", "Adjuvant", "1st line", "2nd+ line", "Recurrent"]
nccn_categories = ["Category 1", "Category 2A", "Category 2B"]
trials = ["TAILORx", "OlympiA", "KEYNOTE", "DESTINY-Breast", "CREATE-X", "CLEOPATRA"]

# 7. 자동 조합 생성
data = []
for _ in range(500):
    regimen = random.choice(unique_regimens)
    
    # 중복 제거 + 정렬
    found_drugs = [drug for drug in target_drugs if drug.lower() in regimen.lower()]
    if found_drugs:
        regimen = " + ".join(sorted(set(found_drugs)))  
        
    drug_info = extract_drug_info(regimen)
    stage = random.choice(stages)
    subtype = random.choice(subtypes)

    if stage == "Stage 0":
        oncotype = "<11"
    elif stage in ["Stage I", "Stage II"] and subtype == "HR+/HER2-":
        oncotype = random.choice(["11–25", "≥26"])
    elif stage == "Stage III" and subtype == "HR+/HER2-":
        oncotype = "≥26"
    else:
        oncotype = "N/A"

    data.append({
        "Stage": stage,
        "Subtype": subtype,
        "OncotypeDx": oncotype,
        "gBRCA": random.choice(["Yes", "No"]),
        "PDL1": random.choice(["Positive", "Negative"]),
        "ResidualDisease": random.choice(["Yes", "No"]),
        "RecommendedRegimen": regimen,
        "TreatmentLine": random.choice(treatment_lines),
        "NCCN_Category": random.choice(nccn_categories),
        "Trial": random.choice(trials),
        "Notes": "Camelot 기반 자동 매핑",
        **drug_info
    })

# 8. CSV 저장
df_final = pd.DataFrame(data)
output_path = os.path.join(base_dir, "final_brion_data.csv")
df_final.to_csv(output_path, index=False, encoding="utf-8-sig")
