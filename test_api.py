#!/usr/bin/env python3
"""
Simple test script to verify API endpoints
Run this after seeding the database
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_health():
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_hospitals():
    print("\n=== Testing Hospitals ===")
    response = requests.get(f"{BASE_URL}/hospitals")
    print(f"Status: {response.status_code}")
    hospitals = response.json()
    print(f"Found {len(hospitals)} hospital(s)")
    if hospitals:
        print(f"First hospital: {hospitals[0]['name']}")

def test_users():
    print("\n=== Testing Users ===")
    response = requests.get(f"{BASE_URL}/users")
    print(f"Status: {response.status_code}")
    users = response.json()
    print(f"Found {len(users)} user(s)")
    for user in users[:3]:
        print(f"  - {user['full_name']} ({user['email']})")

def test_patients():
    print("\n=== Testing Patients (with decryption) ===")
    response = requests.get(f"{BASE_URL}/patients")
    print(f"Status: {response.status_code}")
    patients = response.json()
    print(f"Found {len(patients)} patient(s)")
    for patient in patients[:3]:
        print(f"  - {patient['full_name']} (DOB: {patient['date_of_birth']})")

def test_encounters():
    print("\n=== Testing Encounters ===")
    response = requests.get(f"{BASE_URL}/encounters")
    print(f"Status: {response.status_code}")
    encounters = response.json()
    print(f"Found {len(encounters)} encounter(s)")
    for encounter in encounters[:3]:
        print(f"  - Visit Type: {encounter['visit_type']} (Reason: {encounter['visit_reason']})")

def test_observations():
    print("\n=== Testing Observations ===")
    response = requests.get(f"{BASE_URL}/observations")
    print(f"Status: {response.status_code}")
    observations = response.json()
    print(f"Found {len(observations)} observation(s)")
    for obs in observations[:3]:
        print(f"  - {obs['type']}: {obs['value']} {obs['unit']}")

def test_prescriptions():
    print("\n=== Testing Prescriptions (with decrypted notes) ===")
    response = requests.get(f"{BASE_URL}/prescriptions")
    print(f"Status: {response.status_code}")
    prescriptions = response.json()
    print(f"Found {len(prescriptions)} prescription(s)")
    for rx in prescriptions[:3]:
        print(f"  - {rx['medication']} ({rx['dosage']}) - {rx['frequency']}")
        if rx['notes']:
            print(f"    Notes: {rx['notes']}")

def test_create_patient():
    print("\n=== Testing Create Patient ===")
    new_patient = {
        "full_name": "Test Patient",
        "date_of_birth": "1995-05-20",
        "gender": "Male",
        "phone": "555-9999",
        "address": "999 Test St"
    }
    response = requests.post(f"{BASE_URL}/patients", json=new_patient)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        patient = response.json()
        print(f"Created patient: {patient['full_name']} (ID: {patient['patient_id']})")
        return patient['patient_id']
    return None

def test_update_patient(patient_id):
    if not patient_id:
        return
    print(f"\n=== Testing Update Patient {patient_id} ===")
    update_data = {
        "phone": "555-8888"
    }
    response = requests.put(f"{BASE_URL}/patients/{patient_id}", json=update_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_delete_patient(patient_id):
    if not patient_id:
        return
    print(f"\n=== Testing Delete Patient {patient_id} ===")
    response = requests.delete(f"{BASE_URL}/patients/{patient_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    print("=" * 60)
    print("EHR API Test Suite")
    print("=" * 60)
    
    try:
        test_health()
        test_hospitals()
        test_users()
        test_patients()
        test_encounters()
        test_observations()
        test_prescriptions()
        
        # Test CRUD operations
        patient_id = test_create_patient()
        test_update_patient(patient_id)
        test_delete_patient(patient_id)
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API server.")
        print("   Make sure the app is running: docker-compose up")
    except Exception as e:
        print(f"\n❌ Error: {e}")
