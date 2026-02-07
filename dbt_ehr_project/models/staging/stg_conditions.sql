-- This is a  staging model for conditions
--  To Extract and standardize patient diagnoses

SELECT
    id AS condition_id,
    subject.reference AS patient_reference,
    REPLACE(subject.reference, 'Patient/', '') AS patient_id,
    code.coding[1].code AS icd10_code,
    code.coding[1].display AS condition_name,
    code.coding[1].system AS coding_system,
    clinicalStatus.coding[1].code AS clinical_status,
    CAST(onsetDateTime AS DATE) AS onset_date,
    DATE_DIFF('day', CAST(onsetDateTime AS DATE), CURRENT_DATE) AS days_since_onset
FROM {{ source('raw', 'raw_conditions') }}