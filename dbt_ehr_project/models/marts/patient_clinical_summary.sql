-- Patient clinical summary
-- Combines demographics, conditions, medications, and latest labs
-- Used for patient cohort identification and clinical trial matching

WITH latest_hba1c AS (
    SELECT 
        patient_id,
        value AS latest_hba1c,
        observation_date AS hba1c_date
    FROM {{ ref('stg_observations') }}
    WHERE loinc_code = '4548-4'  -- HbA1c code
    QUALIFY ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY observation_date DESC) = 1
),

latest_glucose AS (
    SELECT 
        patient_id,
        value AS latest_glucose,
        observation_date AS glucose_date
    FROM {{ ref('stg_observations') }}
    WHERE loinc_code = '2339-0'  -- Glucose code
    QUALIFY ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY observation_date DESC) = 1
),

condition_summary AS (
    SELECT
        patient_id,
        COUNT(*) AS total_conditions,
        MAX(CASE WHEN icd10_code LIKE 'E11%' THEN 1 ELSE 0 END) AS has_type2_diabetes,
        MAX(CASE WHEN icd10_code = 'I10' THEN 1 ELSE 0 END) AS has_hypertension,
        MAX(CASE WHEN icd10_code = 'E78.5' THEN 1 ELSE 0 END) AS has_hyperlipidemia
    FROM {{ ref('stg_conditions') }}
    GROUP BY patient_id
),

medication_summary AS (
    SELECT
        patient_id,
        COUNT(*) AS total_medications,
        MAX(CASE WHEN medication_name LIKE '%Metformin%' THEN 1 ELSE 0 END) AS on_metformin,
        MAX(CASE WHEN medication_name LIKE '%Lisinopril%' THEN 1 ELSE 0 END) AS on_lisinopril
    FROM {{ ref('stg_medications') }}
    WHERE status = 'active'
    GROUP BY patient_id
)

SELECT
    p.patient_id,
    p.first_name,
    p.last_name,
    p.gender,
    p.age,
    p.age_group,
    COALESCE(cs.total_conditions, 0) AS total_conditions,
    COALESCE(cs.has_type2_diabetes, 0) AS has_type2_diabetes,
    COALESCE(cs.has_hypertension, 0) AS has_hypertension,
    COALESCE(cs.has_hyperlipidemia, 0) AS has_hyperlipidemia,
    COALESCE(ms.total_medications, 0) AS total_medications,
    COALESCE(ms.on_metformin, 0) AS on_metformin,
    COALESCE(ms.on_lisinopril, 0) AS on_lisinopril,
    h.latest_hba1c,
    h.hba1c_date,
    g.latest_glucose,
    g.glucose_date
FROM {{ ref('stg_patients') }} p
LEFT JOIN condition_summary cs ON p.patient_id = cs.patient_id
LEFT JOIN medication_summary ms ON p.patient_id = ms.patient_id
LEFT JOIN latest_hba1c h ON p.patient_id = h.patient_id
LEFT JOIN latest_glucose g ON p.patient_id = g.patient_id 