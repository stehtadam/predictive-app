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

def upload_prediction_to_blob(prediction_df, original_filename):
    """
    Uploads the full prediction output as a CSV to the 'predictions' container.
    Returns the blob URL.
    """
    from azure.storage.blob import BlobServiceClient
    import io

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING") or st.secrets.get("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING not set.")

    # Convert DataFrame → CSV bytes
    csv_bytes = prediction_df.to_csv(index=False).encode("utf-8")

    # Create blob client
    blob_service = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service.get_container_client("predictions")

    # Ensure container exists
    try:
        container_client.create_container()
    except Exception:
        pass  # already exists

    # Construct filename
    prediction_filename = f"{original_filename}_predictions.csv"

    # Upload
    blob_client = container_client.get_blob_client(prediction_filename)
    blob_client.upload_blob(csv_bytes, overwrite=True)

    # Return URL
    return blob_client.url