import os
from typing import Any, Dict, List, Optional

import httpx
import streamlit as st


class SupabaseREST:
    """
    Minimal async REST client for Supabase.

    Supports:
    - insert into a table
    - select from a table
    """

    def __init__(self, url: str, key: str):
        # Expect URL like: https://<project>.supabase.co
        # We will call /rest/v1/... on top of it
        if url.endswith("/"):
            url = url[:-1]
        self.url = url
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

    async def insert(self, table: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.url}/rest/v1/{table}",
                headers=self.headers,   # now includes Prefer: return=representation
                json=data,
            )

            if resp.status_code >= 400:
                print("---- SUPABASE ERROR ----")
                print("Status:", resp.status_code)
                print("URL:", resp.url)
                print("Response text:", resp.text)
                print("Data sent:", data)
                print("------------------------")

            resp.raise_for_status()

            if resp.text:
                return resp.json()
            return []

    async def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, str]] = None,
        order: Optional[str] = None,
        desc: bool = False,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"select": columns}

        if filters:
            # filters format: {"column": "eq.value", "other_column": "gte.10"}
            params.update(filters)

        if order:
            params["order"] = order
            params["ascending"] = "false" if desc else "true"

        if limit is not None:
            params["limit"] = limit

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.url}/rest/v1/{table}",
                headers=self.headers,
                params=params,
            )
            resp.raise_for_status()
            if resp.text:
                return resp.json()
            return []


@st.cache_resource
def get_supabase_client() -> SupabaseREST:
    """
    Returns a cached REST client using secrets or env vars.
    """
    url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL or SUPABASE_KEY not set.")

    return SupabaseREST(url, key)


# --- App-specific helpers for your `uploads` table ---


async def insert_upload_record(
    supabase: SupabaseREST,
    filename: str,
    blob_url: str,
    task_type: str,
    target_column: Optional[str],
    row_count: int,
    result_preview: List[Dict[str, Any]],
    prediction_blob_url: Optional[str] = None,

):
    data: Dict[str, Any] = {
        "filename": filename,
        "blob_url": blob_url,
        "task_type": task_type,
        "target_column": target_column,
        "row_count": row_count,
        "result_preview": result_preview,
        "prediction_blob_url": prediction_blob_url

    }

    return await supabase.insert("uploads", data)