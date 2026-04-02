MATERIAL_COLLECTION = "material_prices"
HISTORY_COLLECTION = "price_history"
SERVICE_ACCOUNT_KEY_PATH = "serviceAccountKey.json" # For local development, consider environment variables for production

# Quoting
LABOR_RATE_PER_HOUR = 450.00 # Rands per hour
PROJECT_OVERHEAD = 200.00 # Fixed overhead cost for projects
DEFAULT_MARKUP = 1.35 # 35% markup

# Inventory
DEFAULT_STOCK = 5.0
DEFAULT_UNIT = "Standard Unit"

# Email
# Placeholder for default email domain if not found in DB.
# Ideally, actual supplier emails should be stored in the database.
DEFAULT_EMAIL_DOMAIN = "sales@{supplier_name}.co.za"
