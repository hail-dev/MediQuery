import requests
import streamlit as st
from config import API_BASE_URL, HEADERS

def upload_document(file) -> dict | None:
    """
    Upload a PDF file to the FastAPI /upload endpoint.
    Returns the response JSON or None on failure.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/upload",
            headers=HEADERS,
            files={"file": (file.name, file.getvalue(), "application/pdf")},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.json().get('detail', 'Unknown Error')}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannont connect to the API. Make sure the backend is running.")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

def ask_question(question: str, document_id: str | None = None) -> dict | None:
    """
    Send a question to the FastAPI /ask endpoint.
    Returns the response JSON or None on failure.
    """
    try:
        payload = {"question": question}
        if document_id:
            payload["document_id"] = document_id

        response = requests.post(
            f"{API_BASE_URL}/query",
            headers={**HEADERS, "Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Query failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the API. Make sure the backend is running.")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None