import datetime
from typing import List, Dict, Any

# Local imports
import utils
import config

# Add a dictionary to store supplier emails (could be from a separate config or DB)
SUPPLIER_EMAILS = {
    'Maizey Plastics': 'sales@maizeyplastics.co.za',
    'Stixo Durban': 'sales@stixodurban.co.za',
    'Falcon SA': 'sales@falconsa.co.za'
}

def update_supplier_prices(product_name: str, supplier_data: List[Dict[str, Any]]) -> None:
    """
    Saves material data to Firebase with standardized fields,
    identifying the cheapest supplier and including supplier emails.
    """
    if not supplier_data:
        db = utils.get_firestore_client()
        print(f"⚠️ No supplier data provided for {product_name}. Skipping.")
        return

    db = utils.get_firestore_client()
    cheapest = min(supplier_data, key=lambda x: x.get('price', float('inf')))

    # Standardizing keys so app.py and smart_quoter.py can read them easily
    data = {
        'name': product_name,
        'last_updated': datetime.datetime.now(), # Store as datetime object
        'price': float(cheapest.get('price', 0.0)),
        'best_supplier': cheapest['name'],
        'supplier_email': SUPPLIER_EMAILS.get(cheapest['name'], config.DEFAULT_EMAIL_DOMAIN.format(supplier_name=cheapest['name'].lower().replace(' ', ''))),
        'all_quotes': supplier_data,
        'unit': config.DEFAULT_UNIT,
        'current_stock': config.DEFAULT_STOCK
    }

    clean_id = utils.generate_doc_id(product_name)
    db.collection(config.MATERIAL_COLLECTION).document(clean_id).set(data)
    print(f"✅ Synced: {product_name} (Best: R{data['price']} via {data['best_supplier']})")

# --- INVENTORY ---
inventory = {
    "Gloss White Vinyl 50m": [
        {'name': 'Maizey Plastics', 'price': 1180.50},
        {'name': 'Stixo Durban', 'price': 1250.00},
        {'name': 'Falcon SA', 'price': 1300.00}
    ],
    "Corex Board 3mm (Pack 10)": [
        {'name': 'Maizey Plastics', 'price': 850.00},
        {'name': 'Stixo Durban', 'price': 790.00},
        {'name': 'Falcon SA', 'price': 820.00}
    ],
    "Chromadek Sheet 2450x1225": [
        {'name': 'Maizey Plastics', 'price': 650.00},
        {'name': 'Stixo Durban', 'price': 680.00},
        {'name': 'Falcon SA', 'price': 640.00}
    ],
    "PVC Banner 500gsm (per m2)": [
        {'name': 'Maizey Plastics', 'price': 45.00},
        {'name': 'Stixo Durban', 'price': 42.50},
        {'name': 'Falcon SA', 'price': 48.00}
    ],
    "Contravision - One-Way Vision": [
        {'name': 'Maizey Plastics', 'price': 1850.00},
        {'name': 'Stixo Durban', 'price': 1790.00},
        {'name': 'Falcon SA', 'price': 1920.00}
    ]
}

if __name__ == "__main__":
    print("🚀 Starting Local Material Sync...")
    for material, prices in inventory.items():
        update_supplier_prices(material, prices)
    print("--- Sync Complete ---")
    
    
