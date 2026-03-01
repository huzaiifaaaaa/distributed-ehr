import requests
from flask import request, jsonify, current_app
from cluster import raft

def broadcast_replication(model_type, action, data_uuid, payload):
    headers = {"X-Cluster-Auth": current_app.config.get("CLUSTER_AUTH_TOKEN")}
    replication_payload = {
        "type": model_type,
        "action": action,
        "uuid": data_uuid,
        "data": payload
    }
    for name, url in raft.peers.items():
        if name == current_app.config.get("NODE_ID"): 
            continue
        try:
            requests.post(f"{url}/raft/replicate_write", json=replication_payload, headers=headers, timeout=1.0)
        except Exception as e:
            print(f"Failed to sync {model_type} to {name}: {e}")

def handle_write_request(endpoint_func):
    def wrapper(*args, **kwargs):
        if raft.state == "LEADER":
            return endpoint_func(*args, **kwargs)
        
        leader_id = raft.voted_for
        leader_url = raft.peers.get(leader_id)
        if not leader_url:
            return jsonify({"error": "No leader elected in the cluster"}), 503

        try:
            print(f"Forwarding {request.method} request to leader at {leader_url}")
            resp = requests.request(
                method=request.method,
                url=f"{leader_url.rstrip('/')}{request.path}",
                json=request.json,
                headers={k: v for k, v in request.headers if k.lower() != 'host'},
                timeout=2.0
            )
            return (resp.content, resp.status_code, resp.headers.items())
        except Exception as e:
            return jsonify({"error": f"Forwarding failed: {str(e)}"}), 500
            
    wrapper.__name__ = endpoint_func.__name__
    return wrapper