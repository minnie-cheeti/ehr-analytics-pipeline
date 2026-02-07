-- Clinical trial eligible cohort: Type 2 Diabetes
-- Identifies patients eligible for diabetes drug trials
-- Inclusion: Age 18-65, T2DM, HbA1c > 7.5%, on Metformin, no heart failure

SELECT
    patient_id,
    first_name,
    last_name,
    age,
    latest_hba1c,
    hba1c_date,
    total_conditions,
    total_medications,
    'Eligible for T2DM Trial' AS trial_status,
    CASE
        WHEN latest_hba1c > 9.0 THEN 'High Priority'
        WHEN latest_hba1c > 8.0 THEN 'Medium Priority'
        ELSE 'Standard Priority'
    END AS recruitment_priority
FROM {{ ref('patient_clinical_summary') }}
WHERE 1=1
    AND age BETWEEN 18 AND 65
    AND has_type2_diabetes = 1
    AND latest_hba1c > 7.5
    AND on_metformin = 1
ORDER BY latest_hba1c DESC