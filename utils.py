import firebase_admin
import streamlit as st
from firebase_admin import credentials, firestore
from typing import Any, Dict, List
import re

# Assuming config.py is in the same directory
import config

def initialize_firebase() -> None:
    """Initializes the Firebase Admin SDK if not already initialized."""
    if not firebase_admin._apps:
        try:
            # Check if running on Streamlit Cloud with secrets configured
            if "firebase" in st.secrets:
                # Convert the Secret object to a standard dictionary
                firebase_creds = dict(st.secrets["firebase"])
                cred = credentials.Certificate(firebase_creds)
            else:
                # Fallback to local file for development
                cred = credentials.Certificate(config.SERVICE_ACCOUNT_KEY_PATH)
                
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Error initializing Firebase: {e}")

def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client instance."""
    initialize_firebase()
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
        print(f"Error fetching materials: {e}")
        return []