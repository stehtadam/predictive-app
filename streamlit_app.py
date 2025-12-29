import io
import asyncio
import pandas as pd
import streamlit as st

from utils.azure_blob import upload_file_to_blob
from utils.supabase_client import get_supabase_client, insert_upload_record
from utils.predictors import run_predictive_pipeline

st.set_page_config(
    page_title="Vibe Predict",
    page_icon="✨",
    layout="wide"
)

st.title("✨ Vibe Predict")
st.write("Upload a CSV or Excel file and let the app run predictive magic on it.")

# --- Sidebar: configuration ---
st.sidebar.header("Settings")

task_type = st.sidebar.selectbox(
    "Prediction task type",
    ["Auto-detect", "Regression", "Classification", "Clustering"]
)

run_immediately = st.sidebar.checkbox("Run prediction immediately", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("Environment")
st.sidebar.code(
    "Needs:\n"
    "- SUPABASE_URL\n"
    "- SUPABASE_KEY\n"
    "- AZURE_STORAGE_CONNECTION_STRING",
    language="text"
)

# --- Main upload area ---
uploaded_file = st.file_uploader(
    "Upload your data file (CSV or Excel)",
    type=["csv", "xlsx"],
)

if uploaded_file is not None:
    st.success(f"File uploaded: {uploaded_file.name}")
    file_bytes = uploaded_file.read()

    # Reset pointer for pandas
    file_stream = io.BytesIO(file_bytes)

    # Detect type and load into DataFrame
    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(file_stream)
    else:
        df = pd.read_excel(file_stream)

    st.subheader("Preview of your data")
    st.dataframe(df.head())

    # Upload to Azure Blob
    with st.spinner("Uploading to Azure Blob Storage..."):
        blob_url = upload_file_to_blob(
            file_bytes=file_bytes,
            filename=uploaded_file.name
        )
    st.success("File stored in Azure Blob Storage.")

    # Connect to Supabase
    supabase = get_supabase_client()

    # Decide whether to run prediction now
    if run_immediately:
        st.subheader("Running predictive processing...")
        with st.spinner("Crunching numbers with good vibes..."):
            prediction_result, model_info = run_predictive_pipeline(
                df=df,
                task_type=task_type
            )
        st.success("Prediction complete!")

        # Show results
        st.subheader("Prediction output (sample)")
        st.dataframe(prediction_result.head())

        st.subheader("Model info")
        st.json(model_info)

        # Persist metadata + result summary in Supabase
        with st.spinner("Saving metadata and results to Supabase..."):
            asyncio.run(
                insert_upload_record(
                    supabase=supabase,
                    filename=uploaded_file.name,
                    blob_url=blob_url,
                    task_type=model_info["task_type"],
                    target_column=model_info.get("target_column"),
                    row_count=len(df),
                    result_preview=prediction_result.head(10).to_dict(orient="records")
                )
            )

        st.success("Saved to Supabase.")

    else:
        st.info("Prediction not run yet. Toggle 'Run prediction immediately' in the sidebar to process.")


st.markdown("---")
st.caption("Built with Streamlit, Supabase, Azure Blob, and high vibes.")