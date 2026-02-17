from flask import Flask, request, jsonify
from database import db, Hospital, UserRole, User, Patient, Encounter, Observation, Prescription
from config import Config
from encryption import Encryptor, hash_password
from datetime import datetime
import uuid

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
encryptor = Encryptor(app.config["ENCRYPTION_KEY"])

with app.app_context():
    db.create_all()

# ========== HOSPITAL CRUD ==========
@app.route("/hospitals", methods=["POST"])
def create_hospital():
    data = request.json
    hospital = Hospital(
        uuid=str(uuid.uuid4()),
        name=data["name"],
        location=data.get("location")
    )
    db.session.add(hospital)
    db.session.commit()
    return jsonify({
        "hospital_id": hospital.hospital_id,
        "uuid": hospital.uuid,
        "name": hospital.name,
        "location": hospital.location
    }), 201

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

@app.route("/hospitals/<int:hospital_id>", methods=["PUT"])
def update_hospital(hospital_id):
    hospital = Hospital.query.get_or_404(hospital_id)
    data = request.json
    hospital.name = data.get("name", hospital.name)
    hospital.location = data.get("location", hospital.location)
    db.session.commit()
    return jsonify({
        "hospital_id": hospital.hospital_id,
        "uuid": hospital.uuid,
        "name": hospital.name,
        "location": hospital.location
    })

@app.route("/hospitals/<int:hospital_id>", methods=["DELETE"])
def delete_hospital(hospital_id):
    hospital = Hospital.query.get_or_404(hospital_id)
    db.session.delete(hospital)
    db.session.commit()
    return jsonify({"message": "Hospital deleted"}), 200

# ========== USER ROLE CRUD ==========
@app.route("/roles", methods=["POST"])
def create_role():
    data = request.json
    role = UserRole(
        role_name=data["role_name"],
        description=data.get("description")
    )
    db.session.add(role)
    db.session.commit()
    return jsonify({
        "role_id": role.role_id,
        "role_name": role.role_name,
        "description": role.description
    }), 201

@app.route("/roles", methods=["GET"])
def get_roles():
    roles = UserRole.query.all()
    return jsonify([{
        "role_id": r.role_id,
        "role_name": r.role_name,
        "description": r.description
    } for r in roles])

@app.route("/roles/<int:role_id>", methods=["PUT"])
def update_role(role_id):
    role = UserRole.query.get_or_404(role_id)
    data = request.json
    role.role_name = data.get("role_name", role.role_name)
    role.description = data.get("description", role.description)
    db.session.commit()
    return jsonify({
        "role_id": role.role_id,
        "role_name": role.role_name,
        "description": role.description
    })

