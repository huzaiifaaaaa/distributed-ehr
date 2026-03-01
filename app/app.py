from flask import Flask, request, jsonify, abort
from database import db, Patient, Hospital, User, UserRole, Encounter, Observation, Prescription
from cluster import raft
from encryption import Encryptor, hash_password
import uuid
import requests
from replicate import handle_write_request, broadcast_replication

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)
encryptor = Encryptor(app.config["ENCRYPTION_KEY"])

# EHR API ENDPOINTS
# HOSPITAL

@app.route("/hospitals", methods=["POST"])
@handle_write_request
def create_hospital():
    data = request.json
    new_uuid = str(uuid.uuid4())
    
    hospital = Hospital(
        uuid=new_uuid,
        name=data["name"],
        location=data.get("location")
    )
    db.session.add(hospital)
    db.session.commit()
    broadcast_replication("HOSPITAL", "CREATE", new_uuid, data)

    return jsonify({
        "hospital_id": hospital.hospital_id,
        "uuid": hospital.uuid,
        "name": hospital.name,
        "location": hospital.location
    }), 201

@app.route("/hospitals/<int:hospital_id>", methods=["PUT"])
@handle_write_request
def update_hospital(hospital_id):
    hospital = Hospital.query.get_or_404(hospital_id)
    data = request.json
    
    hospital.name = data.get("name", hospital.name)
    hospital.location = data.get("location", hospital.location)
    db.session.commit()

    broadcast_replication("HOSPITAL", "UPDATE", hospital.uuid, {
        "name": hospital.name,
        "location": hospital.location
    })

    return jsonify({
        "hospital_id": hospital.hospital_id,
        "uuid": hospital.uuid,
        "name": hospital.name,
        "location": hospital.location
    })

@app.route("/hospitals/<int:hospital_id>", methods=["DELETE"])
@handle_write_request
def delete_hospital(hospital_id):
    hospital = Hospital.query.get_or_404(hospital_id)
    data_uuid = hospital.uuid
    
    db.session.delete(hospital)
    db.session.commit()
    broadcast_replication("HOSPITAL", "DELETE", data_uuid, None)
    return jsonify({"message": "Hospital deleted"}), 200

@app.route("/hospitals", methods=["GET"])
def get_hospitals():
    hospitals = Hospital.query.all()
    return jsonify([{
        "hospital_id": h.hospital_id,
        "uuid": h.uuid,
        "name": h.name,
        "location": h.location,
        "created_at": h.created_at.isoformat()
    } for h in hospitals])

@app.route("/hospitals/<int:hospital_id>", methods=["GET"])
def get_hospital(hospital_id):
    hospital = Hospital.query.get_or_404(hospital_id)
    return jsonify({
        "hospital_id": hospital.hospital_id,
        "uuid": hospital.uuid,
        "name": hospital.name,
        "location": hospital.location,
        "created_at": hospital.created_at.isoformat()
    })

# USER ROLE

@app.route("/roles", methods=["POST"])
@handle_write_request
def create_role():
    data = request.json
    if UserRole.query.filter_by(role_name=data["role_name"]).first():
        return jsonify({"error": "Role already exists"}), 400

    role = UserRole(
        role_name=data["role_name"],
        description=data.get("description")
    )
    db.session.add(role)
    db.session.commit()

    broadcast_replication("ROLE", "CREATE", data["role_name"], data)
    return jsonify({
        "role_id": role.role_id,
        "role_name": role.role_name,
        "description": role.description
    }), 201

@app.route("/roles/<int:role_id>", methods=["PUT"])
@handle_write_request
def update_role(role_id):
    role = UserRole.query.get_or_404(role_id)
    old_name = role.role_name
    data = request.json
    
    role.role_name = data.get("role_name", role.role_name)
    role.description = data.get("description", role.description)
    db.session.commit()

    broadcast_replication("ROLE", "UPDATE", old_name, {
        "role_name": role.role_name,
        "description": role.description
    })

    return jsonify({
        "role_id": role.role_id,
        "role_name": role.role_name,
        "description": role.description
    })

@app.route("/roles", methods=["GET"])
def get_roles():
    roles = UserRole.query.all()
    return jsonify([{
        "role_id": r.role_id,
        "role_name": r.role_name,
        "description": r.description
    } for r in roles])

# USER

