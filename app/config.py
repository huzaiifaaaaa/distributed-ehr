import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "dev-encryption-key-32-bytes-long!")
    
    # Use SQLite for local development, PostgreSQL in Docker
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", 
        "sqlite:///ehr_local.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JSON_SORT_KEYS = False
