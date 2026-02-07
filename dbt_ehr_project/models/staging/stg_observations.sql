-- This is a staging model for observations
-- To exract lab results and vital signs

SELECT
    id AS observation_id,
    subject.reference AS patient_reference,
    REPLACE(subject.reference, 'Patient/', '') AS patient_id,
    code.coding[1].code AS loinc_code,
    code.coding[1].display AS observation_name,
    status,
    valueQuantity.value AS value,
    valueQuantity.unit AS unit,
    CAST(effectiveDateTime AS DATE) AS observation_date,
    DATE_DIFF('day', CAST(effectiveDateTime AS DATE), CURRENT_DATE) AS days_since_observation
FROM {{ source('raw', 'raw_observations') }}