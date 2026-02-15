from app import app, db
from database import Hospital, UserRole, User, Patient, Encounter, Observation, Prescription
from encryption import Encryptor, hash_password
from datetime import datetime, timedelta
import uuid

def seed_database():
    with app.app_context():
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        encryptor = Encryptor(app.config["ENCRYPTION_KEY"])
        
        print("Creating hospital...")
        hospital = Hospital(
            uuid=str(uuid.uuid4()),
            name="City General Hospital",
            location="123 Main Street, New York, NY 10001"
        )
        db.session.add(hospital)
        db.session.flush()
        
        print("Creating user roles...")
        roles = [
            UserRole(role_name="Doctor", description="Medical doctor"),
            UserRole(role_name="Nurse", description="Nursing staff"),
            UserRole(role_name="Admin", description="Administrative staff")
        ]
        db.session.add_all(roles)
        db.session.flush()
        
        print("Creating users...")
        users = [
            User(
                uuid=str(uuid.uuid4()),
                hospital_id=hospital.hospital_id,
                full_name="Dr. Sarah Johnson",
                email="sarah.johnson@hospital.com",
                password=hash_password("password123"),
                role_id=roles[0].role_id
            ),
            User(
                uuid=str(uuid.uuid4()),
                hospital_id=hospital.hospital_id,
                full_name="Dr. Michael Chen",
                email="michael.chen@hospital.com",
                password=hash_password("password123"),
                role_id=roles[0].role_id
            ),
            User(
                uuid=str(uuid.uuid4()),
                hospital_id=hospital.hospital_id,
                full_name="Nurse Emily Davis",
                email="emily.davis@hospital.com",
                password=hash_password("password123"),
                role_id=roles[1].role_id
            ),
            User(
                uuid=str(uuid.uuid4()),
                hospital_id=hospital.hospital_id,
                full_name="Admin John Smith",
                email="john.smith@hospital.com",
                password=hash_password("password123"),
                role_id=roles[2].role_id
            )
        ]
        db.session.add_all(users)
        db.session.flush()
        
        print("Creating patients...")
        patients = [
            Patient(
                uuid=str(uuid.uuid4()),
                full_name_encrypted=encryptor.encrypt("Alice Williams"),
                date_of_birth_encrypted=encryptor.encrypt("1985-03-15"),
                gender="Female",
                phone_encrypted=encryptor.encrypt("555-0101"),
                address_encrypted=encryptor.encrypt("456 Oak Ave, New York, NY 10002")
            ),
            Patient(
                uuid=str(uuid.uuid4()),
                full_name_encrypted=encryptor.encrypt("Bob Martinez"),
                date_of_birth_encrypted=encryptor.encrypt("1978-07-22"),
                gender="Male",
                phone_encrypted=encryptor.encrypt("555-0102"),
                address_encrypted=encryptor.encrypt("789 Elm St, New York, NY 10003")
            ),
            Patient(
                uuid=str(uuid.uuid4()),
                full_name_encrypted=encryptor.encrypt("Carol Anderson"),
                date_of_birth_encrypted=encryptor.encrypt("1992-11-08"),
                gender="Female",
                phone_encrypted=encryptor.encrypt("555-0103"),
                address_encrypted=encryptor.encrypt("321 Pine Rd, New York, NY 10004")
            )
        ]
        db.session.add_all(patients)
        db.session.flush()
        
        print("Creating encounters...")
        encounters = [
            Encounter(
                patient_id=patients[0].patient_id,
                doctor_id=users[0].user_id,
                hospital_id=hospital.hospital_id,
                visit_type="Checkup",
                visit_reason="Annual physical examination",
                visit_date=datetime.now() - timedelta(days=5)
            ),
            Encounter(
                patient_id=patients[1].patient_id,
                doctor_id=users[1].user_id,
                hospital_id=hospital.hospital_id,
                visit_type="Emergency",
                visit_reason="Chest pain",
                visit_date=datetime.now() - timedelta(days=2)
            ),
            Encounter(
                patient_id=patients[2].patient_id,
                doctor_id=users[0].user_id,
                hospital_id=hospital.hospital_id,
                visit_type="Follow-up",
                visit_reason="Post-surgery check",
                visit_date=datetime.now() - timedelta(days=1)
            )
        ]
        db.session.add_all(encounters)
        db.session.flush()
        
        print("Creating observations...")
        observations = [
            Observation(
                encounter_id=encounters[0].encounter_id,
                patient_id=patients[0].patient_id,
                type="Blood Pressure",
                value="120/80",
                unit="mmHg"
            ),
            Observation(
                encounter_id=encounters[0].encounter_id,
                patient_id=patients[0].patient_id,
                type="Heart Rate",
                value="72",
                unit="bpm"
            ),
            Observation(
                encounter_id=encounters[1].encounter_id,
                patient_id=patients[1].patient_id,
                type="Blood Pressure",
                value="145/95",
                unit="mmHg"
            ),
            Observation(
                encounter_id=encounters[1].encounter_id,
                patient_id=patients[1].patient_id,
                type="Temperature",
                value="98.6",
                unit="°F"
            ),
            Observation(
                encounter_id=encounters[2].encounter_id,
                patient_id=patients[2].patient_id,
                type="Weight",
                value="65",
                unit="kg"
            )
        ]
        db.session.add_all(observations)
        db.session.flush()
        
        print("Creating prescriptions...")
        prescriptions = [
            Prescription(
                encounter_id=encounters[1].encounter_id,
                patient_id=patients[1].patient_id,
                doctor_id=users[1].user_id,
                medication="Lisinopril",
                dosage="10mg",
                frequency="Once daily",
                duration="30 days",
                notes_encrypted=encryptor.encrypt("Take in the morning with food")
            ),
            Prescription(
                encounter_id=encounters[1].encounter_id,
                patient_id=patients[1].patient_id,
                doctor_id=users[1].user_id,
                medication="Aspirin",
                dosage="81mg",
                frequency="Once daily",
                duration="Ongoing",
                notes_encrypted=encryptor.encrypt("Low dose for heart health")
            ),
            Prescription(
                encounter_id=encounters[2].encounter_id,
                patient_id=patients[2].patient_id,
                doctor_id=users[0].user_id,
                medication="Amoxicillin",
                dosage="500mg",
                frequency="Three times daily",
                duration="7 days",
                notes_encrypted=encryptor.encrypt("Complete full course even if symptoms improve")
            )
        ]
        db.session.add_all(prescriptions)
        
        db.session.commit()
        print("\n✅ Database seeded successfully!")
        print(f"   - 1 Hospital")
        print(f"   - {len(roles)} User Roles")
        print(f"   - {len(users)} Users")
        print(f"   - {len(patients)} Patients")
        print(f"   - {len(encounters)} Encounters")
        print(f"   - {len(observations)} Observations")
        print(f"   - {len(prescriptions)} Prescriptions")

if __name__ == "__main__":
    seed_database()
