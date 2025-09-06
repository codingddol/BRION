# BRION
Breast Cancer AI Solution

# BRION 🧬
A Streamlit-based web/application for **breast cancer stage- and subtype-specific drug recommendation**.

---

## 📖 Project Overview
BRION takes user-provided pathological information (T/N/M, ER, PR, HER2, etc.)  
and automatically calculates the **stage** and **subtype** of breast cancer.  
Based on these results, it provides recommended treatment strategies and drugs.

**Key Features:**
- Automatic stage and subtype calculation  
- Filtering by biomarkers (ER, PR, HER2, gBRCA, PDL1, OncotypeDx)  
- Visualization of NCCN guideline category, **reimbursement status, drug cost, and recommended dosage**  
- Built on **Streamlit** for interactive web deployment and application deployment
---

## ⚙️ Setup, Run & Repository Structure

All required libraries are listed in `requirements.txt` and `camelot_requirements.txt`.

```bash
# Create and activate a virtual environment (example: venv)
python -m venv brion-env
source brion-env/bin/activate   # Mac/Linux
brion-env\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit application
streamlit run pcbrion.py or appbrion.py

.
├── appbrion.py               # App launcher (alternative entry point)
├── pcbrion.py                # Main Streamlit application
├── brion_eda.ipynb           # Example EDA notebook
├── brion_eda.py              # EDA script version
├── brion_plot.py             # Plotting/visualization
├── camelot.py                # NCCN table extraction script
├── cap.py                    # Additional script
├── requirements.txt          # Main dependencies
├── camelot_requirements.txt  # Additional Camelot-specific dependencies
└── README.md
