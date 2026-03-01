import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "dev-encryption-key-32-bytes-long!")
    
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///ehr.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cluster/Raft Settings
    NODE_ID = os.environ.get("NODE_ID", "node1")
    NODE_URL = os.environ.get("NODE_URL", "http://localhost:5001")
    # Comma-separated list: node1=http://node1:5001,node2=http://node2:5001
    PEERS = os.environ.get("PEERS", "").split(",") 
    CLUSTER_AUTH_TOKEN = os.environ.get("CLUSTER_AUTH_TOKEN", "dev-token")
    
    # Raft Timing (ms)
    ELECTION_TIMEOUT_RANGE = (150, 300) 
    HEARTBEAT_INTERVAL = 0.05 # 50ms