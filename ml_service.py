import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import utils
import config

def predict_price_trend(material_name: str, days_into_future: int = 30):
    """
    Uses Linear Regression to predict the price of a material in the future.
    """
    db = utils.get_firestore_client()
    clean_id = utils.generate_doc_id(material_name)
    
    # Fetch history - removed order_by to avoid needing manual Firestore indexes
    docs = db.collection(config.HISTORY_COLLECTION).where("material_id", "==", clean_id).stream()
    
    data = []
    for doc in docs:
        d = doc.to_dict()
        # Defensive check for missing data
        if 'timestamp' in d and 'price' in d:
            data.append({
                'timestamp': d['timestamp'].timestamp(), # Convert to unix numeric
                'price': d['price']
            })
    
    if len(data) < 3:
        return None, "Need at least 3 historical data points to predict a trend."

    # Sort by time in Python
    df = pd.DataFrame(data).sort_values('timestamp')
    
    # ML Setup: X = Time, y = Price
    X = df[['timestamp']].values
    y = df['price'].values
    
    # Train the Model
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict for future date
    future_date = datetime.now() + timedelta(days=days_into_future)
    future_timestamp = np.array([[future_date.timestamp()]])
    prediction = model.predict(future_timestamp)[0]
    
    # Calculate confidence (R^2 Score)
    score = model.score(X, y)
    
    return {
        "predicted_price": round(prediction, 2),
        "days": days_into_future,
        "confidence": round(score * 100, 1)
    }, None
