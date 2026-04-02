from typing import Union, Dict, Any

# Local imports
import utils
import config

def calculate_quote(product_name: str, quantity: float, labor_hours: float, complexity: float = 1.0) -> Dict[str, Union[str, float]]:
    """
    Calculates a project quote based on material cost, labor, and markup.

    Args:
        product_name: The name of the material.
        quantity: The quantity of the material needed.
        labor_hours: The estimated labor hours for the project.
        complexity: A multiplier for labor cost (default 1.0).

    Returns:
        A dictionary containing the quote details or an error message.
    """
    db = utils.get_firestore_client()
    doc_id = utils.generate_doc_id(product_name)
    doc = db.collection(config.MATERIAL_COLLECTION).document(doc_id).get()

    if not doc.exists:
        return {"error": "❌ Material not found. Check spelling or run sync."}

    data = doc.to_dict()
    mat_cost = data.get('price', 0.0) * quantity
    labor_cost = (config.LABOR_RATE_PER_HOUR * labor_hours) * complexity
    total = (mat_cost + labor_cost + config.PROJECT_OVERHEAD) * config.DEFAULT_MARKUP

    return {
        "Material": product_name,
        "Total Material Cost": round(mat_cost, 2),
        "Total Labor Cost": round(labor_cost, 2),
        "Final Quote (Inc. Markup)": round(total, 2),
        "Supplier": data['best_supplier']
    }
# Test Case
if __name__ == "__main__":
    res = calculate_quote("Gloss White Vinyl 50m", quantity=1, labor_hours=2)
    print(f"💰 Quote Result: {res}")