@app.route("/users", methods=["POST"])
@handle_write_request
def create_user():
    data = request.json
    new_uuid = str(uuid.uuid4())
    hashed_pw = hash_password(data["password"])
    
    user = User(
        uuid=new_uuid,
        hospital_id=data["hospital_id"],
        full_name=data["full_name"],
        email=data["email"],
        password=hashed_pw,
        role_id=data["role_id"]
    )
    db.session.add(user)
    db.session.commit()

    repl_payload = data.copy()
    repl_payload['password'] = hashed_pw 
    broadcast_replication("USER", "CREATE", new_uuid, repl_payload)

    return jsonify({
        "user_id": user.user_id,
        "uuid": user.uuid,
        "full_name": user.full_name,
        "email": user.email
    }), 201

@app.route("/users/<int:user_id>", methods=["PUT"])
@handle_write_request
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    
    user.full_name = data.get("full_name", user.full_name)
    user.email = data.get("email", user.email)
    
    current_pw = user.password
    if "password" in data:
        current_pw = hash_password(data["password"])
        user.password = current_pw
        
    user.role_id = data.get("role_id", user.role_id)
    db.session.commit()

    broadcast_replication("USER", "UPDATE", user.uuid, {
        "hospital_id": user.hospital_id,
        "full_name": user.full_name,
        "email": user.email,
        "password": current_pw,
        "role_id": user.role_id
    })
    return jsonify({"status": "User updated", "uuid": user.uuid})

@app.route("/users/<int:user_id>", methods=["DELETE"])
@handle_write_request
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    data_uuid = user.uuid
    
    db.session.delete(user)
    db.session.commit()

    broadcast_replication("USER", "DELETE", data_uuid, None)
    return jsonify({"message": "User deleted"}), 200

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{
        "user_id": u.user_id,
        "uuid": u.uuid,
        "full_name": u.full_name,
        "email": u.email,
        "hospital_id": u.hospital_id,
        "role_id": u.role_id,
        "created_at": u.created_at.isoformat()
    } for u in users])

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        "user_id": user.user_id,
        "uuid": user.uuid,
        "full_name": user.full_name,
        "email": user.email,
        "hospital_id": user.hospital_id,
        "role_id": user.role_id,
        "created_at": user.created_at.isoformat()
    })

# RAFT & REPLICATION ENDPOINTS

@app.route("/raft/replicate_write", methods=["POST"])
def replicate_write():
    """Generic receiver that can handle ANY model type."""
    data = request.json
    m_type = data.get("type")
    action = data.get("action")
    payload = data.get("data")
    uid = data.get("uuid")

    try:
        if m_type == "PATIENT":
            if action == "DELETE":
                Patient.query.filter_by(uuid=uid).delete()
            else:
                p = Patient.query.filter_by(uuid=uid).first() or Patient(uuid=uid)
                p.full_name_encrypted = encryptor.encrypt(payload.get('full_name'))
                p.gender = payload.get('gender')
                p.date_of_birth_encrypted = encryptor.encrypt(payload.get('dob'))
                db.session.add(p)

        elif m_type == "HOSPITAL":
            if action == "DELETE":
                Hospital.query.filter_by(uuid=uid).delete()
            else:
                h = Hospital.query.filter_by(uuid=uid).first() or Hospital(uuid=uid)
                h.name = payload.get('name')
                h.location = payload.get('location')
                db.session.add(h)

        elif m_type == "USER":
            if action == "DELETE":
                User.query.filter_by(uuid=uid).delete()
            else:
                u = User.query.filter_by(uuid=uid).first() or User(uuid=uid)
                u.hospital_id = payload.get('hospital_id')
                u.full_name = payload.get('full_name')
                u.email = payload.get('email')
                u.password = payload.get('password')
                u.role_id = payload.get('role_id')
                db.session.add(u)
        
        elif m_type == "ROLE":
            role_name = data.get("uuid") 
            if action == "DELETE":
                UserRole.query.filter_by(role_name=role_name).delete()
            else:
                r = UserRole.query.filter_by(role_name=role_name).first() or UserRole(role_name=role_name)
                r.description = payload.get('description')
                db.session.add(r)

        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

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
        raft.voted_for = data.get("leader_id") 
        raft.start_election_timer()
    return jsonify({"success": True})

# HELPER ENDPOINTS

@app.route("/endpoints", methods=["GET"])
def list_endpoints():
    endpoints = []
    for rule in app.url_map.iter_rules():
        endpoints.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "path": str(rule)
        })
    return jsonify(endpoints), 200

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route("/cluster/leader", methods=["GET"])
def get_leader_info():
    return jsonify({
        "current_node": raft.node_id,
        "is_leader": raft.state == "LEADER",
        "leader_id": raft.voted_for if raft.state == "FOLLOWER" else raft.node_id
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