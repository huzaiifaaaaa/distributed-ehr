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

    # Cluster settings for inter-node communication and Raft
    CLUSTER_AUTH_TOKEN = os.environ.get("CLUSTER_AUTH_TOKEN", "dev-cluster-token")
    # Comma-separated list of peer URLs (e.g. http://node1:5002,http://node2:5002)
    PEER_URLS = os.environ.get("PEER_URLS", "").split(",") if os.environ.get("PEER_URLS") else []
    # Current node's URL (used for identifying leader)
    NODE_URL = os.environ.get("NODE_URL", "http://localhost:5002")
    # Leader URL; in a real Raft cluster this would be elected
    LEADER_URL = os.environ.get("LEADER_URL", NODE_URL)
