from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()


class Hospital(db.Model):
    __tablename__ = "hospital"

    hospital_id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(64), unique=True, index=True, nullable=False)

    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    users = db.relationship("User", back_populates="hospital", cascade="all, delete-orphan")
    encounters = db.relationship("Encounter", back_populates="hospital", cascade="all, delete-orphan")


class UserRole(db.Model):
    __tablename__ = "user_role"

    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    users = db.relationship("User", back_populates="role")


class User(db.Model):
    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(64), unique=True, index=True, nullable=False)

    hospital_id = db.Column(db.Integer, db.ForeignKey("hospital.hospital_id", ondelete="RESTRICT"), nullable=False)

    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    role_id = db.Column(db.Integer, db.ForeignKey("user_role.role_id", ondelete="RESTRICT"), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    hospital = db.relationship("Hospital", back_populates="users")
    role = db.relationship("UserRole", back_populates="users")

    # As doctor in encounters/prescriptions
    doctor_encounters = db.relationship(
        "Encounter",
        back_populates="doctor",
        foreign_keys="Encounter.doctor_id",
    )
    doctor_prescriptions = db.relationship(
        "Prescription",
        back_populates="doctor",
        foreign_keys="Prescription.doctor_id",
    )


class Patient(db.Model):
    __tablename__ = "patient"

    patient_id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(64), unique=True, index=True, nullable=False)

    full_name_encrypted = db.Column(db.Text, nullable=False)
    date_of_birth_encrypted = db.Column(db.Text, nullable=False)

    gender = db.Column(db.String(50), nullable=True)

    phone_encrypted = db.Column(db.Text, nullable=True)
    address_encrypted = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    encounters = db.relationship("Encounter", back_populates="patient", cascade="all, delete-orphan")
    observations = db.relationship("Observation", back_populates="patient", cascade="all, delete-orphan")
    prescriptions = db.relationship("Prescription", back_populates="patient", cascade="all, delete-orphan")


class Encounter(db.Model):
    __tablename__ = "encounter"

    encounter_id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey("patient.patient_id", ondelete="CASCADE"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.user_id", ondelete="RESTRICT"), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospital.hospital_id", ondelete="RESTRICT"), nullable=False)

    visit_type = db.Column(db.String(100), nullable=False)
    visit_reason = db.Column(db.Text, nullable=True)
    visit_date = db.Column(db.DateTime(timezone=True), nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    patient = db.relationship("Patient", back_populates="encounters")
    doctor = db.relationship("User", back_populates="doctor_encounters", foreign_keys=[doctor_id])
    hospital = db.relationship("Hospital", back_populates="encounters")

    observations = db.relationship("Observation", back_populates="encounter", cascade="all, delete-orphan")
    prescriptions = db.relationship("Prescription", back_populates="encounter", cascade="all, delete-orphan")


class Observation(db.Model):
    __tablename__ = "observation"

    observation_id = db.Column(db.Integer, primary_key=True)

    encounter_id = db.Column(db.Integer, db.ForeignKey("encounter.encounter_id", ondelete="CASCADE"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.patient_id", ondelete="CASCADE"), nullable=False)

    type = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(50), nullable=True)

    recorded_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    encounter = db.relationship("Encounter", back_populates="observations")
    patient = db.relationship("Patient", back_populates="observations")


class Prescription(db.Model):
    __tablename__ = "prescription"

    prescription_id = db.Column(db.Integer, primary_key=True)

    encounter_id = db.Column(db.Integer, db.ForeignKey("encounter.encounter_id", ondelete="CASCADE"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.patient_id", ondelete="CASCADE"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.user_id", ondelete="RESTRICT"), nullable=False)

    medication = db.Column(db.String(255), nullable=False)

    # ERD says "doage" (typo). Use "dosage" in code, but map to "doage" if you want exact DB column name.
    dosage = db.Column("doage", db.Column(db.String(100)).type, nullable=True)

    frequency = db.Column(db.String(100), nullable=True)
    duration = db.Column(db.String(100), nullable=True)

    notes_encrypted = db.Column(db.Text, nullable=True)
    prescribed_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    encounter = db.relationship("Encounter", back_populates="prescriptions")
    patient = db.relationship("Patient", back_populates="prescriptions")
    doctor = db.relationship("User", back_populates="doctor_prescriptions", foreign_keys=[doctor_id])
