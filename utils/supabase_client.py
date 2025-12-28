import os
import streamlit as st
from supabase import create_client, Client
from typing import Optional, List, Dict, Any


@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets.get("SUPABASE_URL", None) or os.getenv("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY", None) or os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL or SUPABASE_KEY not set.")

    return create_client(url, key)


def insert_upload_record(
    supabase: Client,
    filename: str,
    blob_url: str,
    task_type: str,
    target_column: Optional[str],
    row_count: int,
    result_preview: List[Dict[str, Any]]
):
    data = {
        "filename": filename,
        "blob_url": blob_url,
        "task_type": task_type,
        "target_column": target_column,
        "row_count": row_count,
        "result_preview": result_preview,
    }

    supabase.table("uploads").insert(data).execute()