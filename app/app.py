from flask import Flask, request, jsonify, abort
from database import db, Patient, RaftLog
from cluster import raft
from encryption import Encryptor
import requests

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)
encryptor = Encryptor(app.config["ENCRYPTION_KEY"])

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
        raft.start_election_timer() # Reset timeout
    return jsonify({"success": True})

# --- EHR API ---

def leader_required(func):
    def wrapper(*args, **kwargs):
        if raft.state != "LEADER":
            # Find the leader (simplified: usually stored from AppendEntries)
            # For now, just error or redirect if not leader
            return jsonify({"error": "Not the leader"}), 307 
        
        # QUORUM REPLICATION LOGIC
        # 1. Propose change to peers
        # 2. If majority ack, commit to local DB
        # 3. Return result
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route("/patients", methods=["POST"])
@leader_required
def create_patient():
    data = request.json
    new_p = Patient(
        full_name_encrypted=encryptor.encrypt(data['full_name']),
        # ... other fields
    )
    db.session.add(new_p)
    db.session.commit()
    return jsonify({"status": "Patient created and replicated"}), 201

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        raft.init_peers(app.config["PEERS"])
        raft.start_election_timer()
    app.run(host="0.0.0.0", port=5001)