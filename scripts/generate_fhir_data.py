"""
Generate synthetic FHIR patient data for EHR analytics pipeline.
Creates realistic patient records with conditions, medications, and observations.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path


# Sample data for realistic generation
FIRST_NAMES = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]

# Type 2 Diabetes related conditions and medications
CONDITIONS = [
    {"code": "E11.9", "display": "Type 2 diabetes mellitus without complications"},
    {"code": "I10", "display": "Essential (primary) hypertension"},
    {"code": "E78.5", "display": "Hyperlipidemia"},
]

MEDICATIONS = [
    {"code": "860975", "display": "Metformin 500 MG"},
    {"code": "197494", "display": "Lisinopril 10 MG"},
    {"code": "617310", "display": "Atorvastatin 20 MG"},
]


def generate_patient(patient_id: int) -> dict:
    """Generate a synthetic FHIR Patient resource as dict."""
    birth_date = datetime.now() - timedelta(days=random.randint(18*365, 75*365))
    
    return {
        "resourceType": "Patient",
        "id": f"patient-{patient_id}",
        "name": [{
            "use": "official",
            "family": random.choice(LAST_NAMES),
            "given": [random.choice(FIRST_NAMES)]
        }],
        "gender": random.choice(["male", "female"]),
        "birthDate": birth_date.strftime("%Y-%m-%d")
    }


def generate_condition(patient_id: int, condition_id: int) -> dict:
    """Generate a synthetic FHIR Condition resource as dict."""
    condition_data = random.choice(CONDITIONS)
    onset_date = datetime.now() - timedelta(days=random.randint(30, 1825))
    
    return {
        "resourceType": "Condition",
        "id": f"condition-{condition_id}",
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": "active"
            }]
        },
        "code": {
            "coding": [{
                "system": "http://hl7.org/fhir/sid/icd-10",
                "code": condition_data["code"],
                "display": condition_data["display"]
            }]
        },
        "subject": {
            "reference": f"Patient/patient-{patient_id}"
        },
        "onsetDateTime": onset_date.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    }


def generate_medication(patient_id: int, med_id: int) -> dict:
    """Generate a synthetic FHIR MedicationRequest resource as dict."""
    med_data = random.choice(MEDICATIONS)
    authored_date = datetime.now() - timedelta(days=random.randint(1, 365))
    
    return {
        "resourceType": "MedicationRequest",
        "id": f"medication-{med_id}",
        "status": "active",
        "intent": "order",
        "medicationCodeableConcept": {
            "coding": [{
                "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                "code": med_data["code"],
                "display": med_data["display"]
            }]
        },
        "subject": {
            "reference": f"Patient/patient-{patient_id}"
        },
        "authoredOn": authored_date.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    }


def generate_observation(patient_id: int, obs_id: int, obs_type: str) -> dict:
    """Generate a synthetic FHIR Observation resource as dict."""
    obs_date = datetime.now() - timedelta(days=random.randint(1, 180))
    
    observation = {
        "resourceType": "Observation",
        "id": f"observation-{obs_id}",
        "status": "final",
        "subject": {
            "reference": f"Patient/patient-{patient_id}"
        },
        "effectiveDateTime": obs_date.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    }
    
    if obs_type == "hba1c":
        observation["code"] = {
            "coding": [{
                "system": "http://loinc.org",
                "code": "4548-4",
                "display": "Hemoglobin A1c/Hemoglobin.total in Blood"
            }]
        }
        observation["valueQuantity"] = {
            "value": round(random.uniform(5.5, 9.5), 1),
            "unit": "%",
            "system": "http://unitsofmeasure.org",
            "code": "%"
        }
    elif obs_type == "glucose":
        observation["code"] = {
            "coding": [{
                "system": "http://loinc.org",
                "code": "2339-0",
                "display": "Glucose [Mass/volume] in Blood"
            }]
        }
        observation["valueQuantity"] = {
            "value": random.randint(80, 200),
            "unit": "mg/dL",
            "system": "http://unitsofmeasure.org",
            "code": "mg/dL"
        }
    
    return observation


def generate_clinical_note(patient_id: int, note_id: int) -> dict:
    """Generate a synthetic clinical note (unstructured text for LLM extraction)."""
    templates = [
        f"Patient presents for routine follow-up. Type 2 Diabetes well controlled on Metformin. HbA1c {round(random.uniform(6.0, 8.5), 1)}%. Blood pressure {random.randint(110, 140)}/{random.randint(70, 90)}. Continue current medications.",
        f"Patient reports increased fatigue. Review of labs shows HbA1c {round(random.uniform(7.5, 9.5), 1)}%. Discussed medication adherence. Added Lisinopril for hypertension management.",
        f"Routine diabetes check. Patient doing well. Recent HbA1c {round(random.uniform(5.5, 7.0), 1)}%. No acute concerns. Schedule follow-up in 3 months.",
    ]
    
    return {
        "id": f"note-{note_id}",
        "patient_id": f"patient-{patient_id}",
        "date": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
        "text": random.choice(templates)
    }


def generate_dataset(num_patients: int = 50):
    """Generate complete synthetic dataset."""
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_patients = []
    all_conditions = []
    all_medications = []
    all_observations = []
    all_notes = []
    
    condition_id = 1
    med_id = 1
    obs_id = 1
    note_id = 1
    
    print(f"Generating {num_patients} synthetic patients...")
    
    for patient_id in range(1, num_patients + 1):
        # Generate patient
        patient = generate_patient(patient_id)
        all_patients.append(patient)
        
        # Generate 1-3 conditions per patient
        num_conditions = random.randint(1, 3)
        for _ in range(num_conditions):
            condition = generate_condition(patient_id, condition_id)
            all_conditions.append(condition)
            condition_id += 1
        
        # Generate 1-3 medications per patient
        num_meds = random.randint(1, 3)
        for _ in range(num_meds):
            medication = generate_medication(patient_id, med_id)
            all_medications.append(medication)
            med_id += 1
        
        # Generate observations (HbA1c and glucose)
        for obs_type in ["hba1c", "glucose"]:
            observation = generate_observation(patient_id, obs_id, obs_type)
            all_observations.append(observation)
            obs_id += 1
        
        # Generate 1-2 clinical notes
        num_notes = random.randint(1, 2)
        for _ in range(num_notes):
            note = generate_clinical_note(patient_id, note_id)
            all_notes.append(note)
            note_id += 1
    
    # Save to files
    with open(output_dir / "patients.json", "w") as f:
        json.dump(all_patients, f, indent=2)
    
    with open(output_dir / "conditions.json", "w") as f:
        json.dump(all_conditions, f, indent=2)
    
    with open(output_dir / "medications.json", "w") as f:
        json.dump(all_medications, f, indent=2)
    
    with open(output_dir / "observations.json", "w") as f:
        json.dump(all_observations, f, indent=2)
    
    with open(output_dir / "clinical_notes.json", "w") as f:
        json.dump(all_notes, f, indent=2)
    
    print(f" Generated {len(all_patients)} patients")
    print(f" Generated {len(all_conditions)} conditions")
    print(f" Generated {len(all_medications)} medications")
    print(f" Generated {len(all_observations)} observations")
    print(f" Generated {len(all_notes)} clinical notes")
    print(f"\nData saved to {output_dir}")


if __name__ == "__main__":
    generate_dataset(num_patients=50)