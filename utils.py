import firebase_admin
import streamlit as st
from firebase_admin import credentials, firestore
from typing import Any, Dict, List
import re

# Assuming config.py is in the same directory
import config

@st.cache_resource
def get_firestore_client() -> firestore.Client:
    """
    Initializes Firebase and returns a cached Firestore client.
    Using st.cache_resource ensures initialization happens only once.
    """
    try:
        app = firebase_admin.get_app()
    except ValueError:
        try:
            if "firebase" in st.secrets:
                firebase_creds = dict(st.secrets["firebase"])
                if "private_key" in firebase_creds:
                    firebase_creds["private_key"] = firebase_creds["private_key"].replace("\\n", "\n")
                cred = credentials.Certificate(firebase_creds)
            else:
                cred = credentials.Certificate(config.SERVICE_ACCOUNT_KEY_PATH)
            
            app = firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Error initializing Firebase: {e}")
            st.stop()
    
    return firestore.client()

def generate_doc_id(product_name: str) -> str:
    """Generates a consistent document ID from a product name.
    Replaces spaces with underscores and slashes with hyphens, and removes other special characters.
    """
    return re.sub(r'[^a-zA-Z0-9_.-]', '', product_name.replace(" ", "_").replace("/", "-"))

def get_all_materials(db: firestore.Client) -> List[Dict[str, Any]]:
    """Fetches all material documents from the Firestore collection."""
    try:
        docs = db.collection(config.MATERIAL_COLLECTION).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        st.error(f"Error fetching materials: {e}")
        return []
