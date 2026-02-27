# Distributed EHR — Repository Summary

Brief local summary of the project for personal reference. This file is created locally and not pushed to any remote.

## What it is
- Flask-based Electronic Health Records (EHR) system providing REST APIs, data encryption, password hashing, PostgreSQL persistence, and Docker support.

## Key features
- CRUD APIs for Hospital, UserRole, User, Patient, Encounter, Observation, Prescription
- **New:** inter-node communication endpoints for cluster peers and simple Raft-style leader replication
- Encryption for patient PII and prescription notes (Fernet)
- Password hashing with Werkzeug
- Docker + Docker Compose for easy setup
- `seed.py` provides sample data

## How to run (short)
- Recommended: `docker-compose up --build`
- Seed data: `docker-compose exec app python seed.py`
- Manual: `pip install -r requirements.txt`, set `DATABASE_URL` in `config.py`, then `python app.py`

## API
- Base URL: http://localhost:5002
- Endpoints for hospitals, roles, users, patients, encounters, observations, prescriptions (see README.md for details)

## Security
- `ENCRYPTION_KEY` (Fernet) for encrypting PII and notes
- `SECRET_KEY` for Flask
- `DATABASE_URL` for PostgreSQL

## Main files
- `app/app.py` — Flask app & routes
- `app/database.py` — SQLAlchemy models
- `app/encryption.py` — encryption helpers
- `app/seed.py` — sample data
- `docker-compose.yml`, `Dockerfile`, `requirements.txt`

## Notes
- This summary is saved locally and was not committed or pushed. Ask if you want it committed locally or expanded.
