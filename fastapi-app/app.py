"""
FastAPI ML Prediction Service
Exposes /predict endpoint that loads a simple ML model and logs predictions to PostgreSQL.
Optionally caches predictions in Redis.
"""

import os
import logging
import json
from datetime import datetime
from typing import Optional

import psycopg2
import psycopg2.extras
import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.dummy import DummyClassifier
import numpy as np

# Configuration
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ml_db")
DB_USER = os.getenv("DB_USER", "ml_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "ml_password")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
USE_REDIS = os.getenv("USE_REDIS", "true").lower() == "true"

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="ML Prediction Service", version="1.0.0")

# Initialize Redis (optional)
redis_client = None
if USE_REDIS:
    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), decode_responses=True)
        redis_client.ping()
        logger.info("Connected to Redis")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        redis_client = None

# Load or create dummy ML model
model = DummyClassifier(strategy="constant", constant=1)
model.fit(np.array([[0], [1]]), np.array([0, 1]))

# Pydantic model for input/output
class PredictionInput(BaseModel):
    feature_1: float
    feature_2: float
    feature_3: float

class PredictionOutput(BaseModel):
    prediction: int
    confidence: float
    timestamp: str
    cached: bool

def init_db():
    """Initialize PostgreSQL database and create tables if needed."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                features JSONB NOT NULL,
                prediction INT NOT NULL,
                confidence FLOAT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

def log_prediction_to_db(features: dict, prediction: int, confidence: float):
    """Log prediction to PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO predictions (features, prediction, confidence)
            VALUES (%s, %s, %s);
            """,
            (json.dumps(features), prediction, confidence)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Prediction logged: {prediction}")
    except Exception as e:
        logger.error(f"Failed to log prediction to DB: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    logger.info("FastAPI service started")

@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes."""
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    """
    Make a prediction using the ML model.
    
    Args:
        input_data: Features for prediction
    
    Returns:
        PredictionOutput with prediction and metadata
    """
    try:
        # Create feature array
        features = np.array([[
            input_data.feature_1,
            input_data.feature_2,
            input_data.feature_3
        ]])
        
        # Create feature dict for logging
        features_dict = {
            "feature_1": input_data.feature_1,
            "feature_2": input_data.feature_2,
            "feature_3": input_data.feature_3
        }
        
        # Check Redis cache first
        cached = False
        cache_key = f"prediction:{json.dumps(features_dict, sort_keys=True)}"
        
        if redis_client:
            try:
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    result = json.loads(cached_result)
                    result["cached"] = True
                    logger.info(f"Cache hit for {features_dict}")
                    return PredictionOutput(**result)
            except Exception as e:
                logger.warning(f"Redis cache lookup failed: {e}")
        
        # Make prediction
        prediction = int(model.predict(features)[0])
        confidence = float(np.random.rand())  # Dummy confidence
        timestamp = datetime.utcnow().isoformat()
        
        # Log to database
        log_prediction_to_db(features_dict, prediction, confidence)
        
        # Cache result in Redis
        if redis_client:
            try:
                result_dict = {
                    "prediction": prediction,
                    "confidence": confidence,
                    "timestamp": timestamp,
                    "cached": False
                }
                redis_client.setex(cache_key, 3600, json.dumps(result_dict))
                logger.info(f"Cached prediction for {features_dict}")
            except Exception as e:
                logger.warning(f"Redis caching failed: {e}")
        
        return PredictionOutput(
            prediction=prediction,
            confidence=confidence,
            timestamp=timestamp,
            cached=cached
        )
    
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