# ========== USER CRUD ==========
@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    user = User(
        uuid=str(uuid.uuid4()),
        hospital_id=data["hospital_id"],
        full_name=data["full_name"],
        email=data["email"],
        password=hash_password(data["password"]),
        role_id=data["role_id"]
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({
        "user_id": user.user_id,
        "uuid": user.uuid,
        "full_name": user.full_name,
        "email": user.email,
        "hospital_id": user.hospital_id,
        "role_id": user.role_id
    }), 201

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

@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.full_name = data.get("full_name", user.full_name)
    user.email = data.get("email", user.email)
    if "password" in data:
        user.password = hash_password(data["password"])
    user.role_id = data.get("role_id", user.role_id)
    db.session.commit()
    return jsonify({
        "user_id": user.user_id,
        "uuid": user.uuid,
        "full_name": user.full_name,
        "email": user.email
    })

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200

# ========== PATIENT CRUD ==========
@app.route("/patients", methods=["POST"])
def create_patient():
    data = request.json
    patient = Patient(
        uuid=str(uuid.uuid4()),
        full_name_encrypted=encryptor.encrypt(data["full_name"]),
        date_of_birth_encrypted=encryptor.encrypt(data["date_of_birth"]),
        gender=data.get("gender"),
        phone_encrypted=encryptor.encrypt(data.get("phone")) if data.get("phone") else None,
        address_encrypted=encryptor.encrypt(data.get("address")) if data.get("address") else None
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify({
        "patient_id": patient.patient_id,
        "uuid": patient.uuid,
        "full_name": encryptor.decrypt(patient.full_name_encrypted),
        "date_of_birth": encryptor.decrypt(patient.date_of_birth_encrypted),
        "gender": patient.gender
    }), 201

@app.route("/patients", methods=["GET"])
def get_patients():
    patients = Patient.query.all()
    return jsonify([{
        "patient_id": p.patient_id,
        "uuid": p.uuid,
        "full_name": encryptor.decrypt(p.full_name_encrypted),
        "date_of_birth": encryptor.decrypt(p.date_of_birth_encrypted),
        "gender": p.gender,
        "phone": encryptor.decrypt(p.phone_encrypted) if p.phone_encrypted else None,
        "address": encryptor.decrypt(p.address_encrypted) if p.address_encrypted else None,
        "created_at": p.created_at.isoformat()
    } for p in patients])

@app.route("/patients/<int:patient_id>", methods=["GET"])
def get_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return jsonify({
        "patient_id": patient.patient_id,
        "uuid": patient.uuid,
        "full_name": encryptor.decrypt(patient.full_name_encrypted),
        "date_of_birth": encryptor.decrypt(patient.date_of_birth_encrypted),
        "gender": patient.gender,
        "phone": encryptor.decrypt(patient.phone_encrypted) if patient.phone_encrypted else None,
        "address": encryptor.decrypt(patient.address_encrypted) if patient.address_encrypted else None,
        "created_at": patient.created_at.isoformat()
    })

@app.route("/patients/<int:patient_id>", methods=["PUT"])
def update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    data = request.json
    if "full_name" in data:
        patient.full_name_encrypted = encryptor.encrypt(data["full_name"])
    if "date_of_birth" in data:
        patient.date_of_birth_encrypted = encryptor.encrypt(data["date_of_birth"])
    patient.gender = data.get("gender", patient.gender)
    if "phone" in data:
        patient.phone_encrypted = encryptor.encrypt(data["phone"]) if data["phone"] else None
    if "address" in data:
        patient.address_encrypted = encryptor.encrypt(data["address"]) if data["address"] else None
    db.session.commit()
    return jsonify({
        "patient_id": patient.patient_id,
        "full_name": encryptor.decrypt(patient.full_name_encrypted),
        "date_of_birth": encryptor.decrypt(patient.date_of_birth_encrypted)
    })

@app.route("/patients/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({"message": "Patient deleted"}), 200

# ========== ENCOUNTER CRUD ==========
@app.route("/encounters", methods=["POST"])
def create_encounter():
    data = request.json
    encounter = Encounter(
        patient_id=data["patient_id"],
        doctor_id=data["doctor_id"],
        hospital_id=data["hospital_id"],
        visit_type=data["visit_type"],
        visit_reason=data.get("visit_reason"),
        visit_date=datetime.fromisoformat(data["visit_date"])
    )
    db.session.add(encounter)
    db.session.commit()
    return jsonify({
        "encounter_id": encounter.encounter_id,
        "patient_id": encounter.patient_id,
        "doctor_id": encounter.doctor_id,
        "hospital_id": encounter.hospital_id,
        "visit_type": encounter.visit_type,
        "visit_reason": encounter.visit_reason,
        "visit_date": encounter.visit_date.isoformat()
    }), 201

@app.route("/encounters", methods=["GET"])
def get_encounters():
    encounters = Encounter.query.all()
    return jsonify([{
        "encounter_id": e.encounter_id,
        "patient_id": e.patient_id,
        "doctor_id": e.doctor_id,
        "hospital_id": e.hospital_id,
        "visit_type": e.visit_type,
        "visit_reason": e.visit_reason,
        "visit_date": e.visit_date.isoformat(),
        "created_at": e.created_at.isoformat()
    } for e in encounters])

@app.route("/encounters/<int:encounter_id>", methods=["GET"])
def get_encounter(encounter_id):
    encounter = Encounter.query.get_or_404(encounter_id)
    return jsonify({
        "encounter_id": encounter.encounter_id,
        "patient_id": encounter.patient_id,
        "doctor_id": encounter.doctor_id,
        "hospital_id": encounter.hospital_id,
        "visit_type": encounter.visit_type,
        "visit_reason": encounter.visit_reason,
        "visit_date": encounter.visit_date.isoformat(),
        "created_at": encounter.created_at.isoformat()
    })

@app.route("/encounters/<int:encounter_id>", methods=["PUT"])
def update_encounter(encounter_id):
    encounter = Encounter.query.get_or_404(encounter_id)
    data = request.json
    encounter.visit_type = data.get("visit_type", encounter.visit_type)
    encounter.visit_reason = data.get("visit_reason", encounter.visit_reason)
    if "visit_date" in data:
        encounter.visit_date = datetime.fromisoformat(data["visit_date"])
    db.session.commit()
    return jsonify({
        "encounter_id": encounter.encounter_id,
        "visit_type": encounter.visit_type,
        "visit_date": encounter.visit_date.isoformat()
    })

@app.route("/encounters/<int:encounter_id>", methods=["DELETE"])
def delete_encounter(encounter_id):
    encounter = Encounter.query.get_or_404(encounter_id)
    db.session.delete(encounter)
    db.session.commit()
    return jsonify({"message": "Encounter deleted"}), 200

# ========== OBSERVATION CRUD ==========

@app.route("/observations", methods=["POST"])
def create_observation():
    data = request.json
    observation = Observation(
        encounter_id=data["encounter_id"],
        patient_id=data["patient_id"],
        type=data["type"],
        value=data["value"],
        unit=data.get("unit")
    )
    db.session.add(observation)
    db.session.commit()
    return jsonify({
        "observation_id": observation.observation_id,
        "encounter_id": observation.encounter_id,
        "patient_id": observation.patient_id,
        "type": observation.type,
        "value": observation.value,
        "unit": observation.unit
    }), 201

@app.route("/observations", methods=["GET"])
def get_observations():
    observations = Observation.query.all()
    return jsonify([{
        "observation_id": o.observation_id,
        "encounter_id": o.encounter_id,
        "patient_id": o.patient_id,
        "type": o.type,
        "value": o.value,
        "unit": o.unit,
        "recorded_at": o.recorded_at.isoformat()
    } for o in observations])

@app.route("/observations/<int:observation_id>", methods=["GET"])
def get_observation(observation_id):
    observation = Observation.query.get_or_404(observation_id)
    return jsonify({
        "observation_id": observation.observation_id,
        "encounter_id": observation.encounter_id,
        "patient_id": observation.patient_id,
        "type": observation.type,
        "value": observation.value,
        "unit": observation.unit,
        "recorded_at": observation.recorded_at.isoformat()
    })

@app.route("/observations/<int:observation_id>", methods=["PUT"])
def update_observation(observation_id):
    observation = Observation.query.get_or_404(observation_id)
    data = request.json
    observation.type = data.get("type", observation.type)
    observation.value = data.get("value", observation.value)
    observation.unit = data.get("unit", observation.unit)
    db.session.commit()
    return jsonify({
        "observation_id": observation.observation_id,
        "type": observation.type,
        "value": observation.value,
        "unit": observation.unit
    })

@app.route("/observations/<int:observation_id>", methods=["DELETE"])
def delete_observation(observation_id):
    observation = Observation.query.get_or_404(observation_id)
    db.session.delete(observation)
    db.session.commit()
    return jsonify({"message": "Observation deleted"}), 200

# ========== PRESCRIPTION CRUD ==========

@app.route("/prescriptions", methods=["POST"])
def create_prescription():
    data = request.json
    prescription = Prescription(
        encounter_id=data["encounter_id"],
        patient_id=data["patient_id"],
        doctor_id=data["doctor_id"],
        medication=data["medication"],
        dosage=data.get("dosage"),
        frequency=data.get("frequency"),
        duration=data.get("duration"),
        notes_encrypted=encryptor.encrypt(data.get("notes")) if data.get("notes") else None
    )
    db.session.add(prescription)
    db.session.commit()
    return jsonify({
        "prescription_id": prescription.prescription_id,
        "encounter_id": prescription.encounter_id,
        "patient_id": prescription.patient_id,
        "doctor_id": prescription.doctor_id,
        "medication": prescription.medication,
        "dosage": prescription.dosage,
        "frequency": prescription.frequency,
        "duration": prescription.duration,
        "notes": encryptor.decrypt(prescription.notes_encrypted) if prescription.notes_encrypted else None
    }), 201

@app.route("/prescriptions", methods=["GET"])
def get_prescriptions():
    prescriptions = Prescription.query.all()
    return jsonify([{
        "prescription_id": p.prescription_id,
        "encounter_id": p.encounter_id,
        "patient_id": p.patient_id,
        "doctor_id": p.doctor_id,
        "medication": p.medication,
        "dosage": p.dosage,
        "frequency": p.frequency,
        "duration": p.duration,
        "notes": encryptor.decrypt(p.notes_encrypted) if p.notes_encrypted else None,
        "prescribed_at": p.prescribed_at.isoformat()
    } for p in prescriptions])

@app.route("/prescriptions/<int:prescription_id>", methods=["GET"])
def get_prescription(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)
    return jsonify({
        "prescription_id": prescription.prescription_id,
        "encounter_id": prescription.encounter_id,
        "patient_id": prescription.patient_id,
        "doctor_id": prescription.doctor_id,
        "medication": prescription.medication,
        "dosage": prescription.dosage,
        "frequency": prescription.frequency,
        "duration": prescription.duration,
        "notes": encryptor.decrypt(prescription.notes_encrypted) if prescription.notes_encrypted else None,
        "prescribed_at": prescription.prescribed_at.isoformat()
    })

@app.route("/prescriptions/<int:prescription_id>", methods=["PUT"])
def update_prescription(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)
    data = request.json
    prescription.medication = data.get("medication", prescription.medication)
    prescription.dosage = data.get("dosage", prescription.dosage)
    prescription.frequency = data.get("frequency", prescription.frequency)
    prescription.duration = data.get("duration", prescription.duration)
    if "notes" in data:
        prescription.notes_encrypted = encryptor.encrypt(data["notes"]) if data["notes"] else None
    db.session.commit()
    return jsonify({
        "prescription_id": prescription.prescription_id,
        "medication": prescription.medication,
        "dosage": prescription.dosage
    })

@app.route("/prescriptions/<int:prescription_id>", methods=["DELETE"])
def delete_prescription(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)
    db.session.delete(prescription)
    db.session.commit()
    return jsonify({"message": "Prescription deleted"}), 200

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Return all endpoints
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
