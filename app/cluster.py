from flask import current_app, request, jsonify
import requests

# Simple cluster manager to handle peers, leader status, and log replication

def get_peers():
    return current_app.config.get("PEER_URLS", [])


def append_log(entry):
    """Append a log entry to the local Raft log (stored in config)."""
    log = current_app.config.setdefault("RAFT_LOG", [])
    log.append(entry)
    current_app.config["RAFT_LOG"] = log
    return log


def get_log():
    return current_app.config.get("RAFT_LOG", [])


def is_leader():
    return current_app.config.get("NODE_URL") == current_app.config.get("LEADER_URL")


def forward_to_leader(path, method="GET", json=None):
    leader = current_app.config.get("LEADER_URL")
    if not leader:
        return None
    url = leader.rstrip("/") + path
    headers = {"X-Cluster-Auth": current_app.config.get("CLUSTER_AUTH_TOKEN")}
    resp = requests.request(method, url, json=json, headers=headers)
    return resp


def replicate_to_peers(path, method="POST", json=None):
    peers = get_peers()
    results = []
    headers = {"X-Cluster-Auth": current_app.config.get("CLUSTER_AUTH_TOKEN")}
    for peer in peers:
        try:
            url = peer.rstrip("/") + path
            r = requests.request(method, url, json=json, headers=headers, timeout=5)
            results.append((peer, r.status_code))
        except Exception as e:
            results.append((peer, str(e)))
    return results


def check_cluster_auth():
    token = request.headers.get("X-Cluster-Auth")
    if token != current_app.config.get("CLUSTER_AUTH_TOKEN"):
        return False
    return True

# endpoint handlers

def register_peer(url):
    peers = get_peers()
    if url not in peers and url != current_app.config.get("NODE_URL"):
        peers.append(url)
        current_app.config["PEER_URLS"] = peers
    return peers


def set_leader(url):
    current_app.config["LEADER_URL"] = url
    return url
