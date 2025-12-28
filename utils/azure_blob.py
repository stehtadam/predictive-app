import os
from azure.storage.blob import BlobServiceClient
import streamlit as st


def _get_blob_service_client():
    # Prefer Streamlit secrets, fallback to environment vars
    conn_str = st.secrets.get("AZURE_STORAGE_CONNECTION_STRING", None) or os.getenv(
        "AZURE_STORAGE_CONNECTION_STRING"
    )
    if not conn_str:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set.")

    return BlobServiceClient.from_connection_string(conn_str)


def upload_file_to_blob(file_bytes: bytes, filename: str, container_name: str = "uploads") -> str:
    blob_service_client = _get_blob_service_client()

    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
    except Exception:
        # Container might already exist; that's fine
        pass

    blob_client = container_client.get_blob_client(filename)
    blob_client.upload_blob(file_bytes, overwrite=True)

    # Construct URL (may vary based on your config; adjust if needed)
    return blob_client.url