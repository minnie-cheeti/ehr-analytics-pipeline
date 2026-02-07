-- This is a taging model for medications
--  To extract medication prescriptions and details

SELECT
    id AS medication_id,
    subject.reference AS patient_reference,
    REPLACE(subject.reference, 'Patient/', '') AS patient_id,
    medicationCodeableConcept.coding[1].code AS rxnorm_code,
    medicationCodeableConcept.coding[1].display AS medication_name,
    status,
    intent,
    CAST(authoredOn AS DATE) AS prescribed_date,
    DATE_DIFF('day', CAST(authoredOn AS DATE), CURRENT_DATE) AS days_since_prescribed
FROM {{ source('raw', 'raw_medications') }}