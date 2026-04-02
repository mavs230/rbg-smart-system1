import firebase_admin
import streamlit as st
from firebase_admin import credentials, firestore
from typing import Any, Dict, List
import re
import os
import sys

# Assuming config.py is in the same directory
import config

def _handle_fatal_error(message: str):
    """Helper to report errors safely in both Streamlit and CLI environments."""
    if st.runtime.exists():
        st.error(message)
        st.stop()
    else:
        print(f"❌ FATAL ERROR: {message}")
        sys.exit(1)

def get_firestore_client() -> firestore.Client:
    """
    Returns a Firestore client. Uses Streamlit caching if running in a web session,
    otherwise performs a standard initialization for CLI scripts.
    """
    if st.runtime.exists():
        return _get_cached_firestore_client()
    return _initialize_firebase_logic()

@st.cache_resource(show_spinner=False)
def _get_cached_firestore_client() -> firestore.Client:
    return _initialize_firebase_logic()

def _initialize_firebase_logic() -> firestore.Client:
    """
    Internal logic to initialize the Firebase app and return the client.
    """
    try:
        app = firebase_admin.get_app()
        return firestore.client(app=app)
    except ValueError:
        pass # Needs initialization

    # 1. Attempt to find credentials
    cred = None
    
    # Check st.secrets safely (st.secrets triggers errors if accessed outside Streamlit)
    try:
        if "firebase" in st.secrets:
            firebase_creds = dict(st.secrets["firebase"])
            if "private_key" in firebase_creds:
                firebase_creds["private_key"] = firebase_creds["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(firebase_creds)
    except:
        pass

    # 2. Fallback to local file
    if not cred and os.path.exists(config.SERVICE_ACCOUNT_KEY_PATH):
        cred = credentials.Certificate(config.SERVICE_ACCOUNT_KEY_PATH)

    if not cred:
        _handle_fatal_error("Firebase Credentials Missing! No st.secrets or serviceAccountKey.json found.")

    # 3. Initialize the app
    try:
        app = firebase_admin.initialize_app(cred)
        return firestore.client(app=app)
    except Exception as e:
        _handle_fatal_error(f"Firebase Initialization Error: {e}")

def generate_doc_id(product_name: str) -> str:
    """Generates a consistent document ID from a product name.
    Replaces spaces with underscores and slashes with hyphens, and removes other special characters.
    """
    if not product_name:
        return "unknown"
    # Normalize to lowercase and strip whitespace to ensure consistent lookups
    normalized_name = product_name.strip().lower()
    return re.sub(r'[^a-zA-Z0-9_.-]', '', normalized_name.replace(" ", "_").replace("/", "-"))

def get_all_materials(db: firestore.Client) -> List[Dict[str, Any]]:
    """Fetches all material documents from the Firestore collection."""
    try:
        docs = db.collection(config.MATERIAL_COLLECTION).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        st.error(f"Error fetching materials: {e}")
        return []
