# ✨ Vibe Predict (Streamlit + Supabase + Azure Blob)

Upload a CSV or Excel file, store it in Azure Blob Storage, run simple predictive processing in Python, and persist metadata in Supabase — all via a beginner-friendly Streamlit app.

---

## 1. Prerequisites

- Python 3.10+
- A Supabase project:
  - SUPABASE_URL
  - SUPABASE_KEY
- An Azure Storage Account:
  - AZURE_STORAGE_CONNECTION_STRING
- (Optional) Streamlit Community Cloud account for deployment

---

## 2. Setup

```bash
git clone <this-repo-url>
cd predictive-app
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt