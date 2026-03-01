from flask import Flask, request, jsonify, abort
from database import db, Patient, Hospital
from cluster import raft
from encryption import Encryptor
import uuid
import requests

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)
encryptor = Encryptor(app.config["ENCRYPTION_KEY"])


def leader_required(func):
    """Ensures write operations only happen on the Leader node."""
    def wrapper(*args, **kwargs):
        if raft.state != "LEADER":
            return jsonify({
                "error": "Not the leader", 
                "hint": f"The current node is a {raft.state}. Send writes to the leader."
            }), 307 
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# --- RAFT INTERNAL ENDPOINTS ---

@app.route("/raft/request_vote", methods=["POST"])
def request_vote():
    data = request.json
    term = data.get("term")
    if term > raft.current_term:
        raft.current_term = term
        raft.voted_for = None
        raft.state = "FOLLOWER"
    
    granted = False
    if term == raft.current_term and (raft.voted_for is None or raft.voted_for == data.get("candidate_id")):
        raft.voted_for = data.get("candidate_id")
        granted = True
        raft.start_election_timer()
    return jsonify({"term": raft.current_term, "vote_granted": granted})

@app.route("/raft/append_entries", methods=["POST"])
def append_entries():
    data = request.json
    if data.get("term") >= raft.current_term:
        raft.state = "FOLLOWER"
        raft.current_term = data.get("term")
        raft.start_election_timer()
    return jsonify({"success": True})

# --- REPLICATION RECEIVER (For Followers) ---

@app.route("/raft/replicate_write", methods=["POST"])
def replicate_write():
    data = request.json
    try:
        if data['type'] == "PATIENT":
            p_data = data['data']
            # Re-encrypt locally to ensure consistency
            new_p = Patient(
                uuid=data['uuid'],
                full_name_encrypted=encryptor.encrypt(p_data.get('full_name')),
                gender=p_data.get('gender'),
                date_of_birth_encrypted=encryptor.encrypt(p_data.get('dob'))
            )
            db.session.add(new_p)
            db.session.commit()
            print(f"Follower successfully replicated patient: {data['uuid']}")
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Replication error on follower: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# --- EHR API ENDPOINTS ---

@app.route("/patients", methods=["POST"])
@leader_required
def create_patient():
    data = request.json
    patient_uuid = str(uuid.uuid4())
    
    # 1. Save to Leader's local DB
    new_p = Patient(
        uuid=patient_uuid,
        full_name_encrypted=encryptor.encrypt(data.get('full_name')),
        gender=data.get('gender'),
        date_of_birth_encrypted=encryptor.encrypt(data.get('dob')),
    )
    db.session.add(new_p)
    db.session.commit()

    # 2. REPLICATION: Tell all followers to do the same
    # Ensure CLUSTER_AUTH_TOKEN matches your config
    headers = {"X-Cluster-Auth": app.config.get("CLUSTER_AUTH_TOKEN")}
    
    for name, url in raft.peers.items():
        # Don't replicate to yourself
        if name == app.config.get("NODE_ID"):
            continue
            
        try:
            print(f"Attempting to replicate to {name} at {url}...")
            requests.post(
                f"{url}/raft/replicate_write", 
                json={"type": "PATIENT", "data": data, "uuid": patient_uuid},
                headers=headers,
                timeout=1.0 # Give it a bit more time
            )
        except Exception as e:
            print(f"Replication failed for {name}: {e}")

    return jsonify({"status": "Patient created and replication triggered", "uuid": patient_uuid}), 201

@app.route("/patients", methods=["GET"])
def get_patients():
    patients = Patient.query.all()
    output = []
    for p in patients:
        output.append({
            "uuid": p.uuid,
            "name": encryptor.decrypt(p.full_name_encrypted),
            "gender": p.gender,
            "dob": encryptor.decrypt(p.date_of_birth_encrypted)
        })
    return jsonify(output)

@app.route("/cluster/leader", methods=["GET"])
def get_leader_info():
    return jsonify({
        "node_id": raft.node_id,
        "state": raft.state,
        "current_term": raft.current_term,
        "peers_configured": list(raft.peers.keys())
    })

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        raft.init_node(
            node_id=app.config.get("NODE_ID"),
            node_url=app.config.get("NODE_URL"),
            peer_list=app.config.get("PEERS", [])
        )
        raft.start_election_timer()
    app.run(host="0.0.0.0", port=5001)